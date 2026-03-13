"""Resolve dynamic object references in rendered HTML.

References use the format ``ref:app_label.model_name:pk`` inside href
attributes.  For example::

    <a href="ref:cms.page:42">My Page</a>

Resolution happens in three steps:
1. Collect all references from the HTML.
2. Batch-fetch referenced objects grouped by model (one query per model).
3. Replace each ``ref:`` URL with the object's ``get_absolute_url()``.

Objects that no longer exist or lack ``get_absolute_url`` are replaced
with ``#``.
"""

import re
from collections import defaultdict

from django.apps import apps

REF_RE = re.compile(r'href="ref:([a-zA-Z0-9_]+\.[a-zA-Z0-9_]+):(\d+)"')


def collect_references(html):
    """Return a dict mapping ``(app_label, model_name)`` to sets of PKs."""
    refs = defaultdict(set)
    for match in REF_RE.finditer(html):
        app_model = match.group(1)
        pk = int(match.group(2))
        try:
            app_label, model_name = app_model.split(".")
        except ValueError:
            continue
        refs[(app_label, model_name)].add(pk)
    return refs


def fetch_objects(refs):
    """Fetch objects for all references, one query per model.

    Returns a dict mapping ``"app_label.model_name:pk"`` to URL strings.
    """
    url_map = {}
    for (app_label, model_name), pks in refs.items():
        try:
            model = apps.get_model(app_label, model_name)
        except LookupError:
            for pk in pks:
                url_map[f"{app_label}.{model_name}:{pk}"] = "#"
            continue

        objects = model.objects.filter(pk__in=pks)
        found_pks = set()
        for obj in objects:
            found_pks.add(obj.pk)
            try:
                url = obj.get_absolute_url()
            except AttributeError:
                url = "#"
            url_map[f"{app_label}.{model_name}:{obj.pk}"] = url

        for pk in pks - found_pks:
            url_map[f"{app_label}.{model_name}:{pk}"] = "#"

    return url_map


def resolve_references(html):
    """Resolve all ``ref:`` URLs in *html* to absolute URLs.

    Returns the HTML unchanged if it contains no references.
    """
    if not html or "ref:" not in html:
        return html

    refs = collect_references(html)
    if not refs:
        return html

    url_map = fetch_objects(refs)

    def _replace(match):
        key = f"{match.group(1)}:{match.group(2)}"
        url = url_map.get(key, "#")
        return f'href="{url}"'

    return REF_RE.sub(_replace, html)
