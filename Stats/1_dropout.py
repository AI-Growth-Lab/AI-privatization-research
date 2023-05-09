import tqdm
import pickle
import random
import pymongo
import pandas as pd
import plotly.express as px
from plotly.offline import plot
import plotly.graph_objects as go
from collections import defaultdict
from plotly.subplots import make_subplots


Client = pymongo.MongoClient("mongodb://localhost:27017")
db = Client["openAlex"]
collection_authors = db["author_profile"]    
collection_ai_authors = db["author_profile_true_ai"]

seniority_dropout = pd.read_csv("Data/seniority_dropout.csv")

docs = collection_authors.find({"true_ai":{"$exists":0}})
author_profile_not_ai = {}

for doc in tqdm.tqdm(docs):
    author_profile_not_ai[doc["AID_cleaned"]] = {i:doc[i] for i in doc if i not in ["_id","AID_cleaned","AID","true_ai"] }


docs = collection_authors.find({"true_ai":{"$exists":1}})
author_profile_ai = {}

for doc in tqdm.tqdm(docs):
    author_profile_ai[doc["AID_cleaned"]] = {i:doc[i] for i in doc if i not in ["_id","AID_cleaned","AID","true_ai"] }



seniority_dropout_ai = seniority_dropout[seniority_dropout['AID'].isin(author_profile_ai)]
seniority_dropout_notai = seniority_dropout[seniority_dropout['AID'].isin(author_profile_not_ai)]


sen2AID = {year:list() for year in seniority_dropout["seniority"].unique()}
AID2sen_ai = {}

for i in tqdm.tqdm(seniority_dropout_ai.iterrows()):
    AID2sen_ai[i[1]["AID"]] = i[1]["seniority"]

for i in tqdm.tqdm(seniority_dropout_notai.iterrows()):
    sen2AID[i[1]["seniority"]].append(i[1]["AID"])




def add_ai():
    list_of_insertion = []
    authors = db["author_profile_ai"].find({})
    for author in tqdm.tqdm(authors):
        list_of_insertion.append(pymongo.UpdateOne({'AID_cleaned': author["AID_cleaned"]}, {'$set': {'ai': 1}}, upsert=True))
        if len(list_of_insertion) % 10000 == 0:
            db["author_profile"].bulk_write(list_of_insertion)
            list_of_insertion = []
            
    db["author_profile"].bulk_write(list_of_insertion)        

"""
def get_dropout_cf(list_aid, window=3, ai = True):
    
    Client = pymongo.MongoClient("mongodb://localhost:27017")
    db = Client["openAlex"]
    collection_authors = db["author_profile"]    
    collection_ai_authors = db["author_profile_true_ai"]
            
    df = pd.DataFrame(0, index=range(2000,2019,1), columns = ["transition", "dropout", "stays_academia","weird_transition"])
    df_ai =  pd.DataFrame(0, index=range(2000,2019,1), columns = ["transition", "dropout", "stays_academia","weird_transition"])

    
            
    for aid in tqdm.tqdm(list_aid):
        author = collection_ai_authors.find_one({"AID_cleaned":aid})
        sen_author = AID2sen_ai[author["AID_cleaned"]]
        author_cf = random.sample(sen2AID[sen_author],1)[0]
        author_cf = collection_authors.find_one({"AID_cleaned":int(author_cf)})
        for year in range(2000,2019,1):
            previous_aff = []
            next_aff = []
            previous_aff_cf = []
            next_aff_cf = []
            for year_temp in range(1997,year):
                try:
                    previous_aff.append(author[str(year_temp)]["aff_type"])
                except:
                    continue
            for year_temp in range(year, year + window + 1):
                try:
                    next_aff.append(author[str(year_temp)]["aff_type"])
                except:
                    continue
            if len(set(previous_aff)) == 1:
                if previous_aff[0] == "education":
                    if len(set(next_aff)) == 0:
                        df_ai.at[year,"dropout"] += 1
                    elif "education" not in next_aff and len(set(next_aff)) != 1:
                        df_ai.at[year,"weird_transition"] += 1 
                    elif "education" not in next_aff and len(set(next_aff)) == 1:
                        df_ai.at[year,"transition"] += 1 
                    elif len(set(next_aff)) == 1 and next_aff[0] == "education":
                        df_ai.at[year,"stays_academia"] += 1 

                    
            for year_temp in range(1997,year):
                try:
                    previous_aff_cf.append(author_cf[str(year_temp)]["aff_type"])
                except:
                    continue
            for year_temp in range(year,year + window +1):
                try:
                    next_aff_cf.append(author_cf[str(year_temp)]["aff_type"])
                except:
                    continue
            if len(set(previous_aff_cf)) == 1:
                if previous_aff_cf[0] == "education":
                    if len(set(next_aff_cf)) == 0:
                        df.at[year,"dropout"] += 1
                    elif "education" not in next_aff_cf and len(set(next_aff_cf)) != 1:
                        df.at[year,"weird_transition"] += 1 
                    elif "education" not in next_aff_cf and len(set(next_aff_cf)) == 1:
                        df.at[year,"transition"] += 1 
                    elif len(set(next_aff_cf)) == 1 and next_aff_cf[0] == "education":
                        df.at[year,"stays_academia"] += 1                     
                    
    return df, df_ai

df, df_ai = get_dropout_cf(list_aid_true_ai, window=3, ai = True)
df['year'] = df.index
df = df.reset_index(level=0)
df["type"] = "non_ai"
df_ai["type"] = "ai"
df_ai['year'] = df_ai.index
df_ai = df_ai.reset_index(level=0)
"""


def get_dropout_cf(window=3, ai = True):
    
    df = {i:{j:0 for j in range(2000,2019,1) } for i in ["transition", "dropout", "stays_academia","weird_transition"]}
    df_ai = {i:{j:0 for j in range(2000,2019,1) } for i in ["transition", "dropout", "stays_academia","weird_transition"]}
    n = 0
    
    for aid in tqdm.tqdm(author_profile_ai):
        author = author_profile_ai[aid]
        sen_author = AID2sen_ai[aid]
        try:
            author_cf = random.sample(sen2AID[sen_author],1)[0]
        except:
            n+=1
            continue
        author_cf = author_profile_not_ai[int(author_cf)]
        for year in range(2000,2019,1):
            previous_aff = []
            next_aff = []
            previous_aff_cf = []
            next_aff_cf = []
            for year_temp in range(1997,year):
                try:
                    previous_aff.append(author[str(year_temp)]["aff_type"])
                except:
                    continue
            for year_temp in range(year, year + window + 1):
                try:
                    next_aff.append(author[str(year_temp)]["aff_type"])
                except:
                    continue
            if len(set(previous_aff)) == 1:
                if previous_aff[0] == "education":
                    if len(set(next_aff)) == 0:
                        df_ai["dropout"][year] += 1
                    elif "education" not in next_aff and len(set(next_aff)) != 1:
                        df_ai["weird_transition"][year] += 1 
                    elif "education" not in next_aff and len(set(next_aff)) == 1:
                        df_ai["transition"][year] += 1 
                    elif len(set(next_aff)) == 1 and next_aff[0] == "education":
                        df_ai["stays_academia"][year] += 1 

               
            for year_temp in range(1997,year):
                try:
                    previous_aff_cf.append(author_cf[str(year_temp)]["aff_type"])
                except:
                    continue
            for year_temp in range(year,year + window +1):
                try:
                    next_aff_cf.append(author_cf[str(year_temp)]["aff_type"])
                except:
                    continue
            if len(set(previous_aff_cf)) == 1:
                if previous_aff_cf[0] == "education":
                    if len(set(next_aff_cf)) == 0:
                        df["dropout"][year] += 1
                    elif "education" not in next_aff_cf and len(set(next_aff_cf)) != 1:
                        df["weird_transition"][year] += 1 
                    elif "education" not in next_aff_cf and len(set(next_aff_cf)) == 1:
                        df["transition"][year] += 1 
                    elif len(set(next_aff_cf)) == 1 and next_aff_cf[0] == "education":
                        df["stays_academia"][year] += 1                    
                    
    return df, df_ai


dict_, dict_ai = get_dropout_cf( window=3, ai = True)
df = pd.DataFrame(0, index=range(2000,2019,1), columns = ["transition", "dropout", "stays_academia","weird_transition"])
df_ai =  pd.DataFrame(0, index=range(2000,2019,1), columns = ["transition", "dropout", "stays_academia","weird_transition"])

for year in range(2000,2019,1):
    df.at[year,"transition"] = dict_["transition"][year]
    df.at[year,"dropout"] = dict_["dropout"][year]
    df.at[year,"stays_academia"] = dict_["stays_academia"][year]
    df.at[year,"weird_transition"] = dict_["weird_transition"][year]
    df_ai.at[year,"transition"] = dict_ai["transition"][year]
    df_ai.at[year,"dropout"] = dict_ai["dropout"][year]
    df_ai.at[year,"stays_academia"] = dict_ai["stays_academia"][year]
    df_ai.at[year,"weird_transition"] = dict_ai["weird_transition"][year]    


df_share = df.div(df.sum(axis=1), axis=0)
df_ai_share = df_ai.div(df_ai.sum(axis=1), axis=0)

df['year'] = df.index
df = df.reset_index(level=0)
df["type"] = "non_ai"
df_ai["type"] = "ai"
df_ai['year'] = df_ai.index
df_ai = df_ai.reset_index(level=0)


df_share["type"] = "non_ai"
df_ai_share["type"] = "non_ai"
df_share['year'] = df_share.index
df_share = df_share.reset_index(level=0)
df_share["type"] = "non_ai"
df_ai_share["type"] = "ai"
df_ai_share['year'] = df_ai_share.index
df_ai_share = df_ai_share.reset_index(level=0)



def get_dropout(list_aid_ai, list_aid, window=3, ai = True):
    
    Client = pymongo.MongoClient("mongodb://localhost:27017")
    db = Client["openAlex"]
    collection_authors = db["author_profile"]    
    collection_ai_authors = db["author_profile_ai"]
        
    df = pd.DataFrame(0, index=range(2000,2019,1), columns = ["transition", "dropout", "stays_academia","weird_transition"])
    df_ai =  pd.DataFrame(0, index=range(2000,2019,1), columns = ["transition", "dropout", "stays_academia","weird_transition"])

    
            
    for aid in tqdm.tqdm(list_aid_ai):
        author = collection_ai_authors.find_one({"AID_cleaned":aid})
        for year in range(2000,2019,1):
            previous_aff = []
            next_aff = []
            previous_aff_cf = []
            next_aff_cf = []
            for year_temp in range(1997,year):
                try:
                    previous_aff.append(author[str(year_temp)]["aff_type"])
                except:
                    continue
            for year_temp in range(year, year + window + 1):
                try:
                    next_aff.append(author[str(year_temp)]["aff_type"])
                except:
                    continue
            if len(set(previous_aff)) == 1:
                if previous_aff[0] == "education":
                    if len(set(next_aff)) == 0:
                        df_ai.at[year,"dropout"] += 1
                    elif "education" not in next_aff and len(set(next_aff)) != 1:
                        df_ai.at[year,"weird_transition"] += 1 
                    elif "education" not in next_aff and len(set(next_aff)) == 1:
                        df_ai.at[year,"transition"] += 1 
                    elif len(set(next_aff)) == 1 and next_aff[0] == "education":
                        df_ai.at[year,"stays_academia"] += 1 

    for aid in tqdm.tqdm(list_aid):
        author = collection_authors.find_one({"AID_cleaned":int(aid)})
                    
        for year_temp in range(1997,year):
            try:
                previous_aff_cf.append(author[str(year_temp)]["aff_type"])
            except:
                continue
        for year_temp in range(year,year + window +1):
            try:
                next_aff_cf.append(author[str(year_temp)]["aff_type"])
            except:
                continue
        if len(set(previous_aff_cf)) == 1:
            if previous_aff_cf[0] == "education":
                if len(set(next_aff_cf)) == 0:
                    df.at[year,"dropout"] += 1
                elif "education" not in next_aff_cf and len(set(next_aff_cf)) != 1:
                    df.at[year,"weird_transition"] += 1 
                elif "education" not in next_aff_cf and len(set(next_aff_cf)) == 1:
                    df.at[year,"transition"] += 1 
                elif len(set(next_aff_cf)) == 1 and next_aff_cf[0] == "education":
                    df.at[year,"stays_academia"] += 1                     
                    
    return df, df_ai

#df, df_ai = get_dropout(list_aid_ai = list_aid_ai_cons3 , list_aid = list_aid_cons3)






# lineplot
df["share_dropout"] = df["dropout"]/(df["dropout"]+df["stays_academia"] + df ["transition"])
df["share_transition"] = df["transition"]/(df["dropout"]+df["stays_academia"] + df ["transition"])
df["share_stays_academia"] = df["stays_academia"]/(df["dropout"]+df["stays_academia"] + df ["transition"])
df_ai["share_dropout"] = df_ai["dropout"]/(df_ai["dropout"]+df_ai["stays_academia"] + df_ai["transition"])
df_ai["share_transition"] = df_ai["transition"]/(df_ai["dropout"]+df_ai["stays_academia"] + df_ai["transition"])
df_ai["share_stays_academia"] = df_ai["stays_academia"]/(df_ai["dropout"]+df_ai["stays_academia"] + df_ai["transition"])
data_merged = pd.concat([df, df_ai], ignore_index=True, sort=False)
data_merged["share_dropout_transition"] = data_merged["share_dropout"] + data_merged["share_transition"]
data_merged["dropout_transition"] = data_merged["dropout"] + data_merged["transition"]


figure = px.line(
    data_frame=data_merged,x="year",y="share_transition", color='type', title="Only education between 1997 and x then new affiliation type during x to x+3"
)

figure.update_layout({
    "plot_bgcolor": "rgba(0, 0, 0, 0)",
    "paper_bgcolor": "rgba(0, 0, 0, 0)",
    })

figure.update_layout(legend=dict(
    title=""
))
    
plot(figure)

figure.write_image("Results/plots/transition_share.png")


figure = px.line(
    data_frame=data_merged,x="year",y="share_dropout", color='type', title="Only education between 1997 and x, dropout of the sample during x to x+3"
)

figure.update_layout({
    "plot_bgcolor": "rgba(0, 0, 0, 0)",
    "paper_bgcolor": "rgba(0, 0, 0, 0)",
    })

figure.update_layout(legend=dict(
    title=""
))
    
plot(figure)

figure.write_image("Results/plots/dropout_share.png")


# All share
figures = [
            px.line(data_merged, x="year", y="share_transition", color='type'),
            px.line(data_merged, x="year", y="share_dropout", color='type', title='Dropout of researcher'),
            px.line(data_merged, x="year", y="share_stays_academia", color='type', title='Stays academia')
    ]

fig = make_subplots(rows=3, cols=1, subplot_titles=("Transitions", 'Dropout of researcher',"Stays academia"))

for i, figure in enumerate(figures):
    for trace in range(len(figure["data"])):
        fig.append_trace(figure["data"][trace], row=i+1, col=1)


plot(fig)
fig.write_image("Results/plots/share_all.png")

#figure.write_image("test.png")
# Test with only stays and dropout

df_share = pd.DataFrame()
df_ai_share = pd.DataFrame()
df_share["transition"] = df["transition"]/ (df["transition"]+df["stays_academia"])
df_share["dropout"] = df["dropout"]/(df["transition"]+df["stays_academia"])
df_share["stays_academia"] = df["stays_academia"]/(df["transition"]+df["stays_academia"])
df_share["type"] = "non_ai"
df_share["year"] = df["year"]

df_ai_share["transition"] = df_ai["transition"]/ (df_ai["transition"]+df_ai["stays_academia"])
df_ai_share["dropout"] = df_ai["dropout"]/(df_ai["transition"]+df_ai["stays_academia"])
df_ai_share["stays_academia"] = df_ai["stays_academia"]/(df_ai["transition"]+df_ai["stays_academia"])
df_ai_share["type"] = "ai"
df_ai_share["year"] = df_ai["year"]


data_share_merged = pd.concat([df_share, df_ai_share], ignore_index=True, sort=False)
data_merged = pd.concat([df, df_ai], ignore_index=True, sort=False)




fig3 = go.Figure(
    data=[
        go.Bar(
            name="AI",
            x=data_merged["year"],
            y=data_merged[data_merged["type"]=="ai"]["transition"],
            offsetgroup=0,
        ),
        #go.Bar(
         #   name="AI",
          #  x=data_merged["year"],
           # y=data_merged[data_merged["type"]=="ai"]["dropout"],
            #offsetgroup=0,
        #),
        go.Bar(
            name="AI",
            x=data_merged["year"],
            y=data_merged[data_merged["type"]=="ai"]["stays_academia"],
            offsetgroup=0,
        ),
        go.Bar(
            name="non-AI",
            x=data_merged["year"],
            y=data_merged[data_merged["type"]=="non_ai"]["transition"],
            offsetgroup=1,
        ),
        #go.Bar(
        #    name="non-AI",
        #    x=data_merged["year"],
        #    y=data_merged[data_merged["type"]=="non_ai"]["dropout"],
        #    offsetgroup=1,
        #),
        go.Bar(
            name="non-AI",
            x=data_merged["year"],
            y=data_merged[data_merged["type"]=="non_ai"]["stays_academia"],
            offsetgroup=1,
        )
    ],
    layout=go.Layout(
        title="Share of outcome for researchers",
        yaxis_title="Share"
    )
)

plot(fig3)

fig4 = go.Figure(
    data=[

        #go.Bar(
        #    name="AI",
        #    x=data_share_merged["year"],
        #    y=data_share_merged[data_share_merged["type"]=="ai"]["dropout"],
        #    offsetgroup=0,
        #),
        go.Bar(
            name="AI stays in academia",
            x=data_share_merged["year"],
            y=data_share_merged[data_share_merged["type"]=="ai"]["stays_academia"],
            offsetgroup=0,
        ),
        go.Bar(
            name="AI do a transition",
            x=data_share_merged["year"],
            y=data_share_merged[data_share_merged["type"]=="ai"]["transition"],
            offsetgroup=0,
        ),        

        #go.Bar(
        #    name="non-AI",
        #    x=data_share_merged["year"],
        #    y=data_share_merged[data_share_merged["type"]=="non_ai"]["dropout"],
        #    offsetgroup=1,
        #),
        go.Bar(
            name="non-AI stays in academia",
            x=data_share_merged["year"],
            y=data_share_merged[data_share_merged["type"]=="non_ai"]["stays_academia"],
            offsetgroup=1,
        ),
        go.Bar(
            name="non-AI do a transition",
            x=data_share_merged["year"],
            y=data_share_merged[data_share_merged["type"]=="non_ai"]["transition"],
            offsetgroup=1,
        )
    ],
    layout=go.Layout(
        title="Share of outcome for researchers",
        yaxis_title="Share"
    )
)

plot(fig4)


t = data_merged[data_merged["type"]=="non_ai"]["transition"][0]
t1 = data_merged[data_merged["type"]=="non_ai"]["transition"][15]
(t1-t)/t

t = data_merged[data_merged["type"]=="ai"]["transition"][19]
t1 = data_merged[data_merged["type"]=="ai"]["transition"][37]
(t1-t)/t

# Share

# Growth smoothed

df_growth_dropout = pd.DataFrame()
df_growth_dropout_ai = pd.DataFrame()
df_growth_dropout["dropout"] = df_share['dropout'].pct_change().rolling(3).mean()
df_growth_dropout["type"] = df_share["type"]
df_growth_dropout["year"] = df_share["year"]
df_growth_dropout_ai["dropout"] = df_ai_share['dropout'].pct_change().rolling(3).mean()
df_growth_dropout_ai["type"] = df_ai_share["type"]
df_growth_dropout_ai["year"] = df_ai_share["year"]
df_dropout = pd.concat([df_growth_dropout, df_growth_dropout_ai], ignore_index=True, sort=False)


df_growth_transition = pd.DataFrame()
df_growth_transition_ai = pd.DataFrame()
df_growth_transition["transition"] = df_share['transition'].pct_change().rolling(3).mean()
df_growth_transition["type"] = df_share["type"]
df_growth_transition["year"] = df_share["year"]
df_growth_transition_ai["transition"] = df_ai_share['transition'].pct_change().rolling(3).mean()
df_growth_transition_ai["type"] = df_ai_share["type"]
df_growth_transition_ai["year"] = df_ai_share["year"]
df_transition = pd.concat([df_growth_transition, df_growth_transition_ai], ignore_index=True, sort=False)

df_growth_stays_academia = pd.DataFrame()
df_growth_stays_academia_ai = pd.DataFrame()
df_growth_stays_academia["stays_academia"] = df_share['stays_academia'].pct_change().rolling(3).mean()
df_growth_stays_academia["type"] = df_share["type"]
df_growth_stays_academia["year"] = df_share["year"]
df_growth_stays_academia_ai["stays_academia"] = df_ai_share['stays_academia'].pct_change().rolling(3).mean()
df_growth_stays_academia_ai["type"] = df_ai_share["type"]
df_growth_stays_academia_ai["year"] = df_ai_share["year"]
df_stays_academia = pd.concat([df_growth_stays_academia, df_growth_stays_academia_ai], ignore_index=True, sort=False)


figures = [
            px.line(df_transition, x="year", y="transition", color='type'),
            px.line(df_dropout, x="year", y="dropout", color='type', title='Dropout of researcher'),
            px.line(df_stays_academia, x="year", y="stays_academia", color='type', title='Stays academia')
    ]

fig = make_subplots(rows=3, cols=1, subplot_titles=("Transitions", 'Dropout',"Stays academia"))

for i, figure in enumerate(figures):
    for trace in range(len(figure["data"])):
        fig.append_trace(figure["data"][trace], row=i+1, col=1)


plot(fig)
fig.write_image("Results/plots/growth_all.png")