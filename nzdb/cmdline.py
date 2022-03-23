#! /usr/bin/env python
# -*- coding:utf-8 -*-

"""
cmdline.py -- command line processing for feed query
"""
import argparse
import sys
from datetime import timedelta

import delorean


class SearchContext:
    def __init__(self, startdate, enddate, query, expand):
        """
        :class: SearchContext, provides context for searches
          expand indicates confidence level for expanded search
        """
        self.startdate = startdate
        self.enddate = enddate
        self.query = query
        self.expand = expand

    def __str__(self):
        return "Search context: {}-{}\nQuery: {}\
         Expand: {}".format(
            self.startdate, self.enddate, self.query, self.expand
        )


def processCmdLine(cl=None):
    """
    Process command line for modules run stand-alone
    return start and end times as datetime objects
    :param cl: command line can be fed by program
    """
    text1 = "Process docs between start and end dates"
    epilog = "Specify dates as yyyy-mm-ddThh:mm:ss.sss \
    or (European style!!) dd/mm/yyyy,\
    specify d days ago with -d option \
    or h hours ago with -H option.\n \
    Query broadened topic with *topic (must be in database)"
    parser = argparse.ArgumentParser(text1, epilog=epilog)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-s", "--start", help="start date/time")
    group.add_argument("-d", "--day", help="start n days ago")
    parser.add_argument("-e", "--end", help="end date/time")
    parser.add_argument("-x", "--expand", help="expand threshold")
    parser.add_argument("-H", "--hour", help="start h hours ago")
    parser.add_argument("query", type=str, nargs="+", help="specify query")
    if cl is None:
        args = parser.parse_args()
    else:
        args = parser.parse_args(cl.split())

    try:
        today = delorean.Delorean()
        if args.day is not None:
            daysAgo = int(args.day)
            startde = today.next_day(-1 * daysAgo)
            endde = today
        elif args.hour is not None:
            hrsAgo = int(args.hour)
            startde = today - timedelta(hours=hrsAgo)
            endde = today
        elif args.start is not None:
            startde = delorean.parse(args.start, yearfirst=True, dayfirst=False)
        else:
            startde = today
        if args.end is not None:
            endde = delorean.parse(args.end, yearfirst=True, dayfirst=False)
        else:
            endde = today
    except Exception as e:
        print("Error parsing date")
        print(e)
        sys.exit(1)
    expand = int(args.expand) if args.expand is not None else None
    query = " ".join(args.query)
    return SearchContext(startde.datetime, endde.datetime, query=query, expand=expand)


if __name__ == "__main__":
    sc = processCmdLine("-d 1 tax")
    print(sc)
    sc = processCmdLine("-d 1 *France")
    print(sc)
    # sc = processCmdLine(None)
    # print(sc)
