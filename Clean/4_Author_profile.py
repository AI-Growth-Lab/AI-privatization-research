import re
import tqdm
import pickle
import pymongo
from collections import defaultdict

with open('Data/list_aid_ai.pickle', 'rb') as f:
    list_aid_ai = pickle.load(f)    

class filter_authors:
    def __init__(self,list_aid):
        self.list_aid = list_aid

    def load_all_ai_ids(self):
        Client = pymongo.MongoClient("mongodb://localhost:27017")
        db = Client["openAlex"]
        collection = db["works_ai_2_False"]
        docs = collection.find()
        
        self.ai_papers = []
        for doc in tqdm.tqdm(docs,desc="get ai papers"):
            self.ai_papers.append(doc["id_cleaned"])


        
    def get_all_pub(self):
    
        Client = pymongo.MongoClient("mongodb://localhost:27017")
        db = Client["openAlex"]
        collection = db["works"]
        self.dict_publication = {aid:[] for aid in self.list_aid}
        docs = collection.find()
        
    
        for doc in tqdm.tqdm(docs, desc="get list publication authors"):
            for author in doc["authorships"]:
                try:
                    id_ = int(re.findall(r'\d+',author["author"]["id"] )[0])
                    self.dict_publication[id_].append(doc["id_cleaned"])
                except:
                    continue

    def check_share_of_ai_paper(self):
        self.final_authors = []
        for author in tqdm.tqdm(self.dict_publication,desc="Get author with atleast 80% of ai papers"):
            n_ai = len([i for i in self.dict_publication[author] if i in self.ai_papers])
            share = n_ai/len(self.dict_publication[author])
            if share > 0.8:
                self.final_authors.append(author)
            self.final_authors.append({author:n_ai})
    
    def save_final(self):
        with open('Data/list_aid_ai_filtered.pickle', 'wb') as handle:
            pickle.dump(self.final_authors, handle, protocol=pickle.HIGHEST_PROTOCOL) 


    def get_final_authors(self):
        self.load_all_ai_ids()
        self.get_all_pub()
        self.check_share_of_ai_paper()
        self.save_final()

inst = filter_authors(list_aid=list_aid_ai)
inst.get_final_authors()
test = inst.final_authors
test2 = inst.dict_publication
ai_papers =  inst.ai_papers


def create_author_profile_list_id(list_aid,year):
    
    Client = pymongo.MongoClient("mongodb://localhost:27017")
    db = Client["openAlex"]
    collection_ai = db["works"]
    collection_ai_authors = db["author_profile"]
    
    collection_ai_authors.create_index([ ("AID_cleaned",1) ])   
    collection_ai_authors.create_index([ ("AID",1) ])   
        
    docs = collection_ai.find({"publication_year":year})
    authors_profile = {aid:defaultdict(list) for aid in list_aid}
    for doc in tqdm.tqdm(docs):
        for author in doc["authorships"]:
            for inst in author["institutions"]:
                try:
                    if inst["type"]:
                        authors_profile[author["author"]["id"]]["type"].append(inst["type"]) 
                        authors_profile[author["author"]["id"]]["display_name"].append(inst["display_name"])
                        aff_id = int(re.findall(r'\d+',inst["id"] )[0])
                        authors_profile[author["author"]["id"]]["inst_id_cleaned"].append(aff_id)
                        authors_profile[author["author"]["id"]]["inst_id"].append(inst["id"])
                except Exception as e :
                    continue

        
    list_of_insertion = []
    for ind in authors_profile:
        if authors_profile[ind]:
            try:
                aff_type = [i for i in authors_profile[ind]["type"] if i != None]
                aff_type = max(aff_type)
                aff_display_name = [i for i in authors_profile[ind]["display_name"] if i != None]
                aff_display_name = max(aff_display_name)
                aff_id = [i for i in authors_profile[ind]["inst_id"] if i != None]                    
                aff_id = max(aff_id)
                aff_id_cleaned = [i for i in authors_profile[ind]["inst_id_cleaned"] if i != None]                    
                aff_id_cleaned = max(aff_id_cleaned)
            except:
                aff_type= None
                aff_display_name = None
                aff_id = None 
                aff_id_cleaned = None 

            id_ = int(re.findall(r'\d+', ind )[0])
            list_of_insertion.append(pymongo.UpdateOne({"AID_cleaned": id_ },
                                                           {'$set': {"AID":ind,str(year): {"aff_type":aff_type,"aff_display_name":aff_display_name,"aff_id":aff_id,"aff_id_cleaned":aff_id_cleaned}}},
                                                           upsert = True))
    if list_of_insertion:
        collection_ai_authors.bulk_write(list_of_insertion)

year = 1997            
with open('Data/list_aid/{}.pickle'.format(year), 'rb') as f:
    list_aid = pickle.load(f)  
create_author_profile_list_id(list_aid,year)
            
def create_author_profile_no_id():

    Client = pymongo.MongoClient("mongodb://localhost:27017")
    db = Client["openAlex"]
    collection_ai = db["works"]
    collection_ai_authors = db["author_profile"]
    collection_institutions = db["institutions"]
    period = range(2006,2022,1)   
    
    docs = collection_institutions.find()
    id2inst_name = {}
    for doc in tqdm.tqdm(docs,desc="getting id2inst"):
        id2inst_name[doc["id"]] = doc["display_name"]
        
     
    collection_ai_authors.create_index([ ("AID_cleaned",1) ])   
    collection_ai_authors.create_index([ ("AID",1) ])   
    for year in tqdm.tqdm(period):
        docs = collection_ai.find({"publication_year":year})
        authors_profile = defaultdict(lambda: defaultdict(list))
        for doc in tqdm.tqdm(docs):
            for author in doc["authorships"]:
                for inst in author["institutions"]:
                    try:
                        if inst["type"] and inst["id"]:
                            authors_profile[author["author"]["id"]]["type"].append(inst["type"]) 
                            authors_profile[author["author"]["id"]]["inst_id"].append(inst["id"])
                    except Exception as e :
                        print(str(e))
                        continue

        
        list_of_insertion = []
        for ind in authors_profile:
            if authors_profile[ind]:
                try:
                    aff_type = [i for i in authors_profile[ind]["type"] if i != None]
                    aff_type = max(set(aff_type), key=aff_type.count)
                    aff_id = [i for i in authors_profile[ind]["inst_id"] if i != None]                    
                    aff_id =  aff_id[[i for i in authors_profile[ind]["type"] if i != None].index(aff_type)]
                    aff_id_cleaned = int(re.findall(r'\d+',aff_id )[0])
                    aff_display_name = id2inst_name[aff_id]
                except:
                    aff_type= None
                    aff_display_name = None
                    aff_id = None 
                    aff_id_cleaned = None 
                try:
                    id_ = int(re.findall(r'\d+', ind )[0])
                except:
                    continue
                list_of_insertion.append(pymongo.UpdateOne({"AID_cleaned": id_ },
                                                               {'$set': {"AID":ind,str(year): {"aff_type":aff_type,"aff_display_name":aff_display_name,"aff_id":aff_id,"aff_id_cleaned":aff_id_cleaned}}},
                                                               upsert = True))
        if list_of_insertion:
            collection_ai_authors.bulk_write(list_of_insertion)

if __name__ == "__main__":
    create_author_profile_no_id()


