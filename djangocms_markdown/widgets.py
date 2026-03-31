from functools import cache

from django import forms
from django.utils.translation import gettext as _

from .settings import EASYMDE_CDN_BASE


@cache
def get_url_endpoint():
    """Get the url for dynamic liks for cms plugins and HTMLFields"""
    from django.contrib.admin import site
    from django.urls import NoReverseMatch
    from cms.utils.urlutils import admin_reverse

    for model_admin in site._registry.values():
        if hasattr(model_admin, "global_link_url_name"):
            return admin_reverse(model_admin.global_link_url_name)
    try:
        return admin_reverse("djangocms_link_link_urls")
    except NoReverseMatch:
        return None


class MarkdownEditorWidget(forms.Textarea):
    """A textarea widget that initializes EasyMDE markdown editor."""

    template_name = "djangocms_markdown/widgets/markdown_editor.html"

    def __init__(self, attrs=None):
        default_attrs = {"class": "markdown-editor"}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        url = get_url_endpoint()
        if url:
            context["widget"]["attrs"]["data-link-autocomplete-url"] = url
            context["widget"]["attrs"]["data-ref-placeholder"] = _(
                "Search for a page or object…"
            )
        return context

    @property
    def media(self):
        css_files = []
        js_files = []

        if EASYMDE_CDN_BASE:
            css_files.append(f"{EASYMDE_CDN_BASE}/easymde.min.css")
            js_files.append(f"{EASYMDE_CDN_BASE}/easymde.min.js")
        else:
            css_files.append("djangocms_markdown/css/easymde.min.css")
            js_files.append("djangocms_markdown/js/easymde.min.js")

        # Include Django admin's select2 assets for the reference picker.
        # Order matters: jquery → select2 → jquery.init (moves jQuery to
        # django.jQuery, carrying the select2 plugin with it).
        if get_url_endpoint():
            css_files.append("admin/css/vendor/select2/select2.min.css")
            css_files.append("admin/css/autocomplete.css")
            js_files.append("admin/js/vendor/jquery/jquery.min.js")
            js_files.append("admin/js/vendor/select2/select2.full.min.js")
            js_files.append("admin/js/jquery.init.js")

        css_files.append("djangocms_markdown/css/markdown_editor.css")
        css_files.append("djangocms_markdown/css/preview_typography.css")
        js_files.append("djangocms_markdown/js/markdown_editor.js")

        return forms.Media(
            css={"all": css_files},
            js=js_files,
        )
