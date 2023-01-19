import tqdm
import pickle
import re
import tqdm
import pymongo
import pandas as pd
from collections import defaultdict



Client = pymongo.MongoClient("mongodb://localhost:27017")
db = Client["openAlex"]
collection = db["works"]

def seniority():

    seniority = defaultdict(int)
    for year in tqdm.tqdm(range(2022,1900,-1)):
        with open('Data/list_aid/{}.pickle'.format(year), 'rb') as f:
            list_aid = pickle.load(f)  
        for id_ in tqdm.tqdm(list_aid):
            seniority[id_] = year
            
    with open('Data/seniority.pickle', 'wb') as handle:
        pickle.dump(seniority, handle, protocol=pickle.HIGHEST_PROTOCOL)                  
    




def dropout():
 
    dropout = defaultdict(int)
    for year in tqdm.tqdm(range(1997,2022,1)):
        with open('Data/list_aid/{}.pickle'.format(year), 'rb') as f:
            list_aid = pickle.load(f)  
        for id_ in tqdm.tqdm(list_aid):
            dropout[id_] = year

    with open('Data/dropout.pickle', 'wb') as handle:
        pickle.dump(dropout, handle, protocol=pickle.HIGHEST_PROTOCOL)         
            

with open('Data/dropout.pickle', 'rb') as f:
        dropout = pickle.load(f)  
       
with open('Data/seniority.pickle', 'rb') as f:
        seniority = pickle.load(f)  

list_of_insertion = [] 
for id_ in tqdm.tqdm(dropout):
    
    list_of_insertion.append([id_,seniority[id_],dropout[id_]])

with open('Data/seniority_dropout.pickle', 'wb') as handle:
    pickle.dump(list_of_insertion, handle, protocol=pickle.HIGHEST_PROTOCOL)                  

columns = ["AID","seniority","dropout"]

df = pd.DataFrame(list_of_insertion,columns=columns)
df["dropout"].hist(bins=23)
df.to_csv("Data/seniority_dropout.csv",index=False)



    
