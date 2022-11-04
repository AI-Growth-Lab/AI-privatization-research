#https://mapequation.github.io/infomap/python/infomap.html

import tqdm
import pickle
import novelpy


for year in tqdm.tqdm(range(2000,2022,1)):
    with open('Data/docs/focal_papers_ids/{}.pickle'.format(year), 'rb') as handle:
        list_ids = pickle.load(handle)       
    
    Wang = novelpy.indicators.Wang2017(collection_name = "concepts",
                                        id_variable = 'id_cleaned',
                                        year_variable = 'publication_year',
                                        variable = "concepts",
                                        sub_variable = "display_name",
                                        focal_year = year,
                                        time_window_cooc = 3,
                                        n_reutilisation = 1)
    Wang.get_indicator()