#!/usr/bin/env python

"""
Run this program to update topics collection in database
  after a change to topics.txt
"""
import os
from collections import namedtuple

from nzdb.configurator import nzdbConfig
from nzdb.dbif import cleanTopicsCollection, getTopics, storeTopic

"""
Builds database from topics.txt
File should be arranged as follows
topic (abbrev used in query):Description:Category:Query
example:
Greece:Greece:Countries:Greece Grèce Grecia Griechenland
"""

row = namedtuple("row", ["topic", "desc", "cat", "query"])


def display_all():
    topics = getTopics()
    for topic in topics:
        print(
            "{}: {} : {} : {}".format(
                topic["topic"], topic["desc"], topic["cat"], topic["query"]
            )
        )


def main():
    fname = nzdbConfig["topicsfile"]
    fname = os.path.expanduser(fname)
    # clean topics collection before updating
    cleanTopicsCollection()
    with open(fname) as f:
        for line in f:
            if line != "\n" and not line.startswith("#"):
                line = line.strip().split(":")
                assert len(line) == 4
                topic = row(*line)._asdict()
                storeTopic(topic)
    display_all()


if __name__ == "__main__":
    main()
