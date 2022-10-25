import tqdm
import pymongo
from collections import defaultdict

# MongoDB connection
Client = pymongo.MongoClient("mongodb://localhost:27017")
db = Client["openAlex"]
collection = db["concepts"]

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
        
    
