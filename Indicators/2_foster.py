#https://mapequation.github.io/infomap/python/infomap.html

import novelpy
import tqdm

for focal_year in tqdm.tqdm(range(2000,2011), desc = "Computing indicator for window of time"):
    Foster = novelpy.indicators.Foster2015(client_name="mongodb://localhost:27017",
                                    db_name = "openAlex_novelty",
                                    collection_name = "concepts",
                                    id_variable = 'id_cleaned',
                                    year_variable = 'publication_year',
                                    variable = "concepts",
                                    sub_variable = "display_name",
                                    focal_year = focal_year,
                                    density = False)
    Foster.get_indicator()
    