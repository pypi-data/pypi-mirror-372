from collections import Counter

from context import (
    Article,
    WikiStew,
    example_article_one,
    example_article_two,
    example_html_three,
    href_to_link_parts,
    is_transcluded,
)

# TODO: test non-English examples, especially in cases where
# we're relying on classnames or extensions such as:
# * references/citations
# * infoboxes
# * message boxes
# * notes
# * math
# * navigation

# TODO: way more extensive plaintext tests. Hitting aspects like:
# * Templated-content within a paragraph that's relevant
# * Lists
# * Tables

def test_get_headings():
    article = Article(example_html_three)
    expected_headers = ["Background", "2000 re-recording", "Certifications", "Judy Collins version", "Chart history",
                        "Weekly charts", "Year-end charts", "Notable recordings", "References"]
    assert [h.title for h in article.wikistew.get_headings()] == expected_headers
    l3_headings = ["Certifications", "Chart history"]
    assert [h.title for h in article.wikistew.get_headings() if h.level == 3] == l3_headings


def test_get_sections():
    article = Article(example_article_two["article_body"]["html"])
    number_of_expected_sections = 3
    assert [s.index for s in article.wikistew.get_sections()] == [i for i in range(number_of_expected_sections)]


def test_get_no_comments():
    article = Article(example_article_one["article_body"]["html"])
    number_of_expected_headers = 0
    assert len(article.wikistew.get_comments()) == number_of_expected_headers


def test_get_wikilinks_one():
    article = Article(example_article_one["article_body"]["html"])
    test_wlink_objs = article.wikistew.get_wikilinks()
    for w in test_wlink_objs:
        print(w, w.namespace_id)
    number_of_expected_wikilinks = 6
    number_of_redirects = 0
    number_of_redlinks = 0
    number_of_disambiguations = 0
    number_of_interwikilinks = 0
    number_of_transclusions = 1
    number_of_namespaces = {0: 5, 12: 1}
    test_redlink = 0
    test_disambiguation = 0
    test_redirect = 0
    test_transclusion = 0
    test_interwiki = 0
    test_namespace = {}
    for item in test_wlink_objs:
        test_namespace[item.namespace_id] = test_namespace.get(item.namespace_id, 0) + 1
        if item.redlink:
            test_redlink += 1
        if item.redirect:
            test_redirect += 1
        if item.disambiguation:
            test_disambiguation += 1
        if item.interwiki:
            test_interwiki += 1
        if is_transcluded(item.html_tag):
            test_transclusion += 1
    assert len(test_wlink_objs) == number_of_expected_wikilinks
    assert test_redlink == number_of_redlinks
    assert test_redirect == number_of_redirects
    assert test_disambiguation == number_of_disambiguations
    assert test_interwiki == number_of_interwikilinks
    assert test_transclusion == number_of_transclusions
    assert test_namespace == number_of_namespaces


def test_get_wikilinks_two():
    article = Article(example_article_two["article_body"]["html"])
    test_wlink_objs = article.wikistew.get_wikilinks()
    number_of_expected_wikilinks = 31
    number_of_redirects = 6
    number_of_redlinks = 2
    number_of_disambiguations = 1
    number_of_interwikilinks = 1
    number_of_transclusions = 4
    number_of_namespaces = {0: 31}
    test_redlink = 0
    test_disambiguation = 0
    test_redirect = 0
    test_transclusion = 0
    test_interwiki = 0
    test_namespace = {}
    for item in test_wlink_objs:
        test_namespace[item.namespace_id] = test_namespace.get(item.namespace_id, 0) + 1
        if item.redlink:
            test_redlink += 1
        if item.redirect:
            test_redirect += 1
        if item.disambiguation:
            test_disambiguation += 1
        if item.interwiki:
            test_interwiki += 1
        if is_transcluded(item.html_tag):
            test_transclusion += 1
    assert len(test_wlink_objs) == number_of_expected_wikilinks
    assert test_redlink == number_of_redlinks
    assert test_redirect == number_of_redirects
    assert test_disambiguation == number_of_disambiguations
    assert test_interwiki == number_of_interwikilinks
    assert test_transclusion == number_of_transclusions
    assert test_namespace == number_of_namespaces


def test_get_externallinks_one():
    article = Article(example_article_one["article_body"]["html"])
    test_exlinks_objs = article.wikistew.get_externallinks()
    number_of_expected_externallinks = 1
    number_of_autolink = 0
    number_of_numbered = 0
    number_of_named = 1
    number_of_transclusion = 1
    test_autolink = 0
    test_named = 0
    test_numbered = 0
    test_transclusion = 0

    for item in test_exlinks_objs:
        if item.autolinked:
            test_autolink += 1
        if item.named:
            test_named += 1
        if item.numbered:
            test_numbered += 1
        if is_transcluded(item.html_tag):
            test_transclusion += 1

    assert len(test_exlinks_objs) == number_of_expected_externallinks
    assert test_autolink == number_of_autolink
    assert test_named == number_of_named
    assert test_numbered == number_of_numbered
    assert test_transclusion == number_of_transclusion


def test_get_externallinks_two():
    article = Article(example_article_two["article_body"]["html"])
    test_exlinks_objs = article.wikistew.get_externallinks()
    number_of_expected_externallinks = 1
    number_of_autolink = 0
    number_of_numbered = 0
    number_of_named = 1
    number_of_transclusion = 1
    test_autolink = 0
    test_named = 0
    test_numbered = 0
    test_transclusion = 0

    for item in test_exlinks_objs:
        if item.autolinked:
            test_autolink += 1
        if item.named:
            test_named += 1
        if item.numbered:
            test_numbered += 1
        if is_transcluded(item.html_tag):
            test_transclusion += 1

    assert len(test_exlinks_objs) == number_of_expected_externallinks
    assert test_autolink == number_of_autolink
    assert test_named == number_of_named
    assert test_numbered == number_of_numbered
    assert test_transclusion == number_of_transclusion


def test_get_categories():
    article = Article(example_article_two["article_body"]["html"])
    test_categories_objs = article.wikistew.get_categories()
    number_of_expected_categories = 11
    number_of_transclusion = 5
    test_transclusions = 0
    for item in test_categories_objs:
        if is_transcluded(item.html_tag):
            test_transclusions += 1
    assert len(test_categories_objs) == number_of_expected_categories
    assert test_transclusions == number_of_transclusion


def test_get_templates():
    article = Article(example_article_two["article_body"]["html"])
    test_templates_objs = article.wikistew.get_templates()
    number_of_expected_templates = 6
    assert len(test_templates_objs) == number_of_expected_templates


def test_get_references():
    article = Article(example_html_three)
    number_of_expected_references = 31
    assert len(article.wikistew.get_references()) == number_of_expected_references


def test_get_lists():
    article = Article(example_html_three)
    number_of_expected_lists = 1  # a ton more in nav box / references but I want just non-transcluded ones
    assert len([l for l in article.wikistew.get_lists() if not l.is_transcluded()]) == number_of_expected_lists


def test_get_citations():
    article = Article(example_article_two["article_body"]["html"])
    number_of_expected_citations = 1
    assert len(article.wikistew.get_citations()) == number_of_expected_citations


def test_get_notes():
    article = Article(example_html_three)
    number_of_expected_notes = 1
    assert len(article.wikistew.get_notes()) == number_of_expected_notes


def test_get_infobox():
    article = Article(example_html_three)
    number_of_expected_infoboxes = 1  # the article has a second one but in a later section
    assert len(article.wikistew.get_infobox()) == number_of_expected_infoboxes


def test_get_wikitables():
    article = Article(example_html_three)
    number_of_expected_wikitables = 3
    assert len(article.wikistew.get_wikitables()) == number_of_expected_wikitables


def test_get_navigation():
    article = Article(example_html_three)
    number_of_expected_navigation = 5
    assert len(article.wikistew.get_nav_boxes()) == number_of_expected_navigation


def test_get_text_formatting():
    section = WikiStew(Article(example_html_three).wikistew.get_sections()[1].html_tag)
    expected_tags = {"blockquote": 1, "sup": 3, "i": 2}
    assert Counter([t.formatting for t in section.get_text_formatting()]) == expected_tags

def test_get_media():
    # TODO: test gallery extraction
    # TODO: test video
    article = Article(example_html_three)
    expected_image_captions = ["", "US single sleeve"]
    expected_image_alt_text = ["", ""]
    expected_icon_captions = ["", ""]
    expected_icon_alt_text = ["", "Edit this at Wikidata"]
    max_icon_pixel_area = 2500  # (50 x 50)
    expected_audio_durations = [20]
    expected_video_durations = []
    article_images = [i for i in article.wikistew.get_images() if (i.height * i.width) > max_icon_pixel_area]
    article_icons = [i for i in article.wikistew.get_images() if (i.height * i.width) <= max_icon_pixel_area]
    assert [i.caption for i in article_images] == expected_image_captions
    assert [i.caption for i in article_icons] == expected_icon_captions
    assert [i.alt_text for i in article_images] == expected_image_alt_text
    assert [i.alt_text for i in article_icons] == expected_icon_alt_text
    assert [a.duration for a in article.wikistew.get_audio()] == expected_audio_durations
    assert [v.duration for v in article.wikistew.get_video()] == expected_video_durations


def test_first_paragraph_two():
    article = Article(example_html_three)
    expected_first_paragraph = "\"Both Sides, Now\" is a song by Canadian singer-songwriter Joni Mitchell. First recorded by Judy Collins, it appeared on the US singles chart during the fall of 1968. The next year it was included on Mitchell's album Clouds, and became one of her best-known songs. It has since been recorded by dozens of artists, including Dion in 1968, Clannad with Paul Young in 1991, and Mitchell herself who re-recorded the song with an orchestral arrangement on her 2000 album Both Sides Now."
    assert next(article.get_plaintext()) == expected_first_paragraph

def test_get_metadata():
    article = Article(example_html_three)
    expected_revid = 1187100446
    expected_ns = 0
    expected_pageid = 6572508
    expected_title = "Both Sides, Now"
    expected_url = "https://en.wikipedia.org/wiki/Both_Sides%2C_Now"

    assert article.get_namespace() == expected_ns
    assert article.get_page_id() == expected_pageid
    assert article.get_revision_id() == expected_revid
    assert article.get_title() == expected_title
    assert article.get_url() == expected_url
    assert article.check_html_compatability()


def test_link_part_util():
    article_href = "./Who_Knows_Where_the_Time_Goes%3F"
    link = href_to_link_parts(article_href, "en")
    assert link.namespace == 0
    assert link.prefix == ""
    assert link.title == "Who Knows Where the Time Goes%3F"

    es_help_href = "./Ayuda:Edición"
    link = href_to_link_parts(es_help_href, "es")
    assert link.namespace == 12
    assert link.prefix == "Ayuda"
    assert link.title == "Edición"
