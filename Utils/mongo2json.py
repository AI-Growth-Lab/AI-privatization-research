# Used to convert data in json to run on HPC for example

import os
import json
import tqdm
import pickle
import pymongo
from pymongo import UpdateOne


def mongo2json(URI,db_name,collection_name, var, id_var, year_var, years = None, use_ids = False):
    
    Client = pymongo.MongoClient(URI)
    db = Client[db_name]
    collection = db[collection_name]
    if years == None:
        years = collection.find({var:{"$exists":True}}).distinct(year_var)
    
    path = "Data/docs/{}".format(collection_name)
    if not os.path.exists(path):
        os.makedirs(path)
    years = [year for year in years if year != None]  
    
    for year in tqdm.tqdm(years):
        to_insert = []
        if use_ids:
            with open('Data/docs/focal_papers_ids/{}.pickle'.format(year), 'rb') as handle:
                list_ids = pickle.load(handle)       
    
        docs = collection.find({year_var:year,var:{"$exists":True}},{"_id":0})
        for doc in tqdm.tqdm(docs):
            if use_ids:
                if doc[id_var] in list_ids:
                    to_insert.append({id_var:doc[id_var], year_var:doc[year_var],var:doc[var]})
            else:
                to_insert.append({id_var:doc[id_var], year_var:doc[year_var],var:doc[var]})
        if to_insert == []:
            continue
        else:
            with open(path + "/{}.json".format(year), 'w') as outfile:
                json.dump(to_insert, outfile)
        
mongo2json(URI = 'mongodb://localhost:27017', db_name = 'openAlex_novelty',
           collection_name = 'concepts', var = 'concepts',id_var = "id_cleaned",
           year_var = "publication_year",years=range(2006,2022,1), use_ids = False)