#https://mapequation.github.io/infomap/python/infomap.html

import tqdm
import pickle
import novelpy

for year in tqdm.tqdm(range(2000,2022,1)):
    with open('Data/docs/focal_papers_ids/{}.pickle'.format(year), 'rb') as handle:
        list_ids = pickle.load(handle)       
    
    Foster = novelpy.indicators.Foster2015(client_name = 'mongodb://localhost:27017',
                                           db_name = "openAlex_novelty",
                                    collection_name = "concepts",
                                    id_variable = 'id_cleaned',
                                    year_variable = 'publication_year',
                                    variable = "concepts",
                                    sub_variable = "display_name",
                                    focal_year = year,
                                    list_ids = list_ids,
                                    density = False)
    Foster.get_indicator()
    