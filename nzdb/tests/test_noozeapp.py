# import json
from urllib.parse import quote
from nzdb.noozeapp import parse_query, extract_options, app

testqs = [
    "-d 1 *Executive *Judicial",
    "-H 8 Warren Gillibrand",
    "-d 5 *Business Schumer",
    "-s 12/15/2017 -e 12/16/2017 Jones *Executive",
]


def test_extract_options():
    expected = ["-d 1", "-H 8", "-d 5", "-s 12/15/2017 -e 12/16/2017"]
    for i in range(len(testqs)):
        parts = testqs[i].split(" ")
        options, _ = extract_options(parts)
        assert options == expected[i]  # nosec


def test_parse_query():
    expected = [
        ["-d 1 *Executive", "-d 1 *Judicial"],
        ['-H 8 "Warren Gillibrand"'],
        ["-d 5 *Business", '-d 5 "Schumer"'],
        [
            "-s 12/15/2017 -e 12/16/2017 *Executive",
            '-s 12/15/2017 -e 12/16/2017 "Jones"',
        ],
    ]
    for i in range(len(testqs)):
        _, queries = parse_query(testqs[i])
        assert queries == expected[i]  # nosec


def test_routes():
    client = app.test_client()
    resp = client.get("/")
    assert b"html" in resp.data  # nosec
    # resp = client.get('/statuses/-d 1 Macron')
    # assert(b'Macron' in resp.data)
    resp = client.get("/error")
    assert b"html" in resp.data  # nosec
    resp = client.get("/stats")  # nosec
    assert b"html" in resp.data  # nosec
    resp = client.get("/help")
    assert b"html" in resp.data  # nosec


def test_json_routes():
    # json api
    client = app.test_client()
    resp = client.get("/json/cats")
    assert resp.content_type == "application/json"  # nosec

    resp = client.get("/json/recent")
    assert resp.status == "200 OK"  # nosec

    data = "data=?-d 1 *France"
    data = quote(data)
    resp = client.get("/json/qry?data=-d%201%20*France")
    assert resp.content_type == "application/json"  # nosec
    assert resp.status == "200 OK"  # nosec


def test_count():
    client = app.test_client()
    resp = client.get("/json/count")
    assert resp.status == "200 OK"  # nosec
    jdata = resp.get_json()
    assert isinstance(jdata["count"], int)  # nosec
