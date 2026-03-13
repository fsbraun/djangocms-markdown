from django.conf import settings

# Markdown extensions to use for rendering
MARKDOWN_EXTENSIONS = getattr(
    settings,
    "DJANGOCMS_MARKDOWN_EXTENSIONS",
    [
        "markdown.extensions.extra",
        "markdown.extensions.codehilite",
        "markdown.extensions.toc",
        "markdown.extensions.sane_lists",
        "djangocms_markdown.extensions.delete",
    ],
)

# Configuration for markdown extensions
MARKDOWN_EXTENSION_CONFIGS = getattr(
    settings,
    "DJANGOCMS_MARKDOWN_EXTENSION_CONFIGS",
    {
        "markdown.extensions.codehilite": {
            "css_class": "highlight",
            "guess_lang": False,
        },
    },
)

# Plugin display name
MARKDOWN_PLUGIN_NAME = getattr(settings, "DJANGOCMS_MARKDOWN_PLUGIN_NAME", "Markdown")

# Plugin module name
MARKDOWN_PLUGIN_MODULE_NAME = getattr(
    settings, "DJANGOCMS_MARKDOWN_PLUGIN_MODULE_NAME", "Generic"
)

# EasyMDE CDN base URL (set to empty string to use local static files instead)
EASYMDE_CDN_BASE = getattr(
    settings,
    "DJANGOCMS_MARKDOWN_EASYMDE_CDN_BASE",
    "https://cdn.jsdelivr.net/npm/easymde@2.20.0/dist",
)
