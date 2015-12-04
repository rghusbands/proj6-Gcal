
from pymongo import MongoClient

import CONFIG

try:
    dbclient = MongoClient(CONFIG.MONGO_URL)
    db = dbclient.MeetMe
    collection = db.dated

except:
    print("Failure opening database.  Is Mongo running? Correct password?")
    sys.exit(1)

for record in collection.find({}):
    print(record)

collection.remove({})

