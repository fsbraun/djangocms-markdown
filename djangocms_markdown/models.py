from cms.models import CMSPlugin
from django.db import models
from django.utils.translation import gettext_lazy as _

from .rendering import render_markdown


class MDText(CMSPlugin):
    """A CMS plugin that stores and renders Markdown content."""

    body = models.TextField(_("Markdown content"), blank=True, default="")
    body_rendered = models.TextField(
        _("Rendered HTML"), blank=True, default="", editable=False
    )

    class Meta:
        verbose_name = _("Markdown text")
        verbose_name_plural = _("Markdown texts")

    def __str__(self):
        return self.body[:100] if self.body else ""

    def save(self, *args, **kwargs):
        self.body_rendered = render_markdown(self.body)
        super().save(*args, **kwargs)
