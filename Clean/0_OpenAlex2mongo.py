import gzip
import shutil
import re
import glob
import pymongo
import tqdm
import json
from joblib import Parallel, delayed

client = pymongo.MongoClient("mongodb://localhost:27017")
db = client['openAlex']

data_path = r"D:\openalex-snapshot\data"


# Best structure for parallel but ugly
def decompress_alldata(path):
    def decompress_data(file,mongopath):
        def get_abstract(words):
            n = max({idx  for name in words for idx in words[name]})+1
            temp_list = [' ']*n
            for word in words:
                idxs = words[word]
                for idx in idxs:
                    temp_list[idx] = word
            abstract = ' '.join(temp_list)
            return abstract
        client = pymongo.MongoClient(mongopath)
        db = client['openAlex']
        col = db[folder]
        f = gzip.open(file, 'rb')
        data = []
        i = 0
        for line in f:
            i += 1
            document = json.loads(line)
            if "abstract_inverted_index" in document.keys():
                if document['abstract_inverted_index']:
                    abstract = get_abstract(document['abstract_inverted_index'])
                    document.update({'abstract':abstract})

                document.pop('abstract_inverted_index')  
            data.append(document)
            if i % 1000 == 0:
                col.insert_many(data)
                data = []

        col.insert_many(data)
                
    folders = ['works']#
    for folder in folders:
        col = db[folder]
        print(folder)
        files = glob.glob(path+'\\'+folder+'\\*\\*.gz')
        Parallel(n_jobs=4)(delayed(decompress_data)(file,"mongodb://localhost:27017") for file in tqdm.tqdm(files))
        if folder != 'venues':
            print('create index...')
            col.create_index([ ('id',1)])

decompress_alldata(data_path)