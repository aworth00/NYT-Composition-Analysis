import requests, pymongo, json, time
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from bs4 import BeautifulSoup
import os
import time


# Url for NYT dev api
NYT_URL = 'http://api.nytimes.com/svc/search/v2/articlesearch.json'
API_KEY = os.environ.get('NYT_KEY')

def init_mongo_client():
    
    '''
    Open mongo client
    identify database to use 
    specify the collection to work from 
    '''
    
    client = pymongo.MongoClient()
    db = client.cap_db    
    coll = db.articles
    return coll


def call_api(url, payload, p=0):
    
    ''' 
    INPUT:
    '''
    payload['page'] = p

    # Get the requested url. Error handling for bad requests should be done in
    # the calling function.
    return requests.get(url, params=payload)


def get_response(r):
    '''
    input: response from request 
    output: meta response, document response 
    '''
    raw = json.loads(r.text)
    return raw['response']['meta'], raw['response']['docs']


def get_soup(url):
    try:
        r = requests.get(url)
    except:
        return None

    #response code 200 == OK ( aka everything went smoothly ) 
    if r.status_code != 200: 
        #print("status_code: ",r.status_code)
        return None

    # return the souped body text 
    return BeautifulSoup(r.text.encode('utf-8'))


def get_body_text(docs):

    # Grab the url from each document, if it exists, then scrape each url for
    # its body text. If we get any errors along the way, continue on to the
    # next document / url to be scraped.
    result = []
    for d in docs:

        # Make a copy of the doc's dictionary
        doc = d.copy()

        # If there's no url (not sure why this happens sometimes) then ditch it
        if not doc['web_url']:
            continue

        # Scrape the doc's url, return a soup object with the url's text.
        soup = get_soup(doc['web_url'])
        if not soup:
            continue

        # Find all of the paragraphs with the correct class.
        # This class tag is specific to NYT articles.
        body = soup.find_all('p', class_= "story-body-text story-content")
        #body = soup.find_all('p', itemprop= "articleBody")
        '''
        For 1987 the articles need a different scraping method, they use 
        itemprop = "articleBody" instead of class = "story-body-text"
        '''
        #body87 = soup87.find_all('p', itemprop= "articleBody")
        #doc87 = '\n'.join([x.get_text().strip() for x in body87])
        if not body:
            #continue
            '''beating the scrape'''
            body = soup.find_all('p', itemprop= "articleBody")
        
        else:
            continue

        # Join the resulting body paragraphs' text (returned in a list).
        ''' original '''
        #doc['body'] = '\n'.join([x.get_text() for x in body])
        
        #for '87'
        #doc['body'] = '\n'.join([x.get_text().strip() for x in body])
        doc['body'] = '\n'.join([x.get_text() for x in body])
        print (doc['web_url'])
        result.append(doc)

    return result


def remove_previously_scraped(coll, docs):
    # Check to see if the mongo collection already contains the docs returned
    # from NYT. Return back a list of the ones that aren't in the collection to
    # be scraped.
    new_docs = []
    for doc in docs:
        # Check fo the document id in mongo. If it finds none, append to
        # new_docs
        cursor = articles.find({'_id': doc['_id']}).limit(1)
        if not cursor.count() > 0:
            new_docs.append(doc)

    if new_docs == []:
        return None

    return new_docs


def get_end_date(dt):
    # String-ify the datetime object to YYYMMDD, which the NYT likes.
    yr   = str(dt.year)
    mon = '0' * (2 - len(str(dt.month))) + str(dt.month)
    day = '0' * (2 - len(str(dt.day))) + str(dt.day)
    return yr + mon + day

def wait_24(num_days=1):
    hold_calls = timedelta(days=num_days)
    return hold_calls


def scrape_articles(coll, last_date):
    page = 0
    while page <= 10:
        print ('Page:', page)
        # Request all of the newest articles matching the search term
        payload  = {'sort': 'newest',
                    'end_date': get_end_date(last_date),
                    'api-key': API_KEY,
                    'type_of_material':'Article'}

        # Call the API with BaseURL + params and page
        r = call_api(NYT_URL, payload, page)
        
        if r.status_code == 429:
            '''
            If the API has been pinged too many times sleep for 
            24 hours and then resume the ping cycle.
            '''
            t = wait_24()
            time.sleep(t.total_seconds)
            
        
        
        '''
        Code below shows that articles are in fact being passed through that aren't
        in the data but it is -- 
        
        update : These articles are returning "article pack" articles which only have 
        a snippet of the text, they do not have the full body of the text (p -- story body)
        which is why the responses come back empty in 67, 87
        '''
        # print ('status_code: ',r.status_code)
        # r = r.json()
        # print (r['response']['meta'])
        # print (r['response']['docs'])
        # break
        
        
        
        # Increment the page before we encounter any potential errors
        page += 1

        # Check to see if the metadata didn't come back. USUALLY happens if
        # page > 100. When it does, reset the whole thing, roll the date back
        # one day, sleep for a couple seconds, then keep going.
        if r.status_code != 200 or page==3:
            page = 0
            if last_date.year in [2017,2007,1997,1987,1977,1967]:
                print('Skipping:{}'.format(last_date.year))
                last_date += relativedelta(years=-1)
            else:
                last_date += relativedelta(days=-1)
                
            print ('End Date:', get_end_date(last_date))
            
            #time.sleep(.5)
            continue
        
        # Halt the program once it reaches 1957
        if last_date.year ==  1957:
            break   

        meta, docs = get_response(r)

        # check for duplicates
        new_docs = remove_previously_scraped(coll, docs)
        if not new_docs: continue

        # Grab only the docs that have these tags
        docs_with_body = get_body_text(new_docs)
        
        for doc in docs_with_body:
            #print (doc)
            #break
            try:
                # Insert each doc into Mongo
                coll.insert(doc)
            except:
                # If there's any error writing it in the db, just move along.
                continue


if __name__ == '__main__':

    # Initialize db & collection
    articles = init_mongo_client()

    # Set the initial end date (scraper starts at this date and moves back in
    # time sequentially)
    #last_date = datetime.now() + relativedelta(days=-30)
    last_date = datetime(2012,12,13)
    
    # 1957 01 16
    '''
        - 2017
        - 2007 
        - 1997 
        - 1987 _ FIXED NEEDED NEW SCRAPE SELECt 
        - 1977
        - 1967 - NONE
        - 1957
    '''    
    
    # Pass the database collection and initial end date into main function
    scrape_articles(articles, last_date)