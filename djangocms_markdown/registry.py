"""Registry for contributions of other apps to djangocms-markdown.

Apps contribute Python-Markdown extensions, the page assets these need and
editor media through their ``cms_config.py`` (see ``cms_config.py`` in this
package). This module must stay importable without django CMS's app
registration (``CMSAppConfig``/``CMSAppExtension``), which does not exist in
django CMS 3.11: it is in the import path of rendering, plugin, field and
widget.
"""

from dataclasses import dataclass, field

import markdown
from django import forms
from django.core.exceptions import ImproperlyConfigured


@dataclass
class Contribution:
    app: str
    extensions: list = field(default_factory=list)
    extension_configs: dict = field(default_factory=dict)
    assets: object = None
    editor_media: object = None


#: Contributions in registration order (django CMS configures apps in
#: ``INSTALLED_APPS`` order).
_contributions = []


# Extensions are contributed by name only. Python-Markdown then creates fresh
# extension instances for every render; a shared Extension instance would carry
# its state (e.g. collected footnotes) from one render into another, also
# across concurrent requests.
_EXTENSIONS_EXPECTED = (
    'a list of extension names (e.g. "my_app.markdown" or '
    '"my_app.markdown:MyExtension"), not extension instances'
)


def _fail(app, attr, expected, value):
    raise ImproperlyConfigured(
        f"{app}: {attr} must be {expected}, got {type(value).__name__}."
    )


def validate_assets(app, assets, source="djangocms_markdown_assets"):
    """Check that *assets* maps sekizai block names to lists of HTML snippets."""
    expected = (
        "a dict mapping sekizai block names to lists of HTML snippets "
        '(e.g. {"css": [\'<link rel="stylesheet" href="...">\']})'
    )
    if not isinstance(assets, dict):
        _fail(app, source, expected, assets)
    for block, snippets in assets.items():
        if not isinstance(block, str):
            _fail(app, source, expected, block)
        if not isinstance(snippets, (list, tuple)):
            _fail(app, f"{source}[{block!r}]", "a list of HTML snippets", snippets)
        for snippet in snippets:
            if not isinstance(snippet, str):
                _fail(app, f"{source}[{block!r}]", "a list of strings", snippet)


def register(
    app, *, extensions=None, extension_configs=None, assets=None, editor_media=None
):
    """Register the contribution of *app*, replacing an earlier one.

    Raises ``ImproperlyConfigured`` (naming *app*) for invalid declarations.
    """
    if extensions is None:
        extensions = []
    if not isinstance(extensions, (list, tuple)):
        _fail(
            app,
            "djangocms_markdown_extensions",
            _EXTENSIONS_EXPECTED,
            extensions,
        )
    for extension in extensions:
        if not isinstance(extension, str):
            _fail(
                app,
                "djangocms_markdown_extensions",
                _EXTENSIONS_EXPECTED,
                extension,
            )

    if extension_configs is None:
        extension_configs = {}
    if not isinstance(extension_configs, dict):
        _fail(
            app,
            "djangocms_markdown_extension_configs",
            "a dict mapping extension names to config dicts",
            extension_configs,
        )
    for name, config in extension_configs.items():
        if not isinstance(name, str) or not isinstance(config, dict):
            _fail(
                app,
                f"djangocms_markdown_extension_configs[{name!r}]",
                "a config dict keyed by the extension name",
                config if isinstance(name, str) else name,
            )

    # Fail at startup, not on the first render, if an extension cannot be
    # loaded (misspelled name, missing package, unknown config option).
    for extension in extensions:
        try:
            markdown.Markdown(
                extensions=[extension],
                extension_configs={extension: extension_configs.get(extension, {})},
            )
        except Exception as error:
            raise ImproperlyConfigured(
                f"{app}: djangocms_markdown_extensions: cannot load extension "
                f"{extension!r} ({type(error).__name__}: {error})."
            ) from error

    if assets is not None and not callable(assets):
        validate_assets(app, assets)

    if editor_media is not None and not (
        isinstance(editor_media, forms.Media) or callable(editor_media)
    ):
        _fail(
            app,
            "djangocms_markdown_editor_media",
            "a django.forms.Media instance or a callable returning one",
            editor_media,
        )

    contribution = Contribution(
        app=app,
        extensions=list(extensions),
        extension_configs={k: dict(v) for k, v in extension_configs.items()},
        assets=assets,
        editor_media=editor_media,
    )
    for index, existing in enumerate(_contributions):
        if existing.app == app:
            _contributions[index] = contribution
            break
    else:
        _contributions.append(contribution)
    return contribution


def get_contributions():
    """Return the registered contributions in registration order."""
    return list(_contributions)


def _append_media(media, other):
    """Return a Media with the files of *media* followed by those of *other*.

    Unlike ``media + other`` this guarantees that the files of *other* come
    last: Django's merge only keeps the relative order within each operand.
    """
    js = list(media._js)
    js += [path for path in other._js if path not in js]
    css = {medium: list(paths) for medium, paths in media._css.items()}
    for medium, paths in other._css.items():
        merged = css.setdefault(medium, [])
        merged += [path for path in paths if path not in merged]
    return forms.Media(css=css, js=js)


def get_editor_media(base=None):
    """Return *base* followed by the editor media of all contributions.

    Contributions are appended in registration order. Returns *base* itself
    (``None`` by default) if there are none.
    """
    media = base
    for contribution in _contributions:
        editor_media = contribution.editor_media
        if editor_media is None:
            continue
        if not isinstance(editor_media, forms.Media):
            editor_media = editor_media()
            if not isinstance(editor_media, forms.Media):
                _fail(
                    contribution.app,
                    "the djangocms_markdown_editor_media callable's return value",
                    "a django.forms.Media instance",
                    editor_media,
                )
        media = editor_media if media is None else _append_media(media, editor_media)
    return media
