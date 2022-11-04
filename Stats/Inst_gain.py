import tqdm
import pymongo
import numpy as np
import pandas as pd
from itertools import permutations 
from itertools import combinations
from collections import defaultdict
import plotly.express as px
from plotly.offline import download_plotlyjs, init_notebook_mode,  plot

Client = pymongo.MongoClient("mongodb://localhost:27017")
db = Client["openAlex"]
collection_ai_name = "works_ai_2_False"
collection_ai = db[collection_ai_name]
collection_ai_authors = db["author_profile_ai"]
period = range(2000,2022,1)

unique_inst = []
docs = collection_ai_authors.find({})

i = 0
for doc in tqdm.tqdm(docs):
    for year in period:
        try:
            unique_inst.append(doc[str(year)]["aff_display_name"])
        except:
            continue
    i += 1
    if i % 10000 ==0:
        unique_inst = list((set(unique_inst)))
unique_inst = list((set(unique_inst)))
unique_inst = [i for i in unique_inst if i not in [None]]

inst_tags = []
for comb in combinations(unique_inst, 2):
    inst_tags += ["_".join(i) for i in permutations(comb)]


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
                transition[year][transition_inst] += 1
        else:
            continue

