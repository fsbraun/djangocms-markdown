import re

import markdown

from . import registry
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


def get_extensions():
    """Return the effective list of Python-Markdown extensions.

    ``DJANGOCMS_MARKDOWN_EXTENSIONS`` first, then the extensions contributed by
    other apps through their ``cms_config.py`` in ``INSTALLED_APPS`` order,
    without duplicates. Resolved on each call since contributions are
    registered during django CMS's setup, after the settings were read.
    """
    extensions = list(MARKDOWN_EXTENSIONS)
    for contribution in registry.get_contributions():
        for extension in contribution.extensions:
            if extension not in extensions:
                extensions.append(extension)
    return extensions


def get_extension_configs():
    """Return the effective extension configs.

    Configs are merged per extension, option by option: options from
    ``DJANGOCMS_MARKDOWN_EXTENSION_CONFIGS`` win over contributed ones, and
    among contributions the app listed first in ``INSTALLED_APPS`` wins.
    """
    configs = {}
    for contribution in registry.get_contributions():
        for name, config in contribution.extension_configs.items():
            merged = configs.setdefault(name, {})
            for option, value in config.items():
                merged.setdefault(option, value)
    for name, config in MARKDOWN_EXTENSION_CONFIGS.items():
        configs[name] = {**configs.get(name, {}), **config}
    return configs


def get_assets(html):
    """Collect the page assets the rendered *html* needs.

    Returns a dict mapping sekizai block names to lists of HTML snippets,
    merged from all contributing apps (without duplicate snippets per block).
    Callable contributions are called with *html* and may return ``None``.
    """
    assets = {}
    for contribution in registry.get_contributions():
        contributed = contribution.assets
        if callable(contributed):
            contributed = contributed(html)
            if contributed is not None:
                registry.validate_assets(
                    contribution.app,
                    contributed,
                    "the djangocms_markdown_assets callable's return value",
                )
        if not contributed:
            continue
        for block, snippets in contributed.items():
            collected = assets.setdefault(block, [])
            for snippet in snippets:
                if snippet not in collected:
                    collected.append(snippet)
    return assets


def add_assets(context, html):
    """Add the assets for the rendered *html* to the sekizai blocks of *context*.

    Does what sekizai's ``{% addtoblock %}`` does for each snippet, so sekizai
    drops snippets already added elsewhere on the page. Does nothing if no
    assets are contributed or if *context* carries no sekizai data (sekizai
    context processor not enabled).
    """
    assets = get_assets(html)
    if not assets:
        return
    from sekizai.helpers import get_varname

    data = context.get(get_varname())
    if data is None:
        return
    for block, snippets in assets.items():
        for snippet in snippets:
            data[block].append(snippet)


def render_markdown(text):
    """Render markdown text to sanitized HTML."""
    if not text:
        return ""
    md = markdown.Markdown(
        extensions=get_extensions(),
        extension_configs=get_extension_configs(),
        output_format="html",
    )
    html = md.convert(text)
    html = _add_table_class(html, TABLE_CLASS)
    return sanitize_html(html)
