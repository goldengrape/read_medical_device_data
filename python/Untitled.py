
# coding: utf-8

# In[5]:


import pandas as pd
def fooA():
    with open("../testdata/ragged.csv", 'rt') as f:
        x0 = pd.read_csv(f,header=None,nrows=2)
        f.seek(0)
        x1= pd.read_csv(f,header=None,skiprows=2,nrows=2)
    return x0,x1
def fooB():
    x0 = pd.read_csv("../testdata/ragged2.csv",header=None,nrows=2)
    x1 = pd.read_csv("../testdata/ragged2.csv",header=None,skiprows=2,nrows=2)
    return x0,x1
def fooC():
    x=pd.read_csv("../testdata/ragged3.csv",header=None,names=range(4))
    x0=x.iloc[:2,:3]
    x1=x.iloc[2:,:]
    return x0,x1


# In[2]:


get_ipython().run_line_magic('timeit', '[fooA() for i in range(100)]')


# In[3]:


get_ipython().run_line_magic('timeit', '[fooB() for i in range(100)]')


# In[4]:


get_ipython().run_line_magic('timeit', '[fooC() for i in range(100)]')


# In[6]:


x=pd.read_csv("../testdata/ragged3.csv",header=None,names=range(4))
x


# In[13]:


x.iloc[0:None,1:2]


# In[38]:


x=pd.Series([1, "2", "   "]).astype(dtype="str").str.strip()
x[0]

