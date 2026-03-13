from django.db import models

from djangocms_markdown.fields import MarkdownField


class TestMarkdownModel(models.Model):
    """Test model with a MarkdownField for use in tests."""

    content = MarkdownField(blank=True, default="")

    class Meta:
        app_label = "tests"
