from django.test import override_settings

from djangocms_markdown.sanitizer import get_sanitizer_kwargs, sanitize_html


class TestSanitizeHtml:
    def test_strips_script_tags(self):
        result = sanitize_html("<p>hello</p><script>alert('xss')</script>")
        assert "<script>" not in result
        assert "<p>hello</p>" in result

    def test_strips_event_handlers(self):
        result = sanitize_html('<p onclick="alert(1)">hello</p>')
        assert "onclick" not in result
        assert "<p>hello</p>" in result

    def test_strips_javascript_urls(self):
        result = sanitize_html('<a href="javascript:alert(1)">click</a>')
        assert "javascript:" not in result

    def test_allows_standard_tags(self):
        html = (
            "<h1>Title</h1><p>Text with <strong>bold</strong> and <em>italic</em></p>"
        )
        result = sanitize_html(html)
        assert result == html

    def test_allows_links(self):
        html = '<a href="https://example.com" target="_blank" rel="noopener">link</a>'
        result = sanitize_html(html)
        assert 'href="https://example.com"' in result
        assert 'target="_blank"' in result

    def test_allows_images(self):
        html = '<img src="https://example.com/img.png" alt="photo" loading="lazy">'
        result = sanitize_html(html)
        assert 'src="https://example.com/img.png"' in result
        assert 'alt="photo"' in result

    def test_allows_code_classes(self):
        html = '<code class="language-python">print()</code>'
        result = sanitize_html(html)
        assert 'class="language-python"' in result

    def test_allows_task_list_input(self):
        html = '<input type="checkbox" checked disabled>'
        result = sanitize_html(html)
        assert "<input" in result

    def test_allows_tables(self):
        html = "<table><thead><tr><th>A</th></tr></thead><tbody><tr><td>1</td></tr></tbody></table>"
        result = sanitize_html(html)
        assert "<table>" in result
        assert "<th>A</th>" in result

    def test_allows_id_attribute(self):
        html = '<h1 id="my-heading">Title</h1>'
        result = sanitize_html(html)
        assert 'id="my-heading"' in result

    def test_allows_data_attributes(self):
        html = '<div data-custom="value">content</div>'
        result = sanitize_html(html)
        assert 'data-custom="value"' in result

    def test_allows_aria_attributes(self):
        html = '<div aria-label="info">content</div>'
        result = sanitize_html(html)
        assert 'aria-label="info"' in result

    def test_empty_string(self):
        assert sanitize_html("") == ""

    def test_none(self):
        assert sanitize_html(None) is None

    def test_strips_iframe(self):
        result = sanitize_html('<iframe src="https://evil.com"></iframe>')
        assert "<iframe" not in result

    def test_strips_style_tag(self):
        result = sanitize_html("<style>body { display: none }</style><p>text</p>")
        assert "<style>" not in result
        assert "<p>text</p>" in result


class TestSanitizerSettings:
    @override_settings(TEXT_HTML_SANITIZE=False)
    def test_sanitize_disabled(self):
        html = "<script>alert('xss')</script>"
        result = sanitize_html(html)
        assert result == html

    @override_settings(TEXT_ADDITIONAL_TAGS=["custom-element"])
    def test_additional_tags(self):
        kwargs = get_sanitizer_kwargs()
        assert "custom-element" in kwargs["tags"]

    @override_settings(TEXT_ADDITIONAL_ATTRIBUTES={"div": {"data-x"}})
    def test_additional_attributes(self):
        kwargs = get_sanitizer_kwargs()
        assert "data-x" in kwargs["attributes"]["div"]

    @override_settings(TEXT_ADDITIONAL_ATTRIBUTES={"div": ["data-x", "data-y"]})
    def test_additional_attributes_as_list(self):
        kwargs = get_sanitizer_kwargs()
        assert "data-x" in kwargs["attributes"]["div"]
        assert "data-y" in kwargs["attributes"]["div"]

    @override_settings(TEXT_ADDITIONAL_PROTOCOLS=["custom", "app"])
    def test_additional_protocols(self):
        kwargs = get_sanitizer_kwargs()
        assert "custom" in kwargs["url_schemes"]
        assert "app" in kwargs["url_schemes"]


class TestRenderMarkdownSanitization:
    """Integration tests: markdown rendering + sanitization."""

    def test_xss_in_markdown_link(self):
        from djangocms_markdown.rendering import render_markdown

        result = render_markdown("[click](javascript:alert(1))")
        assert "javascript:" not in result

    def test_raw_html_in_markdown_sanitized(self):
        from djangocms_markdown.rendering import render_markdown

        result = render_markdown('Hello <script>alert("xss")</script> world')
        assert "<script>" not in result
        assert "Hello" in result

    def test_raw_event_handler_in_markdown(self):
        from djangocms_markdown.rendering import render_markdown

        result = render_markdown('<div onmouseover="alert(1)">hover me</div>')
        assert "onmouseover" not in result

    def test_valid_markdown_preserved(self):
        from djangocms_markdown.rendering import render_markdown

        result = render_markdown("**bold** and `code`")
        assert "<strong>bold</strong>" in result
        assert "<code>code</code>" in result
