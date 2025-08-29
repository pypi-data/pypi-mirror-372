import typing
from dataclasses import dataclass

from bs4 import Tag

from mwparserfromhtml.parse.const import NAMESPACES


@dataclass
class Link:
    title: str
    prefix: str
    namespace: int


def _get_transclusion_id(html_tag: Tag) -> typing.Optional[str]:
    """Check if a specific element is transcluded."""
    if html_tag.has_attr("about") and html_tag["about"].startswith("#mwt"):
        return html_tag["about"]
    return None


def is_transcluded(html_tag: Tag) -> bool:
    """Check if element or any of its parents are transcluded."""
    if _get_transclusion_id(html_tag):
        return True
    for p in html_tag.parents:
        if _get_transclusion_id(p):
            return True
    return False


def href_to_link_parts(href: str, wiki: str) -> Link:
    """Map href attribute to wikilink components."""
    namespace = 0
    prefix = ""
    title = ""
    if ":" in href:
        prefix = href.split(":", maxsplit=1)[0].strip("./").replace("_", " ")
        if prefix in NAMESPACES[wiki]:
            namespace = NAMESPACES[wiki][prefix]
            title = href.split(":", maxsplit=1)[1].replace("_", " ")
        else:
            prefix = ""
    if not namespace:
        title = href.strip("./").replace("_", " ")
    return Link(title, prefix, namespace)
