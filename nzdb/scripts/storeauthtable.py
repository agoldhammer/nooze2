#!/usr/bin/env python
import os

from nzdb.configurator import nzdbConfig
from nzdb.dbif import getAuthors, mapAuthorToLang, storeAuthor


def main():
    authfile = nzdbConfig["authfile"]
    authfile = os.path.expanduser(authfile)
    with open(authfile) as lines:
        for line in lines:
            [author, lang] = line.split(":")
            storeAuthor(author, lang.strip())
    display_all()


def display_all():
    print("inserted")
    authors = getAuthors()
    for author in authors:
        lang = mapAuthorToLang(author)
        print(f"{author} speaks {lang}")


if __name__ == "__main__":
    main()
