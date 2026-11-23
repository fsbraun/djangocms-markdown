# djangocms-markdown

[![PyPI](https://img.shields.io/pypi/v/djangocms-markdown)](https://pypi.org/project/djangocms-markdown/)
[![Python Version](https://img.shields.io/pypi/pyversions/djangocms-markdown)](https://pypi.org/project/djangocms-markdown/)
[![Django Version](https://img.shields.io/pypi/djversions/djangocms-markdown)](https://pypi.org/project/djangocms-markdown/)
[![django CMS Version](https://img.shields.io/pypi/frameworkversions/django-cms/djangocms-markdown)](https://pypi.org/project/djangocms-markdown/)
[![codecov](https://codecov.io/gh/fsbraun/djangocms-markdown/graph/badge.svg?token=LEwTZILg2S)](https://codecov.io/gh/fsbraun/djangocms-markdown)

A markdown content plugin and model field for
[django CMS](https://www.django-cms.org/). Write content in Markdown using an
integrated editor and have it rendered as HTML on your site.

> Attention: Version 0.3.2 is from a different project by the great [Nicolas Noé](https://github.com/niconoe).
> This project is an entirely different rewrite with different goals.


## Features

- **MDText CMS plugin** — add markdown content to any django CMS placeholder
- **MarkdownField** — a model field for storing markdown in your own models,
  with a `.rendered` property that returns HTML
- **EasyMDE editor** — a full-featured markdown editor with toolbar, preview,
  and side-by-side mode in the admin and CMS plugin forms
- **Dynamic object references** — link to any Django object with
  `[text](ref:app.model:pk)` syntax; URLs are resolved at render time so they
  stay up to date. When an object is deleted, the link is replaced with plain
  text.
- **Inline reference picker** — when the cursor is inside a markdown link, a
  select2 autocomplete popup appears above the link, allowing you to search and
  select internal pages or objects. Requires
  [djangocms-link](https://github.com/django-cms/djangocms-link) or a custom
  autocomplete endpoint. If the link text is empty it is filled with the
  selected object's name.
- **Template filter** — `{{ value|render_markdown }}` for rendering markdown
  anywhere in templates
- **Configurable rendering** — uses Python-Markdown with sensible defaults
  (tables, fenced code, syntax highlighting, TOC, and more)
- **Extension hooks** — other django CMS apps can contribute Python-Markdown
  extensions together with their page assets and editor preview
  (see [Extension hooks](#extension-hooks))

## Installation

```bash
pip install djangocms-markdown
```

Add `djangocms_markdown` to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...,
    "djangocms_markdown",
]
```

Run migrations:

```bash
python manage.py migrate djangocms_markdown
```

## Usage

### CMS plugin

After installation the **Markdown** plugin is available in the plugin picker
under the *Generic* module. Add it to any placeholder and write markdown in the
editor. The content is rendered to HTML on save and displayed on the page.

### MarkdownField (models)

Use `MarkdownField` in your own models just like a `TextField`:

```python
from django.db import models
from djangocms_markdown.fields import MarkdownField


class Article(models.Model):
    body = MarkdownField()
```

The field stores raw markdown. Access the rendered HTML through the `.rendered`
property:

```python
article = Article.objects.get(pk=1)
str(article.body)           # raw markdown
article.body.rendered       # rendered HTML (marked safe)
```

In admin forms the field automatically uses the EasyMDE markdown editor.

### Template filter

```django
{% load djangocms_markdown_tags %}

{{ article.body|render_markdown }}
```

## Configuration

All settings are optional.

- **`DJANGOCMS_MARKDOWN_EXTENSIONS`** — list of Python-Markdown extensions to
  enable. Default:

  ```python
  DJANGOCMS_MARKDOWN_EXTENSIONS = [
      "markdown.extensions.extra",
      "markdown.extensions.codehilite",
      "markdown.extensions.toc",
      "markdown.extensions.sane_lists",
  ]
  ```

- **`DJANGOCMS_MARKDOWN_EXTENSION_CONFIGS`** — dict of extension-specific
  configuration. Default:

  ```python
  DJANGOCMS_MARKDOWN_EXTENSION_CONFIGS = {
      "markdown.extensions.codehilite": {
          "css_class": "highlight",
          "guess_lang": False,
      },
  }
  ```

- **`DJANGOCMS_MARKDOWN_PLUGIN_NAME`** — display name of the CMS plugin.
  Default: `"Markdown"`

- **`DJANGOCMS_MARKDOWN_PLUGIN_MODULE_NAME`** — module name the plugin appears
  under in the plugin picker. Default: `"Generic"`

- **`DJANGOCMS_MARKDOWN_TABLE_CLASS`** — CSS class(es) added to every `<table>`
  tag in rendered HTML. Useful for Bootstrap (`"table"`) or other CSS frameworks.
  Set to `""` to disable. Default: `"table"`

- **`DJANGOCMS_MARKDOWN_EASYMDE_CDN_BASE`** — CDN base URL for loading the
  EasyMDE editor. Set to `""` to serve from your own static files instead.
  Default: `"https://cdn.jsdelivr.net/npm/easymde@2.21.0/dist"`

Rendered HTML is sanitized with [nh3](https://github.com/messense/nh3) using
the same settings as
[djangocms-text](https://github.com/django-cms/djangocms-text):

- **`TEXT_HTML_SANITIZE`** — set to `False` to disable sanitization (default `True`)
- **`TEXT_ADDITIONAL_TAGS`** — extra HTML tags to allow
- **`TEXT_ADDITIONAL_ATTRIBUTES`** — extra attributes to allow per tag
- **`TEXT_ADDITIONAL_PROTOCOLS`** — extra URL schemes to allow

## Extension hooks

Other django CMS packages can extend djangocms-markdown with their own
[Python-Markdown extensions](https://python-markdown.github.io/extensions/api/),
together with the frontend assets the generated HTML needs and a matching
editor preview. A project only needs to add such a package to
`INSTALLED_APPS`.

> **django CMS 3.11:** registration uses django CMS's app registration
> (`cms_config.py`), which exists in django CMS 4.1 and later. django CMS 3.11
> never loads `cms_config.py`, so none of the hooks below are available there;
> `DJANGOCMS_MARKDOWN_EXTENSIONS` and `DJANGOCMS_MARKDOWN_EXTENSION_CONFIGS`
> remain the only way to add extensions.

### Registering from `cms_config.py`

An app opts in from its own `cms_config.py`. All attributes except
`djangocms_markdown_enabled` are optional:

```python
# my_app/cms_config.py
from cms.app_base import CMSAppConfig
from django import forms


class MyAppConfig(CMSAppConfig):
    djangocms_markdown_enabled = True
    djangocms_markdown_extensions = ["my_app.markdown"]
    djangocms_markdown_extension_configs = {"my_app.markdown": {"css_class": "spoiler"}}
    djangocms_markdown_assets = {
        "css": ['<link rel="stylesheet" href="/static/my_app/spoiler.css">'],
        "js": ['<script defer src="/static/my_app/spoiler.js" data-animate="true"></script>'],
    }
    djangocms_markdown_editor_media = forms.Media(js=["my_app/spoiler_preview.js"])
```

| Attribute | Value |
|---|---|
| `djangocms_markdown_extensions` | List of Python-Markdown extensions (names or `markdown.Extension` instances). |
| `djangocms_markdown_extension_configs` | Dict mapping extension names to their config dicts. |
| `djangocms_markdown_assets` | Page assets, see [Page assets](#page-assets). |
| `djangocms_markdown_editor_media` | Editor media, see [Editor media and preview](#editor-media-and-preview). |

Invalid declarations raise `ImproperlyConfigured` at startup, naming the app.

- **Order:** the effective extension list is `DJANGOCMS_MARKDOWN_EXTENSIONS`
  first, followed by contributed extensions in `INSTALLED_APPS` order, without
  duplicates.
- **Configs:** extension configs are merged option by option. Options set in
  the project's `DJANGOCMS_MARKDOWN_EXTENSION_CONFIGS` (or its default) win
  over contributed ones; if several apps configure the same option, the app
  listed first in `INSTALLED_APPS` wins.
- **Opting out:** an app decides for itself whether to contribute, e.g. by
  setting `djangocms_markdown_enabled = getattr(settings, "MY_APP_MARKDOWN", True)`.
- **Callables:** where a callable is accepted it is called as a plain function
  (`assets(html)`, `editor_media()`); a function assigned to the attribute is
  not bound to the config instance.
- **Sanitizer:** contributed extensions run before the HTML sanitizer. If an
  extension generates tags or attributes the sanitizer removes, the project
  has to allow them with the `TEXT_ADDITIONAL_*` settings.
- **Stored HTML:** the CMS plugin renders markdown when it is saved. Existing
  plugins pick up newly added extensions when they are saved again.

### Page assets

`djangocms_markdown_assets` tells djangocms-markdown what to add to the page
when rendered markdown is shown. It is either

- a dict mapping [sekizai](https://django-sekizai.readthedocs.io/) block names
  to lists of HTML snippets (see above). Snippets are arbitrary HTML, so they
  can carry attributes such as `defer` or `data-*`; or
- a callable taking the rendered HTML and returning such a dict, or `None` if
  this content needs nothing:

  ```python
  from django.templatetags.static import static


  def spoiler_assets(html):
      if 'class="spoiler"' not in html:
          return None
      return {"js": [f'<script defer src="{static("my_app/spoiler.js")}"></script>']}


  class MyAppConfig(CMSAppConfig):
      djangocms_markdown_enabled = True
      djangocms_markdown_assets = spoiler_assets
  ```

  Callables are evaluated when a page is rendered, never at import time, so
  `static()` is safe to use.

The **CMS plugin** adds the snippets to the sekizai blocks each time it is
rendered on a page (they are not part of the stored HTML). sekizai drops
identical snippets, so each asset is loaded once no matter how many markdown
plugins a page has. The page template needs the usual
`{% render_block "css" %}` and `{% render_block "js" %}`; without them (or
without sekizai's context processor) the page renders normally, just without
the assets.

For **`MarkdownField` and the `render_markdown` filter** in your own
templates, pass the rendered HTML to the `markdown_assets` tag. It outputs
nothing and adds the assets to the sekizai blocks:

```django
{% load djangocms_markdown_tags %}

{% with html=article.body.rendered %}
    {{ html }}
    {% markdown_assets html %}
{% endwith %}
```

In Python, `djangocms_markdown.rendering.get_assets(html)` returns the merged
contributions of all apps as a `{block name: [snippets]}` dict.

### Editor media and preview

`djangocms_markdown_editor_media` is a `django.forms.Media` instance, or a
callable returning one. It is added to the media of the markdown editor widget
after the widget's own files — in the plugin form and in any admin form using
`MarkdownField`. Use it to load styles and scripts for the editor preview.

The editor preview is rendered in the browser and does not know about
server-side extensions. Scripts can register *preview processors* in a global
array; this works regardless of script load order:

```javascript
// my_app/static/my_app/spoiler_preview.js
window.djangocmsMarkdownPreview = window.djangocmsMarkdownPreview || [];
window.djangocmsMarkdownPreview.push({
    // Markdown source in, markdown source out. Runs before the preview is
    // rendered, e.g. to protect a span from markdown with a placeholder.
    before: function (text) {
        return text.replace(/\|\|(.+?)\|\|/g, "<span class=\"spoiler\">$1</span>");
    },
    // Receives a detached element holding the rendered preview and may change
    // it. The element's innerHTML is what the preview shows.
    after: function (element) {
        element.querySelectorAll(".spoiler").forEach(function (spoiler) {
            spoiler.title = "Spoiler";
        });
    },
});
```

Both functions are optional. Processors run in registration order, for
"preview" as well as "side-by-side". An exception in a processor is logged to
the browser console and does not affect the preview or other processors.

### Minimal example app

```
my_app/
├── cms_config.py                     # see "Registering from cms_config.py"
├── markdown.py                       # the Python-Markdown extension
└── static/my_app/
    ├── spoiler.css, spoiler.js       # page assets
    └── spoiler_preview.js            # editor preview processor
```

```python
# my_app/markdown.py — turns ||text|| into <span class="spoiler">text</span>
from markdown.extensions import Extension
from markdown.inlinepatterns import SimpleTagInlineProcessor


class SpoilerProcessor(SimpleTagInlineProcessor):
    def __init__(self, pattern, css_class):
        super().__init__(pattern, "span")
        self.css_class = css_class

    def handleMatch(self, m, data):
        el, start, end = super().handleMatch(m, data)
        el.set("class", self.css_class)
        return el, start, end


class SpoilerExtension(Extension):
    def __init__(self, **kwargs):
        self.config = {"css_class": ["spoiler", "CSS class of the span"]}
        super().__init__(**kwargs)

    def extendMarkdown(self, md):
        md.inlinePatterns.register(
            SpoilerProcessor(r"()\|\|(.+?)\|\|", self.getConfig("css_class")),
            "spoiler",
            175,
        )


def makeExtension(**kwargs):
    return SpoilerExtension(**kwargs)
```

## Contributing

```bash
git clone https://github.com/fsbraun/djangocms-markdown.git
cd djangocms-markdown
python -m venv .venv
source .venv/bin/activate
pip install -e ".[test]"
pytest
```

## License

BSD-3-Clause
