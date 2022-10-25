# Get list of IDS so that we can use it on novelty

import tqdm
import pickle
import pymongo
from collections import defaultdict

Client = pymongo.MongoClient("mongodb://localhost:27017")
db = Client["openAlex"]
collection = db["works_ai_2_False"]

list_ids = defaultdict(list)
docs = collection.find()

for doc in tqdm.tqdm(docs):
    list_ids[doc["publication_year"]].append(doc["id_cleaned"])
    
for year in list_ids:
    with open('Data/docs/focal_papers_ids/{}.pickle'.format(year), 'wb') as handle:
        pickle.dump(list_ids[year], handle, protocol=pickle.HIGHEST_PROTOCOL)

