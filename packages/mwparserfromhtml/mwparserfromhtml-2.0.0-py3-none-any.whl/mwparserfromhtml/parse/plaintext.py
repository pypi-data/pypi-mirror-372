import typing

from bs4 import Tag

from mwparserfromhtml.parse.elements import (
    Category,
    Citation,
    Comment,
    ExternalLink,
    Heading,
    Infobox,
    List,
    Math,
    Media,
    Messagebox,
    Navigation,
    Note,
    Reference,
    Section,
    TextFormatting,
    Wikilink,
    Wikitable,
)
from mwparserfromhtml.parse.utils import is_transcluded


def _tag_to_element(tag: Tag) -> str:
    """Determine if a tag has a specific associated Element type."""
    if Section.is_section(tag):
        return "Section"
    elif Heading.is_heading(tag):
        return "Heading"
    elif tag.name == "a":
        if Category.is_category(tag):
            return "Category"
        elif Wikilink.is_wikilink(tag):
            return "Wikilink"
        elif ExternalLink.is_external_link(tag):
            return "ExternalLink"
    elif tag.name == "table":
        if Wikitable.is_wikitable(tag):
            return "Wikitable"
        elif Messagebox.is_message_box(tag):
            return "Messagebox"
        elif Infobox.is_infobox(tag):
            return "Infobox"
        else:
            return "Table"
    elif Media.is_media(tag):
        return f"Media-{Media.get_media_type(tag)}"
    elif Navigation.is_navigation(tag):
        return "Navigation"
    elif Note.is_hatnote(tag):
        return "Note"
    elif Reference.is_reference(tag):
        return "Reference"
    elif Citation.is_citation(tag):
        return "Citation"
    elif List.is_list(tag):
        return "List"
    elif Math.is_math(tag):
        return "Math"
    elif Comment.is_comment(tag):
        return "Comment"
    elif TextFormatting.is_text_formatting(tag):
        return f"TF-{tag.name}"
    return ""


def html_to_plaintext(
    parent_node: Tag,
    transcluded: bool = False,
    parent_types: typing.Optional[typing.List[str]] = None,
    para_context: typing.Optional[str] = None,
) -> typing.Iterator[typing.Tuple[str, bool, typing.List[str], str]]:
    """
    recursive depth-first search function to traverse the HTML tree.
    this expects either `html.body` (full article) as initial input
    or individual sections. otherwise it'll work but paragraph
    context will be unreliable.

    returns generator that is tuple with following elements:
    - plaintext string extracted from the HTML node
    - boolean indicating if this element was transcluded
    - List of elements that are parents to the string to help filter if e.g.,
      the string is nested within an infobox. Only covers elements with explicit
      class objects and not all HTML tags.
    - paragraph context. One of the following strings:
        - `pre-first-para`: content that appears before first <p> element in section
        - `in-para`: content directly in a <p> element
        - `between-paras`: content not directly in <p> node but between first and last paragraph in section
        - `post-last-para`: content after last <p> node in section
    """
    element = _tag_to_element(parent_node)
    if parent_types is None:  # root - initiate empty list of parent node types
        parent_types = []
    section_layer = False

    # top-level section node. identify index and number of paragraphs
    if element == "Section":
        section_layer = True
        first_para = None
        last_para = None
        for i, c in enumerate(parent_node.children):
            if c.name == "p":
                if first_para is None:
                    first_para = i
                last_para = i

    # base Element class doesn't tell us anything so don't add to parent nodes list.
    # Also add a few additional special details that are from classes and help in
    # guiding what sort of content the text is.
    if element:
        parent_types.append(element)
    if "nomobile" in parent_node.get("class", []):
        parent_types.append("nomobile")
    if "noprint" in parent_node.get("class", []):
        parent_types.append("noprint")

    # loop through direct children to node
    for i, cnode in enumerate(parent_node.children):
        # identify paragraph context
        if section_layer:
            if first_para is None or i < first_para:
                para_context = "pre-first-para"
            elif cnode.name == "p":
                para_context = "in-para"
            elif i <= last_para:
                para_context = "between-paras"
            else:
                para_context = "post-last-para"
        # if node has attributes (tag), keep recursively iterating through them
        if hasattr(cnode, "attrs"):
            yield from html_to_plaintext(
                cnode,
                transcluded or is_transcluded(cnode),
                parent_types.copy(),
                para_context,
            )
        else:  # we've reached base raw string for a tag -- output its text and metadata
            yield (cnode.text, transcluded, parent_types, para_context)
