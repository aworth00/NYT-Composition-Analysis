import numpy as np
import pandas as pd 

from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import make_pipeline

'''
Example -- df_17 is a cleaned pandas df, which is strictly articles within 
2017
'''
#X_train, X_test, y_train, y_test = train_test_split(df_17['body'], df_17['new_desk'], test_size=0.30, random_state=42)

model = MultinomialNB()
vec = TfidfVectorizer()

train_mod = make_pipeline(vec,model)
train_mod.fit(X_train,y_train)
train_mod.predict_proba(X_test)
y_pred = train_mod.predict(X_test)

print(train_mod.score(y_pred,y_test))

