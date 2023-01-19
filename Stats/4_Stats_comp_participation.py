import tqdm
import pymongo
import numpy as np
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from plotly.offline import download_plotlyjs, init_notebook_mode,  plot

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
df_all.index = list(period)

#%% Evolution Paper with atleast one author from company


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

share_df_com.to_csv("Data/comp_participation.csv", index=False)

figure = px.line(
    data_frame=share_df_com,title="Paper with atleast one author from company"
)

figure.update_layout({
    "plot_bgcolor": "rgba(0, 0, 0, 0)",
    "paper_bgcolor": "rgba(0, 0, 0, 0)",
    })

figure.update_layout(legend=dict(
    title=""
))
    
plot(figure)



#%% Evolution of share of company authors in paper

df_share_com_per_paper = pd.DataFrame(np.zeros(shape = (len( list(period)),2)), index = list(period),columns = ["Mean","Mean without solo papers"])


for year in tqdm.tqdm(period):
    docs = collection_ai.find({"publication_year":year})
    share = []
    share_normalized = []
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
                if len(doc["authorships"]) > 1:
                    share_normalized.append((n_comp/n_author))
        except:
            continue
    df_share_com_per_paper.at[year,"Mean"] = np.mean(share)
    df_share_com_per_paper.at[year,"Mean without solo papers"] = np.mean(share_normalized)


df_share_com_per_paper.to_csv("Data/comp_share_auth.csv", index=False)
            

figure = px.line(
    data_frame=df_share_com_per_paper, title=""
)

figure.update_layout({
    "plot_bgcolor": "rgba(0, 0, 0, 0)",
    "paper_bgcolor": "rgba(0, 0, 0, 0)",
    })

figure.update_layout(legend=dict(
    title=""
))
    
plot(figure)
