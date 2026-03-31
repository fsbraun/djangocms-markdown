import pytest
from cms.models import Placeholder
from django.template import Context

from djangocms_markdown.cms_plugins import MDTextPlugin
from djangocms_markdown.models import MDText


@pytest.mark.django_db
class TestMDTextModel:
    def test_create(self):
        placeholder = Placeholder.objects.create(slot="test")
        plugin = MDText(
            body="# Hello",
            placeholder=placeholder,
            position=1,
            language="en",
            plugin_type="MDTextPlugin",
        )
        plugin.save()
        assert plugin.body == "# Hello"
        assert "<h1" in plugin.body_rendered

    def test_save_renders_markdown(self):
        placeholder = Placeholder.objects.create(slot="test")
        plugin = MDText(
            body="**bold** and *italic*",
            placeholder=placeholder,
            position=1,
            language="en",
            plugin_type="MDTextPlugin",
        )
        plugin.save()
        assert "<strong>bold</strong>" in plugin.body_rendered
        assert "<em>italic</em>" in plugin.body_rendered

    def test_save_empty_body(self):
        placeholder = Placeholder.objects.create(slot="test")
        plugin = MDText(
            body="",
            placeholder=placeholder,
            position=1,
            language="en",
            plugin_type="MDTextPlugin",
        )
        plugin.save()
        assert plugin.body_rendered == ""

    def test_str(self):
        plugin = MDText(body="Hello world")
        assert str(plugin) == "Hello world"

    def test_str_long(self):
        plugin = MDText(body="x" * 200)
        assert len(str(plugin)) == 100

    def test_str_empty(self):
        plugin = MDText(body="")
        assert str(plugin) == ""

    def test_update_re_renders(self):
        placeholder = Placeholder.objects.create(slot="test")
        plugin = MDText(
            body="# Version 1",
            placeholder=placeholder,
            position=1,
            language="en",
            plugin_type="MDTextPlugin",
        )
        plugin.save()
        assert "Version 1" in plugin.body_rendered

        plugin.body = "# Version 2"
        plugin.save()
        plugin.refresh_from_db()
        assert "Version 2" in plugin.body_rendered


@pytest.mark.django_db
class TestMDTextPlugin:
    def test_plugin_registered(self):
        from cms.plugin_pool import plugin_pool

        assert "MDTextPlugin" in plugin_pool.plugins

    def test_plugin_attributes(self):
        assert MDTextPlugin.model is MDText
        assert MDTextPlugin.disable_child_plugins is False

    def test_render(self):
        placeholder = Placeholder.objects.create(slot="test")
        instance = MDText(
            body="**hello**",
            placeholder=placeholder,
            position=1,
            language="en",
            plugin_type="MDTextPlugin",
        )
        instance.save()

        plugin = MDTextPlugin()
        context = Context({"request": None})
        new_context = plugin.render(context, instance, placeholder)
        assert "<strong>hello</strong>" in new_context["body"]
