#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys

from nzdb.cmdline import processCmdLine
from nzdb.dbif import instrumented_esearch
from nzdb.prettytext import printMatches


class SearchException(Exception):
    pass


def main():
    search_context = processCmdLine()
    err, cursor, times = instrumented_esearch(search_context)
    if err is not None:
        print("Error parsing query:", err)
    else:
        t0, t1, t2, t3 = times
        printMatches(cursor)
        print(f"get_db {t1 - t0}, search {t2 - t1}, sort {t3 - t2}")


if __name__ == "__main__":
    main()
    sys.exit(0)
