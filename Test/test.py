import tqdm
from pymongo import MongoClient
from pymongo.errors import InvalidBSON

db = MongoClient()['openAlex']
collection = db['works']

mongo_query = {}
mongo_date_projection = {"_id": True} # many more date columns ommitted here
mongo_projection = {"_id": 1} # many more date columns ommitted here
mongo_cursor = collection.find(mongo_query,
                               projection=mongo_projection,
                               no_cursor_timeout=True)

for record in tqdm.tqdm(mongo_cursor):
    record_id = record.get('_id')
    try:
        item = collection.find_one({'_id': record_id}, mongo_date_projection)
    except InvalidBSON:
        print(f'Record with id {record_id} contains invalid BSON')