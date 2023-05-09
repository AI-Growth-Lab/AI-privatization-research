import tqdm
import pymongo
from collections import defaultdict, Counter

# MongoDB connection
Client = pymongo.MongoClient("mongodb://localhost:27017")
db = Client["openAlex"]
collection = db["concepts"]
collection_work = db["works_ai_2_False"]

#%%

# Get children of "Artificial intelligence"
concepts_ai = defaultdict(list)
docs = collection.find({})
for doc in tqdm.tqdm(docs):
    for concept in doc["ancestors"]:
        if concept["display_name"] == "Artificial intelligence":
            concepts_ai[doc["level"]].append(doc["display_name"])
   
# Get children of "Machine learning"            
concepts_ml = defaultdict(list)
docs = collection.find({})
for doc in tqdm.tqdm(docs):
    for concept in doc["ancestors"]:
        if concept["display_name"] == "Machine learning":
            concepts_ml[doc["level"]].append(doc["display_name"])

# Stats on overlap
overlap_share_ai = []
overlap_share_ml = []
for key in concepts_ai:
    overlap_share_ai.append(len([i for i in concepts_ai[key] if i in concepts_ml[key]])/len(concepts_ai[key]))
    overlap_share_ml.append(len([i for i in concepts_ai[key] if i in concepts_ml[key]])/len(concepts_ml[key]))

# If concept in ai and ml save
keywords_ai = []
for key in concepts_ai:
    keywords_ai += [i for i in concepts_ai[key] if i in concepts_ml[key]]
keywords_ai += ["Artificial intelligence","Machine learning"]


with open("hierarchy_keywords.txt", 'w') as output:
    for keyword in keywords_ai:
        output.write(keyword + '\n')
        
    
#%% Keep track of level

concepts = defaultdict(int)

n = 0
docs = collection_work.find({})
for doc in tqdm.tqdm(docs):
    done = False
    for concept in doc["concepts"]:
        if concept["score"] > 0.5:
            if concept["level"] == 1:
                concepts[concept["display_name"]] += 1
                done = True
    if done == False:
        n += 1

top_100 = Counter(concepts)
top_100 = [i[0] for i in top_100 if i[0] not in ['Computer Science', 'Artificial Intelligence', 'Machine Learning']] 


concepts2hierarchy = defaultdict(list)
docs = collection.find({})
for doc in tqdm.tqdm(docs):
    for concept in doc["ancestors"]:
        if concept["display_name"] in top_100:
            concepts2hierarchy[doc["display_name"]].append(concept["display_name"])
            
id2concepts = defaultdict(list)
docs = collection_work.find({})
for doc in tqdm.tqdm(docs):
    for concept in doc["concepts"]:
        if concept["display_name"] in top_100 and concept["score"] > 0.3:
            id2concepts[doc["id_cleaned"]].append(concept["display_name"])
        elif concept["display_name"] in concepts2hierarchy and concept["score"]>0.5:
            id2concepts[doc["id_cleaned"]] += concepts2hierarchy["display_name"]

unique_concepts = []
    
for doc in tqdm.tqdm(id2concepts):
    unique_concepts += id2concepts[doc]

Counter(unique_concepts)


with open("data/hierarchy_keywords.txt", 'r') as f:
    keywords = f.read().split("\n")[0:-1]
keywords = [keyword.lower() for keyword in keywords]

