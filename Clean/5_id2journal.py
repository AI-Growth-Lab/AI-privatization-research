# Novelty indicators on references

import re
import tqdm
import pymongo

Client = pymongo.MongoClient("mongodb://localhost:27017")
db = Client["openAlex"]
collection = db["works"]
collection_ref = db["id_journal"]

db_restricted = Client["openAlex_novelty"]
collection_restricted = db_restricted["references"]

def id2journal():
    docs = collection.find({})
    list_of_insertion = []
    for doc in tqdm.tqdm(docs):
        try:
            if doc["host_venue"]["issn_l"]:
                list_of_insertion.append({"id_cleaned":doc["id_cleaned"],"journal":doc["host_venue"]["issn_l"]})
                if len(list_of_insertion) == 10000:
                    collection_ref.insert_many(list_of_insertion)
                    list_of_insertion = []
        except:
            continue


def create_journal_coll():
    docs = collection.find({}, no_cursor_timeout=True).skip(203060539)
    list_of_insertion = []
    
    for doc in tqdm.tqdm(docs):
        if len(doc["referenced_works"]) > 0:
            list_journals = []
            for ref in doc["referenced_works"]:
                id_ = int(re.findall(r'\d+',ref )[0])
                try:
                    list_journals.append(collection_ref.find_one({"id_cleaned":id_})["journal"])
                except:
                    continue
            if list_journals:
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
