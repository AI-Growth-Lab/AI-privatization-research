import re
import tqdm
import pymongo
from langdetect import detect
from collections import defaultdict

Client = pymongo.MongoClient("mongodb://localhost:27017")
db = Client["openAlex"]
collection_ai_name = "works_ai_2_False"
collection_ai = db[collection_ai_name]
collection_ai_authors = db["author_profile_ai"]
period = range(2000,2022,1)


def create_author_profile_ram_opti():
    collection_ai_authors.create_index([ ("AID_cleaned",1) ])   
    collection_ai_authors.create_index([ ("AID",1) ])   
    for year in period:
        docs = collection_ai.find({"publication_year":year})
        authors_profile = defaultdict(lambda: defaultdict(list))
        for doc in tqdm.tqdm(docs):
            for author in doc["authorships"]:
                try:
                    for inst in author["institutions"]:
                        authors_profile[author["author"]["id"]]["type"].append(inst["type"])
                        authors_profile[author["author"]["id"]]["display_name"].append(inst["display_name"])
                except:
                    continue
        list_of_insertion = []
        for ind in authors_profile:
            if authors_profile[ind]:
                try:
                    aff_type = max(authors_profile[ind]["type"],key=authors_profile[ind]["type"].count)
                except:
                    aff_type= None
                try:
                    aff_display_name = max(authors_profile[ind]["display_name"],key=authors_profile[ind]["display_name"].count)
                except:
                    aff_display_name = None
                id_ = int(re.findall(r'\d+', ind )[0])
                list_of_insertion.append(pymongo.UpdateOne({"AID_cleaned": id_ },
                                                               {'$set': {"AID":ind,str(year): {"aff_type":aff_type,"aff_display_name":aff_display_name}}},
                                                               upsert = True))
        collection_ai_authors.bulk_write(list_of_insertion)


if __name__ == "__main__":
    create_author_profile_ram_opti()
