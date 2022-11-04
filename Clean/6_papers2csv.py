# Create csv dataframe of papers
import re
import tqdm
import json
import pymongo
import pandas as pd

period = range(2000,2022,1)

Client = pymongo.MongoClient("mongodb://localhost:27017")
db = Client["openAlex"]
collection = db["works_ai_2_False"]



data = []
for year in tqdm.tqdm(period):
    with open("Results/lee/concepts/{}.json".format(year),"r") as f:
      data += json.load(f)
data = {i["id_cleaned"]:i["concepts_lee"] for i in data}

columns = ["id", "year", "title", "type", "oa", "cited_by_count", "list_aid", "concepts", "issn","novelty_lee"]
list_of_insertion = []

docs = collection.find()
for doc in tqdm.tqdm(docs):
    year = doc["publication_year"]
    _id = doc["id_cleaned"]
    title = doc["title"]
    _type = doc["type"]
    oa = doc["open_access"]["is_oa"]
    cited_by_count = doc["cited_by_count"]
    try:
        novelty_lee = data[_id]["score"]["novelty"]
    except:
        novelty_lee = None
        
    list_aid = []
    for author in doc["authorships"]:
        try:
            author_id = str(re.findall(r'\d+',author["author"]["id"] )[0])
            list_aid.append(author_id)
        except:
            continue
    if list_aid: 
        list_aid = "\n".join(list_aid)
    else:
        list_aid = None
    
    try:
        concepts = [concept["display_name"].lower() for concept in doc["concepts"]]
    except:
        pass    
    concepts = "\n".join(concepts)
    if doc["host_venue"]["issn_l"]:  
        issn = doc["host_venue"]["issn_l"]
    else:
        issn = None
    list_of_insertion.append([_id, year, title, _type, oa, cited_by_count, list_aid, concepts,issn,novelty_lee])
    
df=pd.DataFrame(list_of_insertion,columns=columns)
df.to_csv("Data/works.csv",index=False)


