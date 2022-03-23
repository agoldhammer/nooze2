"""
dupdetect -- detect duplicate or near-duplicate textts
"""

import re
from collections import defaultdict
from hashlib import blake2b


def isURL(text):
    """
     Detects URLs in text via regexp
     :param text: string possible containing regexp
     :return true/false:
     :rtype: boolean
    """

    pattern = r"(https?:/\S*)"
    p = re.compile(pattern)
    if p.match(text.strip()):
        return True
    else:
        return False


def tokenize(text):
    """
     Breaks text into tokens, eliminating URLs
     :param text: a status text
     :return: list of tokens
     :rtype: list
    """
    # take care of edge case where url is surrounded by newlines
    text = text.replace("\n", " ")
    # replace ellipses
    text = text.replace("\u2026", "")
    tokens = text.split(" ")
    return [token for token in tokens if not isURL(token)]


DUP = True
NOTDUP = False


def filter_dups(cursor):
    """
     Eliminates near duplicates from cursor of statuses
     :param cursor: a cursor of statuses
     :return: isdup, status generator; isdup TRUE if
        status is a near dup of one alread seen
     :rtype: generator
    """

    hashes = defaultdict(list)
    for status in cursor:
        b = blake2b(digest_size=20)
        tokens = tokenize(status["text"])
        urlstripped = " ".join(tokens)
        b.update(urlstripped.encode("latin-1", "backslashreplace"))
        h = b.hexdigest()
        # real statuses have ids but testing statuses don't, so
        # we kludge this by appending a 1 if there is no id
        hashes[h].append(status.get("id", 1))
        if len(hashes[h]) == 1:  # this status is new, so yield it
            yield NOTDUP, status
        else:
            yield DUP, status


# Called by noozeapp
def dedupe(cursor):
    """
     Takes cursor of statuses with duplicates and returns cursor without
        duplicates
     :param cursor: cursor of statuses
     :return cursor: deduplicated cursor
     :rtype: generator
    """

    for isdup, status in filter_dups(cursor):
        if not isdup:
            yield status
