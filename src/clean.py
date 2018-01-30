import pandas as pd 
import numpy as np 
from textstat.textstat import textstat
from pymongo import MongoClient
import pickle 
import seaborn as sns 
import matplotlib.pyplot as plt
import seaborn as sns 


def start_mongo():
    '''
    Used to start the DB if you want to update & or access
    
    '''
    client = MongoClient()
    db = client.cap_db
    collection = db.nyt
    #data = pd.DataFrame(list(collection.find()))
    articles = pd.DataFrame(list(db.articles.find()))

def clean_with_mongo():
    '''
    MongoDB syntax for in mongo cleaning 
    '''
    # collection = db.nyt
    db.collection.remove({$where: 'this.body.length<2'})
    db.collection.remove({body: {$regex: /^Digitized text of this article is not available/i}})

def drop_columns(df,list_of_columns):
    df = df[list_of_columns]
    return df

def update_mongo_flesch_kincaid():
    '''
    This function is meant to append all rows in data base with a new 
    variable that represents the flesch_kincaid reading level
    of the article being looked at. TO MONGO DB
    '''
    cursor = db.articles.find()
    for doc in cursor:
        article_id=doc['_id']
        flesch_score = textstat.flesch_reading_ease(doc['body'])
        articles.update_one({'_id':article_id},{'$set':{'flesch_kincaid_score':int(flesch_score)}})        
    # Need to figure out try except still in update_mongo_flesch_kincaid

# def score_update_pandas(df):
#     '''
#     writing test flesch-kincaid-ease score inside jupyter notebook
#     '''
#     if df['flesch_kincaid']:
#         pass 
#     else:
#         df['flesch_kincaid']=np.nan
# 
#     nan_list = []
#     for row, article in enumerate(df['body']):
#         if len(df['body'][row])>0:
#             x = article
#             try:
#                 df.loc[row,'flesch_kincaid']=textstat.flesch_reading_ease(x)
#             except (ValueError):
# 
#                 df.loc[row,'flesch_kincaid']=np.nan()
#                 nan_list.append(row)
#         else:
#             continue
# 
#     if len(nan_list)>0:
#         return nan_list

def add_reading_levels(df):
    for row,body in enumerate(df['body']):
        x = df['body'][row]
        df.loc[row,'flesch_kincaid']=textstat.flesch_kincaid_grade(x)
        df.loc[row,'fk_score']=textstat.flesch_reading_ease(x)
        #df.loc[row,'smog_index']=textstat.smog_index(x)
        df.loc[row,'gunning_fog']=textstat.gunning_fog(x)
        #df.loc[row,'difficult_words']=textstat.difficult_words(x)
        #df.loc[row,'text_standard']=textstat.text_standard(x)
    return df
def to_pickle(df,filename):
    return df.to_pickle(filename)

def load_pickle(file): 
    return pickle.load(file)

def del_rows():
    '''
    Get rid of rows where there was no body of text 
    '''
    delete = []
    for row,x in enumerate(articles['body']):
        if len(x)<2:
            print(row,x)
            delete.append(row)
    
    for x in delete:
        articles.drop(x,inplace=True)

    return articles.reset_index()


def add_year(df):
    '''
    Input: dataframe 
    Function Operation: Add a 'year' column denoting the year it was made
    '''
    df['year']=df.pub_date.apply(lambda x: int(x[:4]))
    return df 

def drop_not_digitized(df):
    '''
    Input: Dataframe 
    Output: Dataframe with rows where the articles have note been digitized removed 
    '''
    for row,x in enumerate(df['fk_score']):
        if x == 47.96:
            df.drop(row,inplace=True)
def del_rows():
    '''
    Get rid of rows where there was no body of text 
    '''
    delete = []
    for row,x in enumerate(articles['body']):
        if len(x)<2:
            print(row,x)
            delete.append(row)
    
    for x in delete:
        articles.drop(x,inplace=True)

    return articles.reset_index()    

def clean_authors(df):
    '''
    Adding columns for authors
    '''
    for row, x in enumerate(df['byline']):
        author = df['byline'][row]['original'][3:]
        df.loc[row,'author']=author
    
def count_plot(df):
    #df = articles
    sns.countplot(x="year",data=df)
    plt.show  

def remove_excess_years(df):
    '''
    Input: dataframe with all years 
    Output: datframe with strictly years that are a decade apart excluding 1967
    '''
    value_list=[2017,2007,1997,1987,1977,1957]
    new_df = df[df.year.isin(value_list)]
    #new_df.year.unique()  
    return new_df
# x = 'year' y = 'flesch_kincaid'
def vio_plot(x,y,df):
    # fig = plt.figure(figsize=(20,10))
    # ax = sns.violinplot(x=x, y=y, data=article_data)
    # plt.show()
    
    sns.set_style('whitegrid')
    fig = plt.figure(figsize=(30,20))
    ax = sns.violinplot(x='year',y='fk_score',data=new_df,palette='Set3')
    ax.axhline(y=30)#PhD
    ax.axhline(y=50)#College
    ax.axhline(y=70)#8th Grade
    ax.set_ylim(bottom=0,top=100)
    ax.tick_params('both',labelsize=30)
    ax.set_xlabel('Year',fontsize=30)
    ax.set_ylabel('Flesch_Kincaid', fontsize=30)
    ax.scatter(2017, 63.203, marker='o', color='white', s=30, zorder=3)
    #sns.set_style('whitegrid')
    #plt.plot(2017,63.2)
    plt.savefig('fk_violin.png')

if __name__=='__main__':
    load_pickle()
    start_mongo()
    clean_with_mongo()
    drop_columns(['_id','body','byline','document_type','headline','keywords','new_desk','print_page','pub_date','section_name','source','type_of_material','web_url','word_count'])