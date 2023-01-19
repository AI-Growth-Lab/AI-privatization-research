# Create dataframe for regressions

import re
import tqdm
import pickle
import pymongo
import pandas as pd

Client = pymongo.MongoClient("mongodb://localhost:27017")
db = Client["openAlex"]
collection = db["institutions"]

docs = collection.find()
columns = ["IID","IID_cleaned","works_count","cited_by_count","type","country_code","display_name"]
list_of_insertion = []
for doc in tqdm.tqdm(docs):
    list_of_insertion.append({"IID":doc["id"],
                              "IID_cleaned":int(re.findall(r'\d+', doc["id"] )[0]),
                              "works_count": doc["works_count"],
                              "cited_by_count":doc["cited_by_count"],
                              "type":doc["type"],
                              "country_code":doc["country_code"],
                              "display_name":doc["display_name"]})
    

df=pd.DataFrame(list_of_insertion,columns=columns)
df.to_csv("Data/institutions.csv",index=False)
    