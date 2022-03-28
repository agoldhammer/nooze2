#!/usr/bin/env python
import os
import sys

from nzdb.configurator import nzdbConfig
from nzdb.dbif import getAuthors, mapAuthorToLang, storeAuthor, cleanAuthorsCollection


def main():
    authfile = nzdbConfig["authfile"]
    authfile = os.path.expanduser(authfile)
    cleanAuthorsCollection()
    with open(authfile) as lines:
        for line in lines:
            [author, lang] = line.split(":")
            storeAuthor(author, lang.strip())
    display_all()
    sys.exit(0)


def display_all():
    print("inserted")
    authors = getAuthors()
    for author in authors:
        lang = mapAuthorToLang(author)
        print(f"{author} speaks {lang}")


if __name__ == "__main__":
    main()
