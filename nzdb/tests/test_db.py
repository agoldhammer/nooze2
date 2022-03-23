from nzdb.connectdb import get_db
from nzdb.dbif import getTopics, esearch, storeAuthor, getUnknownAuthors
from nzdb.cmdline import processCmdLine
from nzdb.dupdetect import isURL, tokenize, filter_dups, dedupe


def test_connect():
    db = get_db()
    info = db.client.server_info()
    assert info is not None  # nosec


def test_topics():
    topics = getTopics()
    for topic in topics:
        assert topic["desc"] != ""  # nosec


def test_bad_topic():
    """
    If we query with a *topic not in db, shd get back empty string
    """
    search_context = processCmdLine("-d 1 *xyznonsense")
    err, cursor = esearch(search_context)
    assert err is not None  # nosec
    assert cursor == []  # nosec


def test_isURL():
    s1 = "https://www.agmardor.com"
    s2 = "http://www.agm.com"
    s3 = "xyz"
    s4 = "https:/"
    assert isURL(s1)  # nosec
    assert isURL(s2)  # nosec
    assert isURL(s3) is False  # nosec
    assert isURL(s4)  # nosec


def test_tokenize():
    text = "Now is the time for all good men http://www.agm.com"
    tokenized = ["Now", "is", "the", "time", "for", "all", "good", "men"]
    assert tokenize(text) == tokenized  # nosec


def test_filter_dups1():
    cursor = [
        {"text": "this is a tweet"},
        {"text": "this is another"},
        {"text": "this is a tweet"},
        {"text": "this is another http://www.example.com"},
        {"text": "this is à fifth"},
    ]
    results = [False, False, True, True, False]
    for isdup, _ in filter_dups(cursor):
        assert isdup == results.pop(0)  # nosec
    filtered = [status for status in dedupe(cursor)]
    assert filtered == [cursor[0], cursor[1], cursor[4]]  # nosec


def test_unknown_find():
    storeAuthor("xyz123zyx", "U")
    found = False
    unknowns = getUnknownAuthors()
    for unk in unknowns:
        if unk["author"] == "xyz123zyx":
            found = True
    assert found  # nosec
