import logging
import re
from collections import OrderedDict, defaultdict
from itertools import chain, groupby
from time import perf_counter

from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_bootstrap import Bootstrap
from flask.json import JSONEncoder

from nzdb.configurator import nzdbConfig
from nzdb.dbif import (
    fetch_recent,
    getCount,
    getTopics,
    websearch,
    xcount,
    xcounts,
    xwebsearch,
    xgraphdb,
)

import ujson as json

# TODO! removing dupdetect for now
# from nzdb.dupdetect import dedupe


class WebQueryParseException(Exception):
    pass


LOGFILENAME = nzdbConfig["logfile"]
LOGNAME = nzdbConfig["logname"]

# configuration
DEBUG = False
logger = logging.getLogger(LOGNAME)
logging.basicConfig(level=logging.DEBUG)
f_handler = logging.FileHandler(LOGFILENAME)
f_format = logging.Formatter("%(asctime)s:%(name)s-app:%(levelname)s:%(message)s")
f_handler.setFormatter(f_format)
f_handler.setLevel(logging.NOTSET)
logger.addHandler(f_handler)

SECRET_KEY = nzdbConfig["SECRET_KEY"]
USERNAME = nzdbConfig["USERNAME"]
PASSWORD = nzdbConfig["PASSWORD"]

templates = nzdbConfig["templates"]
static = nzdbConfig["static"]
# ?FIXME! add to config eventually
images = "~/Prog/nooze2/app/images/signature.jpg"

app = Flask(__name__, template_folder=templates, static_folder=static)

# added 2/18/21 per
# https://stackoverflow.com/questions/37931927/why-is-flasks-jsonify-method-slow/37932098
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = False
app.config["JSON_SORT_KEYS"] = False
# app.config.from_object(__name__)

# manager = Manager(app)
bootstrap = Bootstrap(app)


# for below hack, see
# https://stackoverflow.com/questions/64203233/how-can-i-use-ujson-as-a-flask-encoder-decoder
class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        try:
            return json.dumps(obj)
        except TypeError:
            return JSONEncoder.default(self, obj)


app.json_encoder = CustomJSONEncoder


# timing, return time in ms
def mstimer():
    return 1000 * perf_counter()


def getStats():
    """
    :returns: dictionary {"size": total num statuses,
        "cats": dict of stats} where
        a stat is a dictionary {"query": str descriptor of topic, "stat":
            is slug describing no of entries on topic and % of total}
    """
    size = getCount()
    topics = list(getTopics())
    topics = sorted(topics, key=lambda topic: topic["cat"])
    # for topic in topics:
    #     # TODO: fix this, looking back only 1 week but comparing to all time
    #     query = "-d 7 " + topic["query"]
    #     err, cursor = websearch(query)
    #     if not err:
    #         n = cursor.estimated_document_count()
    #         topic["count"] = n
    #         topic["percent"] = "{:.2%}".format(1.0 * n / size)
    groups = groupby(topics, key=lambda topic: topic["cat"])
    temp = defaultdict(list)
    for cat, group in groups:
        for topic in group:
            temp[cat].append(topic)
    cats = OrderedDict()
    keys = sorted([k for k in temp])
    for key in keys:
        cats[key] = temp[key]
    return size, cats


# added this to speed up load of home page
# differs from longer getStats by not providing topic stats,
# which are not needed for home page, only for stats page
def getShortStats():
    """
    :returns: dictionary {"size": total num statuses,
        "cats" is dict of "topics", where
        "topics": list of stats}
    """
    size = getCount()
    topics = list(getTopics())
    topics = sorted(topics, key=lambda topic: topic["cat"])
    groups = groupby(topics, key=lambda topic: topic["cat"])
    temp = defaultdict(list)
    for cat, group in groups:
        for topic in group:
            temp[cat].append(topic)
    cats = OrderedDict()
    keys = sorted([k for k in temp])
    for key in keys:
        cats[key] = temp[key]
    return size, cats


class Row:
    """docstring for Row"""

    def __init__(self, header, statuses):
        self.statuses = statuses
        self.header = header


@app.template_filter("taburlize")
def taburlize(s):
    """flask filter similar to urlize but sets target to new tab"""
    pattern = r"(https?://\S+)"
    p = re.compile(pattern)
    return p.sub(r'<a href="\1" target="_blank"> ...more &#10149; </a>', s)


@app.route("/error")
def showError():
    return render_template("error.html")


@app.route("/stats")
def showStats():
    n, cats = getStats()
    return render_template("stats.html", n=n, cats=cats)


@app.route("/help")
def showHelp():
    return render_template("help.html")


# https://stackoverflow.com/questions/63052492/cant-load-icons-from-manifest-json-file
# @app.route("/static/icons/<path:filename>")
# def icons(filename):
#     return send_from_directory("./static/icons", filename)


def extract_options(parts):
    """
    Extract options from query, such as -d 5 xxx
    """
    options = ""
    newparts = []
    n = len(parts)
    skip = False
    for i in range(len(parts)):
        if skip:
            skip = False
            continue
        if (parts[i].startswith("-")) and i + 1 < n:
            if parts[i][1] not in "dseH":
                # -d -s -e are only valid options
                raise WebQueryParseException
            # remove option indicator and value and add to options
            clause = " ".join([parts[i], parts[i + 1]])
            if options != "":
                options = " ".join([options, clause])
            else:
                options = clause
            skip = True  # skip ahead in iteration
        else:
            newparts.append(parts[i])
    if options == "":
        # valid query must have options
        raise WebQueryParseException
    return options, newparts


def parse_query(query):
    """
    Transform complex query into simpler subqueries that can be processed
    by processCmdLine and then combined in showNews by chaining
    returns err, queries; err is None if no exception, True otherwise
    """
    parts = query.split(" ")
    try:
        if len(parts) < 3:
            # -x 1 somequery is minimal query, so will have 3 or more parts
            raise WebQueryParseException
        options, parts = extract_options(parts)
    # TODO: make this catch more fine-grained.
    # right now taking care of both WebQueryParseException and
    # index out of range exception from parts[1][1] avoe when a bare -
    # is entered in a custom query
    except Exception as e:
        print(query, e)
        return True, []
    starred = []
    unstarred = []
    for part in parts:
        if part.startswith("*"):
            starred.append(part)
        else:
            unstarred.append(part)
    queries = []
    for query in starred:
        queries.append(" ".join([options, query]))
    unstarred_stringed = " ".join(unstarred)
    unstarred_quoted = f'"{unstarred_stringed}"'
    if unstarred:
        queries.append(" ".join([options, unstarred_quoted]))
    return False, queries


def handleQuery(query):
    err, queries = parse_query(query)
    if err:
        flash("Error in query, try again!")
        return redirect(url_for("query"))
    cursors = []
    for subquery in queries:
        err, cursor = websearch(subquery)
        if not err:
            cursors.append(cursor)
        elif err:
            flash("Error in query, try again! " + str(err))
    # kludgy error signaling mechanism
    if not cursors:
        query = None
    # eliminate near duplicates from the display

    # TODO!! for now, remove dedupe from processing chai
    # print(f"cursors: {cursors}")
    # statuses = dedupe(chain(*cursors))
    # return statuses
    return chain.from_iterable(cursors)


@app.route("/")
def query():
    if request.method == "GET":
        return render_template("index.html")
    else:
        return redirect("/error")


@app.route("/json/cats", methods=["GET", "PUT"])
def cats_json():
    n, cats = getShortStats()
    resp = jsonify(count=n, cats=cats)
    return resp


@app.route("/json/count", methods=["GET"])
def count_json():
    n = getCount()
    resp = jsonify(count=n)
    return resp


@app.route("/json/recent", methods=["GET", "POST"])
def recent_json():
    # this will get last 3 hours of posts
    t0 = mstimer()
    error, cursor = fetch_recent()
    t1 = mstimer()
    if error is None:
        # cursor = [unid(s) for s in cursor]
        # t2 = mstimer_ns()
        resp = jsonify([s for s in cursor])
        # resp.headers["Access-Control-Allow-Origin"] = "*"
        t2 = mstimer()
        logger.debug(f"recent: fetch {t1 - t0},  jsonify {t2 - t1} ")
        return resp
    else:
        t0 = 0
        return 0


# TODO: need to do something about flashed error messages in handleQuery
# These won't work with the json interface


@app.after_request
def after_req(resp):
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    resp.headers["server"] = "Nooze Server 0.2.1"
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return resp


@app.route("/json/qry", methods=["GET", "POST"])
def qry_json():
    logger.debug(f"qry_json: {request.args}")
    query = request.args.get("data")
    # print(query)
    t0 = mstimer()
    statuses = handleQuery(query)
    t1 = mstimer()
    # statuses = [unid(s) for s in statuses]
    # t2 = mstimer_ns()
    # resp = jsonify([s for s in statuses])
    resp = jsonify(list(statuses))
    t2 = mstimer()
    logger.debug(f"qry_json: fetch {t1 - t0}, jsonify {t2 - t1} ")
    return resp


@app.route("/json/xqry", methods=["POST"])
def xqry():
    xquery = request.get_json()
    err, statuses = xwebsearch(xquery)
    if err is None:
        resp = jsonify(statuses=list(statuses), error=0)
    else:
        resp = jsonify(statuses=[], error=str(err))
    return resp


@app.route("/json/xcount", methods=["POST"])
def count():
    xquery = request.get_json()
    err, res = xcount(xquery)
    if err is None:
        resp = jsonify(count=res["count"], intervals=res["intervals"], error=0)
    else:
        resp = jsonify(count=0, error=str(err))
    return resp


@app.route("/json/intvlcounts", methods=["POST"])
def intvlcounts():
    """
    query {words: ["Macron"], start: daatestring,
     interval: e.g, 1d, 1m, 24h, n: num of intervals}
    """
    xcounts_qry = request.get_json()
    err, result = xcounts(xcounts_qry)
    if err is None:
        resp = jsonify(intervals=result, error=0)
    else:
        resp = jsonify(intervals=[], error=str(err))

    return resp


@app.route("/json/xgraph", methods=["POST"])
def xgraph():
    """Receive set of queries for graphing of counts
    query: {subqueries: [query1, query2]}
    start: datestring
    title: string
    interval: e.g. 1d, 1m, 24h
    n: num of intervals}

    ex: {
    "subqueries": [["Pecresse"], ["Zemmour"], ["Pen"]],
    "start": "2022-02-14",
    "interval": "1d",
    "n": 7
      }
    """
    query = request.get_json()
    err, result = xgraphdb(query)
    if err is None:
        resp = jsonify(result=result, error=0)
    else:
        resp = jsonify(result=None, error=str(err))
    return resp
