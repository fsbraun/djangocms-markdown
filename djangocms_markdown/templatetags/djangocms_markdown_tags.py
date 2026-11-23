from django import template
from django.utils.safestring import mark_safe

from ..references import resolve_references
from ..rendering import add_assets, render_markdown

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
    return mark_safe(resolve_references(render_markdown(str(value))))


@register.simple_tag(takes_context=True)
def markdown_assets(context, html):
    """Add the assets rendered markdown needs to the page's sekizai blocks.

    Apps extending djangocms-markdown can contribute CSS/JS for the HTML their
    extensions produce. The CMS plugin adds these automatically; use this tag
    for markdown rendered in your own templates. It outputs nothing::

        {% load djangocms_markdown_tags %}
        {% with html=object.content|render_markdown %}
            {{ html }}
            {% markdown_assets html %}
        {% endwith %}
    """
    if html:
        add_assets(context, str(html))
    return ""
