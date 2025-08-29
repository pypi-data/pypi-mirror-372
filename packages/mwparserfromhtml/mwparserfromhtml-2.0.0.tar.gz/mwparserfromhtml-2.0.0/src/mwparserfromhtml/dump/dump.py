import datetime
import json
import os
import tarfile
from pathlib import Path

from mwparserfromhtml.parse.article import Article


class HTMLDump:
    """
    Class file to create instances of Wikimedia Enterprise HTML Dumps
    """

    def __init__(self, filepath: str = None, fileobj=None) -> None:
        """
        Constructor for HTMLDump class
        """
        assert filepath is not None or fileobj is not None

        if fileobj is not None:
            self.size = -1.0
            if filepath is None:
                # fileobj may not have useful path info, so we'll only
                # use it if no filename is explicitly provided
                self.database = str(Path(fileobj.name).name).split("-")[0]

            self.tarfile_open_args = {
                "name": None,
                "fileobj": fileobj,
                "mode": f"{fileobj.mode.strip('b+')}:gz",
            }
        elif filepath is not None:
            self.size = os.path.getsize(filepath) / (1024 * 1024 * 1024)
            self.database = str(Path(filepath).name).split("-")[0]

            self.tarfile_open_args = {
                "name": filepath,
                "fileobj": None,
                "mode": "r:gz",
            }

    def __str__(self) -> str:
        """
        String representation of the HTMLDump class
        """
        return f" HTMLDump (database = {self.database}, size = {self.size} GB"

    def __repr__(self) -> str:
        """
        String representation of the HTMLDump class
        """
        return str(self)

    def __iter__(self):
        """
        Iterator of the Article class
        """
        return self.read_dump()

    def read_dump(self):
        """
        Reads a dump file and returns an iterator of the rows.
        Returns:
            Iterator[List[Any]]: iterator of the rows
        """

        tar_file_ = tarfile.open(**self.tarfile_open_args)
        count = 0
        while True:
            html_fn = tar_file_.next()
            if html_fn is None:
                tar_file_.close()
                return

            else:
                with tar_file_.extractfile(html_fn) as file_input:
                    for line in file_input:
                        article = json.loads(line)
                        count += 1
                        try:
                            yield Document(article)
                        except Exception:
                            print(f"Article parsing failed for: {article}")
                            continue


class Document:
    """
    Class file to create instances of documents within Wikimedia Enterprise HTML Dumps
    """

    def __init__(self, document) -> None:
        """
        Constructor for Article class
        """
        self.document = document
        self.html = Article(document["article_body"]["html"])

    def __str__(self):
        """
        String representation of the Article class
        """
        return f"Document({self.get_title()})"

    def __repr__(self):
        return str(self)

    def get_namespace(self) -> int:
        return self.document["namespace"]["identifier"]

    def get_title(self) -> str:
        return self.document["name"]

    def get_page_id(self) -> int:
        return self.document["identifier"]

    def get_wikitext(self) -> str:
        return self.document["article_body"]["wikitext"]

    def get_qid(self) -> str:
        return self.document["main_entity"]["identifier"]

    def get_article_creation_date(self) -> datetime.date:
        return datetime.datetime.strptime(
            self.document["date_created"], "%Y-%m-%dT%H:%M:%SZ"
        )

    def get_curr_revision_time(self) -> datetime.date:
        return datetime.datetime.strptime(
            self.document["date_modified"], "%Y-%m-%dT%H:%M:%SZ"
        )

    def get_prev_revision_time(self) -> datetime.date:
        return datetime.datetime.strptime(
            self.document["date_previously_modified"], "%Y-%m-%dT%H:%M:%SZ"
        )
