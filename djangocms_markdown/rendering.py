import re

import markdown

from .sanitizer import sanitize_html
from .settings import MARKDOWN_EXTENSION_CONFIGS, MARKDOWN_EXTENSIONS, TABLE_CLASS


def _add_table_class(html, css_class):
    """Add a CSS class to all <table> tags in *html*."""
    if not css_class:
        return html

    def _replace(match):
        tag = match.group(0)
        if "class=" in tag:
            # Append to existing class attribute
            return re.sub(
                r'class="([^"]*)"',
                lambda m: f'class="{m.group(1)} {css_class}"',
                tag,
            )
        # Insert class before the closing >
        return tag[:-1] + f' class="{css_class}">'

    return re.sub(r"<table\b[^>]*>", _replace, html, flags=re.IGNORECASE)


def render_markdown(text):
    """Render markdown text to sanitized HTML."""
    if not text:
        return ""
    md = markdown.Markdown(
        extensions=MARKDOWN_EXTENSIONS,
        extension_configs=MARKDOWN_EXTENSION_CONFIGS,
        output_format="html",
    )
    html = md.convert(text)
    html = _add_table_class(html, TABLE_CLASS)
    return sanitize_html(html)
