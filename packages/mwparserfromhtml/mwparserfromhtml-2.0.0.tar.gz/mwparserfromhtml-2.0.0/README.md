# mwparserfromhtml

`mwparserfromhtml` is a Python library for parsing and mining metadata from the Enterprise HTML Dumps that has been recently made available by the [Wikimedia Enterprise](https://enterprise.wikimedia.com/). The 6 most updated Enterprise HTML dumps can be accessed from [*this location*](https://dumps.wikimedia.org/other/enterprise_html/runs/). The aim of this library is to provide an interface to work with these HTML dumps and extract the most relevant features from an article.

Besides using the HTML dumps, users can also use the [Wikipedia API](https://en.wikipedia.org/api/rest_v1/#/Page%20content/get_page_html__title_) to obtain the HTML of a particular article from their title and parse the HTML string with this library.

## Motivation
When rendering contents, MediaWiki converts wikitext to HTML, allowing for the expansion of macros to include more material. The HTML version of a Wikipedia page generally has more information than the original source wikitext. So, it's reasonable that anyone who wants to analyze Wikipedia's content as it appears to its readers would prefer to work with HTML rather than wikitext. Traditionally, only the wikitext version has been available in the [XML-dumps](https://dumps.wikimedia.org/backup-index.html). Now, with the introduction of the Enterprise HTML dumps in 2021, anyone can now easily access and use HTML dumps (and they should).

However, parsing HTML to extract the necessary information is not a simple process. An inconspicuous user may know how to work with HTMLs but they might not be used to the specific format of the dump files. Also the wikitext translated to HTMLs by the MediaWiki API have many different edge-cases and requires heavy investigation of the documentation to get a grasp of the structure. Identifying the features from this HTML is no trivial task! Because of all these hassles, it is likely that individuals would continue working with wikitext as there are already excellent ready-to-use parsers for it (such as [mwparserfromhell](https://github.com/earwig/mwparserfromhell)).
Therefore, we wanted to write a Python library that can efficiently parse the HTML-code of an article from the Wikimedia Enterprise dumps to extract relevant elements such as text, links, templates, etc. This will hopefully lower the technical barriers to work with the HTML-dumps and empower researchers and others to take advantage of this beneficial resource.

## Features
* Iterate over large tarballs of HTML dumps without extracting them to memory (memory efficient, but not subscriptable unless converted to a list)
* Extract major article metadata like Category, Templates, Wikilinks, External Links, Media, References etc. with their respective type and status information
* Easily extract the content of an article from the HTML dump and customizing the level of detail
* Generate summary statistics for the articles in the dump


## Installation

You can install ``mwparserfromhtml`` with ``pip``:

```bash
$ pip install mwparserfromhtml
```

## Basic Usage
Check out [`example_notebook.ipynb`](docs/tutorials/example_notebook.ipynb) to have a runnable example.

* Import the dump module from the library and load the dump:

```python
from mwparserfromhtml import HTMLDump

html_file_path = "TARGZ_FILE_PATH"
html_dump = HTMLDump(html_file_path)
```

* Iterate over the articles in the dump:

```python
for article in html_dump:
    print(article.get_title())
```

* Extract the plain text of an article from the dump, i.e. remove anything that is not text such as infoboxes,
citation footnotes, or categories and replace links with their [anchor text](https://en.wikipedia.org/wiki/Anchor_text):

```python
for article in html_dump:
    print(article.get_title())
    prev_heading = "_Lead"
    for heading, paragraph in article.html.wikistew.get_plaintext(exclude_transcluded_paragraphs=True,
                                                                  exclude_para_context=None,  # set to {"pre-first-para", "between-paras", "post-last-para"} for more conservative approach
                                                                  exclude_elements={"Heading", "Math", "Citation", "List", "Wikitable", "Reference"}):
        if heading != prev_heading:
            print(f"\n{heading}:")
            prev_heading = heading
        print(paragraph)
```

* Extract the number of Sections, Comments, Headings, Wikilinks, Categories, Text Formatting Elements, External Links, Templates, References, Citations, Images, Audio, Video, Lists, Math Elements, Infoboxes, Wikitables, Navigational Boxes, Message Boxes and Notes from the dump.

```python
for article in html_dump:
    print(f"Number of Sections: {len(article.wikistew.get_sections())}")
    print(f"Number of Comments: {len(article.wikistew.get_comments())}")
    print(f"Number of Headings: {len(article.wikistew.get_headings())}")
    print(f"Number of Wikilinks: {len(article.wikistew.get_wikilinks())}")
    print(f"Number of Categories: {len(article.wikistew.get_categories())}")
    print(f"Number of Text Formatting Elements: {len(article.wikistew.get_text_formatting())}")
    print(f"Number of External Links: {len(article.wikistew.get_externallinks())}")
    print(f"Number of Templates: {len(article.wikistew.get_templates())}")
    print(f"Number of References: {len(article.wikistew.get_references())}")
    print(f"Number of Citations: {len(article.wikistew.get_citations())}")
    print(f"Number of Images: {len(article.wikistew.get_images())}")
    print(f"Number of Audio: {len(article.wikistew.get_audio())}")
    print(f"Number of Video: {len(article.wikistew.get_video())}")
    print(f"Number of Lists: {len(article.wikistew.get_lists())}")
    print(f"Number of Math Elements: {len(article.wikistew.get_math())}")
    print(f"Number of Infoboxes: {len(article.wikistew.get_infobox())}")
    print(f"Number of Wikitables: {len(article.wikistew.get_wikitables())}")
    print(f"Number of Navigational Boxes: {len(article.wikistew.get_nav_boxes())}")
    print(f"Number of Message Boxes: {len(article.wikistew.get_message_boxes())}")
    print(f"Number of Notes: {len(article.wikistew.get_notes()}")

```

* Alternatively, you can process stand-alone Parsoid HTML e.g., from the APIs and convert to an `Article` object to extract the features
```python
from mwparserfromhtml import Article
import requests

lang = "en"
title = "Both Sides, Now"
r = requests.get(f'https://{lang}.wikipedia.org/api/rest_v1/page/html/{title}')
article = Article(r.text)
print(f"Article Name: {article.get_title()}")
print(f"Abstract: {article.wikistew.get_first_paragraph()}")
```

## Project Information
- [Licensing](https://gitlab.wikimedia.org/repos/research/html-dumps/-/blob/main/LICENSE)
- [Repository](https://gitlab.wikimedia.org/repos/research/html-dumps)
- [Issue Tracker](https://gitlab.wikimedia.org/repos/research/html-dumps/-/issues)
- [Contribution Guidelines](CONTRIBUTION.md)
- [Tutorials](docs/tutorials)

## Acknowledgements

This project was started as part of an [Outreachy](https://www.outreachy.org/) internship from May--August 2022. This project has benefited greatly from the work of Earwig ([mwparserfromhell](https://github.com/earwig/mwparserfromhell)) and Slavina Stefanova ([mwsql](https://github.com/mediawiki-utilities/python-mwsql)).
