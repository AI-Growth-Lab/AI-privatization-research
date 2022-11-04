# Create dataframe for regressions

import re
import tqdm
import pickle
import pymongo
import pandas as pd
from collections import defaultdict
from genderComputer import GenderComputer

gc = GenderComputer() #https://github.com/tue-mdse/genderComputer

Client = pymongo.MongoClient("mongodb://localhost:27017")
db = Client["openAlex"]
collection = db["works_ai_2_False"]
collection_all = db["works"]
collection_ai_authors = db["author_profile_ai"]
period = range(1997,2022,1)


#%%


def seniority_all():
    try:
        with open('Data/seniority_all_restricted.pickle', 'rb') as f:
            seniority_all = pickle.load(f)        
    except:
        
        seniority_all = defaultdict(int)
        
        docs = collection_all.find()
        
        for doc in tqdm.tqdm(docs):
            for author in doc["authorships"]:
                try:
                    id_ = int(re.findall(r'\d+',author["author"]["id"] )[0])
                    if doc["publication_year"] != None:
                        if seniority_all[id_] == 0:
                            seniority_all[id_] = doc["publication_year"]
                        else:
                            if seniority_all[id_] > doc["publication_year"]:
                                seniority_all[id_] = doc["publication_year"]
                except:
                    continue
        with open('Data/seniority_all.pickle', 'wb') as handle:
            pickle.dump(seniority_all, handle, protocol=pickle.HIGHEST_PROTOCOL)
    return seniority_all



#%%

authors_profile = defaultdict(lambda: defaultdict(dict))
seniority = {}

for year in tqdm.tqdm(period):
    docs = collection.find({"publication_year":year})
    for doc in tqdm.tqdm(docs):
        authors_in_comp = []
        authors_participation = []
        
        try:
            concepts = [concept["display_name"].lower() for concept in doc["concepts"]]
        except:
            pass

        for author in doc["authorships"]:
            try:
                id_ = int(re.findall(r'\d+',author["author"]["id"] )[0])
            except:
                continue
            authors_participation.append(id_)

            # dl
            if "deep learning" in concepts:
                authors_profile[year][id_]["dl"] = 1
            
            # deg_cen
            try:
                if len(doc["authorships"]) > 1:
                    authors_profile[year][id_]["deg_cen"] += (1/(len(doc["authorships"]) - 1)) 
                else:
                    authors_profile[year][id_]["deg_cen"] += 0
            except:
                if len(doc["authorships"]) > 1:
                    authors_profile[year][id_]["deg_cen"] = (1/(len(doc["authorships"]) - 1))              
                else:
                    authors_profile[year][id_]["deg_cen"] = 0
            
            # gender

            try:
                authors_profile[year][id_]["gender"] = gc.resolveGender(author["author"]["display_name"], None)
            except:
                pass         
            # in_comp or not
            for inst in author["institutions"]:
                try:
                    if inst["type"] == "company":
                        authors_in_comp.append(id_)
                except:
                    continue
                
            # paper_n
            try:
                authors_profile[year][id_]["paper_n"] += (1/len(doc["authorships"]))
            except:
                authors_profile[year][id_]["paper_n"] = (1/len(doc["authorships"]))           
            
            # citationAID
            
            try:
                authors_profile[year][id_]["citation"] += doc["cited_by_count"]
            except:
                authors_profile[year][id_]["citation"] = doc["cited_by_count"]

            # seniority
            if id_ in seniority:
               authors_profile[year][id_]["seniority"] = doc["publication_year"] - seniority[id_]
            else:
                authors_profile[year][id_]["seniority"] = 0  
                seniority[id_] = doc["publication_year"]
            
            n_sen = 0
            # seniority_all
            if id_ in seniority_all:
                authors_profile[year][id_]["seniority_all"] = doc["publication_year"] - seniority_all[id_]
            else:
                n_sen += 1
                
            # Most common concept
            try:
                authors_profile[year][id_]["concept_list"] += concepts
            except:
                authors_profile[year][id_]["concept_list"] = concepts                             
                
        # deg_cen_comp
        for i in authors_participation:
            if i in authors_in_comp:
                try:
                    if len(authors_participation) > 1:
                        authors_profile[year][i]["deg_cen_comp"] += len(authors_in_comp)-1/(len(authors_participation) - 1)
                    else:
                        authors_profile[year][i]["deg_cen_comp"] += 0
                except:
                    if len(authors_participation) > 1:
                        authors_profile[year][i]["deg_cen_comp"] = len(authors_in_comp)-1/(len(authors_participation) - 1)                   
                    else:
                        authors_profile[year][i]["deg_cen_comp"] = 0                        
            else:
                try:
                    if len(authors_participation) > 1:
                        authors_profile[year][i]["deg_cen_comp"] += len(authors_in_comp)/(len(authors_participation )- 1)
                    else:
                        authors_profile[year][i]["deg_cen_comp"] += 0
                except:
                    if len(authors_participation) > 1:
                        authors_profile[year][i]["deg_cen_comp"] = len(authors_in_comp)/(len(authors_participation) - 1)                    
                    else:
                        authors_profile[year][i]["deg_cen_comp"] = 0
        


#{id_cleaned:4212529325}

# Add switcher, transited in observable carrier yes/no, transited_t since when , transition (when)

transition_dict = {year:defaultdict(int) for year in range(1998,2021)}
for year in range(1998,2021):
    context = list(range(year-1, year+2))
    query = {str(i)+".aff_type":{"$exists":1,"$ne":None} for i in context }
    docs = collection_ai_authors.find(query)
    for doc in tqdm.tqdm(docs):
        id_ = int(re.findall(r'\d+',doc["AID"] )[0])
        if doc[str(year-1)]["aff_type"] != doc[str(year)]["aff_type"] and doc[str(year)]["aff_type"] == doc[str(year+1)]["aff_type"]:
            transition_name = doc[str(year-1)]["aff_type"]  + "_" + doc[str(year)]["aff_type"]
            if transition_name == "education_company":
                transition_dict[year][id_] += 1
        else:
            continue

transited_t_dict = defaultdict(list)
for year in tqdm.tqdm(range(1998,2021)):
    for id_ in transition_dict[year]:
        transited_t_dict[id_].append(year)

for year in tqdm.tqdm(range(1997,2022,1)):
    for id_ in authors_profile[year]:
        if id_ in transited_t_dict:
            switcher = 1
            if year == transited_t_dict[id_][0]:
                transition = 1
            else:
                transition = 0
            transited_t = year - transited_t_dict[id_][0] 
        else:
            switcher = 0
            transition = 0
            transited_t = None
        authors_profile[year][id_]["switcher"] = switcher
        authors_profile[year][id_]["transition"] = transition
        authors_profile[year][id_]["transited_t"] = transited_t

docs = collection_ai_authors.find()
for doc in tqdm.tqdm(docs):
    for year in range(1997,2022):        
        try:
            if doc["AID_cleaned"] in authors_profile[year]:
                authors_profile[year][doc["AID_cleaned"]]["aff_id"] = doc[str(year)]["aff_id"]
            else:
                continue
        except:
            authors_profile[year][doc["AID_cleaned"]]["aff_id"] = None
            
        try:
            if doc["AID_cleaned"] in authors_profile[year]:
                authors_profile[year][doc["AID_cleaned"]]["aff_type"] = doc[str(year)]["aff_type"]
            else:
                continue
        except:
            authors_profile[year][doc["AID_cleaned"]]["aff_type"] = None  
            

columns = ["year","AID","deg_cen","deg_cen_comp","paper_n","seniority","seniority_all","concepts","DL","switcher","transition","transited_t","gender","aff_id","aff_type"]
list_of_insertion = []
for year in tqdm.tqdm(range(1997,2022,1)):    
    for id_ in tqdm.tqdm(authors_profile[year]):             
        deg_cen = authors_profile[year][id_]["deg_cen"]
        deg_cen_comp = authors_profile[year][id_]["deg_cen_comp"]
        paper_n = authors_profile[year][id_]["paper_n"]
        seniority = authors_profile[year][id_]["seniority"]
        try:
            seniority_all = authors_profile[year][id_]["seniority_all"]
        except:
            seniority_all = None
        concepts = "\n".join(authors_profile[year][id_]["concept_list"])
        try:
            DL = authors_profile[year][id_]["dl"]
        except:
            DL = 0
        try:
            gender = authors_profile[year][id_]["gender"]
        except:
            gender = None
        switcher = authors_profile[year][id_]["switcher"]
        transition = authors_profile[year][id_]["transition"]
        transited_t = authors_profile[year][id_]["transited_t"]
        try:
            aff_id  = authors_profile[year][id_]["aff_id"]
        except:
            aff_id  = None
        try:
            aff_type  = authors_profile[year][id_]["aff_type"]
        except:
            aff_type  = None
        list_of_insertion.append([year, id_, deg_cen, deg_cen_comp, paper_n, seniority, seniority_all, concepts, DL, switcher,
                           transition, transited_t,gender,aff_id,aff_type])

df=pd.DataFrame(list_of_insertion,columns=columns)
df.to_csv("Data/variables.csv",index=False)


