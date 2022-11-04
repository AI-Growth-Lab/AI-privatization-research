import tqdm
import pymongo
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
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

#%% Transition plot
unique_tags = []
docs = collection_ai_authors.find({})

i = 0
for doc in tqdm.tqdm(docs):
    for year in period:
        try:
            unique_tags.append(doc[str(year)]["aff_type"])
        except:
            continue
    i += 1
    if i % 10000 ==0:
        unique_tags = list((set(unique_tags)))
unique_tags = list((set(unique_tags)))
unique_tags = [i for i in unique_tags if i not in [None]]

transition_tags = []
for comb in combinations(unique_tags, 2):
    transition_tags += ["_".join(i) for i in permutations(comb)]
    


# t-2 = t-1 != t = t+1

transition = {year:defaultdict(int) for year in range(2001,2021)}
for year in range(2002,2021):
    context = list(range(year-2, year+2))
    query = {str(i):{"$exists":1,"$ne":None} for i in context }
    docs = collection_ai_authors.find(query)
    for doc in tqdm.tqdm(docs):
        if doc[str(year-1)]["aff_type"] == doc[str(year-2)]["aff_type"] and doc[str(year-1)]["aff_type"] != doc[str(year)]["aff_type"] and doc[str(year)]["aff_type"] == doc[str(year+1)]["aff_type"]:
            transition_name = doc[str(year-1)]["aff_type"]  + "_" + doc[str(year)]["aff_type"]
            transition[year][transition_name] += 1
        else:
            continue

df_transition_all = pd.DataFrame(np.zeros(shape = (len( list(range(2002,2020))),len(transition_tags)+1)), index = list(range(2002,2020)),columns = transition_tags+["Total"])
df_transition_all = df_transition_all.fillna(0)

for year in range(2002,2021):
    n = 0
    for tag in transition[year]:
        df_transition_all.at[year,tag] = transition[year][tag]
        n += transition[year][tag]
    df_transition_all.at[year,"Total"] = n
    
top_ten = list(df_transition_all.sum().sort_values().tail(11).index)
df_top_ten = df_transition_all[top_ten].drop("Total",axis=1)
df_top_ten.plot.bar(stacked=True, figsize=(10, 6))
plt.title("{} t-2 equals".format(collection_ai_name))
plt.legend(bbox_to_anchor=(1.04, 1), loc="upper left")


df_top_ten_share =  pd.DataFrame()
for col in df_transition_all[top_ten].columns:
    df_top_ten_share[col] = df_transition_all[top_ten][col] / df_transition_all[top_ten]['Total']

df_top_ten_share.drop("Total",axis=1).plot.bar(stacked=True, figsize=(10, 6))
plt.title("{} t-2 equals".format(collection_ai_name))
plt.legend(bbox_to_anchor=(1.04, 1), loc="upper left")

# edu-comp comp-edu


df_transition_comp_edu = pd.DataFrame()
for year in range(2001,2021):
    df_transition_comp_edu[year] = [transition[year]["education_company"],-transition[year]["company_education"]]
df_transition_comp_edu = df_transition_comp_edu.T
df_transition_comp_edu.columns = ["education_company","company_education"]


sns.lineplot(data = df_transition_comp_edu)
plt.title("{} t-2 equals".format(collection_ai_name))

#%% t-1 != t = t+1

transition = {year:defaultdict(int) for year in range(2001,2021)}
for year in range(2001,2021):
    context = list(range(year-1, year+2))
    query = {str(i):{"$exists":1,"$ne":None} for i in context }
    docs = collection_ai_authors.find(query)
    for doc in tqdm.tqdm(docs):
        if doc[str(year-1)]["aff_type"] != doc[str(year)]["aff_type"] and doc[str(year)]["aff_type"] == doc[str(year+1)]["aff_type"]:
            transition_name = doc[str(year-1)]["aff_type"]  + "_" + doc[str(year)]["aff_type"]
            transition[year][transition_name] += 1
        else:
            continue

df_transition_all = pd.DataFrame(np.zeros(shape = (len( list(range(2001,2021))),len(transition_tags)+1)), index = list(range(2001,2021)),columns = transition_tags+["Total"])
df_transition_all = df_transition_all.fillna(0)

for year in range(2001,2021):
    n = 0
    for tag in transition[year]:
        df_transition_all.at[year,tag] = transition[year][tag]
        n += transition[year][tag]
    df_transition_all.at[year,"Total"] = n

    
df_transition_all.to_csv("Data/fig4.csv", index=False)

top_ten = list(df_transition_all.sum().sort_values().tail(11).index)
df_top_ten = df_transition_all[top_ten].drop("Total",axis=1)
df_top_ten.plot.bar(stacked=True, figsize=(10, 6))
plt.title("Absolute value of researchers' transition")
plt.legend(bbox_to_anchor=(1.04, 1), loc="upper left")


df_top_ten_share =  pd.DataFrame()
for col in df_transition_all[top_ten].columns:
    df_top_ten_share[col] = df_transition_all[top_ten][col] / df_transition_all[top_ten]['Total']

df_top_ten_share.drop("Total",axis=1).plot.bar(stacked=True, figsize=(10, 6))
plt.title("{} t-1".format(collection_ai_name))
plt.legend(bbox_to_anchor=(1.04, 1), loc="upper left")


# edu-comp comp-edu

df_transition_comp_edu = pd.DataFrame()
for year in range(2001,2021):
    df_transition_comp_edu[year] = [transition[year]["education_company"],-transition[year]["company_education"]]
df_transition_comp_edu = df_transition_comp_edu.T
df_transition_comp_edu.columns = ["education_company","company_education"]

df_transition_comp_edu.to_csv("Data/comp_edu.csv", index=False)
df_transition_comp_edu.columns = ["education_company","company_education"]
figure = px.line(
        data_frame=df_transition_comp_edu
    )

plot(figure) 

ax = sns.lineplot(data = df_transition_comp_edu)
plt.title("Flow of researchers between academia and private companies")
ax.locator_params(integer=True)
plt.show()


#%% Institution transition

unique_types = []
unique_names = []
docs = collection_ai_authors.find({})

i = 0
for doc in tqdm.tqdm(docs):
    for year in period:
        try:
            unique_types.append(doc[str(year)]["aff_type"])
            unique_names.append(doc[str(year)]["aff_type"])
        except:
            continue
    i += 1
    if i % 10000 ==0:
        unique_types = list((set(unique_types)))
        unique_names = list((set(unique_names)))
        
unique_types = list((set(unique_types)))
unique_types = [i for i in unique_types if i not in [None]]

unique_names = list((set(unique_names)))
unique_names = [i for i in unique_names if i not in [None]]


transition_tags = []
for comb in combinations(unique_tags, 2):
    transition_tags += ["_".join(i) for i in permutations(comb)]

#%% t-1 != t = t+1

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

df_transition_all = pd.DataFrame(np.zeros(shape = (len( list(range(2001,2021))),len(inst_tags)+1)), index = list(range(2001,2021)),columns = inst_tags+["Total"])
df_transition_all = df_transition_all.fillna(0)

for year in tqdm.tqdm(range(2001,2021)):
    n = 0
    for tag in tqdm.tqdm(transition[year]):
        df_transition_all.at[year,tag] = transition[year][tag]
        n += transition[year][tag]
    df_transition_all.at[year,"Total"] = n


df_transition_all = df_transition_all.loc[:, df_transition_all.sum() >=1]

df_transition_all.to_csv("Data/fig5.csv", index=False)    
top_ten = list(df_transition_all.sum().sort_values().tail(11).index)
df_top_ten = df_transition_all[top_ten].drop("Total",axis=1)
df_top_ten.plot.bar(stacked=True, figsize=(10, 6))
plt.title("Absolute value of Academia company transition")
plt.legend(bbox_to_anchor=(1.04, 1), loc="upper left")

transition[2010]
sorted(transition[2020], key=transition[2020].get, reverse=True)[:5]
