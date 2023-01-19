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
from collections import Counter

Client = pymongo.MongoClient("mongodb://localhost:27017")
db = Client["openAlex"]
collection_ai_name = "works_ai_2_False"
collection_ai = db[collection_ai_name]
collection_ai_authors = db["author_profile_ai"]
period = range(2000,2022,1)

with open("Data/hierarchy_keywords.txt", 'r') as f:
    keywords = f.read().split("\n")[0:-1]
keywords = [keyword.lower() for keyword in keywords]


# unique companies, unique journals, unique conferences

docs = collection_ai.find({})

n_comp = []
n_inst = []
for doc in tqdm.tqdm(docs):
    try:
        for author in doc["authorships"]:
            for inst in author["institutions"]:
                if inst["type"] == "company":
                    n_comp.append(inst["display_name"])
                if inst["type"] == "education":
                    n_inst.append(inst["display_name"])
    except:
        continue
len(list(set(n_comp)))
len(list(set(n_inst)))


n_issn = []

docs = collection_ai.find({})

for doc in tqdm.tqdm(docs):
    try:
        n_issn.append(doc["host_venue"]["issn_l"])
    except:
        continue

len(list(set(n_issn)))

#%% Evolution plots publication



# Publication per year restricted

df = pd.DataFrame(index = ["Adversarial system","Deep learning","Reinforcement learning","Total"])

for year in tqdm.tqdm(period):
    n_adversarial = 0
    n_deep = 0
    n_reinforcment = 0
    n = 0
    docs = collection_ai.find({"publication_year":year})
    for doc in docs:
        n += 1
        try:
            for concept in doc["concepts"]:
                if concept["display_name"] == "Adversarial system":
                    n_adversarial += 1
                if concept["display_name"] == "Deep learning":
                    n_deep += 1
                if concept["display_name"] == "Reinforcement learning":
                    n_reinforcment += 1
        except:
            continue
    df[year] = [n_adversarial, n_deep, n_reinforcment, n]

df = df.T

fig, ax = plt.subplots(1, 1, figsize=(12, 8), dpi=300)
df.plot(ax=ax,lw=2, title="{}".format(collection_ai_name))
plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right')
ax.set_ylabel("Papers")
ax.locator_params(integer=True)
#df['month'] = df.index
#df.to_csv("Data/fig1a.csv", index=False)

# Shared publication per year restricted

share_df = pd.DataFrame()
for col in ["Adversarial system","Deep learning","Reinforcement learning"]:
    share_df[col] = df[col] / df['Total']
    
fig, ax = plt.subplots(1, 1, figsize=(12, 8), dpi=300)
share_df.plot(ax=ax,lw=2,title="{}".format(collection_ai_name))
plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right')
ax.set_ylabel("Papers")
ax.locator_params(integer=True)


# Publication per year on all categories

df_all = pd.DataFrame(np.zeros(shape = (len( list(period)),len(keywords)+1)), index = list(period),columns = keywords+["Total"])

for year in tqdm.tqdm(period):
    docs = collection_ai.find({"publication_year":year})
    n = 0
    for doc in tqdm.tqdm(docs):
        for concept in doc["concepts"]:
            try:
                df_all.at[year,concept["display_name"].lower()] += 1
            except:
                continue
        df_all.at[year,"Total"] += 1


df_all.to_csv("Data/fig1.csv", index=False)

growth = ((df_all.loc[2021]-df_all.loc[2015])/df_all.loc[2015])
growth.replace([np.inf, - np.inf], np.nan, inplace = True) 
growth.dropna(inplace=True)


fig, ax = plt.subplots(1, 1, figsize=(12, 8), dpi=300)
#df_all[list(df_all.sum().sort_values().tail(6).index)].plot(ax=ax,lw=2, title="{}".format(collection_ai_name))
df_all[list(df_all.sum().sort_values().tail(6).index)].plot(ax=ax,lw=2, title="Evolution of AI documents")
plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right')
plt.legend(bbox_to_anchor=(1.04, 1), loc="upper left")
ax.set_ylabel("Papers")
ax.locator_params(integer=True)

# Top 5 growth between 2018-2021

fig, ax = plt.subplots(1, 1, figsize=(12, 8), dpi=300)
#df_all[list(df_all.sum().sort_values().tail(6).index)].plot(ax=ax,lw=2, title="{}".format(collection_ai_name))
df_all[list(growth.sort_values().tail(5).index)].plot(ax=ax,lw=2, title="Evolution of AI documents")
plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right')
plt.legend(bbox_to_anchor=(1.04, 1), loc="upper left")
ax.set_ylabel("Papers")
ax.locator_params(integer=True)

# Shared publication per year on all categories

share_df_all = pd.DataFrame()
for col in keywords:
    share_df_all[col] = df_all[col] / df_all['Total']
    


fig, ax = plt.subplots(1, 1, figsize=(12, 8), dpi=300)
share_df_all[[ i for i in list(df_all.max().sort_values().tail(6).index) if i != "Total"]].plot(ax=ax,lw=2, title="{}".format(collection_ai_name))
plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right')
plt.legend(bbox_to_anchor=(1.04, 1), loc="upper left")
ax.set_ylabel("Papers")
ax.locator_params(integer=True)

#%% Evolution plots OA

df = pd.DataFrame(index = ["oa","arxiv","biorxiv","Total"])

where = []
for year in tqdm.tqdm(period):
    docs = collection_ai.find({"publication_year":year})
    for doc in docs:
        try:
            if doc["open_access"]["oa_url"]:
                where.append(doc["open_access"]["oa_url"])
        except:
            continue

where = list(set([i.split("//")[1].split("/")[0] for i in where]))

df_oa = pd.DataFrame(np.zeros(shape = (len( list(period)),len(where)+1)), index = list(period),columns = where+["Total"])

for year in tqdm.tqdm(period):
    docs = collection_ai.find({"publication_year":year})
    n = 0
    for doc in tqdm.tqdm(docs):
        if doc["open_access"]["oa_url"]:
            try:
                url = doc["open_access"]["oa_url"].split("//")[1].split("/")[0]
                df_oa.at[year,url] += 1
                df_oa.at[year,"Total"] += 1
            except:
                continue
       
df_oa.to_csv("Data/fig2.csv", index=False)

fig, ax = plt.subplots(1, 1, figsize=(12, 8), dpi=300)
df_oa[list(df_oa.drop("Total",axis=1).sum().sort_values().tail(6).index)].plot(ax=ax,lw=2, title="{}".format(collection_ai_name))
plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right')
ax.set_ylabel("Evolution of open access behavior")
ax.locator_params(integer=True)
plt.savefig('Results/Publication_oa_{}.png'.format(collection_ai_name))

# Shared publication Total

share_df = pd.DataFrame()
for col in ["oa","arxiv","biorxiv","Total"]:
    share_df[col] = df[col] / df['Total']
    
fig, ax = plt.subplots(1, 1, figsize=(12, 8), dpi=300)
share_df.drop("Total",axis=1).plot(ax=ax,lw=2,title="{}".format(collection_ai_name))
plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right')
ax.set_ylabel("share of papers in our collection")
ax.locator_params(integer=True)

plt.savefig('Results/Publication_oa_on_total_{}.png'.format(collection_ai_name))

# Share publication openaccess
share_df = pd.DataFrame()
share_df["share_oa"] = df_oa["Total"] / df_all['Total']
    
fig, ax = plt.subplots(1, 1, figsize=(12, 8), dpi=300)
share_df.plot(ax=ax,lw=2,title="Share of open access papers")
plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right')
ax.set_ylabel("Share")
ax.locator_params(integer=True)
ax.legend().remove()

plt.savefig('Results/Publication_oa_on_OA_{}.png'.format(collection_ai_name))



#%% Evolution of difference between education and company

df_all_comp = pd.DataFrame(np.zeros(shape = (len( list(period)),len(keywords)+1)), index = list(period),columns = keywords+["Total"])
df_all_edu = pd.DataFrame(np.zeros(shape = (len( list(period)),len(keywords)+1)), index = list(period),columns = keywords+["Total"])


for year in tqdm.tqdm(period):
    docs = collection_ai.find({"publication_year":year})
    for doc in tqdm.tqdm(docs):
        comp_part = False
        edu_part = False
        for concept in doc["concepts"]:
            try:
                for author in doc["authorships"]:
                    for inst in author["institutions"]:
                        try:
                            if inst["type"] == "company":
                                comp_part = True
                            if inst["type"] == "education":
                                edu_part = True
                        except:
                            continue
                if comp_part:
                    df_all_comp.at[year,concept["display_name"].lower()] += 1
                if edu_part:
                    df_all_edu.at[year,concept["display_name"].lower()] += 1                
            except:
                continue



df_all_edu_share = pd.DataFrame()
for col in keywords:
    df_all_edu_share[col] = df_all_edu[col] / df_all['Total']

#%% Evolution of solo author

df_solo = pd.DataFrame(np.zeros(shape = (len( list(period)),2)), index = list(period),columns = ["n","n_solo"])
df_solo

for year in tqdm.tqdm(period):
    docs = collection_ai.find({"publication_year":year})
    for doc in tqdm.tqdm(docs):
        df_solo.at[year,"n"] += 1
        if len(doc["authorships"]) == 1:
            df_solo.at[year,"n_solo"] += 1
df_solo["n_solo"] =  df_solo["n_solo"]/df_solo["n"]       
df_solo.to_csv("Data/Share_solo.csv", index=False)
             

#%% Keywords that cooccur the most with "deep learning"

most_cooc_dl = defaultdict(int)

for year in tqdm.tqdm(period):
    docs = collection_ai.find({"publication_year":year})
    n = 0
    for doc in tqdm.tqdm(docs):
        temp_keywords = []
        for concept in doc["concepts"]:
            try:
                temp_keywords.append(concept["display_name"].lower())
            except:
                continue
        if "deep learning" in temp_keywords:
            for i in temp_keywords:
                if i == "deep learning":
                    continue
                most_cooc_dl[i] += 1 

sorted(most_cooc_dl, key= most_cooc_dl.get, reverse=True)[:5]
cooc = [i for i in dict(Counter(most_cooc_dl).most_common(5))]

