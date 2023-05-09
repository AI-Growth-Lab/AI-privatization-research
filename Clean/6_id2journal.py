# Novelty indicators on references

import re
import tqdm
import pymongo
from collections import defaultdict

Client = pymongo.MongoClient("mongodb://localhost:27017")
db = Client["openAlex"]
collection = db["works"]
collection_ref = db["id_journal"]

db_restricted = Client["openAlex_novelty"]
collection_restricted = db_restricted["references"]

def id2journal():
    docs = collection.find({})
    list_of_insertion = []
    collection_ref.create_index([ ("id_cleaned",1) ])   
    for doc in tqdm.tqdm(docs):
        try:
            if doc["host_venue"]["issn_l"]:
                list_of_insertion.append({"id_cleaned":doc["id_cleaned"],"journal":doc["host_venue"]["issn_l"],"year":doc["publication_year"]})
                if len(list_of_insertion) == 10000:
                    collection_ref.insert_many(list_of_insertion)
                    list_of_insertion = []
        except:
            continue


def create_journal_coll():
    
    id2journal = defaultdict(dict)
    docs = collection_ref.find()
    for doc in tqdm.tqdm(docs):
        id2journal[doc["id_cleaned"]]["journal"] = doc["journal"]
        id2journal[doc["id_cleaned"]]["year"] = doc["year"]    
        
    docs = collection.find({}, no_cursor_timeout=True)
    list_of_insertion = []
    
    collection.create_index([ ("id_cleaned",1) ])      
    collection.create_index([ ("publication_year",1) ])      

    for doc in tqdm.tqdm(docs):
        if len(doc["referenced_works"]) > 0:
            list_journals = []
            for ref in doc["referenced_works"]:
                id_ = int(re.findall(r'\d+',ref )[0])
                try:
                    list_journals.append(id2journal[id_])
                except:
                    continue
            if list_journals:
                list_journals = [i for i in list_journals if i != {} ]
                list_of_insertion.append({"id_cleaned":doc["id_cleaned"],
                                          "publication_year":doc["publication_year"],
                                          "referenced_works":list_journals})
            if len(list_of_insertion) == 10000:
                collection_restricted.insert_many(list_of_insertion)
                list_of_insertion = []            
    collection_restricted.insert_many(list_of_insertion)
    list_of_insertion = [] 

if __name__ == "__main__":
    id2journal()
    create_journal_coll()
