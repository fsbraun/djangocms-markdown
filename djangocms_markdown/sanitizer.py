from copy import deepcopy

import nh3
from django.conf import settings


def _get_text_setting(name, default):
    """Get a setting from TEXT_* (djangocms-text) namespace."""
    return getattr(settings, name, default)


def get_sanitizer_kwargs():
    """Build nh3.clean() kwargs respecting djangocms-text TEXT_* settings.

    Reuses the same settings as djangocms-text for consistency:
    - TEXT_HTML_SANITIZE: enable/disable sanitization (default True)
    - TEXT_ADDITIONAL_TAGS: extra allowed HTML tags
    - TEXT_ADDITIONAL_ATTRIBUTES: extra allowed attributes per tag
    - TEXT_ADDITIONAL_PROTOCOLS: extra allowed URL schemes
    """
    tags = deepcopy(nh3.ALLOWED_TAGS)
    attributes = deepcopy(nh3.ALLOWED_ATTRIBUTES)
    url_schemes = deepcopy(nh3.ALLOWED_URL_SCHEMES)
    generic_attribute_prefixes = {"data-", "aria-"}

    # Markdown-specific tags/attributes that nh3 defaults may not include
    markdown_additional = {
        "*": {"style", "class", "role", "id"},
        "a": {"href", "target", "rel"},
        "img": {"src", "alt", "title", "width", "height", "loading"},
        "input": {"type", "checked", "disabled"},  # for task list checkboxes (opt-in)
        "td": {"align"},
        "th": {"align"},
        "code": {"class"},  # codehilite language classes
        "span": {"class"},  # codehilite spans
        "pre": {"class"},
        "div": {"class"},  # codehilite wrapper divs
        "label": {"class"},  # for task list labels (opt-in)
    }

    markdown_additional_tags = {"input", "label", "span", "div", "details", "summary"}

    tags |= markdown_additional_tags

    for tag, attrs in markdown_additional.items():
        attributes[tag] = attributes.get(tag, set()) | attrs

    # Apply TEXT_ADDITIONAL_TAGS from djangocms-text settings
    additional_tags = _get_text_setting("TEXT_ADDITIONAL_TAGS", ())
    tags |= set(additional_tags)

    # Apply TEXT_ADDITIONAL_ATTRIBUTES from djangocms-text settings
    additional_attributes = _get_text_setting("TEXT_ADDITIONAL_ATTRIBUTES", {})
    for tag, attrs in additional_attributes.items():
        if isinstance(attrs, (list, tuple)):
            attrs = set(attrs)
        attributes[tag] = attributes.get(tag, set()) | attrs

    # Apply TEXT_ADDITIONAL_PROTOCOLS from djangocms-text settings
    additional_protocols = _get_text_setting("TEXT_ADDITIONAL_PROTOCOLS", ())
    url_schemes |= set(additional_protocols)

    return {
        "tags": tags,
        "attributes": attributes,
        "url_schemes": url_schemes,
        "generic_attribute_prefixes": generic_attribute_prefixes,
        "link_rel": None,
    }


def sanitize_html(html):
    """Sanitize HTML using nh3, respecting djangocms-text settings.

    Returns the input unchanged if TEXT_HTML_SANITIZE is False.
    """
    if not html:
        return html

    if _get_text_setting("TEXT_HTML_SANITIZE", True) is False:
        return html

    return nh3.clean(html, **get_sanitizer_kwargs())
