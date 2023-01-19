import tqdm
import pickle
import pandas as pd
import numpy as np
import seaborn as sns
import plotly.express as px
from plotly.offline import plot
df = pd.read_csv("Data/seniority_dropout.csv")

with open('Data/list_aid_ai.pickle', 'rb') as f:
    list_aid_ai = pickle.load(f)   

df["dropout"].hist(bins=23)
df["is_ai"] = 0
df["cat"] = None
df.loc[df["AID"].isin(list_aid_ai),"is_ai"] = 1
df["leaving"] = df["dropout"] - df["seniority"]
df.loc[df["leaving"] <= 1, 'cat'] = "oneshot"
df.loc[(df["leaving"] <= 5) & (df["leaving"] > 1),"cat"] = "early"
df.loc[(df["leaving"] <= 10) & (df["leaving"] > 5),"cat"] = "mid_1"
df.loc[(df["leaving"] <= 15) & (df["leaving"] > 10),"cat"] = "mid_2"
df.loc[df["leaving"] > 15,'cat'] = "late"

df[(df["cat"] == "early") & (df["is_ai"]==1)].groupby(["dropout"]).count()

list_of_insertion = []
for year in tqdm.tqdm(range(1997,2016,1)):
    #Permanent in 
    n = len(df[(df["cat"] == "early") & (df["is_ai"]==0) & (df["dropout"]>year)])
    list_of_insertion.append(n)

list_of_insertion
for cat in set(df["cat"]):

    test = df[df['cat']==cat][["AID","dropout","is_ai"]].groupby(["dropout","is_ai"]).count()
    
    columns = ["share","share_ai","year"]
    
    list_of_insertion = []
    for year in tqdm.tqdm(range(1997,2016,1)):
        #n_ai_researcher_left = sum([test.loc[year_temp].loc[1] for year_temp in range(year,2022,1)])
        #n_researcher_left = sum([test.loc[year_temp].loc[0] for year_temp in range(year,2022,1)])
        n_ai_researcher_left = sum([test.loc[year_temp].loc[1] for year_temp in range(1997,2022,1)])
        n_researcher_left = sum([test.loc[year_temp].loc[0] for year_temp in range(1997,2022,1)])

        share_n_researcher = int(test.loc[year].loc[0])/int(n_researcher_left)
        share_ai_researcher = int(test.loc[year].loc[1])/int(n_ai_researcher_left)
        list_of_insertion.append([share_n_researcher, share_ai_researcher, year])
    
    df_temp = pd.DataFrame(list_of_insertion,columns=columns)
    df_temp = pd.melt(df_temp,id_vars=['year'],var_name='type', value_name='value')
    
    
    # Dropout per year left researcher
    """
    fig = px.bar(df_temp, x="year", color="type",
                 y='value',
                 title="A Grouped Bar Chart With Plotly Express in Python {}".format(cat),
                 barmode='group',
                 height=600
                )
    """
    
    fig = px.line(df_temp, x="year", color="type",
                 y='value',
                 title="A Grouped Bar Chart With Plotly Express in Python {}".format(cat),
                 height=600
                )   
    plot(fig)
    before = df_temp[(df_temp['year']==1997) & (df_temp["type"] == "share")  ]["value"]
    after = df_temp[(df_temp['year']==2015) & (df_temp["type"] == "share")  ]["value"]
    print(before, "\t", after, "\t", cat)

    
sum(df_temp[df_temp['type']=='share']["value"])

df_temp

# Testing others
df_temp = df[df['cat']=="phd"][["AID","dropout","is_ai"]].groupby(["dropout","is_ai"]).count()
columns = ["n_dropout","n_dropout_ai","year"]

list_of_insertion = []
for year in tqdm.tqdm(range(2000,2016,1)):
    n_dropout = int(df_temp.loc[year].loc[0])
    n_dropout_ai = int(df_temp.loc[year].loc[1])
    list_of_insertion.append([n_dropout, n_dropout_ai, year])

df_temp = pd.DataFrame(list_of_insertion,columns=columns)
df_temp = pd.melt(df_temp,id_vars=['year'],var_name='type', value_name='value')

df_temp

fig = px.line(df_temp, x="year", color="type",
             y='value',
             title="A Grouped Bar Chart With Plotly Express in Python phd",
             height=600
            )

plot(fig)


list_of_insertion = []
# Number of phds date of entering and leaving after phd ?
columns = ["n_dropout","n_dropout_ai","year"]
for year in tqdm.tqdm(range(2000,2016,1)):
    df_temp = df[df['cat']=="phd"][df['seniority']==year][["AID","is_ai"]].groupby(["is_ai"]).count()
    n_dropout = int(df_temp.loc[0])
    n_dropout_ai = int(df_temp.loc[1])
    n_stays = len(df.loc[df["leaving"] > 5][df['seniority']==year][df["is_ai"] == 0])
    n_stays_ai = len(df.loc[df["leaving"] > 5][df['seniority']==year][df["is_ai"] == 1])
    share = n_dropout/(n_dropout + n_stays)
    share_ai = n_dropout_ai/(n_dropout_ai + n_stays_ai)
    list_of_insertion.append([share, share_ai, year])

df_temp = pd.DataFrame(list_of_insertion,columns=columns)
df_temp = pd.melt(df_temp,id_vars=['year'],var_name='type', value_name='value')
df_temp['value_log'] = np.log2(df_temp['value'])

fig = px.line(df_temp, x="year", color="type",
             y='value',
             title="A Grouped Bar Chart With Plotly Express in Python phd",
             height=600
            )
plot(fig)


# n_entering /n_outing

columns = ["type","value","year","value_entering"]
list_of_insertion = []
for year in tqdm.tqdm(range(2000,2021,1)):
    n_entering = len(df[(df['seniority']==year) & (df["is_ai"] == 0)  & (df["cat"] == "late")])
    n_outing = len(df[(df['dropout']==year) & (df["is_ai"] == 0) & (df["cat"] == "late")])
    n_entering_ai = len(df[(df['seniority']==year) & (df["is_ai"] == 1) & (df["cat"] == "late")])
    n_outing_ai = len(df[(df['dropout']==year) & (df["is_ai"] == 1) & (df["cat"] == "late")])
    ratio = n_outing/n_entering
    ratio_ai = n_outing_ai/n_entering_ai
    list_of_insertion.append(["non_ai",ratio,year,n_entering])
    list_of_insertion.append(["ai",ratio_ai,year,n_entering_ai])    
df_temp = pd.DataFrame(list_of_insertion,columns=columns)


fig = px.line(df_temp, x="year", color="type",
             y='value_entering',
             title="A Grouped Bar Chart With Plotly Express in Python phd",
             height=600
            )
plot(fig)
