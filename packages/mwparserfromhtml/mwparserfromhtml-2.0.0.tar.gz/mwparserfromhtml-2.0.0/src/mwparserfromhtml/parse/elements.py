from bs4 import Comment as bsComment  # for parsing the HTML
from bs4 import Tag

from mwparserfromhtml.parse.utils import href_to_link_parts, is_transcluded


class Element:
    """
    Base class to instantiate a wiki element from the HTML
    """

    def __init__(self, html_tag: Tag):
        self.name = self.__class__.__name__
        self.html_tag = html_tag

    def __str__(self):
        return f"{self.name} ({self.html_tag})"

    def is_transcluded(self):
        return is_transcluded(self.html_tag)


class Wikilink(Element):
    """
    Instantiates a Wikilink object from HTML string. The Wikilink object contains the following attributes:
    - disambiguation: boolean, True if if the wikilink leads to a disambiguation page
    - redirect: boolean, True if the wikilink is a redirect
    - redlink: boolean, True if the wikilink is a redlink
    - interwiki: boolean, True if the wikilink is an interwiki link
    """

    def __init__(self, html_tag: Tag, wiki: str = "en"):
        """
        Args:
            html_tag: a BeautifulSoup Tag object.
            language: the language of article content, required for determining the namespace of the wikilink.
        """
        super().__init__(html_tag)
        self.title = html_tag["title"] if html_tag.has_attr("title") else ""
        self.text = html_tag.text
        self.namespace_id = href_to_link_parts(self.title, wiki).namespace
        self.disambiguation = False
        self.redirect = False
        self.redlink = False
        self.interwiki = False

        if html_tag.has_attr("class"):
            if "new" in html_tag["class"]:  # redlink
                self.redlink = True
            if "mw-disambig" in html_tag["class"]:  # disambiguation
                self.disambiguation = True
            if "mw-redirect" in html_tag["class"]:  # redirect
                self.redirect = True
            if "extiw" in html_tag["class"]:
                self.interwiki = True

    @staticmethod
    def is_wikilink(html_tag: Tag) -> bool:
        return (
            html_tag.name == "a"
            and html_tag.has_attr("rel")
            and "mw:WikiLink"
            in "".join(html_tag["rel"])  # keeps things like mw:WikiLink/Interwiki
        )


class ExternalLink(Element):
    """
    Instantiates an ExternalLink object from HTML string.
    The ExternalLink object contains the following attributes:
    - autolinked: boolean, True if the external link is not a numbered or a named link
    - numbered: boolean, True if the external link is a numbered link
    - named: boolean, True if the external link is a named link
    """

    def __init__(self, html_tag: Tag):
        """
        Args:
            html_tag: a BeautifulSoup Tag object.
        """
        super().__init__(html_tag)
        self.title = html_tag["title"] if html_tag.has_attr("title") else ""
        self.link = html_tag["href"] if html_tag.has_attr("href") else ""
        self.autolinked = False
        self.numbered = False
        self.named = False
        if "text" in html_tag["class"]:
            self.named = True
        elif "autonumber" in html_tag["class"]:
            self.numbered = True
        else:
            self.autolinked = True

    @staticmethod
    def is_external_link(html_tag: Tag) -> bool:
        return (
            html_tag.name == "a"
            and html_tag.has_attr("rel")
            and "mw:ExtLink" in html_tag["rel"]
        )


class TextFormatting(Element):
    """
    Instantiates a TextFormatting object from a BeautifulSoup Tag object.
    The TextFormatting object contains the following attributes:
    - formatting: the type of formatting applied
    """

    def __init__(self, html_tag: Tag):
        """
        Args:
            html_tag: a BeautifulSoup Tag object.
        """
        super().__init__(html_tag)
        self.formatting = html_tag.name

    @staticmethod
    def is_text_formatting(html_tag: Tag) -> bool:
        return html_tag.name in {
            "b",
            "strong",
            "i",
            "em",
            "dfn",
            "blockquote",
            "code",
            "q",
            "mark",
            "small",
            "del",
            "s",
            "ins",
            "u",
            "sub",
            "sup",
            "pre",
        }


class Category(Element):
    """
    Instantiates a Category object from a BeautifulSoup Tag object.
    The Category object contains the following attributes:
    - title: the title of the Category normalized from the link
    """

    def __init__(self, html_tag: Tag):
        """
        Args:
            html_tag: a BeautifulSoup Tag object.
        """
        super().__init__(html_tag)
        self.link = html_tag["href"] if html_tag.has_attr("href") else ""
        try:
            self.title = self.link.split(":", 1)[1].replace("_", " ")
        except IndexError:
            self.title = self.link.replace("_", " ")

    @staticmethod
    def is_category(html_tag: Tag) -> bool:
        return (
            html_tag.name == "link"
            and html_tag.has_attr("rel")
            and "mw:PageProp/Category" in html_tag["rel"]
        )


class Reference(Element):
    """
    Instantiates a References object from HTML string.
    The References object contains the following attributes:
    """

    def __init__(self, html_tag: Tag):
        """
        Args:
            html_tag: a BeautifulSoup Tag object.
            Reference objects include the following attribute:
            - ref_id: the id of the reference, that can be used to connect it with the place of reference
        """
        super().__init__(html_tag)
        self.ref_id = html_tag["id"]
        self.ref_text = html_tag.find("span", attrs={"class": "mw-reference-text"})

    @staticmethod
    def is_reference(html_tag: Tag) -> bool:
        return (
            html_tag.name == "li"
            and html_tag.has_attr("id")
            and html_tag["id"].startswith("cite_note-")
        )


class Citation(Element):
    """
    Instantiates a Citation object from HTML string.
    While a Reference object refers to the unique reference
    (at the bottom of the article), a Citation object refers
    to an instance of that Reference being cited in text and
    is represented with e.g., [1] superscript.
    The Citation object contains the following attributes:
    """

    def __init__(self, html_tag: Tag):
        """
        Args:
            html_tag: a BeautifulSoup Tag object.
            Reference objects include the following attribute:
            - ref_id: the id of the reference, that can be used to connect it with the place of reference
        """
        super().__init__(html_tag)
        self.cite_id = html_tag["id"]
        # self.ref_id = TODO parse data-mw templatedata and extract cite_note-ID

    @staticmethod
    def is_citation(html_tag: Tag) -> bool:
        return (
            html_tag.name == "sup"
            and html_tag.has_attr("typeof")
            and "mw:Extension/ref" in html_tag["typeof"]
        )


class List(Element):
    """
    Instantiates a List object from HTML string.
    Each object is an entire list (series of <li> elements).
    The data from the individual list items can be extracted
    by iterating through the <li> children.
    """

    def __init__(self, html_tag: Tag):
        """
        Args:
            html_tag: a BeautifulSoup Tag object.
            Reference objects include the following attribute:
            - ordered: boolean. True if ordered (<ol>). False if not (<ul>).
        """
        super().__init__(html_tag)
        self.ordered = html_tag.name == "ol"

    @staticmethod
    def is_list(html_tag) -> bool:
        return html_tag.name in {"ul", "ol"}


class Media(Element):
    """
    Instantiates a Media object from HTML string. The Media object contains the following attributes:
    - title: the title of the media
    - link: the link to the media
    - extension: file extension
    - caption: caption associated with the media
    """

    def __init__(self, html_tag: Tag):
        """
        Args:
            html_tag: a BeautifulSoup Tag object.
            media_type: if the value is one, it represents an image object.
            Otherwise, it can be audio or video.
        """
        super().__init__(html_tag)
        self.caption = self.get_caption()
        self.media_tag = (
            self.html_tag.find("img")
            or self.html_tag.find("audio")
            or self.html_tag.find("video")
            or {}
        )
        # get filename but lop off "./File:" prefix
        self.title = self.media_tag.get("resource", "").split(":", maxsplit=1)[-1]
        # extract extension -- e.g., "jpg"
        self.extension = self.title.rsplit(".", maxsplit=1)[-1]
        self.height = int(self.media_tag.get("height", -1))
        self.width = int(self.media_tag.get("width", -1))
        self.alt_text = self.media_tag.get("alt", "")
        self.duration = int(self.media_tag.get("data-durationhint", 0))

    @staticmethod
    def is_media(html_tag: Tag) -> bool:
        return html_tag.has_attr("typeof") and html_tag["typeof"].startswith("mw:File")

    @staticmethod
    def get_media_type(html_tag: Tag) -> str:
        """Get type of media (img, audio, video)"""
        if html_tag.find("img"):
            return "img"
        elif html_tag.find("audio"):
            return "audio"
        elif html_tag.find("video"):
            return "video"
        else:
            return "other"

    def get_caption(self) -> str:
        """Get plaintext caption for media (if exists)."""
        try:
            # standard file
            return self.html_tag.find("figcaption").text
        except AttributeError:
            try:
                # gallery
                # * Description: https://www.mediawiki.org/wiki/Help:Images#Rendering_a_gallery_of_images
                # * Spec: https://www.mediawiki.org/wiki/Specs/HTML/2.8.0/Extensions/Gallery
                return self.html_tag.find(attrs={"class": "mw-file-description"}).attrs[
                    "title"
                ]
            except (AttributeError, KeyError):
                try:
                    # some infobox images
                    if "caption" in "".join(self.html_tag.next_sibling["class"]):
                        return self.html_tag.next_sibling.text
                except (KeyError, TypeError):
                    pass
        return ""


class Wikitable(Element):
    """
    Instantiates a Wikitable object from HTML string.
    """

    def __init__(self, html_tag: Tag):
        """
        Args:
            html_tag: a BeautifulSoup Tag object.
        """
        super().__init__(html_tag)

    @staticmethod
    def is_wikitable(html_tag: Tag) -> bool:
        return (
            html_tag.name == "table"
            and html_tag.has_attr("class")
            and "wikitable" in html_tag["class"]
        )


class Infobox(Element):
    """
    Instantiates an Infobox object from HTML string.
    """

    def __init__(self, html_tag: Tag):
        """
        Args:
            html_tag: a BeautifulSoup Tag object.
        """
        super().__init__(html_tag)

    @staticmethod
    def is_infobox(html_tag: Tag) -> bool:
        return (
            html_tag.name == "table"
            and html_tag.has_attr("class")
            and "infobox" in "".join(html_tag["class"])  # french uses infobox_v2
        )


class Navigation(Element):
    """
    Instantiates a Navigation object from HTML string.
    Common subbtypes include:
    - navboxes (<div class="navbox...): classic centered box at bottom with related links
    - sidebars (<table class="sidebar...): below infobox; links to other content in series
    - sideboxes (<div class="sideb-box...): see also; links to media in other sister projects
    - portalboxes (<ul class="portalbox...): at bottom; links to related portals
    - sister project boxes (<div class="sister-box...): see also; links to media on other sister projects
    """

    def __init__(self, html_tag: Tag):
        """
        Args:
            html_tag: a BeautifulSoup Tag object.
        """
        super().__init__(html_tag)

    def get_type(self) -> str:
        if self.is_navbox(self.html_tag):
            return "navbox"
        elif self.is_sidebar(self.html_tag):
            return "sidebar"
        elif self.is_sidebox(self.html_tag):
            return "sidebox"
        elif self.is_portalbox(self.html_tag):
            return "portalbox"
        elif self.is_sister_project(self.html_tag):
            return "sisterprojectbox"
        else:
            return "navigation"

    @staticmethod
    def is_navigation(html_tag: Tag) -> bool:
        return html_tag.has_attr("role") and html_tag["role"] == "navigation"

    @staticmethod
    def is_navbox(html_tag: Tag) -> bool:
        return (
            html_tag.name == "div"
            and html_tag.has_attr("class")
            and "navbox" in html_tag["class"]
        )

    @staticmethod
    def is_sidebar(html_tag: Tag) -> bool:
        return (
            html_tag.name == "table"
            and html_tag.has_attr("class")
            and "sidebar" in html_tag["class"]
        )

    @staticmethod
    def is_sidebox(html_tag: Tag) -> bool:
        return (
            html_tag.name == "div"
            and html_tag.has_attr("class")
            and "side-box" in html_tag["class"]
        )

    @staticmethod
    def is_portalbox(html_tag: Tag) -> bool:
        # portalbox; portal-bar; portal
        return (
            html_tag.name == "ul"
            and html_tag.has_attr("class")
            and "portal" in "".join(html_tag["class"])
        )

    @staticmethod
    def is_sister_project(html_tag: Tag) -> bool:
        # sistersitebox; sister-box; sisterlinks
        return (
            html_tag.name == "div"
            and html_tag.has_attr("class")
            and "sister" in "".join(html_tag["class"])
        )


class Note(Element):
    """
    Instantiates a Note object from HTML string.
    Common subbtypes include:
    - hatnotes (<div class="hatnote...)
    - article stub boxes (<div class="asbox...)
    - disambiguation boxes (<div class="dmbox...)
    """

    def __init__(self, html_tag: Tag):
        """
        Args:
            html_tag: a BeautifulSoup Tag object.
        """
        super().__init__(html_tag)

    def get_type(self) -> str:
        if self.is_hatnote(self.html_tag):
            return "hatnote"
        elif self.is_dmbox(self.html_tag):
            return "dmbox"
        elif self.is_asbox(self.html_tag):
            return "asbox"
        else:
            return "note"

    def get_date(self) -> str:
        date = self.html_tag.find("span", attrs={"class": "date"})
        if date:
            date = date.text
        return date

    @staticmethod
    def is_note(html_tag: Tag) -> bool:
        return html_tag.has_attr("role") and html_tag["role"] == "note"

    @staticmethod
    def is_hatnote(html_tag: Tag) -> bool:
        return (
            html_tag.name == "div"
            and html_tag.has_attr("class")
            and "hatnote" in "".join(html_tag["class"])
        )

    @staticmethod
    def is_dmbox(html_tag: Tag) -> bool:
        return (
            html_tag.name == "div"
            and html_tag.has_attr("class")
            and "dmbox" in html_tag["class"]
        )

    @staticmethod
    def is_asbox(html_tag: Tag) -> bool:
        return (
            html_tag.name == "div"
            and html_tag.has_attr("class")
            and ("asbox" in html_tag["class"] or "stub" in html_tag["class"])
        )


class Messagebox(Element):
    """
    Instantiates a Message object from HTML string.
    Depending on the namespace, the message box can be multiple types:
    - ambox: Main article namespace
    - cmbox: Category namespace
    - fmbox: Footer/header (any namespace)
    - imbox: Image namespace
    - tmbox: Talk namespace
    - ombox: Other namespace or specialized styling
    """

    def __init__(self, html_tag: Tag):
        """
        Args:
            html_tag: a BeautifulSoup Tag object.
        """
        super().__init__(html_tag)

    def get_date(self) -> str:
        date = self.html_tag.find("span", attrs={"class": "date"})
        if date:
            date = date.text
        return date

    @staticmethod
    def is_message_box(html_tag: Tag) -> bool:
        return (
            html_tag.name == "table"
            and html_tag.has_attr("class")
            and "mbox" in "".join(html_tag["class"])
        )


class Math(Element):
    """
    Instantiates an Math object from HTML string.
    """

    def __init__(self, html_tag: Tag):
        """
        Args:
            html_tag: a BeautifulSoup Tag object.
        """
        super().__init__(html_tag)

    @staticmethod
    def is_math(html_tag: Tag) -> bool:
        return (
            html_tag.name == "span"
            and html_tag.has_attr("typeof")
            and "mw:Extension/math" in html_tag["typeof"]
        )


class Comment(Element):
    """Instantiates a Comment object from HTML string."""

    def __init__(self, html_tag: Tag):
        """
        Args:
            html_tag: a BeautifulSoup Tag object.
        """
        super().__init__(html_tag)
        self.plaintext = html_tag.string  # override to easily expose comment text

    @staticmethod
    def is_comment(html_tag: Tag) -> bool:
        return isinstance(html_tag, bsComment)


class Heading(Element):
    """
    Instantiates a Heading object from HTML string.

    The Heading object contains the following attributes:
    - level: how nested the section is (ranges from top-level 2 to highly-nested 6)
    """

    def __init__(self, html_tag: Tag):
        """
        Args:
            html_tag: a BeautifulSoup Tag object.
        """
        super().__init__(html_tag)
        self.level = int(html_tag.name.strip("h"))
        self.title = html_tag.text.strip()

    @staticmethod
    def is_heading(html_tag: Tag) -> bool:
        return html_tag.name in {"h2", "h3", "h4", "h5", "h6"}


class Section(Element):
    """
    Instantiates a Section object from HTML string.

    The Section object contains the following attributes:
    - index: which section on the page it is (O-indexed)
    """

    def __init__(self, html_tag: Tag):
        """
        Args:
            html_tag: a BeautifulSoup Tag object.
        """
        super().__init__(html_tag)
        self.index = int(html_tag.attrs.get("data-mw-section-id", -1))
        self.heading = ""
        try:
            heading = html_tag.find()
            if heading.name.startswith("h"):
                self.heading = heading.attrs["id"]
        except Exception:
            pass

    @staticmethod
    def is_section(html_tag: Tag) -> bool:
        return html_tag.name == "section"
