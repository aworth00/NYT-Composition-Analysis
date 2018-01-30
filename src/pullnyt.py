import requests
import json
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, CollectionInvalid
import datetime as dt
import time 
import pandas as pd 
import numpy as np
import os
import nytimes 

# client = MongoClient()
# # Access/Initiate Database
# db = client['cap_db']
# # Access/Initiate Table
# tab = db['nyt']

'''
Testing two different query types
'''

def single_query(link, payload):
    response = requests.get(link, params=payload)
    if response.status_code != 200:
        print ('WARNING', response.status_code)
    else:
        return response.json()

def alternate():
    api = nytimes.get_article_search_obj
    articles2 = api.search(begin_date = 19640109,end_date=19640110, page=1, source = 'The New York Times',\
                      #type_of_material='Front Page',facet_filter=True)

if __name__=='__main__':
    link = 'http://api.nytimes.com/svc/search/v2/articlesearch.json'
    payload = {'api-key': '','num_pages':1}
    q = single_query(link, payload)
    
            
    