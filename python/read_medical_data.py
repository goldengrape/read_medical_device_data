
# coding: utf-8

# # 通用读取函数

# In[1]:


import pandas as pd
from pandas import DataFrame
import numpy as np
import os
import json
from dlm import dlmread, dlmread_df
from dlm import cellblock2num


# In[2]:


def max_column(catalog_dict):
    borders=[cellblock2num(v["location"])[3] for k,v in catalog_dict.items() ]
    return max(borders)+1


# In[3]:


def open_data_file(data_file,json_data_file):
    with open(json_data_file, 'r') as f:
        json_data = json.load(f)
    sep=json_data["sep"]
    catalog_dict=json_data["catalog"]
    max_col=max_column(catalog_dict)
    df=pd.read_csv(data_file,sep=sep,names=range(max_col),header=None)
    return df,catalog_dict


# In[4]:


def read_medical_data(data_file,catalog,json_data_file):
    df, catalog_dict=open_data_file(data_file,json_data_file)
    if type(catalog)==str:
        if catalog.lower() != "all":
            data=dlmread_df(df,catalog_dict[catalog]["location"],catalog_dict[catalog]["dtype"])
        elif catalog.lower() == "all":
            catalog=catalog_dict.keys()
            data={cat:dlmread_df(df,catalog_dict[cat]["location"],catalog_dict[cat]["dtype"]) for cat in catalog}
        elif type(catalog)==list:
            data={cat:dlmread_df(df,catalog_dict[cat]["location"],catalog_dict[cat]["dtype"]) for cat in catalog}
    return data
    


# In[5]:


def read_medical_data_one_by_one(data_file,catalog,json_data_file):
    '''
    从datafile中读取catalog所定义的数据块, 以pandas DataFrame的格式返回数据. 
    - datafile: 需要读取的数据文件, 例如"病人ID.csv"
    - catalog:  需要读取的数据块类型, 例如角膜地形图前表面数据"FRONT"
    - jsondatafile: 用于描述设备文件的json文件, 规定了每个类型所对应的数据块
    '''
    
    catalog_dict= pd.read_json(json_data_file,typ = 'series')
    with open(data_file,'rt') as f: 
#     if True:
#         f=data_file
        if type(catalog)==str:
            if catalog.lower() != "all":
                data=dlmread(f,';',catalog_dict[catalog])
            elif catalog.lower() == "all":
                catalog=catalog_dict.keys()
                data={cat:dlmread(f,';',catalog_dict[cat]) for cat in catalog}
        elif type(catalog)==list:
            data={cat:dlmread(f,';',catalog_dict[cat]) for cat in catalog}
    return data


# In[13]:


# 测试用: 
if __name__=="__main__" and True:
    dpath=os.path.join('..','testdata')
    dname='WAM5500.csv'

    datafilename=os.path.join(dpath,dname)

#     catalog='CornealThickness'
#     catalog=["TangentialAnterior","TangentialPosterior"]
    catalog='all'
    
    jpath=os.path.join("..","medical_device_data")
    jname="GrandSeikoWAM5500.json"
    jsonfilename=os.path.join(jpath,jname)
    data=read_medical_data(datafilename,catalog,jsonfilename)
    print(data["power"])

