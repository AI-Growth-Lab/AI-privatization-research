import tqdm
import pymongo
import pickle
from collections import defaultdict

Client = pymongo.MongoClient("mongodb://localhost:27017")
db = Client["openAlex"]
collection_all = db["works"]
collection_ai_name = "works_ai_2_False"
collection_ai = db[collection_ai_name]
collection_ai_authors = db["author_profile_ai"]
period = range(2000,2022,1)

unique_inst = []
docs = collection_ai_authors.find({})

list_switcher = defaultdict(dict)
transition = {year:defaultdict(int) for year in range(2001,2021)}
for year in range(2001,2021):
    context = list(range(year-1, year+2))
    query = {str(i)+".aff_type":{"$exists":1,"$ne":None} for i in context }
    docs = collection_ai_authors.find(query)
    for doc in tqdm.tqdm(docs):
        if doc[str(year-1)]["aff_type"] != doc[str(year)]["aff_type"] and doc[str(year)]["aff_type"] == doc[str(year+1)]["aff_type"]:
            transition_name = doc[str(year-1)]["aff_type"]  + "_" + doc[str(year)]["aff_type"]
            if transition_name == "education_company":
                transition_inst = doc[str(year-1)]["aff_display_name"]  + "_" + doc[str(year)]["aff_display_name"]
                list_switcher[doc["AID_cleaned"]]["transition_inst"] = doc[str(year)]["aff_display_name"]
                list_switcher[doc["AID_cleaned"]]["year"] = year                                  
        else:
            continue

unique_inst_with_transition = []

for i in list_switcher:
    unique_inst_with_transition.append(list_switcher[i]["transition_inst"])
    
unique_inst_with_transition = list(set(unique_inst_with_transition))

def create_inst_kb():
    unique_inst_kb = {year:defaultdict(list) for year in range(1997,2023)}
    
    
    docs = collection_all.find({})
    
    for doc in tqdm.tqdm(docs):
        year = doc["publication_year"]
        if year:
            if year >= 1997 and year <= 2022:
                done = False
                concepts = [concept["display_name"].lower() for concept in doc["concepts"]]
                for author in doc["authorships"]:
                    if author["institutions"]:
                        for inst in author["institutions"]:
                            if inst:
                                if inst["display_name"] in unique_inst_with_transition and done == False:
                                    unique_inst_kb[year][inst["display_name"]] += concepts
                                    done = True
            else:
                continue
    
    
    with open('Data/unique_inst_kb.pickle', 'wb') as handle:
        pickle.dump(unique_inst_kb, handle, protocol=pickle.HIGHEST_PROTOCOL)  

with open('Data/unique_inst_kb.pickle', 'rb') as f:
    unique_inst_kb = pickle.load(f)  


