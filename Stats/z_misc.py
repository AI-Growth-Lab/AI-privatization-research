import tqdm
import pandas as pd 
import plotly.express as px
from plotly.offline import plot
import pymongo


Client = pymongo.MongoClient("mongodb://localhost:27017")
db = Client["openAlex"]
collection_ai_authors = db["author_profile_ai"]


df_variables = pd.read_csv("Data/variables.csv")
df_variables = df_variables[df_variables["year"]>=2000]
df_static = pd.read_csv("Data/author_static.csv")
df_works = pd.read_csv("Data/variables.csv")


# 1 aff
authors_1_aff = list(set(df_variables[pd.notna(df_variables["aff_type"])]["AID"]))
n_authors_1_aff = len(set(df_variables[pd.notna(df_variables["aff_type"])]["AID"]))


# 3 consecutive years

authors_3_cons_aff = []

for year in range(2000,2022):
    context = list(range(year-1, year+2))
    query = {str(i):{"$exists":1,"$ne":None} for i in context }
    docs = collection_ai_authors.find(query)
    for doc in tqdm.tqdm(docs):
        authors_3_cons_aff.append(doc["AID_cleaned"])

authors_3_cons_aff = list(set(authors_3_cons_aff))

# Create list of authors
list_edu = list(df_static[df_static['AID'].isin(authors_3_cons_aff)][df_static[df_static['AID'].isin(authors_3_cons_aff)]["type"] == "education"]["AID"])
list_comp = list(df_static[df_static['AID'].isin(authors_3_cons_aff)][df_static[df_static['AID'].isin(authors_3_cons_aff)]["type"] == "company"]["AID"])
list_switcher = list(df_static[df_static['AID'].isin(authors_3_cons_aff)][df_static[df_static['AID'].isin(authors_3_cons_aff)]["type"] == "switcher"]["AID"])



# Freq per type on author 1 aff

freq = df_static[df_static['AID'].isin(authors_3_cons_aff)]["type"].value_counts().to_dict()
freq["education"]/len(authors_3_cons_aff)
freq["company"]/len(authors_3_cons_aff)
freq["switcher"]/len(authors_3_cons_aff)


# paper mean per type on author 1 aff

df_variables[df_variables['AID'].isin(list_edu)].groupby('AID').sum()["paper_n"].mean()
df_variables[df_variables['AID'].isin(list_comp)].groupby('AID').sum()["paper_n"].mean()
df_variables[df_variables['AID'].isin(list_switcher)].groupby('AID').sum()["paper_n"].mean()

# paper mean per type on author 1 aff

df_variables[df_variables['AID'].isin(list_edu)].groupby('AID').sum()["paper_n"].mean()
df_variables[df_variables['AID'].isin(list_comp)].groupby('AID').sum()["paper_n"].mean()
df_variables[df_variables['AID'].isin(list_switcher)].groupby('AID').sum()["paper_n"].mean()

# n_citation sum

df_variables[df_variables['AID'].isin(list_edu)].groupby('AID').sum()["citation"].mean()
df_variables[df_variables['AID'].isin(list_comp)].groupby('AID').sum()["citation"].mean()
df_variables[df_variables['AID'].isin(list_switcher)].groupby('AID').sum()["citation"].mean()

# n_citation mean

df_variables[df_variables['AID'].isin(list_edu)].groupby('AID').mean()["citation"].mean()
df_variables[df_variables['AID'].isin(list_comp)].groupby('AID').mean()["citation"].mean()
df_variables[df_variables['AID'].isin(list_switcher)].groupby('AID').mean()["citation"].mean()

# n_citation mean mean

df_variables[df_variables['AID'].isin(list_edu)].groupby('AID').mean()["citation_mean"].mean()
df_variables[df_variables['AID'].isin(list_comp)].groupby('AID').mean()["citation_mean"].mean()
df_variables[df_variables['AID'].isin(list_switcher)].groupby('AID').mean()["citation_mean"].mean()

# n_gender

df_variables["gender"].replace("female", 0,inplace=True)
df_variables["gender"].replace('male',1,inplace=True)
df_variables["gender"].replace('unisex',None,inplace=True)
df_variables["gender"] = pd.to_numeric(df_variables["gender"])

df_variables[df_variables['AID'].isin(list_edu)].groupby("AID")["gender"].min().mean()
df_variables[df_variables['AID'].isin(list_comp)].groupby('AID')["gender"].max().mean()
df_variables[df_variables['AID'].isin(list_switcher)].groupby('AID')["gender"].min().mean()


def gb_mode(df, keys, column):
    return (
        df.groupby(keys + [column], sort=False)
        .size()
        .sort_values(ascending=False, kind='mergesort')
        .reset_index(column)
        .groupby(keys)
        [column]
        .head(1)
        .sort_index()
    )

df = df_variables[df_variables['AID'].isin(list_edu)]
gb_mode(df_variables[df_variables['AID'].isin(list_edu)],["AID"], "gender").mean()
gb_mode(df_variables[df_variables['AID'].isin(list_comp)],["AID"], "gender").mean()
gb_mode(df_variables[df_variables['AID'].isin(list_switcher)],["AID"], "gender").mean()







fig = px.histogram(df_variables["citation_mean"])
plot(fig)

# 


