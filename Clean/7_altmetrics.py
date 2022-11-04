# https://api.altmetric.com/

import time
import tqdm
import json
import pymongo
import requests



Client = pymongo.MongoClient("mongodb://localhost:27017")
db = Client["openAlex"]
collection = db["works_ai_2_False"]
collection_output = db["altmetrics"]

try:
    with open("logs/last_it_altmetrics.txt","r") as f:
        last_it = int(f.read())
except:
    last_it = 0

docs = collection.find({},no_cursor_timeout=True).skip(last_it)

for doc in tqdm.tqdm(docs):
    last_it += 1
    if doc["doi"]:
        doi = doc["doi"].split("doi.org/")[-1]
        response = requests.get("https://api.altmetric.com/v1/doi/{}".format(doi))
        if response.status_code != 200 and response.status_code != 404:
            break
        if response.status_code == 200:
            try:
                collection_output.insert_one(json.loads(response.content))
            except:
                time.sleep(0.5)
                with open("logs/last_it_altmetrics.txt","w") as f:
                    f.write(str(last_it))            
                continue
            time.sleep(0.5)
            with open("logs/last_it_altmetrics.txt","w") as f:
                f.write(str(last_it))
        else:
            time.sleep(1)
            continue
    else:
        continue

