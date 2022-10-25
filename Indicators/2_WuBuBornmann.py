import tqdm
import pickle
import pymongo
import novelpy

Client = pymongo.MongoClient("mongodb://localhost:27017")
db = Client["openAlex"]
collection = db["works_ai_2_False"]

year = 2004

with open('Data/docs/focal_papers_ids/{}.pickle'.format(year), 'rb') as handle:
    list_ids = pickle.load(handle)       
    
disruptiveness = novelpy.Disruptiveness(
    client_name = 'mongodb://localhost:27017',
    db_name = 'openAlex_novelty',
    collection_name = 'Citation_net_cleaned',
    focal_year = year,
    id_variable = 'id_cleaned',
    variable = "citations_cleaned",
    refs_list_variable ='refs',
    cits_list_variable = 'cited_by',
    year_variable = 'publication_year',
    list_ids = list_ids)

disruptiveness.get_indicators()

"""
db_output = Client["openAlex_novelty"]
collection_output = db["output_disruptiveness"]
collection.delete_many({"year":2002})
"""