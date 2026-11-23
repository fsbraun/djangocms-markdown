from djangocms_markdown.widgets import MarkdownEditorWidget

from .utils import media_paths


class TestMarkdownEditorWidget:
    def test_default_attrs(self):
        widget = MarkdownEditorWidget()
        assert "markdown-editor" in widget.attrs.get("class", "")

    def test_custom_attrs_merged(self):
        widget = MarkdownEditorWidget(attrs={"id": "my-editor"})
        assert widget.attrs["id"] == "my-editor"
        assert "markdown-editor" in widget.attrs.get("class", "")

    def test_media_cdn(self):
        widget = MarkdownEditorWidget()
        media = widget.media
        css = str(media)
        js = str(media)
        assert "easymde.min.css" in css
        assert "easymde.min.js" in js
        assert "markdown_editor.css" in css
        assert "markdown_editor.js" in js

    def test_media_contains_custom_files(self):
        widget = MarkdownEditorWidget()
        js_list, css_list = media_paths(widget.media)
        assert any("markdown_editor.js" in f for f in js_list)
        assert any("markdown_editor.css" in f for f in css_list)

    def test_render(self):
        widget = MarkdownEditorWidget()
        html = widget.render("body", "# Hello", attrs={"id": "id_body"})
        assert "id_body" in html
        assert "markdown-editor" in html

    def test_render_with_value(self):
        widget = MarkdownEditorWidget()
        html = widget.render("body", "**bold**", attrs={"id": "id_body"})
        assert "**bold**" in html
