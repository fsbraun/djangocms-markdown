from django import forms

from .settings import EASYMDE_CDN_BASE


class MarkdownEditorWidget(forms.Textarea):
    """A textarea widget that initializes EasyMDE markdown editor."""

    template_name = "djangocms_markdown/widgets/markdown_editor.html"

    def __init__(self, attrs=None):
        default_attrs = {"class": "markdown-editor"}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)

    @property
    def media(self):
        css_files = []
        js_files = []

        if EASYMDE_CDN_BASE:
            css_files.append(f"{EASYMDE_CDN_BASE}/easymde.min.css")
            js_files.append(f"{EASYMDE_CDN_BASE}/easymde.min.js")
        else:
            css_files.append("djangocms_markdown/css/easymde.min.css")
            js_files.append("djangocms_markdown/js/easymde.min.js")

        css_files.append("djangocms_markdown/css/markdown_editor.css")
        js_files.append("djangocms_markdown/js/markdown_editor.js")

        return forms.Media(
            css={"all": css_files},
            js=js_files,
        )
