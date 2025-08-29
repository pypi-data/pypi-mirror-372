import ast
import typing

from bs4 import BeautifulSoup, Tag

from mwparserfromhtml.parse.const import HTML_VERSION
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
from mwparserfromhtml.parse.plaintext import html_to_plaintext


class Article:
    """
    Class file to create instance of a Wikipedia article from the dump
    """

    def __init__(self, html: str, flatten_sections: bool = False) -> None:
        """
        Constructor for Article class
        """
        parsed_html = BeautifulSoup(html, "html.parser")
        wiki = parsed_html.find("base")["href"].split(".")[0].strip("//")
        self.wikistew = WikiStew(parsed_html, wiki)
        # make all sections first-order children of body as opposed to
        # potentially nested underneath each other. Useful for anything
        # where you iterate by sections and don't want duplicates
        if flatten_sections:
            adjusted = True
            while adjusted:
                subsections = []
                for d in self.wikistew.tag.descendants:
                    # tag is section nested under another section. only move first-order nested sections
                    # on each pass. otherwise doubly-nested sections will get out-of-order
                    if (
                        Section.is_section(d)
                        and Section.is_section(d.parent)
                        and d.parent not in subsections
                    ):
                        subsections.append(d)
                if not len(subsections):
                    adjusted = False
                for i in range(len(subsections) - 1, -1, -1):
                    subsections[i].parent.insert_after(subsections[i])

    def __str__(self) -> str:
        """
        String representation of the Article class
        """
        return f"Article({self.get_title()})"

    def __repr__(self) -> str:
        return str(self)

    def check_html_compatability(self) -> bool:
        """Checks if article HTML version matches library expectations."""
        try:
            return (
                self.wikistew.tag.find("meta", {"property": "mw:htmlVersion"})[
                    "content"
                ]
                == HTML_VERSION
            )
        except TypeError:
            return False

    def get_wiki(self) -> str:
        """Wikipedia language edition."""
        return self.wikistew.tag.find("base")["href"].split(".")[0].strip("//")

    def get_namespace(self) -> int:
        """Namespace ID."""
        return int(
            self.wikistew.tag.find("meta", {"property": "mw:pageNamespace"})["content"]
        )

    def get_title(self) -> str:
        """Page title."""
        return self.wikistew.tag.title.text

    def get_page_id(self) -> int:
        """Page ID."""
        return int(self.wikistew.tag.find("meta", {"property": "mw:pageId"})["content"])

    def get_revision_id(self) -> int:
        """Revision ID."""
        return int(self.wikistew.tag.find("html")["about"].rsplit("/", maxsplit=1)[1])

    def get_url(self) -> str:
        """Article URL"""
        href = self.wikistew.tag.find("link", {"rel": "dc:isVersionOf"})["href"]
        return f"https:{href}"

    def get_plaintext(self) -> typing.Generator[str, None, None]:
        """Opinionated plaintext extraction function."""
        skip_elements = {
            "Category",
            "Citation",
            "Comment",
            "Heading",
            "Infobox",
            "List",
            "Math",
            "Media-audio",
            "Media-img",
            "Media-video",
            "Messagebox",
            "Navigational",
            "Note",
            "Reference",
            "TF-sup",  # superscript: a little excessive but gets non-citation notes such as citation-needed tags.
            "Table",
            "Wikitable",
        }
        skip_para_contexts = {"pre-first-para", "between-paras", "post-last-para"}
        for chunk in WikiStew(self.wikistew.tag.body).to_plaintext(
            skip_elements, skip_para_contexts, exclude_transcluded_paragraphs=True
        ):
            for paragraph in chunk.split("\n"):
                paragraph = paragraph.strip()
                if paragraph:
                    yield paragraph


class WikiStew:
    """
    Class file for any generic block of BeautifulSoup HTML
    """

    def __init__(self, tag: typing.Union[Tag, str], wiki: str = "en"):
        """
        Constructor for HTML class
        """
        if isinstance(tag, str):
            self.tag = BeautifulSoup(tag, "html.parser")
        else:
            self.tag = tag
        self.wiki = wiki

    def get_sections(self) -> typing.List[Section]:
        """
        extract the article sections from a BeautifulSoup object.
        Returns:
            typing.List[Section]: list of sections
        """
        return [Section(t) for t in self.tag.find_all() if Section.is_section(t)]

    def get_comments(self) -> typing.List[Comment]:
        """
        extract the comments from a BeautifulSoup object.
        Returns:
            typing.List[Comment]: list of comments
        """
        return [Comment(t) for t in self.tag.find_all(string=Comment.is_comment)]

    def get_headings(self) -> typing.List[Heading]:
        """
        extract the headings from a BeautifulSoup object.
        Returns:
            typing.List[Heading]: list of headings
        """
        return [Heading(t) for t in self.tag.find_all() if Heading.is_heading(t)]

    def get_wikilinks(self) -> typing.List[Wikilink]:
        """
        extract wikilinks from a BeautifulSoup object.
        Returns:
            typing.List[Wikilink]: list of wikilinks
        """
        return [
            Wikilink(t, self.wiki)
            for t in self.tag.find_all()
            if Wikilink.is_wikilink(t)
        ]

    def get_categories(self) -> typing.List[Category]:
        """
        extract categories from a BeautifulSoup object.
        Returns:
            typing.List[Category]: list of categories
        """
        return [Category(t) for t in self.tag.find_all() if Category.is_category(t)]

    def get_text_formatting(self) -> typing.List[TextFormatting]:
        """
        extract text formattting from a BeautifulSoup object.
        Returns:
            typing.List[TextFormattting]: list to text-formatting elements
        """
        return [
            TextFormatting(t)
            for t in self.tag.find_all()
            if TextFormatting.is_text_formatting(t)
        ]

    def get_externallinks(self) -> typing.List[ExternalLink]:
        """
        extract external links from a BeautifulSoup object.
        Returns:
            typing.List[ExternalLink]: list of external links
        """
        return [
            ExternalLink(t)
            for t in self.tag.find_all()
            if ExternalLink.is_external_link(t)
        ]

    def get_templates(self) -> typing.Dict[str, dict]:
        """
        extract templates from a BeautifulSoup object.
        Returns:
            typing.Dict[str, dict]: dictionary of template IDs and data
        """

        # Template parts dictionaries can be complicated. They might be a single template or a list of multiple.
        # We parse the string to a dictionary but allow the handling to other functions
        # See: https://www.mediawiki.org/wiki/Specs/HTML#Template_markup
        templates = {}
        for t in self.tag.find_all():
            if t.has_attr("typeof") and "mw:Transclusion" in t.attrs["typeof"]:
                try:
                    template_name = t["about"]
                    template_data = ast.literal_eval(t["data-mw"])
                    templates[template_name] = template_data
                except Exception:
                    continue

        return templates

    def get_references(self) -> typing.List[Reference]:
        """
        extract references from a BeautifulSoup object.
        Returns:
            typing.List[Reference]: list of references
        """
        return [Reference(t) for t in self.tag.find_all() if Reference.is_reference(t)]

    def get_citations(self) -> typing.List[Citation]:
        """
        extract citations from a BeautifulSoup object.
        Returns:
            typing.List[Citation]: list of citations
        """
        return [Citation(t) for t in self.tag.find_all() if Citation.is_citation(t)]

    def get_images(self) -> typing.List[Media]:
        """
        extract images from a BeautifulSoup object.
        Returns:
            typing.List[Media]: list of image media objects
        """
        return [
            Media(t)
            for t in self.tag.find_all()
            if Media.is_media(t) and Media.get_media_type(t) == "img"
        ]

    def get_audio(self) -> typing.List[Media]:
        """
        extract audio from a BeautifulSoup object.
        Returns:
            typing.List[Media]: list of audio media objects
        """
        return [
            Media(t)
            for t in self.tag.find_all()
            if Media.is_media(t) and Media.get_media_type(t) == "audio"
        ]

    def get_video(self) -> typing.List[Media]:
        """
        extract videos from a BeautifulSoup object.
        Returns:
            typing.List[Media]: list of video media objects
        """
        return [
            Media(t)
            for t in self.tag.find_all()
            if Media.is_media(t) and Media.get_media_type(t) == "video"
        ]

    def get_lists(self) -> typing.List[List]:
        """Get List elements from BeautifulSoup object.

        Returns:
            typing.List[List]: list of List objects
        """
        return [List(t) for t in self.tag.find_all() if List.is_list(t)]

    def get_math(self) -> typing.List[Math]:
        """Get Math elements from BeautifulSoup object.

        Returns:
            typing.List[Math]: list of math objects
        """
        return [Math(t) for t in self.tag.find_all() if Math.is_math(t)]

    def get_infobox(self) -> typing.List[Infobox]:
        """Get infoboxes from BeautifulSoup object.

        Infobox is a table in the lead section that has a class
        with the word `infobox` in it. Sometimes infobox templates
        are re-used for navigational links, hence the lead section
        requirement. This generally will be just one infobox at most
        but we retain list for consistency and in case there are multiple.
        """
        return [Infobox(t) for t in self.tag.find("section") if Infobox.is_infobox(t)]

    def get_wikitables(self) -> typing.List[Wikitable]:
        """Get wikitables from BeautifulSoup object.

        Wikitables are core content tables found
        within articles.
        """
        return [Wikitable(t) for t in self.tag.find_all() if Wikitable.is_wikitable(t)]

    def get_nav_boxes(self) -> typing.List[Navigation]:
        """Get navigational boxes from BeautifulSoup object.

        Navigational boxes are boxes that contain links
        to related content.
        """
        return [
            Navigation(t) for t in self.tag.find_all() if Navigation.is_navigation(t)
        ]

    def get_message_boxes(self) -> typing.List[Messagebox]:
        """Get message boxes from BeautifulSoup object.

        Message boxes are informational messages in
        the form of a table contained within articles.
        """
        return [
            Messagebox(t) for t in self.tag.find_all() if Messagebox.is_message_box(t)
        ]

    def get_notes(self) -> typing.List[Note]:
        """Get notes from BeautifulSoup object.

        Notes are boxes that help readers understand
        whether they are on the correct page.
        """
        return [Note(t) for t in self.tag.find_all() if Note.is_note(t)]

    def to_plaintext(
        self,
        exclude_elements=None,
        exclude_para_context=None,
        exclude_transcluded_paragraphs=False,
    ) -> typing.Generator[str, None, None]:
        """
        extract plaintext from the HTML object in a depth-first manner.

        Args:
            exclude_elements: set. Set of element types to skip over. Leave none to ignore.
            exclude_para_context: set. Set of paragraph contexts to skipp over. Leave none to ignore.
            exclude_transcluded_paragraphs: boolean. True if paragraphs that are fully transcluded should be skipped.
        Yields:
            heading: either article title (lead section) or heading title (all others)
            plaintext: plaintext for a paragraph in that section
        """
        plaintext = ""
        transcluded_paragraph = True  # True unless a non-transcluded element found
        prev_para_context = "pre-first-para"
        for (
            node_plaintext,
            transcluded,
            element_types,
            para_context,
        ) in html_to_plaintext(self.tag):
            # excluded element type -- e.g., Citations -- so skip
            if exclude_elements and exclude_elements.intersection(element_types):
                continue

            # paragraph break -- dump content and restart
            elif node_plaintext == "\n" and set(element_types) == {"Section"}:
                if plaintext.strip() and (
                    not exclude_transcluded_paragraphs or not transcluded_paragraph
                ):
                    yield plaintext
                plaintext = ""
                transcluded_paragraph = True
                prev_para_context = para_context

            # exclude based on paragraph context -- e.g., no pre-paragraph content
            elif exclude_para_context and para_context in exclude_para_context:
                continue

            # very rare Parsoid bug (?) where missing paragraph break between heading in paragraph nodes
            # dump content and restart but retain current node
            elif para_context != prev_para_context:
                if plaintext.strip() and (
                    not exclude_transcluded_paragraphs or not transcluded_paragraph
                ):
                    yield plaintext
                plaintext = node_plaintext
                # paragraph only transcluded if all (non-whitespace) elements are transcluded
                transcluded_paragraph = transcluded or not node_plaintext.strip()
                prev_para_context = para_context

            # within paragraph that we're keeping - retain info
            else:
                plaintext += node_plaintext
                prev_para_context = para_context
                # paragraph only transcluded if all (non-whitespace) elements are transcluded
                if not transcluded and node_plaintext.strip():
                    transcluded_paragraph = False

        if plaintext.strip() and (
            not exclude_transcluded_paragraphs or not transcluded_paragraph
        ):
            yield plaintext
