import re
import tqdm
import pickle
import pymongo
import pandas as pd
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


transition = {year:defaultdict(int) for year in period}
for year in range(2000,2021):
    context = list(range(year-1, year+2))
    query = {str(i)+".aff_type":{"$exists":1,"$ne":None} for i in context }
    docs = collection_ai_authors.find(query)
    for doc in tqdm.tqdm(docs):
        if doc[str(year-1)]["aff_type"] != doc[str(year)]["aff_type"] and doc[str(year)]["aff_type"] == doc[str(year+1)]["aff_type"]:
            transition_name = doc[str(year-1)]["aff_type"]  + "_" + doc[str(year)]["aff_type"]
            if transition_name == "education_company":
                transition[year][doc[str(year)]["aff_display_name"]] += 1 
                unique_inst.append(doc[str(year)]["aff_display_name"])                              
        else:
            continue

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
                                if inst["display_name"] in unique_inst and done == False:
                                    unique_inst_kb[year][inst["display_name"]] += concepts
                                    done = True
            else:
                continue
    
    
    with open('Data/unique_inst_kb.pickle', 'wb') as handle:
        pickle.dump(unique_inst_kb, handle, protocol=pickle.HIGHEST_PROTOCOL)  

# create_inst_kb()

def create_researcher_kb(focal_year):

    with open('Data/list_aid_ai.pickle', 'rb') as f:
        list_aid = pickle.load(f)     
        
    #unique_researcher_kb = {year:defaultdict(list) for year in range(1997,2023)}
    unique_researcher_kb = {aid:[] for aid in list_aid}
    
    docs = collection_all.find({})
    
    for doc in tqdm.tqdm(docs):
        year = doc["publication_year"]
        if year:
            if year == focal_year:
                concepts = [concept["display_name"].lower() for concept in doc["concepts"]]
                for author in doc["authorships"]:
                    try:
                        id_ = int(re.findall(r'\d+',author["author"]["id"] )[0])
                        unique_researcher_kb[year][id_] += concepts
                    except:
                        continue
            else:
                continue
    
    
    with open('Data/unique_researcher_kb_{}.pickle'.format(focal_year), 'wb') as handle:
        pickle.dump(unique_researcher_kb, handle, protocol=pickle.HIGHEST_PROTOCOL)  

create_researcher_kb(focal_year = 1998)

with open('Data/unique_inst_kb.pickle', 'rb') as f:
    unique_inst_kb = pickle.load(f)  

with open('Data/unique_researcher_kb.pickle', 'rb') as f:
     pickle.load(f)  

list_of_insertion = []

for year in tqdm.tqdm(period):
    for inst in unique_inst_kb[year]:
        try:
            n_transition = transition[year][inst]
            n_common_kb = len(set(unique_inst_kb[year][inst]).intersection([i for t in range(1997,year,1) for i in unique_inst_kb[t][inst]]))
            list_of_insertion.append([n_transition,n_common_kb/len(set(unique_inst_kb[year][inst]))])
        except:
            continue

df = pd.DataFrame(list_of_insertion,columns=["n_transition","n_common"])
df.to_csv("data/inst_gain.csv")


# get knowledge base of switcher

author_transition = []

for year in range(2000,2021):
    context = list(range(year-1, year+2))
    query = {str(i)+".aff_type":{"$exists":1,"$ne":None} for i in context }
    docs = collection_ai_authors.find(query)
    for doc in tqdm.tqdm(docs):
        if doc[str(year-1)]["aff_type"] != doc[str(year)]["aff_type"] and doc[str(year)]["aff_type"] == doc[str(year+1)]["aff_type"]:
            transition_name = doc[str(year-1)]["aff_type"]  + "_" + doc[str(year)]["aff_type"]
            if transition_name == "education_company":
                author_transition.append(doc["AID_cleaned"])                       
        else:
            continue

