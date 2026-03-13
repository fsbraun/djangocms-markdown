import pytest

from djangocms_markdown.forms import MDTextForm
from djangocms_markdown.widgets import MarkdownEditorWidget


class TestMDTextForm:
    def test_form_has_body_field(self):
        form = MDTextForm()
        assert "body" in form.fields

    def test_body_uses_markdown_widget(self):
        form = MDTextForm()
        assert isinstance(form.fields["body"].widget, MarkdownEditorWidget)

    def test_body_not_required(self):
        form = MDTextForm()
        assert not form.fields["body"].required

    def test_valid_form(self):
        form = MDTextForm(data={"body": "# Hello"})
        assert form.is_valid()

    def test_empty_form_valid(self):
        form = MDTextForm(data={"body": ""})
        assert form.is_valid()

    def test_form_media(self):
        form = MDTextForm()
        media = str(form.media)
        assert "easymde" in media
        assert "markdown_editor" in media
