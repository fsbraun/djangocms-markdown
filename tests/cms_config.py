from cms.app_base import CMSAppConfig
from django import forms

MARK = "tests.markdown_ext:MarkExtension"
INSERT = "tests.markdown_ext:InsertExtension"

MARK_CSS = '<link rel="stylesheet" href="/static/tests/mark.css">'
SHARED_JS = '<script defer src="/static/tests/shared.js" data-config="{}"></script>'


class TestsCMSConfig(CMSAppConfig):
    djangocms_markdown_enabled = True
    djangocms_markdown_extensions = [MARK, INSERT]
    djangocms_markdown_extension_configs = {
        INSERT: {"css_class": "tests-ins", "role": "note"},
    }
    djangocms_markdown_assets = {"css": [MARK_CSS], "js": [SHARED_JS]}
    djangocms_markdown_editor_media = forms.Media(
        css={"all": ["tests/preview.css"]},
        js=["tests/preview.js"],
    )
