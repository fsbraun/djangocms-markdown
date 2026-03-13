from djangocms_markdown.rendering import render_markdown


class TestRenderMarkdown:
    def test_empty_string(self):
        assert render_markdown("") == ""

    def test_none(self):
        assert render_markdown(None) == ""

    def test_basic_paragraph(self):
        result = render_markdown("Hello world")
        assert "<p>Hello world</p>" in result

    def test_script_tag_stripped(self):
        result = render_markdown("<script>alert(1)</script>")
        assert "<script" not in result

    def test_html_with_event_handler_stripped(self):
        result = render_markdown('<img src="x" onerror="alert(1)">')
        # nh3 allows <img> but strips dangerous attributes
        assert "onerror" not in result
        assert "<img" in result

    def test_bold(self):
        result = render_markdown("**bold text**")
        assert "<strong>bold text</strong>" in result

    def test_italic(self):
        result = render_markdown("*italic text*")
        assert "<em>italic text</em>" in result

    def test_heading(self):
        result = render_markdown("# Heading 1")
        assert "<h1" in result
        assert "Heading 1</h1>" in result

    def test_heading_levels(self):
        for level in range(1, 7):
            result = render_markdown(f"{'#' * level} Heading {level}")
            assert f"<h{level}" in result

    def test_unordered_list(self):
        md = "- item 1\n- item 2\n- item 3"
        result = render_markdown(md)
        assert "<ul>" in result
        assert "<li>item 1</li>" in result

    def test_ordered_list(self):
        md = "1. first\n2. second\n3. third"
        result = render_markdown(md)
        assert "<ol>" in result
        assert "<li>first</li>" in result

    def test_inline_code(self):
        result = render_markdown("`code`")
        assert "<code>code</code>" in result

    def test_fenced_code_block(self):
        md = "```python\nprint('hello')\n```"
        result = render_markdown(md)
        assert "<code" in result
        assert "print" in result

    def test_link(self):
        result = render_markdown("[link](https://example.com)")
        assert '<a href="https://example.com">' in result
        assert "link</a>" in result

    def test_image(self):
        result = render_markdown("![alt text](https://example.com/img.png)")
        assert "<img" in result
        assert "img.png" in result

    def test_blockquote(self):
        result = render_markdown("> quoted text")
        assert "<blockquote>" in result
        assert "quoted text" in result

    def test_horizontal_rule(self):
        result = render_markdown("---")
        assert "<hr" in result

    def test_table(self):
        md = "| A | B |\n|---|---|\n| 1 | 2 |"
        result = render_markdown(md)
        assert "<table>" in result
        assert "<th>" in result
        assert "<td>" in result

    def test_task_list(self):
        md = "- [x] done\n- [ ] todo"
        result = render_markdown(md)
        assert "task-list" in result
        assert "done" in result
        assert "todo" in result

    def test_multiline(self):
        md = "# Title\n\nParagraph one.\n\nParagraph two."
        result = render_markdown(md)
        assert "<h1" in result
        assert "<p>Paragraph one.</p>" in result
        assert "<p>Paragraph two.</p>" in result
