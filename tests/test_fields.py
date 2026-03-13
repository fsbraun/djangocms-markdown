import pytest
from django import forms
from django.utils.safestring import SafeString

from djangocms_markdown.fields import (
    MarkdownField,
    MarkdownFieldDescriptor,
    MarkdownFormField,
    MarkdownRenderedValue,
)
from djangocms_markdown.widgets import MarkdownEditorWidget


class TestMarkdownRenderedValue:
    def test_str_value(self):
        val = MarkdownRenderedValue("**bold**")
        assert str(val) == "**bold**"

    def test_rendered_property(self):
        val = MarkdownRenderedValue("**bold**")
        assert "<strong>bold</strong>" in val.rendered

    def test_rendered_is_safe(self):
        val = MarkdownRenderedValue("hello")
        assert isinstance(val.rendered, SafeString)

    def test_empty_rendered(self):
        val = MarkdownRenderedValue("")
        assert val.rendered == ""

    def test_isinstance_str(self):
        val = MarkdownRenderedValue("test")
        assert isinstance(val, str)

    def test_string_operations(self):
        val = MarkdownRenderedValue("hello world")
        assert val.upper() == "HELLO WORLD"
        assert val.split() == ["hello", "world"]
        assert len(val) == 11


class TestMarkdownFieldDescriptor:
    def test_get_on_class_returns_descriptor(self):
        descriptor = MarkdownFieldDescriptor(None)
        descriptor.attr_name = "content"
        assert descriptor.__get__(None, object) is descriptor

    def test_get_wraps_value(self):
        descriptor = MarkdownFieldDescriptor(None)
        descriptor.attr_name = "content"

        class Obj:
            pass

        obj = Obj()
        obj.__dict__["content"] = "**test**"
        result = descriptor.__get__(obj, type(obj))
        assert isinstance(result, MarkdownRenderedValue)
        assert str(result) == "**test**"

    def test_get_returns_none_for_none(self):
        descriptor = MarkdownFieldDescriptor(None)
        descriptor.attr_name = "content"

        class Obj:
            pass

        obj = Obj()
        obj.__dict__["content"] = None
        assert descriptor.__get__(obj, type(obj)) is None

    def test_get_caches_wrapped_value(self):
        descriptor = MarkdownFieldDescriptor(None)
        descriptor.attr_name = "content"

        class Obj:
            pass

        obj = Obj()
        obj.__dict__["content"] = "test"
        result1 = descriptor.__get__(obj, type(obj))
        result2 = descriptor.__get__(obj, type(obj))
        assert result1 is result2

    def test_set_wraps_value(self):
        descriptor = MarkdownFieldDescriptor(None)
        descriptor.attr_name = "content"

        class Obj:
            pass

        obj = Obj()
        descriptor.__set__(obj, "**bold**")
        assert isinstance(obj.__dict__["content"], MarkdownRenderedValue)

    def test_set_none(self):
        descriptor = MarkdownFieldDescriptor(None)
        descriptor.attr_name = "content"

        class Obj:
            pass

        obj = Obj()
        descriptor.__set__(obj, None)
        assert obj.__dict__["content"] is None

    def test_set_already_wrapped(self):
        descriptor = MarkdownFieldDescriptor(None)
        descriptor.attr_name = "content"

        class Obj:
            pass

        obj = Obj()
        val = MarkdownRenderedValue("test")
        descriptor.__set__(obj, val)
        assert obj.__dict__["content"] is val


class TestMarkdownFormField:
    def test_default_widget(self):
        field = MarkdownFormField()
        assert isinstance(field.widget, MarkdownEditorWidget)

    def test_custom_widget_preserved(self):
        custom_widget = forms.Textarea()
        field = MarkdownFormField(widget=custom_widget)
        assert isinstance(field.widget, forms.Textarea)
        assert not isinstance(field.widget, MarkdownEditorWidget)

    def test_clean(self):
        field = MarkdownFormField(required=False)
        assert field.clean("# Hello") == "# Hello"

    def test_not_required(self):
        field = MarkdownFormField(required=False)
        assert field.clean("") == ""


class TestMarkdownField:
    def test_formfield_returns_markdown_form_field(self):
        field = MarkdownField()
        form_field = field.formfield()
        assert isinstance(form_field, MarkdownFormField)

    def test_formfield_has_markdown_widget(self):
        field = MarkdownField()
        form_field = field.formfield()
        assert isinstance(form_field.widget, MarkdownEditorWidget)


@pytest.mark.django_db
class TestMarkdownFieldOnModel:
    def test_field_set_and_get(self):
        from tests.test_models import TestMarkdownModel

        obj = TestMarkdownModel(content="**bold**")
        assert str(obj.content) == "**bold**"
        assert isinstance(obj.content, MarkdownRenderedValue)

    def test_field_rendered(self):
        from tests.test_models import TestMarkdownModel

        obj = TestMarkdownModel(content="**bold**")
        assert "<strong>bold</strong>" in obj.content.rendered

    def test_field_save_and_load(self):
        from tests.test_models import TestMarkdownModel

        obj = TestMarkdownModel(content="# Test heading")
        obj.save()

        loaded = TestMarkdownModel.objects.get(pk=obj.pk)
        assert str(loaded.content) == "# Test heading"
        assert "<h1" in loaded.content.rendered
