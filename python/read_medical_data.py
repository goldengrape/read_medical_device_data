
# coding: utf-8

# # 通用读取函数

# 根据每个设备的json描述文件, 读取csv数据文件中的数据. 
# 
# json描述文件: 
# ```json
# {"sep": csv文件的分隔符号
#  "category": 
#    {
#    "数据类1": {"location": 数据块位置, "dtype": 数据类型}, 
#    "数据类2": {"location": "A1..B3", "dtype": "numeric"}, 
#    ...
#    }
# }
# ```

# In[1]:


import pandas as pd
from pandas import DataFrame
import numpy as np
import os
import json
from dlm import dlmread, dlmread_df
from dlm import cellblock2num


# In[2]:


def max_column(category_dict):
    # 确定文件的最大列数. 
    # 形如
    # 1, 2, 3
    # 1, 2, 3, 4
    # 这样的csv文件, 直接读取会出错, 需要设定所有的列名
    borders=[cellblock2num(v["location"])[3] for k,v in category_dict.items() ]
    return max(borders)+1


# In[3]:


def open_data_file(data_file,json_data_file):
    with open(json_data_file, 'r') as f:
        json_data = json.load(f)
    sep=json_data["sep"]
    category_dict=json_data["category"]
    max_col=max_column(category_dict)
    df=pd.read_csv(data_file,sep=sep,names=range(max_col),header=None)
    return df,category_dict


# In[4]:


def read_medical_data(data_file,category,json_data_file):
    '''
    从datafile中读取category所定义的数据块, 以pandas DataFrame的格式返回数据. 
    - datafile: 需要读取的数据文件, 例如"病人ID.csv"
    - category:  需要读取的数据块类型, 例如角膜地形图前表面数据"FRONT"
    - jsondatafile: 用于描述设备文件的json文件, 规定了每个类型所对应的数据块
    如果提取的是多个数据块类型, 返回字典
    '''
    # 读取文件
    df, category_dict=open_data_file(data_file,json_data_file)
    # category可以是一个类别, 也可以是all描述为所有类别, 也可以是一个列表
    if type(category)==str:
        if category.lower() != "all": # 如果只是一个类别
            data=dlmread_df(df,category_dict[category]["location"],category_dict[category]["dtype"])
        elif category.lower() == "all": # 如果是all, 要提取所有类别
            category=category_dict.keys()
            data={cat:dlmread_df(df,category_dict[cat]["location"],category_dict[cat]["dtype"]) for cat in category}
        elif type(category)==list: 
            data={cat:dlmread_df(df,category_dict[cat]["location"],category_dict[cat]["dtype"]) for cat in category}
    return data
    


# In[5]:


def read_medical_data_one_by_one(data_file,catalog,json_data_file):
    '''
    从datafile中读取category所定义的数据块, 以pandas DataFrame的格式返回数据. 
    - datafile: 需要读取的数据文件, 例如"病人ID.csv"
    - category:  需要读取的数据块类型, 例如角膜地形图前表面数据"FRONT"
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


# In[18]:


# 测试用: 
if __name__=="__main__" and True:
    dpath=os.path.join('..','testdata',"HRT","csv")
    dname='HRT.csv'

    datafilename=os.path.join(dpath,dname)

#     category='CornealThickness'
#     category=["TangentialAnterior","TangentialPosterior"]
    category='all'
    
    jpath=os.path.join("..","medical_device_data")
    jname="HRT.json"
    jsonfilename=os.path.join(jpath,jname)
    data=read_medical_data(datafilename,category,jsonfilename)
    print(data["OS_data"])

