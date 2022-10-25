import tqdm
import pymongo
import novelpy

Client = pymongo.MongoClient("mongodb://localhost:27017")
db = Client["openAlex"]
collection = db["works_ai_2_False"]

list_ids = []


for year in range(2000,2022,1):
    docs = collection.find({"publication_year":year})
    
    for doc in tqdm.tqdm(docs):
        list_ids.append(doc["id_cleaned"])
    

    Lee = novelpy.indicators.Lee2015(client_name="mongodb://localhost:27017",
                                    db_name = "openAlex_novelty",
                                    collection_name = "concepts",
                                    id_variable = 'id_cleaned',
                                    year_variable = 'publication_year',
                                    variable = "concepts",
                                    sub_variable = "display_name",
                                    focal_year = year,
                                    density = False,
                                    list_ids = list_ids)
    Lee.get_indicator()
        

