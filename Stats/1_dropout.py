import tqdm
import pymongo
import pandas as pd
import plotly.express as px
from plotly.offline import download_plotlyjs, init_notebook_mode,  plot
import plotly.graph_objects as go
import pickle


Client = pymongo.MongoClient("mongodb://localhost:27017")
db = Client["openAlex"]
collection_ai_authors = db["author_profile_ai"]

"""
list_of_insertion = []
authors = db["author_profile_ai"].find({})
for author in tqdm.tqdm(authors):
    list_of_insertion.append(pymongo.UpdateOne({'AID_cleaned': author["AID_cleaned"]}, {'$set': {'ai': 1}}, upsert=True))
    if len(list_of_insertion) % 10000 == 0:
        db["author_profile"].bulk_write(list_of_insertion)
        list_of_insertion = []
        
db["author_profile"].bulk_write(list_of_insertion)        
"""  
    


def get_dropout(ai = True, window=3):
    
    Client = pymongo.MongoClient("mongodb://localhost:27017")
    db = Client["openAlex"]
    if ai:
        collection_ai_authors = db["author_profile_ai"]
    else:
        collection_ai_authors = db["author_profile"]    
        
    list_of_insertion = []
    
    for year in tqdm.tqdm(range(2000,2016,1)):
        dropout = 0
        transition = 0
        stays_academia = 0
        if ai:
            authors = collection_ai_authors.find({})
        else:
            authors = collection_ai_authors.find({'ai':{"$exists":0}})
        for author in tqdm.tqdm(authors):            
            previous_aff = []
            next_aff = []
            for year_temp in range(1997,year):
                try:
                    previous_aff.append(author[str(year_temp)]["aff_type"])
                except:
                    continue
            for year_temp in range(year,year + window +1):
                try:
                    next_aff.append(author[str(year_temp)]["aff_type"])
                except:
                    continue
            if len(set(previous_aff)) == 1:
                if previous_aff[0] == "education":
                    if len(set(next_aff)) == 0:
                        dropout += 1
                    elif "education" not in next_aff:
                        transition += 1
                    elif len(set(next_aff)) == 1 and next_aff[0] == "education":
                        stays_academia += 1
                        
        list_of_insertion.append([year, transition, dropout,stays_academia])
                        
    columns = ["year", "transition", "dropout", "stays_academia"]       
    
    df = pd.DataFrame(list_of_insertion,columns=columns)
    
    return df

df = get_dropout(ai = False, window=3)
df_ai = get_dropout(ai = True, window=3)

df["share_dropout"] = df["dropout"]/(df["dropout"]+df["stays_academia"] + df ["transition"])
df["share_transition"] = df["transition"]/(df["dropout"]+df["stays_academia"] + df ["transition"])
df["share_stays_academia"] = df["stays_academia"]/(df["dropout"]+df["stays_academia"] + df ["transition"])

figure = px.line(
    data_frame=df,x="year",y="transition",title="Only education between 1997 and x, dropout or no education during x to x+3"
)

figure.update_layout({
    "plot_bgcolor": "rgba(0, 0, 0, 0)",
    "paper_bgcolor": "rgba(0, 0, 0, 0)",
    })

figure.update_layout(legend=dict(
    title=""
))
    
plot(figure)

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

df["type"] = "non_ai"
df_ai["type"] = "ai"

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

t = data_merged[data_merged["type"]=="ai"]["transition"][16]
t1 = data_merged[data_merged["type"]=="ai"]["transition"][31]
(t1-t)/t

