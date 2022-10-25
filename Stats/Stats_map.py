import tqdm
import pickle
import pymongo
import collections
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from itertools import permutations 
from itertools import combinations
from collections import defaultdict

period = range(2000,2022,1)

Client = pymongo.MongoClient("mongodb://localhost:27017")
db = Client["openAlex"]
collection_ai_name = "works_ai_2_False"
collection_ai = db[collection_ai_name]
collection_institution = db["institutions"]


with open("Data/hierarchy_keywords.txt", 'r') as f:
    keywords = f.read().split("\n")[0:-1]
keywords = [keyword.lower() for keyword in keywords]






def inst_map():

    docs = collection_institution.find()
    inst2geo = defaultdict(dict)
    for doc in tqdm.tqdm(docs):
        inst2geo[doc["id"]] = {"lon":doc["geo"]["longitude"],"lat":doc["geo"]["latitude"]}
    
    df = pd.DataFrame(columns = ["year",'lon','lat','n_papers','n_authors',"concept"])
    
    for year in tqdm.tqdm(period):
        docs = collection_ai.find({"publication_year":year})
        inst2stats = defaultdict(lambda: defaultdict(dict))
        for doc in tqdm.tqdm(docs):
            for concept in doc["concepts"]:
                concept_name = concept["display_name"].lower()
                if concept_name in keywords:             
                    temp_institutions = []
                    for author in doc["authorships"]:
                        for inst in author["institutions"]:
                            temp_institutions.append(inst["id"])
                            try:
                                inst2stats[inst["id"]][concept_name]["authors"].append(author["author"]["id"])
                            except:
                                inst2stats[inst["id"]][concept_name]["authors"] = [author["author"]["id"]]
                    for inst in list(set(temp_institutions)):
                        try:
                            inst2stats[inst][concept_name]["n_papers"] += 1
                        except:
                            inst2stats[inst][concept_name]["n_papers"] = 1
        for inst in tqdm.tqdm(inst2stats):
            if inst:
                for concept in inst2stats[inst]:
                    n_authors = len(list(set(inst2stats[inst][concept]["authors"])))
                    n_papers = inst2stats[inst][concept]["n_papers"]
                    lon = inst2geo[inst]["lon"]
                    lat = inst2geo[inst]["lat"]    
                    df.loc[len(df)] = [year, lon, lat, n_papers,n_authors,concept]
    df.to_csv("Data/inst_map.csv", index=False)
    
def country_map():
    country2geo = {}
    countries = pd.read_csv("data/countries.csv")
    for row in countries.iterrows():
        country2geo[row[1]["country"]] = {"lon":row[1]["longitude"],"lat":row[1]["latitude"]}

    list_of_insertion = []      
    for year in tqdm.tqdm(period):
        docs = collection_ai.find({"publication_year":year})
        inst2stats = defaultdict(lambda: defaultdict(dict))
        for doc in tqdm.tqdm(docs):
            for concept in doc["concepts"]:
                concept_name = concept["display_name"].lower()
                if concept_name in keywords:             
                    temp_institutions = []
                    for author in doc["authorships"]:
                        for inst in author["institutions"]:
                            try:
                                temp_institutions.append(inst["country_code"])
                            except:
                                continue
                            try:
                                inst2stats[inst["country_code"]][concept_name]["authors"].append(author["author"]["id"])
                            except:
                                try:
                                    inst2stats[inst["country_code"]][concept_name]["authors"] = [author["author"]["id"]]
                                except:
                                    continue
                    for inst in list(set(temp_institutions)):
                        try:
                            inst2stats[inst][concept_name]["n_papers"] += 1
                        except:
                            inst2stats[inst][concept_name]["n_papers"] = 1
          
        for country in tqdm.tqdm(inst2stats):
            try:
                if country:
                    for concept in inst2stats[country]:
                        n_authors = len(list(set(inst2stats[country][concept]["authors"])))
                        n_papers = inst2stats[country][concept]["n_papers"]
                        lon = country2geo[country]["lon"]
                        lat = country2geo[country]["lat"]    
                        list_of_insertion.append([year, lon, lat, n_papers,n_authors,concept])
            except:
                continue
    df = pd.DataFrame(list_of_insertion,columns = ["year",'lon','lat','n_papers','n_authors',"concept"])
    df.to_csv("Data/country_map.csv", index=False)