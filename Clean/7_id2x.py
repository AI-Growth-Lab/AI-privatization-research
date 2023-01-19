# Novelty using shibayama (title/abs) or maybe concepts ? Will make things faster

import tqdm
import pymongo
from langdetect import detect

Client = pymongo.MongoClient("mongodb://localhost:27017")
db = Client["openAlex"]
collection = db["works"]


            
            
def get_Title_abs_restricted():
    db = Client["openAlex"]
    collection = db["works"]
    db_restricted = Client["openAlex_novelty"]
    collection_abstract = db_restricted["Title_abs"]
    collection_abstract.create_index([ ("id",1) ])   
    collection_abstract.create_index([ ("id_cleaned",1) ])   
    collection_abstract.create_index([ ("publication_year",1) ])  
         
    
    docs = collection.find({})
    list_of_insertion = []
    for doc in tqdm.tqdm(docs):
        try:
            if detect(doc["title"]) == "en":
                title = doc["title"]
            else:
                continue
        except:
            title = None
        try:
            abstract = doc["abstract"]
        except:
            abstract = None
        if title or abstract:
            list_of_insertion.append({"id":doc["id"],
                                      "id_cleaned":doc["id_cleaned"],
                                      "publication_year":doc["publication_year"],
                                      "title":title,
                                      "abstract":abstract})
            if len(list_of_insertion) == 10000:
                collection_abstract.insert_many(list_of_insertion)
                list_of_insertion = []            
    collection_abstract.insert_many(list_of_insertion)
    list_of_insertion = [] 

def get_concept_restricted():
    db = Client["openAlex"]
    collection = db["works"]
    db_restricted = Client["openAlex_novelty"]
    collection_concept = db_restricted["concepts"]
    collection_concept.create_index([ ("id",1) ])   
    collection_concept.create_index([ ("id_cleaned",1) ])   
    collection_concept.create_index([ ("publication_year",1) ])           
    docs = collection.find({})
    
    list_of_insertion = []
    for doc in tqdm.tqdm(docs):
        list_of_insertion.append({"id":doc["id"],
                                  "id_cleaned":doc["id_cleaned"],
                                  "publication_year":doc["publication_year"],
                                  "concepts":doc["concepts"]})
        if len(list_of_insertion) == 10000:
            collection_concept.insert_many(list_of_insertion)
            list_of_insertion = []            
    collection_concept.insert_many(list_of_insertion)
    list_of_insertion = [] 

    


if __name__ == "__main__":
    get_Title_abs_restricted()
    get_concept_restricted()



