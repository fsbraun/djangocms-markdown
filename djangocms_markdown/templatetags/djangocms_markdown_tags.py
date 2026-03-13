from django import template
from django.utils.safestring import mark_safe

from ..rendering import render_markdown

register = template.Library()


@register.filter(name="render_markdown")
def render_markdown_filter(value):
    """Template filter to render markdown to HTML.

    Usage::

        {% load djangocms_markdown_tags %}
        {{ object.content|render_markdown }}
    """
    if not value:
        return ""
    return mark_safe(render_markdown(str(value)))
