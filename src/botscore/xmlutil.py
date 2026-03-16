"""
XML helpers for the extracted runtime core.
"""

from __future__ import annotations


def indent_xml(node, level=0, indentstring='    '):
    """Indent xml node"""
    text2indent = '\n' + level * indentstring
    if len(node):
        if not node.text or not node.text.strip():
            node.text = text2indent + indentstring
        for subnode in node:
            indent_xml(subnode, level + 1, indentstring=indentstring)
            if not subnode.tail or not subnode.tail.strip():
                subnode.tail = text2indent + indentstring
        if not node[-1].tail or not node[-1].tail.strip():
            node[-1].tail = text2indent
    else:
        if level and (not node.tail or not node.tail.strip()):
            node.tail = text2indent
