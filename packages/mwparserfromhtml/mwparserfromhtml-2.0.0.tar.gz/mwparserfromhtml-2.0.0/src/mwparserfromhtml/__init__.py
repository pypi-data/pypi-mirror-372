from .dump.dump import HTMLDump
from .parse.article import Article, WikiStew

__title__ = "mwparserfromhtml"
__summary__ = """mwparserfromhtml is a package that supports plaintext
and object extraction from Wikipedia HTML dumps"""
__url__ = "https://gitlab.wikimedia.org/repos/research/html-dumps"

__version__ = "2.0.0"

__license__ = "MIT License"

__all__ = ["HTMLDump", "Article", "WikiStew"]
