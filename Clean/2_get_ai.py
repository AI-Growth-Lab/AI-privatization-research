import tqdm
import pymongo


Client = pymongo.MongoClient("mongodb://localhost:27017")
db = Client["openAlex"]
collection = db["works"]

docs = collection.find()

with open("data/hierarchy_keywords.txt", 'r') as f:
    keywords = f.read().split("\n")[0:-1]
keywords = [keyword.lower() for keyword in keywords]



def get_ai(keywords,comb = 1,tresh = False):
    collection_ai = db["works_ai_{}_{}".format(comb,tresh)]
    try:
        collection_ai.create_index([ ("id",1) ])   
        collection_ai.create_index([ ("publication_year",1) ])         
    except:
        pass
    docs = collection.find({})
    list_of_insertion = []
    for doc in tqdm.tqdm(docs):
        n = 0
        for concept in doc["concepts"]:
            if concept["display_name"].lower() in keywords:
                if tresh:
                    if concept["score"] > levels[concept["level"]] :
                        n += 1
                else:
                    n += 1
        if n >= comb:
            try:
                if doc["publication_year"] >= 1500 and doc["publication_year"] <= 1996:
                    doc.pop("_id")
                    list_of_insertion.append(doc)
            except:
                continue
    
        if len(list_of_insertion) == 10000:
            collection_ai.insert_many(list_of_insertion)
            list_of_insertion = []            
    collection_ai.insert_many(list_of_insertion)
    list_of_insertion = []


def add_ai_key_works():
    Client = pymongo.MongoClient("mongodb://localhost:27017")
    db = Client["openAlex"]
    collection = db["works"]
    collection_ai = db["works_ai_2_False"]
    
    docs = collection_ai.find({},no_cursor_timeout=True).skip(62000+1555299)
    list_of_insertion = []
    for doc in tqdm.tqdm(docs):
        list_of_insertion.append(pymongo.UpdateOne({'id_cleaned':  doc["id_cleaned"] }, {'$set': {'true_ai': 1}}))
    
        if len(list_of_insertion) == 1000:
            collection.bulk_write(list_of_insertion)
            list_of_insertion = []
    collection.bulk_write(list_of_insertion)

if __name__ == "__main__":
    # Number of keywords we want in a paper
    comb = 2
    # Levels of confidence for each level of concept
    tresh = False
    levels = {1:0.3, 2:0.5, 3:0.7, 4:0.8, 5:0.9}

    get_ai(keywords, comb = comb, tresh = tresh)
