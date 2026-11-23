"""Python-Markdown extensions contributed by the test apps."""

from markdown.extensions import Extension
from markdown.inlinepatterns import SimpleTagInlineProcessor


class MarkExtension(Extension):
    """``==text==`` -> ``<mark>text</mark>``"""

    def extendMarkdown(self, md):
        md.inlinePatterns.register(
            SimpleTagInlineProcessor(r"()==(.+?)==", "mark"), "tests_mark", 175
        )


class _InsertProcessor(SimpleTagInlineProcessor):
    def __init__(self, pattern, attrs):
        super().__init__(pattern, "ins")
        self.attrs = attrs

    def handleMatch(self, m, data):
        el, start, end = super().handleMatch(m, data)
        for name, value in self.attrs.items():
            if value:
                el.set(name, value)
        return el, start, end


class InsertExtension(Extension):
    """``++text++`` -> ``<ins>text</ins>`` with configurable class and role."""

    def __init__(self, **kwargs):
        self.config = {
            "css_class": ["", "CSS class of the <ins> tag"],
            "role": ["", "role attribute of the <ins> tag"],
        }
        super().__init__(**kwargs)

    def extendMarkdown(self, md):
        attrs = {
            "class": self.getConfig("css_class"),
            "role": self.getConfig("role"),
        }
        md.inlinePatterns.register(
            _InsertProcessor(r"()\+\+(.+?)\+\+", attrs), "tests_insert", 174
        )
