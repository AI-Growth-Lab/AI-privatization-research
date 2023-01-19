# list of authors in ai 

import os
import re
import tqdm
import pickle
import pymongo

def get_list_ai_researcher(starting_year = 1997):
    
    Client = pymongo.MongoClient("mongodb://localhost:27017")
    db = Client["openAlex"]
    collection = db["works_ai_2_False"]
    
    list_aid = set()
    docs = collection.find()
    for doc in tqdm.tqdm(docs):
        if doc["publication_year"] >= starting_year:
            for author in doc["authorships"]:
                try:
                    id_ = int(re.findall(r'\d+',author["author"]["id"] )[0])
                    list_aid.add(id_)
                except:
                    continue
    list_aid = list(list_aid)
    with open('Data/list_aid_ai.pickle', 'wb') as handle:
        pickle.dump(list_aid, handle, protocol=pickle.HIGHEST_PROTOCOL)  
    

def get_list_aid_per_year(year):

    Client = pymongo.MongoClient("mongodb://localhost:27017")
    db = Client["openAlex"]
    collection = db["works"]
    
    list_aid = []
    docs = collection.find({"publication_year":year})

    for doc in tqdm.tqdm(docs):
        for author in doc["authorships"]:
            try:
                id_ = int(re.findall(r'\d+',author["author"]["id"] )[0])
                list_aid.append(id_)
            except:
                continue
    

    if not os.path.exists('Data/list_aid'):
       os.makedirs('Data/list_aid')  
       
    with open('Data/list_aid/{}.pickle'.format(year), 'wb') as handle:
        pickle.dump(list(set(list_aid)), handle, protocol=pickle.HIGHEST_PROTOCOL)  
        

