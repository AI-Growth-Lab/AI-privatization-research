import re
import tqdm
import pickle
import pymongo
from collections import defaultdict

Client = pymongo.MongoClient("mongodb://localhost:27017")
db = Client["openAlex"]
collection = db["works"]

docs = collection.find({})

with open('Data/list_aid_ai.pickle', 'rb') as f:
    list_aid = pickle.load(f)   
    
h_index_list = {aid:defaultdict(list) for aid in list_aid}

for doc in tqdm.tqdm(docs):
    for author in doc["authorships"]:
        try:
            id_ = int(re.findall(r'\d+',author["author"]["id"] )[0])
        except:
            continue
        try:
            h_index_list[id_][doc["publication_year"]].append(doc["cited_by_count"])
        except:
            continue   
    
h_index_list_cleaned = {aid:defaultdict(float) for aid in list_aid}
for author in tqdm.tqdm(h_index_list):
    temp_h_index = []
    for year in range(2000,2020):
        try:
            temp_h_index += h_index_list[author][year]
            h_index_list_cleaned[author][year]  = sum(x >= i + 1 for i, x in enumerate(sorted(temp_h_index, reverse=True)))
        except:
            continue
        



with open('Data/h_index.pickle', 'wb') as handle:
    pickle.dump(h_index_list_cleaned, handle, protocol=pickle.HIGHEST_PROTOCOL)  