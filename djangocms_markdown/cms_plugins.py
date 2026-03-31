from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from .forms import MDTextForm
from .models import MDText
from .references import resolve_references
from .settings import MARKDOWN_PLUGIN_MODULE_NAME, MARKDOWN_PLUGIN_NAME


@plugin_pool.register_plugin
class MDTextPlugin(CMSPluginBase):
    model = MDText
    name = MARKDOWN_PLUGIN_NAME
    module = MARKDOWN_PLUGIN_MODULE_NAME
    form = MDTextForm
    render_template = "djangocms_markdown/plugins/markdown.html"
    fieldsets = ((None, {"fields": ("body",)}),)

    def render(self, context, instance, placeholder):
        context = super().render(context, instance, placeholder)
        context["body"] = resolve_references(instance.body_rendered)
        return context
