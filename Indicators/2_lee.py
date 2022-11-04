import tqdm
import pickle
import pymongo
import novelpy

Client = pymongo.MongoClient("mongodb://localhost:27017")
db = Client["openAlex"]
collection = db["works_ai_2_False"]


for year in tqdm.tqdm(range(2000,2022,1)):
    with open('Data/docs/focal_papers_ids/{}.pickle'.format(year), 'rb') as handle:
        list_ids = pickle.load(handle)       
    

    Lee = novelpy.indicators.Lee2015(
                                    collection_name = "concepts",
                                    id_variable = 'id_cleaned',
                                    year_variable = 'publication_year',
                                    variable = "concepts",
                                    sub_variable = "display_name",
                                    focal_year = year,
                                    density = False,
                                    list_ids = list_ids)
    Lee.get_indicator()
        

