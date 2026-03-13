"""Markdown extension for ~~strikethrough~~ syntax, rendering as <del>."""

from markdown import Extension
from markdown.inlinepatterns import InlineProcessor
from xml.etree.ElementTree import Element

DEL_RE = r"(?<!\~)\~\~(?!\~)(.+?)(?<!\~)\~\~(?!\~)"


class DelInlineProcessor(InlineProcessor):
    def handleMatch(self, m, data):
        el = Element("del")
        el.text = m.group(1)
        return el, m.start(0), m.end(0)


class DeleteExtension(Extension):
    def extendMarkdown(self, md):
        md.inlinePatterns.register(DelInlineProcessor(DEL_RE, md), "del", 175)


def makeExtension(**kwargs):
    return DeleteExtension(**kwargs)
