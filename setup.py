from setuptools import setup, find_packages

setup(
    name="nzdb",
    version="0.3",
    author="Art Goldhammer",
    description="News Aggregator Web App",
    author_email="art.goldhamme@gmail.com",
    keywords="news aggregator Europe politics",
    url="https://github.com/agoldhammer/nooze",
    #     scripts=[
    #         "nzdb/bin/query",
    #         "nzdb/bin/maketopics",
    #         "nzdb/bin/readfeed",
    #         "nzdb/bin/storeauthtable",
    #     ],
    entry_points={
        "console_scripts": [
            "storeauths = nzdb.scripts.storeauthtable:main",
            "storetopics = nzdb.scripts.storetopics:main",
            "readfeed = nzdb.scripts.readfeed:main",
            "unknown = nzdb.scripts.idknown:showUknowns",
            "query = nzdb.scripts.query:main",
        ]
    },
    packages=find_packages(),
)
