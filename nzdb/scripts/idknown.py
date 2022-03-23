#!/usr/bin/env python

from nzdb.dbif import getUnknownAuthors


def showUknowns():
    print("Unknown authors:")
    for unknown in getUnknownAuthors():
        print(unknown)


if __name__ == "__main__":
    showUknowns()
