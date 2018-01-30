import nytimes
import datetime as dt
import json

search_obj = nytimes.get_article_search_obj([API_KEY])


article_search_frontpage(q = None, num_pages = 1, begin_date = None, end_date = None, filename = None)
if __name__=='__main__':
    
    sample = search_obj.article_search_frontpage(begin_date=19570907,end_date=19570907)
    print(len(sample))