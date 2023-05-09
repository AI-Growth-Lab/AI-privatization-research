# Create dataframe for regressions

import re
import tqdm
import json
import pickle
import pymongo
import pandas as pd
import numpy as np
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


with open('Data/seniority_all_restricted.pickle', 'rb') as f:
    seniority_all_restricted = pickle.load(f)  

with open('Data/dropout_all_restricted.pickle', 'rb') as f:
    dropout_all = pickle.load(f)   

with open('Data/authors_profile_cleaned.pickle', 'rb') as f:
    authors_profile_cleaned = pickle.load(f)  

with open('Data/h_index.pickle', 'rb') as f:
    h_index = pickle.load(f)  
    
with open('Data/id2concepts.pickle', 'rb') as f:
    id2concepts = pickle.load(f)  

#%% 

authors_profile = defaultdict(lambda: defaultdict(dict))
seniority = {}

for year in tqdm.tqdm(period):
    docs = collection.find({"publication_year":year})
    for doc in tqdm.tqdm(docs):
        authors_in_comp = []
        authors_participation = []
        
        try:
            #concepts = [concept["display_name"].lower() for concept in doc["concepts"]]
            concepts = id2concepts[doc["id_cleaned"]]
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
            
            # citation cited_by_count

            try:
                authors_profile[year][id_]["cited_by_count"] += doc["cited_by_count"]
            except:
                authors_profile[year][id_]["cited_by_count"] = doc["cited_by_count"]

            # Append citation
            
            try:
                authors_profile[year][id_]["citation_array"].append(doc["cited_by_count"])
            except:
                authors_profile[year][id_]["citation_array"] = [doc["cited_by_count"]]           

            
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
            if id_ in seniority_all_restricted:
                authors_profile[year][id_]["seniority_all"] = doc["publication_year"] - seniority_all_restricted[id_]
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


#%% Add switcher, transited in observable carrier yes/no, transited_t since when , transition (when)

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
            

columns = ["year","AID","deg_cen","deg_cen_comp","paper_n","seniority","seniority_all","concepts","DL","switcher","transition","transited_t","gender","aff_id","aff_type","citation","citation_mean"]
list_of_insertion = []



for year in tqdm.tqdm(range(1997,2022,1)):    
    for id_ in tqdm.tqdm(authors_profile[year]):             
        deg_cen = authors_profile[year][id_]["deg_cen"]
        deg_cen_comp = authors_profile[year][id_]["deg_cen_comp"]
        paper_n = authors_profile[year][id_]["paper_n"]
        seniority = authors_profile[year][id_]["seniority"]
        citation = authors_profile[year][id_]["citation"]
        citation_mean = np.mean(authors_profile[year][id_]["citation_array"])

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
                           transition, transited_t,gender,aff_id,aff_type, citation,citation_mean])


df=pd.DataFrame(list_of_insertion,columns=columns)
df.to_csv("Data/variables.csv",index=False)

#%% static df

single_aff = {}
switcher_aff = defaultdict(list)

authors = collection_ai_authors.find()
for author in tqdm.tqdm(authors):
    list_aff = []
    for year in range(1997,2021):
        try:
            list_aff.append(author[str(year)]["aff_type"])
        except:
            continue
    if len(set(list_aff)) == 1:
        if list_aff[0] == "other":
            single_aff[author["AID_cleaned"]] = "only_other"
        else:
            single_aff[author["AID_cleaned"]] = list_aff[0]
        
s = set( val for val in single_aff.values())
            
for year in range(1998,2021):
    context = list(range(year-1, year+2))
    query = {str(i)+".aff_type":{"$exists":1,"$ne":None} for i in context }
    docs = collection_ai_authors.find(query)
    for doc in tqdm.tqdm(docs):
        id_ = int(re.findall(r'\d+',doc["AID"] )[0])
        if doc[str(year-1)]["aff_type"] != doc[str(year)]["aff_type"] and doc[str(year)]["aff_type"] == doc[str(year+1)]["aff_type"]:
            transition_name = doc[str(year-1)]["aff_type"]  + "_" + doc[str(year)]["aff_type"]
            switcher_aff[id_].append({"year":year,"transition_name":transition_name})            
        else:
            continue

n_multiple = 0
for author in switcher_aff:
    if len(switcher_aff[author]) > 1:
        n_multiple += 1
        n_education_company = 0
        for trans in switcher_aff[author]:
            if trans['transition_name'] == "education_company":
                n_education_company += 1
                
        if n_education_company > 1:
            print(author,switcher_aff[author])


n_edu = 0
n_edu_single = 0
n_edu_multiple = 0
for author in switcher_aff:
    for trans in switcher_aff[author]:
        if trans['transition_name'] == "education_company":
            n_edu += 1
        if trans['transition_name'] == "education_company" and len(switcher_aff[author]) == 1:
            n_edu_single += 1
        if trans['transition_name'] == "education_company" and len(switcher_aff[author]) > 1:
            n_edu_multiple += 1


# 7931 switcher, 1140 with multiple transition
# 1118 with atleast one education_company from them 164(14.6%) with multiple transition (so 954 single education_company transition)
# 57 education went to company and then came back to education 
# 10 education went to company and then left again somewhere else
# 4 education went to company-education-company 


columns = ["AID", "seniority","dropout","type"]    
list_of_insertion = []

for author in tqdm.tqdm(seniority_all_restricted):
    type_ = "other"
    doc = collection_ai_authors.find_one({"AID_cleaned":author})
#    try:
#        ai = doc["true_ai"]
#    except:
#        ai = 0
    if author in switcher_aff:
        if len(switcher_aff[author]) > 1:
            type_ = "multiple_transition"
        else:
            type_ = switcher_aff[author][0]["transition_name"]
    elif author in single_aff:
        type_ = single_aff[author]        
    list_of_insertion.append([author, seniority_all_restricted[author], dropout_all[author], type_])
    



df_static = pd.DataFrame(list_of_insertion, columns=columns)
df_static[df_static["type"]=="multiple_transition"]
df_static[df_static["ai"]==1]

df_static.to_csv("Data/author_static.csv",index=False)
set(df_static["type"])
df_static["type"].describe()
df_static[df_static["ai"]==1]["type"].value_counts().to_dict()
