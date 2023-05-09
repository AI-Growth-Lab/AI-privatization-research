import re
import tqdm
import pickle
import pymongo
from collections import defaultdict
#from joblib import Parallel, delayed



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
    collection_ai = db["works_ai_2_False"]
    collection_ai_authors = db["author_profile_ai"]
    collection_institutions = db["institutions"]
    period = range(1997,2022,1)   
    
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

def create_author_profile_no_id():

    Client = pymongo.MongoClient("mongodb://localhost:27017")
    db = Client["openAlex"]
    collection_ai = db["works_ai_2_False"]
    collection_ai_authors = db["author_profile_ai"]
    collection_institutions = db["institutions"]
    period = range(1997,2022,1)   
    
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

def clean_less_than_3():
    Client = pymongo.MongoClient("mongodb://localhost:27017")
    db = Client["openAlex"]
    collection_authors = db["author_profile_ai"]
    
    docs = collection_authors.find()
    
    list_of_insertion = []
    n = 0
    for doc in tqdm.tqdm(docs):
        n += 1
        if len(doc) < 6:  
            list_of_insertion.append(doc["AID_cleaned"])
        if len(doc) >= 6:
            years = []
            for key in doc:
                try:
                    years.append(int(key))
                except:
                    continue
            pct_obs = len(years)/(max(years) - min(years) + 1)
            print(doc["AID_cleaned"],years, pct_obs)
            if pct_obs < 0.5:
                list_of_insertion.append(doc["AID_cleaned"])
    for author in tqdm.tqdm(list_of_insertion):
        collection_authors.delete_one({'AID_cleaned':author})
    
clean_less_than_3()



with open('Data/list_aid_ai.pickle', 'rb') as f:
    list_aid_ai = pickle.load(f)    
    
Client = pymongo.MongoClient("mongodb://localhost:27017")
db = Client["openAlex"]
collection = db["author_profile_true_ai"]
list_aid = []
docs = collection.find()
for doc in tqdm.tqdm(docs):
    list_aid.append(doc["AID_cleaned"])

class filter_authors:
    def __init__(self,list_aid):
        self.list_aid = list_aid
        Client = pymongo.MongoClient("mongodb://localhost:27017")
        self.db = Client["openAlex"]
        
    def load_all_ai_ids(self):

        collection = self.db["works_ai_2_False"]
        docs = collection.find()
        
        self.ai_papers = []
        for doc in tqdm.tqdm(docs,desc="get ai papers"):
            self.ai_papers.append(doc["id_cleaned"])


        
    def get_all_pub(self):
    

        collection = self.db["works"]
        self.dict_publication = {aid:[] for aid in self.list_aid}
        docs = collection.find()
        
    
        for doc in tqdm.tqdm(docs, desc="get list publication authors"):
            try:
                if doc["publication_year"] >= 1997:
                    for author in doc["authorships"]:
                        try:
                            id_ = int(re.findall(r'\d+',author["author"]["id"] )[0])
                            self.dict_publication[id_].append(doc["id_cleaned"])
                        except:
                            continue
            except:
                continue

    def check_share_of_ai_paper(self):
        self.final_authors = []
        for author in tqdm.tqdm(self.dict_publication,desc="Get author with atleast 80% of ai papers"):
            #n_ai = len([i for i in self.dict_publication[author] if i in self.ai_papers])
            n_ai = len(set(self.dict_publication[author]).intersection(self.ai_papers))
            share = n_ai/len(self.dict_publication[author])
            if n_ai > 3 or share >= 0.5:
                self.final_authors.append(author)
    
    def save_final(self):
        with open('Data/list_aid_ai_filtered.pickle', 'wb') as handle:
            pickle.dump(self.final_authors, handle, protocol=pickle.HIGHEST_PROTOCOL) 
    
    def add_info_mongo(self):
        list_of_insertion = []
        for author in tqdm.tqdm(self.final_authors):
            list_of_insertion.append(pymongo.UpdateOne({'AID_cleaned': author}, {'$set': {'true_ai': 1}}, upsert=True))
            if len(list_of_insertion) % 10000 == 0:
                self.db["author_profile"].bulk_write(list_of_insertion)
                list_of_insertion = []
            
        self.db["author_profile"].bulk_write(list_of_insertion)        

    def create_author_profile_true_ai(self):
        docs = self.db["author_profile"].find({'true_ai': {"$exists":1}})
        list_of_insertion = []
        for doc in tqdm.tqdm(docs):
            list_of_insertion.append(doc)
        
        self.db["author_profile_true_ai"].insert_many(list_of_insertion)
        
    def unset_ai_key(self):
        self.db["author_profile_ai"].update_many({}, { "$unset" : { "ai" : 1} })
    
    def get_final_authors(self):
        self.load_all_ai_ids()
        self.get_all_pub()
        #self.check_share_of_ai_paper()
        #self.save_final()
        #self.add_info_mongo()

inst = filter_authors(list_aid=list_aid)
#inst.unset_ai_key()
inst.get_final_authors()

works = inst.dict_publication
works_final = []

i = 0
for author in tqdm.tqdm(works):
    works_final += works[author]
    i += 1
    if i % 10000 == 0:
        works_final = list(set(works_final))
test = inst.final_authors

with open('Data/works_true_ai.pickle', 'wb') as handle:
    pickle.dump(works_final, handle, protocol=pickle.HIGHEST_PROTOCOL) 

collection_work = db["works"]
collection_works_true_ai = db["works_from_true_ai"]

list_of_insertion = []
for work in tqdm.tqdm(works_final):
    doc = collection_work.find_one({"id_cleaned":work})
    list_of_insertion.append(doc)
    if len(list_of_insertion) == 10000:
        collection_works_true_ai.insert_many(list_of_insertion)
        list_of_insertion = []
collection_works_true_ai.insert_many(list_of_insertion)



Client = pymongo.MongoClient("mongodb://localhost:27017")
db = Client["openAlex"]
collection = db["author_profile_true_ai"]
docs = collection.find()
author_profile_cleaned = {}
for doc in tqdm.tqdm(docs):
    author_profile_cleaned[doc["AID_cleaned"]] = doc
        
def get_works_true_ai():

    Client = pymongo.MongoClient("mongodb://localhost:27017")
    db = Client["openAlex"]
    collection = db["works"]
    collection_authors  = db["author_profile_true_ai"]
    list_aid = []
    
    docs = collection_authors.find({})
    for doc in tqdm.tqdm(docs):
        list_aid.append(doc["AID_cleaned"])
    
    dict_publication = {aid:list() for aid in list_aid}
    docs = collection.find()
    
    for doc in tqdm.tqdm(docs, desc="get list publication authors"):
        if doc["publication_year"]:
            year = doc["publication_year"]
            if year>= 1997 and year <= 2021:  
                for author in doc["authorships"]:
                    try:
                        id_ = int(re.findall(r'\d+',author["author"]["id"] )[0])
                        dict_publication[id_].append(doc["id_cleaned"])
                    except Exception as e:
                        continue
    works = []
    i = 0
    for author in tqdm.tqdm(dict_publication):
        works += dict_publication[author]
        i += 1
        if i % 1000 == 0:
            works = list(set(works))
    
def get_list_aid_3_years_cons():
    Client = pymongo.MongoClient("mongodb://localhost:27017")
    db = Client["openAlex"]
    collection_ai_authors = db["author_profile_ai"]
    collection_authors = db["author_profile"]    
    
    
    list_aid = []
    list_aid_ai = []
    
    authors = collection_ai_authors.find()
    for author in tqdm.tqdm(authors):
        if len(author) >= 6:
            list_aid_ai.append(author["AID_cleaned"])
    
    
    authors = collection_authors.find()
    for author in tqdm.tqdm(authors):
        if len(author) >= 6:
            list_aid.append(author["AID_cleaned"])
        
    with open('Data/list_aid_ai_cons3.pickle', 'wb') as handle:
        pickle.dump(list_aid_ai, handle, protocol=pickle.HIGHEST_PROTOCOL)   
    
    with open('Data/list_aid_cons3.pickle', 'wb') as handle:
        pickle.dump(list_aid, handle, protocol=pickle.HIGHEST_PROTOCOL)   