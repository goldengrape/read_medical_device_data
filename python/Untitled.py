
# coding: utf-8

# In[21]:


import pandas as pd
my_cols = range(10)
x = pd.read_csv("../testdata/ragged.csv",names=my_cols).dropna(how='all',axis=1) 
x

