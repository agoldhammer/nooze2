#!/usr/bin/env python

"""read news feeds from twitter"""

import logging
from logging import FileHandler
from time import sleep

import click
from nzdb.configurator import nzdbConfig
from nzdb.dbif import (
    AuthorNotFound,
    DuplicateStatus,
    get_lastread,
    mapAuthorToLang,
    store_lastread,
    storeStatus,
)
from nzdb.nzauth import getTwitterApi
from nzdb.prettytext import printStatus
from tweepy import Cursor, TweepError

LOGFILENAME = nzdbConfig["logfile"]
LOGNAME = nzdbConfig["logname"]
# OWNER = nzdbConfig['owner']
# SLUG = nzdbConfig['slug']
LIST_ID = nzdbConfig["list_id"]
logger = None

processed = 0
added = 0
skipped = 0
maxid = 0


def pruneStatus(status):
    """Prunes status record to store only info of interest
    :param status: the status record
    :returns pruned status as dictionary
    """
    return {
        "id": status.id,
        "author": status.author.screen_name,
        "created_at": status.created_at,
        "source": status.source,
        "text": status.text,
    }


def processStatus(i, status, quiet):
    """Process a Twitter status record
    :param i: sequence number
    :param status: the status record
    :returns nothing
     .. prints notification of duplicate record and does not insert
    """
    global processed, added, skipped, maxid
    processed += 1
    status_id = status.id
    if status_id > maxid:
        maxid = status_id
    created_at = status.created_at
    try:
        status = pruneStatus(status)
        author = status["author"]
        try:
            language_code = mapAuthorToLang(author)
            status["language_code"] = language_code
        except AuthorNotFound:
            # missing authors are logged but recorded as Unknown
            status["language_code"] = "U"
            logger.info(f"Author not found {author}")
        storeStatus(status)
        # If, successful, display the entry being processed ...
        if not quiet:
            out = "\n---\n{}. author {} id {}  time {} via {}"
            print(out.format(i + 1, author, status_id, created_at, status["source"]))
            printStatus(status)
        added += 1
    # if status is already in db, we get here
    except DuplicateStatus:
        skipped += 1


def setup_logging():
    # print("Processing usnews feeds for nzdb")
    global logger
    logger = logging.getLogger(LOGNAME)
    logger.setLevel(logging.INFO)
    fh = FileHandler(LOGFILENAME)
    fh.setLevel(logging.INFO)
    myformat = logging.Formatter("%(asctime)s-%(name)s:%(levelname)s--%(message)s")
    fh.setFormatter(myformat)
    logger.addHandler(fh)


@click.command()
@click.option("--quiet/--verbose", default=True, help="default quiet")
@click.option("-d", "--daemon/--no-daemon", default=False, help="run as daemon")
@click.option("--sleeptime", default=900, help="sleep time in secs")
def main(quiet, daemon, sleeptime):
    global maxid, processed, added, skipped

    setup_logging()

    msg = ""
    while True:
        try:
            api = getTwitterApi(wait=True, notify=True)
            # this will return 0, 0 on virgin database
            _, maxid = get_lastread()
            processed = added = skipped = 0
            # setting sinceid to None does the right thing
            sinceid = None if maxid == 0 else maxid
            for i, status in enumerate(
                Cursor(api.list_timeline, list_id=LIST_ID, since_id=sinceid).items()
            ):
                processStatus(i, status, quiet)

            store_lastread(maxid)
            msg = f"processed {processed}. added {added}.\
        skipped {skipped} maxid {maxid}"
            logger.info(msg)
        except TweepError as e:
            print(e)
        if not quiet:
            print(msg)
        if not daemon:
            break
        else:
            sleep(sleeptime)


if __name__ == "__main__":

    # pylint: disable=no-value-for-parameter
    main()
