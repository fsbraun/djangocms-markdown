# djangocms-markdown

[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/djangocms-markdown)](https://pypi.org/project/djangocms-markdown/)
[![PyPI - Django Version](https://img.shields.io/pypi/djversions/djangocms-markdown)](https://pypi.org/project/djangocms-markdown/)
[![PyPI - Django CMS Version](https://img.shields.io/pypi/frameworkversions/django-cms/djangocms-markdown)](https://pypi.org/project/djangocms-markdown/)
[![codecov](https://codecov.io/gh/fsbraun/djangocms-markdown/graph/badge.svg?token=LEwTZILg2S)](https://codecov.io/gh/fsbraun/djangocms-markdown)

A markdown content plugin and model field for
[django CMS](https://www.django-cms.org/). Write content in Markdown using an
integrated editor and have it rendered as HTML on your site.

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
  Default: `"https://cdn.jsdelivr.net/npm/easymde@2.20.0/dist"`

Rendered HTML is sanitized with [nh3](https://github.com/messense/nh3) using
the same settings as
[djangocms-text](https://github.com/django-cms/djangocms-text):

- **`TEXT_HTML_SANITIZE`** — set to `False` to disable sanitization (default `True`)
- **`TEXT_ADDITIONAL_TAGS`** — extra HTML tags to allow
- **`TEXT_ADDITIONAL_ATTRIBUTES`** — extra attributes to allow per tag
- **`TEXT_ADDITIONAL_PROTOCOLS`** — extra URL schemes to allow

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
