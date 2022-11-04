import tqdm
import pickle
import pymongo
import novelpy

Client = pymongo.MongoClient("mongodb://localhost:27017")
db = Client["openAlex"]
collection = db["works_ai_2_False"]
db_output = Client["openAlex_novelty"]
collection_output = db_output["output_disruptiveness"]

year = 2011

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
collection_output = db_output["output_disruptiveness"]
collection_output.delete_many({"year":2009})
collection_output.delete_many({"year":2008})
"""