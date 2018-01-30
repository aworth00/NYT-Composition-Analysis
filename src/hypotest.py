import numpy as np
import pandas as pd 
from statsmodels.stats.weightstats import ztest
from scipy.stats import ttest_ind
import itertools
from statsmodels.sandbox.stats.multicomp import multipletests

years = [2017,2007,1997,1987,1977,1957] 
comb = list(itertools.combinations(l,2))

_2017vs = [x for x in comb if 2017 in x]

# for x in _2017vs: 
# 
#     y2017= np.array(article_data.loc[article_data['year'] == x[0], 'flesch_kincaid'])[:3000]
#     y_test = np.array(article_data.loc[article_data['year'] == x[1], 'flesch_kincaid'])[:3000]
# 
#     if y2017.mean()>y_test.mean():
#         alt = 'larger'
#     else:
#         alt = 'smaller'
# 
#     ttest, pval = ztest(y2017,y_test,alternative=alt)
# 
#     print('H0: {} = {}'.format(x[0],x[1]))
#     print('H1: {} != {}'.format(x[0],x[1]))
#     print('{} mean flesch_kincaid {:0.3f}'.format(x[0],y2017.mean()))
#     print('{} mean flesch_kincaid {:0.3f}'.format(x[1],y_test.mean()))
#     print("Ztest = {:0.4f} and P-value = {}".format(ttest,pval))
#     print ('------------------------------------------------------------------------------------')


'''
UTILIZING THE SCIPY STATS TTEST_IND
'''

comb2 = list(itertools.combinations(new_df.year.unique(),2))
_2017vs = [x for x in comb if 2017 in x]
pval_list = []
for x in _2017vs: 
    
    #y2017= np.array(articles.loc[articles['year'] == x[0], 'fk_score'].sample(len(articles['year']==2017)))#[:3500]
    y2017= np.array(new_df.loc[articles['year'] == x[0], 'fk_score'])#[:3500]
    y_test = np.array(new_df.loc[articles['year'] == x[1], 'fk_score'])#[:3500]
    
    if y2017.mean()>y_test.mean():
        alt = 'larger'
    else:
        alt = 'smaller'
    
    ttest, pval = ttest_ind(y2017,y_test,equal_var=False)
    pval_list.append(pval)
    print('H0: {} = {}'.format(x[0],x[1]))
    print('H1: {} != {}'.format(x[0],x[1]))
    print('{} mean flesch_kincaid {:0.3f}'.format(x[0],y2017.mean()))
    print('{} mean flesch_kincaid {:0.3f}'.format(x[1],y_test.mean()))
    print("Ztest = {:0.4f} and P-value = {}".format(ttest,pval))
    print(multipletests(pval_list,.05,method='fdr_bh'))
    print("=====================================================")


