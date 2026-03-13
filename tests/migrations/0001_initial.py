from django.db import migrations, models
import djangocms_markdown.fields


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="TestMarkdownModel",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "content",
                    djangocms_markdown.fields.MarkdownField(blank=True, default=""),
                ),
            ],
        ),
    ]
