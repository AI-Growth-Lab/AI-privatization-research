# Create csv dataframe of papers
import re
import tqdm
import json
import pickle
import pymongo
import pandas as pd

period = range(1997,2022,1)

Client = pymongo.MongoClient("mongodb://localhost:27017")
db = Client["openAlex"]
collection = db["works_ai_2_False"]

db_output = Client["openAlex_novelty"]
collection_disruptiveness = db_output["output_disruptiveness"]

data = []
for year in tqdm.tqdm(period):
    with open("Results/lee/concepts/{}.json".format(year),"r") as f:
      data += json.load(f)
      
with open('Data/id2concepts.pickle', 'rb') as f:
    id2concepts = pickle.load(f)  

data = {i["id_cleaned"]:i["concepts_lee"] for i in data}

columns = ["id", "year", "title", "type", "oa", "cited_by_count", "list_aid", "concepts", "issn",
           "novelty_lee","DI1","DI5","DI5nok","DI1nok","DeIn","Breadth","Depth"]
list_of_insertion = []

docs = collection.find()

n = 0
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
                
    try:
        doc_temp = collection_disruptiveness.find_one({"id_cleaned":_id})
        DI1 = doc_temp["disruptiveness"]["DI1"]
        DI5 = doc_temp["disruptiveness"]["DI5"]
        DI5nok = doc_temp["disruptiveness"]["DI5nok"]
        DI1nok = doc_temp["disruptiveness"]["DI1nok"]
        DeIn = doc_temp["disruptiveness"]["DeIn"]        
        Breadth = doc_temp["disruptiveness"]["Breadth"]        
        Depth = doc_temp["disruptiveness"]["Depth"]
    except Exception as e:
        n += 1        
        DI1 = None
        DI5 = None
        DI5nok = None
        DI1nok = None
        DeIn = None     
        Breadth = None    
        Depth = None
        
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
        concepts = [concept.lower() for concept in id2concepts[doc["id_cleaned"]]]
    except:
        pass    
    concepts = "\n".join(concepts)
    if doc["host_venue"]["issn_l"]:  
        issn = doc["host_venue"]["issn_l"]
    else:
        issn = None
    list_of_insertion.append([_id, year, title, _type, oa, cited_by_count, list_aid, concepts,
                              issn, novelty_lee, DI1, DI5, DI5nok, DI1nok, DeIn, Breadth, Depth])
    
df = pd.DataFrame(list_of_insertion,columns=columns)
df["DI5"].describe()
df.to_csv("Data/works.csv",index=False)


