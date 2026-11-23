from unittest.mock import patch

import cms.app_base
import pytest
from cms.models import Placeholder
from cms.plugin_rendering import ContentRenderer
from django import forms
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ImproperlyConfigured
from django.template import Context, Template
from django.test import RequestFactory
from sekizai.context import SekizaiContext
from sekizai.helpers import get_varname

from djangocms_markdown import registry, rendering
from djangocms_markdown.models import MDText
from djangocms_markdown.settings import MARKDOWN_EXTENSION_CONFIGS, MARKDOWN_EXTENSIONS
from djangocms_markdown.widgets import MarkdownEditorWidget

from .utils import media_paths

# django CMS 3.11 has no cms_config support: the test apps' cms_config.py files
# are never loaded there (and cannot be imported).
HAS_CMS_CONFIG = hasattr(cms.app_base, "CMSAppConfig")
requires_cms_config = pytest.mark.skipif(
    not HAS_CMS_CONFIG, reason="django CMS without cms_config support"
)

MARK = "tests.markdown_ext:MarkExtension"
INSERT = "tests.markdown_ext:InsertExtension"
ADMONITION = "markdown.extensions.admonition"
MARK_CSS = '<link rel="stylesheet" href="/static/tests/mark.css">'
SHARED_JS = '<script defer src="/static/tests/shared.js" data-config="{}"></script>'
INSERT_JS = '<script src="/static/other_app/insert.js"></script>'


@pytest.fixture
def no_contributions(monkeypatch):
    """Run a test as if no app contributed anything."""
    monkeypatch.setattr(registry, "_contributions", [])


def make_plugin(body):
    placeholder = Placeholder.objects.create(slot="test")
    instance = MDText(
        body=body,
        placeholder=placeholder,
        position=1,
        language="en",
        plugin_type="MDTextPlugin",
    )
    instance.save()
    return instance


def render_plugin(instance, context):
    """Render a plugin the way django CMS does when rendering a page."""
    request = RequestFactory().get("/")
    request.user = AnonymousUser()
    request.session = {}
    context["request"] = request
    return ContentRenderer(request).render_plugin(instance, context)


def render_blocks(context):
    """Render the sekizai blocks (sekizai ends each block with a newline)."""
    template = Template(
        '{% load sekizai_tags %}{% render_block "css" %}|{% render_block "js" %}'
    )
    return template.render(context)


@requires_cms_config
class TestCMSConfigRegistration:
    """Contributions of "tests" and "tests.other_app" via their cms_config.py."""

    def test_constants_match_cms_configs(self):
        from tests import cms_config
        from tests.other_app import cms_config as other_cms_config

        assert (MARK, INSERT) == (cms_config.MARK, cms_config.INSERT)
        assert (MARK_CSS, SHARED_JS) == (cms_config.MARK_CSS, cms_config.SHARED_JS)
        assert INSERT_JS == other_cms_config.INSERT_JS

    def test_apps_registered_in_installed_apps_order(self):
        apps = [c.app for c in registry.get_contributions()]
        assert apps == ["tests", "tests.other_app"]

    def test_contributed_extensions_applied(self):
        html = rendering.render_markdown("==marked== and ++inserted++")
        assert "<mark>marked</mark>" in html
        assert ">inserted</ins>" in html
        html = rendering.render_markdown("!!! note\n    Careful")
        assert 'class="admonition note"' in html

    def test_contributed_extensions_applied_on_plugin_save(self, db):
        instance = make_plugin("==marked==")
        assert "<mark>marked</mark>" in instance.body_rendered

    def test_extension_order_and_deduplication(self):
        # Settings first, then contributions in INSTALLED_APPS order. INSERT
        # (contributed twice) and sane_lists (in the settings and contributed)
        # appear once.
        assert rendering.get_extensions() == [
            *MARKDOWN_EXTENSIONS,
            MARK,
            INSERT,
            ADMONITION,
        ]

    def test_settings_extensions_come_first(self):
        with patch.object(rendering, "MARKDOWN_EXTENSIONS", [ADMONITION, INSERT]):
            assert rendering.get_extensions() == [
                ADMONITION,
                INSERT,
                MARK,
                "markdown.extensions.sane_lists",
            ]

    def test_extension_configs_first_app_wins(self):
        configs = rendering.get_extension_configs()
        assert configs[INSERT] == {"css_class": "tests-ins", "role": "note"}
        for name, config in MARKDOWN_EXTENSION_CONFIGS.items():
            assert configs[name] == config
        html = rendering.render_markdown("++inserted++")
        assert '<ins class="tests-ins" role="note">inserted</ins>' in html

    def test_project_extension_configs_win(self):
        project = {INSERT: {"css_class": "project"}}
        with patch.object(rendering, "MARKDOWN_EXTENSION_CONFIGS", project):
            configs = rendering.get_extension_configs()
            html = rendering.render_markdown("++inserted++")
        # Options are merged per extension; the project's value wins
        assert configs == {INSERT: {"css_class": "project", "role": "note"}}
        assert '<ins class="project" role="note">inserted</ins>' in html

    def test_configs_are_not_mutated(self):
        before = registry.get_contributions()[0].extension_configs[INSERT].copy()
        with patch.object(
            rendering, "MARKDOWN_EXTENSION_CONFIGS", {INSERT: {"css_class": "x"}}
        ):
            rendering.get_extension_configs()
        assert registry.get_contributions()[0].extension_configs[INSERT] == before
        assert INSERT not in MARKDOWN_EXTENSION_CONFIGS

    def test_assets_dict_and_callable_returning_none(self):
        # "tests" contributes a dict, "tests.other_app" a callable that needs
        # nothing for this content
        assert rendering.get_assets("<p>plain</p>") == {
            "css": [MARK_CSS],
            "js": [SHARED_JS],
        }

    def test_assets_callable_merged_without_duplicates(self):
        assert rendering.get_assets("<p><ins>x</ins></p>") == {
            "css": [MARK_CSS],
            "js": [SHARED_JS, INSERT_JS],
        }

    def test_plugin_adds_assets_to_sekizai_blocks(self, db):
        context = SekizaiContext()
        content = render_plugin(make_plugin("++inserted++"), context)
        # Assets are not part of the plugin's own output
        assert content == '<p><ins class="tests-ins" role="note">inserted</ins></p>'
        assert render_blocks(context) == f"{MARK_CSS}\n|{SHARED_JS}\n{INSERT_JS}\n"

    def test_plugin_assets_deduplicated_across_plugins(self, db):
        context = SekizaiContext()
        render_plugin(make_plugin("++one++"), context)
        render_plugin(make_plugin("==two=="), context)
        render_plugin(make_plugin("++three++"), context)
        assert render_blocks(context) == f"{MARK_CSS}\n|{SHARED_JS}\n{INSERT_JS}\n"

    def test_plugin_assets_not_stored_at_save_time(self, db):
        instance = make_plugin("++inserted++")
        assert "<script" not in instance.body_rendered
        assert "<link" not in instance.body_rendered

    def test_plugin_renders_without_sekizai_context(self, db):
        content = render_plugin(make_plugin("==marked=="), Context())
        assert content == "<p><mark>marked</mark></p>"

    def test_template_tag_adds_assets(self):
        template = Template(
            "{% load djangocms_markdown_tags sekizai_tags %}"
            '{% render_block "css" %}|'
            "{% with html=content|render_markdown %}"
            "{{ html }}{% markdown_assets html %}"
            "{% endwith %}"
            '|{% render_block "js" %}'
        )
        rendered = template.render(SekizaiContext({"content": "++inserted++"}))
        assert rendered == (
            f"{MARK_CSS}\n|"
            '<p><ins class="tests-ins" role="note">inserted</ins></p>'
            f"|{SHARED_JS}\n{INSERT_JS}\n"
        )

    def test_template_tag_without_sekizai_context(self):
        template = Template(
            "{% load djangocms_markdown_tags %}"
            "{{ content|render_markdown }}"
            "{% markdown_assets content|render_markdown %}"
        )
        rendered = template.render(Context({"content": "==marked=="}))
        assert rendered == "<p><mark>marked</mark></p>"

    def test_widget_media_merged_after_own_files(self):
        js, css = media_paths(MarkdownEditorWidget().media)
        own_js = js.index("djangocms_markdown/js/markdown_editor.js")
        own_css = css.index("djangocms_markdown/css/preview_typography.css")
        # Contributions follow the widget's files, in INSTALLED_APPS order
        assert js[own_js + 1 :] == ["tests/preview.js", "other_app/preview.js"]
        assert css[own_css + 1 :] == ["tests/preview.css"]
        assert any("easymde.min.js" in path for path in js[:own_js])


class FakeAppConfig:
    name = "broken_app"


def configure(**attrs):
    """Run a declaration through the real CMS extension."""
    from cms.app_base import CMSAppConfig

    from djangocms_markdown.cms_config import MarkdownCMSExtension

    attrs = {"djangocms_markdown_enabled": True, **attrs}
    config_class = type("BrokenCMSConfig", (CMSAppConfig,), attrs)
    MarkdownCMSExtension().configure_app(config_class(FakeAppConfig()))


@requires_cms_config
class TestDeclarationValidation:
    @pytest.mark.parametrize(
        "attrs",
        [
            {"djangocms_markdown_extensions": "my_app.markdown"},
            {"djangocms_markdown_extensions": [1]},
            {"djangocms_markdown_extensions": ["no_such_module.markdown"]},
            {"djangocms_markdown_extensions": ["tests.markdown_ext:Missing"]},
            {
                "djangocms_markdown_extensions": [INSERT],
                "djangocms_markdown_extension_configs": {INSERT: {"unknown": 1}},
            },
            {"djangocms_markdown_extensions": {"my_app.markdown": {}}},
            {"djangocms_markdown_extension_configs": ["my_app.markdown"]},
            {"djangocms_markdown_extension_configs": {"my_app.markdown": "x"}},
            {"djangocms_markdown_extension_configs": {1: {}}},
            {"djangocms_markdown_assets": ["<script></script>"]},
            {"djangocms_markdown_assets": "<script></script>"},
            {"djangocms_markdown_assets": {"js": "<script></script>"}},
            {"djangocms_markdown_assets": {"js": [1]}},
            {"djangocms_markdown_assets": {1: []}},
            {"djangocms_markdown_editor_media": ["my_app/preview.js"]},
            {"djangocms_markdown_editor_media": {"js": ["my_app/preview.js"]}},
        ],
    )
    def test_invalid_declaration(self, attrs):
        before = registry.get_contributions()
        with pytest.raises(ImproperlyConfigured, match="^broken_app: djangocms_"):
            configure(**attrs)
        # Nothing is registered for the offending app
        assert registry.get_contributions() == before

    def test_all_attributes_optional(self, no_contributions):
        configure()
        (contribution,) = registry.get_contributions()
        assert contribution.app == "broken_app"
        assert rendering.get_extensions() == list(MARKDOWN_EXTENSIONS)
        assert rendering.get_assets("<p>x</p>") == {}
        assert registry.get_editor_media() is None

    def test_functions_are_not_bound_to_the_config(self, no_contributions):
        def assets(html):
            return {"js": [f"<!-- {html} -->"]}

        def editor_media():
            return forms.Media(js=["x.js"])

        configure(
            djangocms_markdown_assets=assets,
            djangocms_markdown_editor_media=editor_media,
        )
        assert rendering.get_assets("x") == {"js": ["<!-- x -->"]}
        assert media_paths(registry.get_editor_media()) == (["x.js"], [])

    def test_staticmethod_declarations(self, no_contributions):
        configure(djangocms_markdown_assets=staticmethod(lambda html: None))
        assert rendering.get_assets("x") == {}


class TestRegistry:
    """The registry itself; needs no cms_config support."""

    @pytest.mark.skipif(HAS_CMS_CONFIG, reason="django CMS loads cms_config.py")
    def test_cms_config_never_imported_without_support(self):
        import sys

        import djangocms_markdown.cms_plugins
        import djangocms_markdown.fields  # noqa: F401

        assert "djangocms_markdown.cms_config" not in sys.modules
        assert registry.get_contributions() == []

    def test_register_replaces_earlier_contribution(self, no_contributions):
        abbr, nl2br = "markdown.extensions.abbr", "markdown.extensions.nl2br"
        registry.register("app_a", extensions=[abbr])
        registry.register("app_b", extensions=[ADMONITION])
        registry.register("app_a", extensions=[nl2br])
        assert [c.app for c in registry.get_contributions()] == ["app_a", "app_b"]
        with patch.object(rendering, "MARKDOWN_EXTENSIONS", [ADMONITION]):
            assert rendering.get_extensions() == [ADMONITION, nl2br]

    def test_extension_instances_rejected(self, no_contributions):
        # A shared instance would leak state between renders (and requests)
        from tests.markdown_ext import MarkExtension

        with pytest.raises(ImproperlyConfigured, match="^app_a: .*not extension"):
            registry.register("app_a", extensions=[MarkExtension()])
        assert registry.get_contributions() == []

    def test_contributed_extension_state_not_shared_between_renders(
        self, no_contributions
    ):
        registry.register("app_a", extensions=["markdown.extensions.footnotes"])
        first = rendering.render_markdown("Private[^1]\n\n[^1]: secret note")
        second = rendering.render_markdown("Public text")
        assert "secret note" in first
        assert "secret note" not in second
        assert "footnote" not in second

    def test_callables_not_called_on_registration(self, no_contributions):
        def fail(*args):
            raise AssertionError("called too early")

        registry.register("app_a", assets=fail, editor_media=fail)

    def test_invalid_assets_callable_result(self, no_contributions):
        registry.register("app_a", assets=lambda html: ["<script></script>"])
        with pytest.raises(ImproperlyConfigured, match="^app_a: "):
            rendering.get_assets("<p>x</p>")

    def test_invalid_editor_media_callable_result(self, no_contributions):
        registry.register("app_a", editor_media=lambda: ["x.js"])
        with pytest.raises(ImproperlyConfigured, match="^app_a: "):
            str(MarkdownEditorWidget().media)

    def test_assets_callable_receives_rendered_html(self, no_contributions, db):
        seen = []
        registry.register("app_a", assets=lambda html: seen.append(html))
        render_plugin(make_plugin("**bold**"), SekizaiContext())
        assert seen == ["<p><strong>bold</strong></p>"]


class TestWithoutContributions:
    """Without contributions everything behaves as before the hooks existed."""

    def test_extensions_and_configs_from_settings_only(self, no_contributions):
        assert rendering.get_extensions() == list(MARKDOWN_EXTENSIONS)
        assert rendering.get_extension_configs() == MARKDOWN_EXTENSION_CONFIGS

    def test_rendering_unchanged(self, no_contributions):
        text = "==marked== ++inserted++\n\n| a |\n|---|\n| b |"
        import markdown

        from djangocms_markdown.sanitizer import sanitize_html

        md = markdown.Markdown(
            extensions=MARKDOWN_EXTENSIONS,
            extension_configs=MARKDOWN_EXTENSION_CONFIGS,
            output_format="html",
        )
        expected = sanitize_html(
            md.convert(text).replace("<table>", '<table class="table">')
        )
        assert "==marked== ++inserted++" in expected
        assert rendering.render_markdown(text) == expected

    def test_no_assets(self, no_contributions):
        assert rendering.get_assets("<p><ins>x</ins></p>") == {}

    def test_plugin_output_and_sekizai_untouched(self, no_contributions, db):
        context = SekizaiContext()
        content = render_plugin(make_plugin("**hello**"), context)
        assert content == "<p><strong>hello</strong></p>"
        assert not context[get_varname()]
        assert render_blocks(context) == "\n|\n"

    def test_plugin_template_unchanged(self):
        from django.template.loader import get_template

        template = get_template("djangocms_markdown/plugins/markdown.html")
        assert template.template.source == "{{ body|safe }}"

    def test_template_tag_outputs_nothing(self, no_contributions):
        template = Template(
            "{% load djangocms_markdown_tags %}"
            "{{ content|render_markdown }}{% markdown_assets content %}"
        )
        context = SekizaiContext({"content": "**hello**"})
        assert template.render(context) == "<p><strong>hello</strong></p>"
        assert not context[get_varname()]

    def test_widget_media_unchanged(self, no_contributions):
        js, css = media_paths(MarkdownEditorWidget().media)
        assert js[-1] == "djangocms_markdown/js/markdown_editor.js"
        assert css[-2:] == [
            "djangocms_markdown/css/markdown_editor.css",
            "djangocms_markdown/css/preview_typography.css",
        ]
        assert "preview" not in " ".join(js)
