"""django CMS app registration for djangocms-markdown (django CMS 4.1+).

Other apps opt in from their own ``cms_config.py``::

    class MyAppConfig(CMSAppConfig):
        djangocms_markdown_enabled = True
        djangocms_markdown_extensions = ["my_app.markdown"]
        djangocms_markdown_extension_configs = {"my_app.markdown": {...}}
        djangocms_markdown_assets = {"css": [...], "js": [...]}  # or a callable
        djangocms_markdown_editor_media = forms.Media(...)  # or a callable

Callables are called as plain functions (``assets(html)``, ``editor_media()``):
a function assigned to one of these attributes is not bound to the config
instance.

django CMS 3.11 never loads this file. Nothing else in this package may import
it.
"""

import inspect

from cms.app_base import CMSAppExtension

from . import registry


def _get(cms_config, name):
    """Read a declaration without turning plain functions into bound methods."""
    value = inspect.getattr_static(cms_config, name, None)
    if isinstance(value, (staticmethod, classmethod, property)):
        value = getattr(cms_config, name)
    return value


class MarkdownCMSExtension(CMSAppExtension):
    def configure_app(self, cms_config):
        app_config = getattr(cms_config, "app_config", None)
        app = getattr(app_config, "name", None) or type(cms_config).__module__
        registry.register(
            app,
            extensions=_get(cms_config, "djangocms_markdown_extensions"),
            extension_configs=_get(cms_config, "djangocms_markdown_extension_configs"),
            assets=_get(cms_config, "djangocms_markdown_assets"),
            editor_media=_get(cms_config, "djangocms_markdown_editor_media"),
        )
