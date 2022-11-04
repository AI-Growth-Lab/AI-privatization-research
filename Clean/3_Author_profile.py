import re
import tqdm
import pymongo
from collections import defaultdict

Client = pymongo.MongoClient("mongodb://localhost:27017")
db = Client["openAlex"]
collection_ai_name = "works_ai_2_False"
collection_ai = db[collection_ai_name]
collection_ai_authors = db["author_profile_ai"]
period = range(1997,2022,1)


def create_author_profile_ram_opti():
    collection_ai_authors.create_index([ ("AID_cleaned",1) ])   
    collection_ai_authors.create_index([ ("AID",1) ])   
    for year in period:
        docs = collection_ai.find({"publication_year":year})
        authors_profile = defaultdict(lambda: defaultdict(list))
        for doc in tqdm.tqdm(docs):
            for author in doc["authorships"]:
                for inst in author["institutions"]:
                    try:
                        if inst["type"]:
                            authors_profile[author["author"]["id"]]["type"].append(inst["type"]) 
                            authors_profile[author["author"]["id"]]["display_name"].append(inst["display_name"])
                            try:
                                aff_id = int(re.findall(r'\d+',inst["id"] )[0])
                            except:
                                aff_id = None
                            authors_profile[author["author"]["id"]]["inst_id_cleaned"].append(aff_id)
                            authors_profile[author["author"]["id"]]["inst_id"].append(inst["id"])
                    except Exception as e :
                        print(str(e))
                        continue

        
        list_of_insertion = []
        for ind in authors_profile:
            if authors_profile[ind]:
                try:
                    aff_type = [i for i in authors_profile[ind]["type"]]
                    aff_type = max(aff_type)
                except:
                    aff_type= None
                try:
                    aff_display_name = [i for i in authors_profile[ind]["display_name"]]
                    aff_display_name = max(aff_display_name)
                except:
                    aff_display_name = None
                try:
                    aff_id = [i for i in authors_profile[ind]["inst_id"]]                    
                    aff_id = max(aff_id)
                except:
                    aff_id = None 
                try:
                    aff_id_cleaned = [i for i in authors_profile[ind]["inst_id_cleaned"]]                    
                    aff_id_cleaned = max(aff_id_cleaned)
                except:
                    aff_id_cleaned = None 
                id_ = int(re.findall(r'\d+', ind )[0])
                list_of_insertion.append(pymongo.UpdateOne({"AID_cleaned": id_ },
                                                               {'$set': {"AID":ind,str(year): {"aff_type":aff_type,"aff_display_name":aff_display_name,"aff_id":aff_id,"aff_id_cleaned":aff_id_cleaned}}},
                                                               upsert = True))
        collection_ai_authors.bulk_write(list_of_insertion)


if __name__ == "__main__":
    create_author_profile_ram_opti()
