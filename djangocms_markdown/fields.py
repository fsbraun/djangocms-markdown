from django import forms
from django.db import models
from django.utils.safestring import mark_safe

from .references import resolve_references
from .rendering import render_markdown
from .widgets import MarkdownEditorWidget


class MarkdownFormField(forms.CharField):
    """Form field for markdown content with the EasyMDE editor widget."""

    widget = MarkdownEditorWidget

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MarkdownEditorWidget())
        super().__init__(*args, **kwargs)


class MarkdownRenderedValue(str):
    """A string subclass that holds markdown text and provides rendered HTML."""

    def __new__(cls, raw):
        instance = super().__new__(cls, raw)
        return instance

    @property
    def rendered(self):
        """Return the markdown rendered as HTML, marked safe for templates."""
        return mark_safe(resolve_references(render_markdown(str(self))))


class MarkdownFieldDescriptor:
    """Descriptor that wraps field values in MarkdownRenderedValue."""

    def __init__(self, field):
        self.field = field

    def __set_name__(self, owner, name):
        self.attr_name = name

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        raw = instance.__dict__.get(self.attr_name, "")
        if raw is None:
            return None
        if not isinstance(raw, MarkdownRenderedValue):
            raw = MarkdownRenderedValue(raw)
            instance.__dict__[self.attr_name] = raw
        return raw

    def __set__(self, instance, value):
        if value is not None and not isinstance(value, MarkdownRenderedValue):
            value = MarkdownRenderedValue(value)
        instance.__dict__[self.attr_name] = value


class MarkdownField(models.TextField):
    """
    A model field that stores markdown content.

    Access the raw markdown via ``str(obj.field)`` and the rendered
    HTML via ``obj.field.rendered``.

    Uses EasyMDE as the editor widget in forms and admin.
    """

    def contribute_to_class(self, cls, name):
        super().contribute_to_class(cls, name)
        descriptor = MarkdownFieldDescriptor(self)
        descriptor.attr_name = name
        setattr(cls, name, descriptor)

    def formfield(self, **kwargs):
        kwargs.setdefault("form_class", MarkdownFormField)
        kwargs.setdefault("widget", MarkdownEditorWidget())
        return super().formfield(**kwargs)
