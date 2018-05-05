
# coding: utf-8

# # 通用读取函数

# In[16]:


import pandas as pd
from pandas import DataFrame
import os
from dlm import dlmread


# In[19]:


def read_medical_data(data_file,catalog,json_data_file):
    '''
    从datafile中读取catalog所定义的数据块, 以pandas DataFrame的格式返回数据. 
    - datafile: 需要读取的数据文件, 例如"病人ID.csv"
    - catalog:  需要读取的数据块类型, 例如角膜地形图前表面数据"FRONT"
    - jsondatafile: 用于描述设备文件的json文件, 规定了每个类型所对应的数据块
    '''
    
    catalog_dict= pd.read_json(json_data_file,typ = 'series')
    data=dlmread(data_file,';',catalog_dict[catalog])
    return data


# In[20]:


# 测试用: 
if __name__=="__main__" and True:
    dpath=os.path.join('..','testdata')
    dname='sirius.csv'
    datafilename=os.path.join(dpath,dname)
    catalog='CornealThickness'
    
    jpath=os.path.join("..","medical_device_data")
    jname="sirius.json"
    jsonfilename=os.path.join(jpath,jname)
    
    data=read_medical_data(datafilename,catalog,jsonfilename)
    print(data)

