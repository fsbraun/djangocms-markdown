from cms.app_base import CMSAppConfig
from django import forms

from tests.cms_config import INSERT, SHARED_JS

ADMONITION = "markdown.extensions.admonition"
INSERT_JS = '<script src="/static/other_app/insert.js"></script>'


def assets(html):
    """Only content with an <ins> tag needs assets."""
    if "<ins" not in html:
        return None
    return {"js": [SHARED_JS, INSERT_JS]}


def editor_media():
    return forms.Media(js=["other_app/preview.js"])


class OtherAppCMSConfig(CMSAppConfig):
    djangocms_markdown_enabled = True
    # INSERT is also contributed by "tests", sane_lists is a project default
    djangocms_markdown_extensions = [
        INSERT,
        "markdown.extensions.sane_lists",
        ADMONITION,
    ]
    djangocms_markdown_extension_configs = {
        INSERT: {"css_class": "other-ins"},
    }
    djangocms_markdown_assets = assets
    djangocms_markdown_editor_media = editor_media
