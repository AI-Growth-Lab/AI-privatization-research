import tqdm
import pymongo
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


Client = pymongo.MongoClient("mongodb://localhost:27017")
db = Client["openAlex"]
collection_ai_name = "works_ai_2_False"
collection_ai = db[collection_ai_name]
collection_ai_authors = db["author_profile_ai"]
period = range(2000,2022,1)

with open("Data/hierarchy_keywords.txt", 'r') as f:
    keywords = f.read().split("\n")[0:-1]
keywords = [keyword.lower() for keyword in keywords]

df_all = pd.read_csv("Data/fig1.csv")

#%% Evolution plots company


df_com = pd.DataFrame(np.zeros(shape = (len( list(period)),2)), index = list(period),columns = ["Company","Total"])

for year in tqdm.tqdm(period):
    docs = collection_ai.find({"publication_year":year})
    for doc in tqdm.tqdm(docs):
        comp_part = False
        df_com.at[year,"Total"] += 1
        if doc["authorships"]:
            for author in doc["authorships"]:
                for inst in author["institutions"]:
                    try:
                        if inst["type"] == "company":
                            comp_part = True
                    except:
                        continue
        if comp_part == True:
            df_com.at[year,"Company"] += 1

share_df_com = pd.DataFrame()
share_df_com["share_com"] = df_com["Company"] / df_all['Total']

fig, ax = plt.subplots(1, 1, figsize=(12, 8), dpi=300)
share_df_com.plot(ax=ax,lw=2,title="Share of papers with atleast one author from a company")
plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right')
ax.set_ylabel("Share")
ax.locator_params(integer=True)
ax.legend().remove()


df_share_com_per_paper = pd.DataFrame(np.zeros(shape = (len( list(period)),1)), index = list(period),columns = ["Mean"])


for year in tqdm.tqdm(period):
    docs = collection_ai.find({"publication_year":year})
    share = []
    for doc in tqdm.tqdm(docs):
        n_comp = 0
        n_author = 0
        if doc["authorships"]:
            for author in doc["authorships"]:
                n_author += 1
                done = False
                for inst in author["institutions"]:
                    try:
                        if inst["type"] == "company":
                            if done == False:
                                n_comp += 1
                                done = True
                    except:
                        continue
        try:
            if n_comp != 0:
                share.append((n_comp/n_author))
        except:
            continue
    df_share_com_per_paper.at[year,"Mean"] = np.mean(share)
            

fig, ax = plt.subplots(1, 1, figsize=(12, 8), dpi=300)
df_share_com_per_paper.plot(ax=ax,lw=2,title="Share of authors that are in a company in papers with atleast one author from a company")
plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right')
ax.set_ylabel("Share")
ax.locator_params(integer=True)
ax.legend().remove()