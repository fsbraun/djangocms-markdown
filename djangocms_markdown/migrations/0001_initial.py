from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("cms", "0022_auto_20180620_1551"),
    ]

    operations = [
        migrations.CreateModel(
            name="MDText",
            fields=[
                (
                    "cmsplugin_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        related_name="%(app_label)s_%(class)s",
                        serialize=False,
                        to="cms.cmsplugin",
                    ),
                ),
                (
                    "body",
                    models.TextField(
                        blank=True, default="", verbose_name="Markdown content"
                    ),
                ),
                (
                    "body_rendered",
                    models.TextField(
                        blank=True,
                        default="",
                        editable=False,
                        verbose_name="Rendered HTML",
                    ),
                ),
            ],
            options={
                "verbose_name": "Markdown text",
                "verbose_name_plural": "Markdown texts",
            },
            bases=("cms.cmsplugin",),
        ),
    ]
