"""Resolve dynamic object references in rendered HTML.

References use the format ``ref:app_label.model_name:pk`` inside href
or src attributes.  For example::

    <a href="ref:cms.page:42">My Page</a>
    <img src="ref:myapp.image:7" alt="Photo">

Resolution happens in three steps:
1. Collect all references from the HTML.
2. Batch-fetch referenced objects grouped by model (one query per model).
3. Replace each ``ref:`` URL with the object's ``get_absolute_url()``.

Unresolved links are replaced with their plain text content.
Unresolved images are removed entirely.
"""

import re
from collections import defaultdict

from django.apps import apps

_REF_PATTERN = r"ref:([a-zA-Z0-9_]+\.[a-zA-Z0-9_]+):(\d+)"

REF_RE = re.compile(r'(?:href|src)="' + _REF_PATTERN + r'"')
LINK_RE = re.compile(r'<a\s[^>]*href="' + _REF_PATTERN + r'"[^>]*>(.*?)</a>')
IMG_RE = re.compile(r'<img\s[^>]*src="' + _REF_PATTERN + r'"[^>]*/?\s*>')


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
    Missing objects or objects without ``get_absolute_url`` map to ``None``.
    """
    url_map = {}
    for (app_label, model_name), pks in refs.items():
        try:
            model = apps.get_model(app_label, model_name)
        except LookupError:
            for pk in pks:
                url_map[f"{app_label}.{model_name}:{pk}"] = None
            continue

        objects = model.objects.filter(pk__in=pks)
        found_pks = set()
        for obj in objects:
            found_pks.add(obj.pk)
            try:
                url = obj.get_absolute_url() or None
            except AttributeError:
                url = None
            url_map[f"{app_label}.{model_name}:{obj.pk}"] = url

        for pk in pks - found_pks:
            url_map[f"{app_label}.{model_name}:{pk}"] = None

    return url_map


def resolve_references(html):
    """Resolve all ``ref:`` URLs in *html* to absolute URLs.

    Resolved references become normal links/images. Unresolved links
    are replaced with their plain text content. Unresolved images are
    removed entirely.

    Returns the HTML unchanged if it contains no references.
    """
    if not html or "ref:" not in html:
        return html

    refs = collect_references(html)
    if not refs:
        return html

    url_map = fetch_objects(refs)

    def _replace_link(match):
        key = f"{match.group(1)}:{match.group(2)}"
        url = url_map.get(key)
        if url is None:
            return match.group(3)
        return match.group(0).replace(f'href="ref:{key}"', f'href="{url}"')

    def _replace_img(match):
        key = f"{match.group(1)}:{match.group(2)}"
        url = url_map.get(key)
        if url is None:
            return ""
        return match.group(0).replace(f'src="ref:{key}"', f'src="{url}"')

    html = LINK_RE.sub(_replace_link, html)
    html = IMG_RE.sub(_replace_img, html)
    return html
