import markdown

from .sanitizer import sanitize_html
from .settings import MARKDOWN_EXTENSION_CONFIGS, MARKDOWN_EXTENSIONS


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
    return sanitize_html(html)
