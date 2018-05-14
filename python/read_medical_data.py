
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


def read_medical_data_one_by_one(data_file,catalog,json_data_file):
    '''
    从datafile中读取category所定义的数据块, 以pandas DataFrame的格式返回数据. 
    - datafile: 需要读取的数据文件, 例如"病人ID.csv"
    - category:  需要读取的数据块类型, 例如角膜地形图前表面数据"FRONT"
    - jsondatafile: 用于描述设备文件的json文件, 规定了每个类型所对应的数据块
    '''
    
    catalog_dict= pd.read_json(json_data_file,typ = 'series')
    data=[]
    with open(data_file,'rt') as f: 
#     if True:
#         f=data_file
        if type(catalog)==str:
            if catalog.lower() != "all":
                data=dlmread(f,';',catalog_dict[catalog])
            elif catalog.lower() == "all":
                catalog=catalog_dict.keys()
                data={cat:dlmread(f,';',catalog_dict[cat]) for cat in catalog}
#         elif type(catalog)==list:
        else:
            print("list!")
            data={cat:dlmread(f,';',catalog_dict[cat]) for cat in catalog}
    return data


# In[5]:


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
#     else:
        data={cat:dlmread_df(df,category_dict[cat]["location"],category_dict[cat]["dtype"]) 
              for cat in category }
    return data
    


# In[6]:


# 测试用: 
if __name__=="__main__" and True:
    dpath=os.path.join('..','testdata')
    dname='HRT001.csv'

    datafilename=os.path.join(dpath,dname)

#     category='CornealThickness'
#     category=["TangentialAnterior","TangentialPosterior"]
    category=['DOB', 'sex', 'date', 'Asymmetry_data']
    
    jpath=os.path.join("..","medical_device_data")
    jname="HRT.json"
    jsonfilename=os.path.join(jpath,jname)
    data=read_medical_data(datafilename,category,jsonfilename)
#     print(data["OS_data"])


# # 根据分类文件读取数据文件序列

# * 分类文件class.csv: 
# 
# |class	|HRT	|humphrey|
# |:--|:--|:--|
# |OS_glaucoma	|HRT001.csv	|HFA001.csv|
# |OD_glaucoma	|HRT002.csv	|HFA002.csv|
# |OS_normal	|HRT003.csv	|HFA003.csv|
# |OD_normal	|HRT004.csv	|HFA004.csv|
# 
# 第一列说明分类, 可以是数字或字符, 可以有多个类别
# 
# 之后的列是不同检查的设备名称和文件列表. 设备仅支持带有json文件说明的 
# 

# * 数据类别选取文件analysis_catagory.csv, 
# 
# 需要用户手动编辑, 首行说明检查的设备, 每一列说明从每个检查设备数据文件提取的数据类别. 
# 
# |HRT|	humphrey|
# |:--|:--|
# |DOB	|DOB|
# |sex	|MD|
# |date	|data|
# |Asymmetry_data	|
# 

# * JSON字典: 
# 每种设备的JSON说明文件所在的位置

# In[7]:


def get_class_and_category_df(class_path,class_fname,category_path,category_fname,jpath):
    #读取分类文件
#     class_path=os.path.join('..','testdata')
#     class_fname="class.csv"
    classfilename=os.path.join(class_path,class_fname)
    class_df=pd.read_csv(classfilename)

    # 读取数据类别选取文件
#     category_path=class_path
#     category_fname="analysis_category.csv"
    category_filename=os.path.join(category_path,category_fname)
    category_df=pd.read_csv(category_filename)

    # jsonfile_dict:
#     jpath=os.path.join("..","medical_device_data")
    jname_dict={"HRT": os.path.join(jpath,"HRT.json"),
                "humphrey": os.path.join(jpath,"humphrey.json"),
                "GrandSeikoWAM5500": os.path.join(jpath,"GrandSeikoWAM5500.json"),
                "pentacam": os.path.join(jpath,"pentacam.json"),
                "sirius": os.path.join(jpath,"sirius.json")
               }
    return class_df,category_df,jname_dict


# ## 展开数据
# 每个数据应当展开成一列

# In[8]:


def flatten_data(data):
    data_list=[]
    for v in data.values():
        data_list+=(v.values.flatten().tolist())
    return data_list


# ## 取得数据集
# 数据集包括两部分, X和Y. 
# 
# * Y是标签数据, 也就是class.csv中class的那一列数据. 
# * X是每个数据文件中蕴含的所有数据, 排成一列. 

# In[9]:


def get_data(class_path,class_fname,category_path,category_fname,jpath):
    class_df,category_df,jname_dict= get_class_and_category_df(class_path,class_fname,category_path,category_fname,jpath)
    machine_list=class_df.columns[1:]
    X_data=[]
    for idx in range(len(class_df)):
#         class_data=class_df.loc[idx,"class"]
        row_data=[]
        for machine in machine_list:
        # machine="HRT"
            dname=class_df.loc[idx,machine]
            datafilename=os.path.join(dpath,dname)
            category=list(category_df[machine].dropna().values)
            jsonfilename=jname_dict[machine]
            mdata=read_medical_data(datafilename,category,jsonfilename)
            row_data+=flatten_data(mdata)
        X_data.append(row_data)
    X=pd.DataFrame(X_data).T
    Y=class_df["class"]
    return X,Y


# In[10]:


if __name__=="__main__":
    data_path=os.path.join('..','testdata')
    jpath=os.path.join("..","medical_device_data")
    X,Y=get_data(data_path,"class.csv",data_path,"analysis_category.csv",jpath)

