"""
import novelpy

clean = novelpy.utils.preprocess_disruptiveness.create_citation_network(client_name = 'mongodb://localhost:27017',
                                                                        db_name = 'openAlex_novelty',
                                                                        collection_name = "Citation_net",
                                                                        id_variable = "id",year_variable = "publication_year", variable = "referenced_works")
clean.id2citedby()
clean.update_db()

import re
import tqdm
import pymongo

client_name = 'mongodb://localhost:27017'
db_name = 'openAlex_novelty'
collection_name = "Citation_net_cleaned"

Client = pymongo.MongoClient(client_name)
db = Client[db_name]
collection  = db[collection_name]

docs = collection.find({},no_cursor_timeout=True)

list_of_insertion = []
for doc in tqdm.tqdm(docs):
    refs = doc["citations"]["refs"]
    cited_by = doc["citations"]["cited_by"]
    refs_cleaned = [int(re.findall(r'\d+', i)[0]) for i in refs]
    cited_by_cleaned = [int(re.findall(r'\d+', i)[0]) for i in cited_by]
    list_of_insertion.append(
        pymongo.UpdateOne({"id_cleaned": doc["id_cleaned"]}, 
                           {"$set":{"citations_cleaned": {"refs":refs_cleaned,"cited_by":cited_by_cleaned}}})
        )
    if len(list_of_insertion) == 1000:
        collection.bulk_write(list_of_insertion)
        list_of_insertion = []
collection.bulk_write(list_of_insertion)
list_of_insertion = []

#757189/1057628
"""
import json 
import glob
import pickle

files = glob.glob('Data/docs/Citation_net_cleaned/*.json')
docs = []
for file in files:
    with open(file, 'r') as f:
        docs += json.load(f)
with open('Data/docs/Citation_net_cleaned.pkl', 'wb') as file:     
        # A new file will be created
    pickle.dump(docs, file)       
              
