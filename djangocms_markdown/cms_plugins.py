from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from .forms import MDTextForm
from .models import MDText
from .references import resolve_references
from .rendering import add_assets
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
        # Assets contributed by other apps go to the sekizai blocks at page
        # render time (not into the stored HTML), so sekizai de-duplicates them.
        add_assets(context, context["body"])
        return context
