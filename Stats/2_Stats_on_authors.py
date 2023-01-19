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
import plotly.graph_objects as go
import random

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
plt.title("Top 10 type of transition")

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
plt.title("Absolute value of researchers' transition type (top 10)")
plt.legend(bbox_to_anchor=(1.04, 1), loc="upper left")


df_top_ten_share =  pd.DataFrame()
for col in df_transition_all[top_ten].columns:
    df_top_ten_share[col] = df_transition_all[top_ten][col] / df_transition_all[top_ten]['Total']

df_top_ten_share.drop("Total",axis=1).plot.bar(stacked=True, figsize=(10, 6))
plt.title("Share of researchers' transition type (top 10)")
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
        
inst_tags = []
for year in tqdm.tqdm(range(2001,2021)):
    inst_tags += list(set(transition[year]))
    inst_tags = list(set(inst_tags))


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
top_ten = list(df_transition_all.sum().sort_values().tail(16).index)
df_top_ten = df_transition_all[top_ten].drop("Total",axis=1)
df_top_ten.plot.bar(stacked=True, figsize=(10, 6))
plt.title("Absolute value of Academia company transition (top 10)")
plt.legend(bbox_to_anchor=(1.04, 1), loc="upper left")

transition[2010]
sorted(transition[2020], key=transition[2020].get, reverse=True)[:5]

#sanki diagram


columns = ["source","target","value"]
list_of_insertion = []
for i in unique_tags:
    list_of_insertion.append(["education",i,0])

df = pd.DataFrame(list_of_insertion,columns=columns)
df.index = df["target"]

transition = {year:defaultdict(int) for year in range(2001,2021)}
for year in range(2000,2021):
    context = list(range(year-1, year+2))
    query = {str(i)+".aff_type":{"$exists":1,"$ne":None} for i in context }
    docs = collection_ai_authors.find(query)
    for doc in tqdm.tqdm(docs):
        if doc[str(year-1)]["aff_type"] != doc[str(year)]["aff_type"] and doc[str(year)]["aff_type"] == doc[str(year+1)]["aff_type"]:
            transition_name = doc[str(year-1)]["aff_type"]  + "_" + doc[str(year)]["aff_type"]
            if doc[str(year-1)]["aff_type"] == "education":
                df.at[doc[str(year)]["aff_type"],"value"] += 1
        elif doc[str(year-1)]["aff_type"] == doc[str(year)]["aff_type"] and doc[str(year)]["aff_type"] == doc[str(year+1)]["aff_type"]:
            if doc[str(year-1)]["aff_type"] == "education":
                df.at[doc[str(year)]["aff_type"],"value"] += 1        
        else:
            continue


# Real app

# Nodes & links

nodes = [['ID', 'Label', 'Color']]
node2id = {}
j = 0
for i in unique_tags:
    hex_color = "#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])
    if i == "education":
        hex_color = "#247AFD"
        hex_color_education = hex_color.lstrip('#')
    nodes.append([j,i,hex_color])
    node2id[i] = j
    j += 1




n_total = df["value"].sum()
links = [['Source','Target','Value','Link Color']]
for i in df.iterrows():
    source = node2id[i[1]["source"]] 
    target = node2id[i[1]["target"]] 
    value = i[1]["value"]
    link_color = list(int(hex_color_education[i:i+2], 16) for i in (0, 2, 4))
    link_color.append(value/n_total) 
    link_color = str("rgba({},{},{},{})".format(link_color[0],link_color[1],link_color[2],link_color[3]))
    links.append([source,target,value,link_color])
    


"""
# links with some data for illustrative purposes ################

nodes = [['ID', 'Label', 'Color'],
        [0,'AKJ Education','#4994CE'],
        [1,'Amazon','#8A5988'],
        [2,'Flipkart','#449E9E'],
        [3,'Books','#7FC241'],
        [4,'Computers & tablets','#D3D3D3'],
        [5,'Other','#4994CE'],]


#links = [
#    ['Source','Target','Value','Link Color'],
#    
#    # AKJ
#    [0,3,846888,'rgba(127, 194, 65, 0.2)'],
#    [0,4,1045,'rgba(127, 194, 65, 0.2)'],
#    
#    # Amazon
#    [1,3,1294423,'rgba(211, 211, 211, 0.5)'],
#    [1,4,42165,'rgba(211, 211, 211, 0.5)'],
#    [1,5,415,'rgba(211, 211, 211, 0.5)'],
#    
#    # Flipkart
#    [2,5,1,'rgba(253, 227, 212, 1)'],]
#################################################################
"""

# Retrieve headers and build dataframes
nodes_headers = nodes.pop(0)
links_headers = links.pop(0)
df_nodes = pd.DataFrame(nodes, columns = nodes_headers)
df_links = pd.DataFrame(links, columns = links_headers)

# Sankey plot setup
data_trace = dict(
    type='sankey',
    domain = dict(
      x =  [0,1],
      y =  [0,1]
    ),
    orientation = "h",
    valueformat = ".0f",
    node = dict(
      pad = 10,
    # thickness = 30,
      line = dict(
        color = "black",
        width = 0
      ),
      label =  df_nodes['Label'].dropna(axis=0, how='any'),
      color = df_nodes['Color']
    ),
    link = dict(
      source = df_links['Source'].dropna(axis=0, how='any'),
      target = df_links['Target'].dropna(axis=0, how='any'),
      value = df_links['Value'].dropna(axis=0, how='any'),
      color = df_links['Link Color'].dropna(axis=0, how='any'),
  )
)

layout = dict(
        title = "Researcher leaving education during the period 2000-2020",
    height = 772,
    font = dict(
      size = 24),)

fig = dict(data=[data_trace], layout=layout)
plot(fig)

