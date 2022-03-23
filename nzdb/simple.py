import pymongo

client = pymongo.MongoClient("192.168.0.128", connect=False)
print(client)
# time.sleep(10)
db = client["euronews"]
print(db)
auths = db.authors.find()
for a in auths:
    print(a)
topics = db.topics.find()
for t in topics:
    print(t)
