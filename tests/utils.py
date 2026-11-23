import re


def media_paths(media):
    """Return the (js, css) URLs of a ``forms.Media`` in output order.

    Reads the rendered media rather than ``Media._js``/``Media._css``, whose
    items are strings or asset objects depending on the Django version.
    """
    html = str(media)
    js = re.findall(r'<script[^>]*\ssrc="([^"]+)"', html)
    css = re.findall(r'<link[^>]*\shref="([^"]+)"', html)
    return js, css
