from django.template import Context, Template
from django.utils.safestring import SafeString

from djangocms_markdown.templatetags.djangocms_markdown_tags import (
    render_markdown_filter,
)


class TestRenderMarkdownFilter:
    def test_basic_rendering(self):
        result = render_markdown_filter("**bold**")
        assert "<strong>bold</strong>" in result

    def test_returns_safe_string(self):
        result = render_markdown_filter("hello")
        assert isinstance(result, SafeString)

    def test_empty_value(self):
        assert render_markdown_filter("") == ""

    def test_none_value(self):
        assert render_markdown_filter(None) == ""

    def test_template_usage(self):
        template = Template(
            "{% load djangocms_markdown_tags %}{{ content|render_markdown }}"
        )
        context = Context({"content": "# Hello"})
        rendered = template.render(context)
        assert "<h1" in rendered
        assert "Hello" in rendered

    def test_template_with_complex_markdown(self):
        template = Template(
            "{% load djangocms_markdown_tags %}{{ content|render_markdown }}"
        )
        md = "- item 1\n- item 2"
        context = Context({"content": md})
        rendered = template.render(context)
        assert "<ul>" in rendered
        assert "<li>item 1</li>" in rendered
