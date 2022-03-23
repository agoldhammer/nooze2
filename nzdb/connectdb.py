import sys

from pymongo import MongoClient  # , TEXT, ASCENDING

from nzdb.configurator import nzdbConfig

DBNAME = nzdbConfig["DBNAME"]
DBHOST = nzdbConfig["DBHOST"]

_thedb = None


def conn():
    """connect to Mongo db dbname

    Args:
        dbname ([string]): name of the db

    Returns:
        mongo db: a mongo db instance
    """
    # db with 4 collections: statuses, authors, topics, hashestodocids
    print("db init", DBHOST)
    client = MongoClient(DBHOST, connect=True)
    return client


def get_db():
    global _thedb
    if _thedb is None:
        client = conn()
        if client is None:
            print("Couldn't connect to database, exiting")
            sys.exit(1)
        else:
            _thedb = client[DBNAME]
    return _thedb


if __name__ == "__main__":
    db = get_db()
    print("db is", db)
    for a in db.authors.find():
        print(a)
