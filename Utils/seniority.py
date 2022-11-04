import tqdm
import pickle
import re
import tqdm
import pymongo
from collections import defaultdict

Client = pymongo.MongoClient("mongodb://localhost:27017")
db = Client["openAlex"]
collection_ai_authors = db["author_profile_ai"]
collection = db["works_ai_2_False"]

"""
docs = collection_ai_authors.find()

list_aid = []
for doc in tqdm.tqdm(docs):
    list_aid.append(doc["AID_cleaned"])


docs = collection.find()
for doc in tqdm.tqdm(docs):
    for author in doc["authorships"]:
        try:
            list_aid.append(int(re.findall(r'\d+',author["author"]["id"] )[0]))
        except:
            continue

list_aid = list(set(list_aid))
print("loading list_aid")
with open('Data/list_aid.pickle', 'wb') as f:
    pickle.dump(list_aid,f)    
"""
    
print("loading senio")
with open('Data/seniority_all.pickle', 'rb') as f:
    seniority_all = pickle.load(f)        

print("loading list_aid")
with open('Data/list_aid.pickle', 'rb') as f:
    list_aid = pickle.load(f)        

print("dict comprehension")
seniority_all_restricted = {id_:min(x for x in seniority_all[id_] if x is not None) for id_ in list_aid }

print("inserting new list")
with open('Data/seniority_all_restricted.pickle', 'wb') as handle:
    pickle.dump(seniority_all_restricted, handle, protocol=pickle.HIGHEST_PROTOCOL)

