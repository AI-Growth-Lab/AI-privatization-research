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


Client = pymongo.MongoClient("mongodb://localhost:27017")
db = Client["openAlex"]
collection_ai_name = "works_ai_2_False"
collection_ai = db[collection_ai_name]
collection_ai_authors = db["author_profile_ai"]
period = range(2000,2022,1)

unique_type = []
docs = collection_ai.find({})

i = 0
for doc in tqdm.tqdm(docs):
    for year in period:
        try:
            unique_type.append(doc["type"])
        except:
            continue
    i += 1
    if i % 10000 ==0:
        unique_type = list((set(unique_type)))

unique_type = list((set(unique_type)))
unique_type = [i for i in unique_type if i not in [None]]

df_all = pd.DataFrame(np.zeros(shape = (len( list(period)),len(unique_type)+1)), index = list(period),columns =unique_type+["Total"])

for year in tqdm.tqdm(period):
    docs = collection_ai.find({"publication_year":year})
    n = 0
    for doc in tqdm.tqdm(docs):
        try:
            df_all.at[year,doc["type"]] += 1
        except:
            continue
        df_all.at[year,"Total"] += 1

df_all.to_csv("Data/fig3.csv", index=False)

fig, ax = plt.subplots(1, 1, figsize=(12, 8), dpi=300)
df_all[list(df_all.drop("Total",axis=1).sum().sort_values().tail(5).index)].plot(ax=ax,lw=2, title="Evolution of document types")
plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right')
plt.legend(bbox_to_anchor=(1.04, 1), loc="upper left")
ax.set_ylabel("Papers")
ax.locator_params(integer=True)
