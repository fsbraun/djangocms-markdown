import markdown

from .settings import MARKDOWN_EXTENSION_CONFIGS, MARKDOWN_EXTENSIONS


def render_markdown(text):
    """Render markdown text to HTML."""
    if not text:
        return ""
    md = markdown.Markdown(
        extensions=MARKDOWN_EXTENSIONS,
        extension_configs=MARKDOWN_EXTENSION_CONFIGS,
        output_format="html",
    )
    return md.convert(text)
