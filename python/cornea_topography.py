
# coding: utf-8

# # 读取角膜地形图

# 从数据文件中读取所需要的数据, 并转换成Pandas DataFrame的形式. 
# 
# Pandas DataFrame支持多种索引方式, 并且能够方便转换成numpy array进行运算. 

# ## 必要的函数库
# 
# * pandas: 常用数据读写处理的工具包, 如果未安装应考虑使用anaconda安装
# 

# In[6]:


import pandas as pd
# import numpy as np
from pandas import DataFrame, Series
import re
import os


# # 构造工具
# 

# ## 构造dlmread
# 仿照MatLab里面的dlmread
# ```matlab
# M = dlmread(filename,delimiter,[R1 C1 R2 C2])
# ```
# 注意其中行列数字按照excel表格中的形式写, 首行=1, 首列=1. 否则一个大的表格数起来太麻烦了. 

# In[78]:


def dlmread(filename,delimiter,R1,C1,R2,C2,header=None):
    s=range(R1-1)
    n=R2-R1+1
    cols=range(C1-1,C2)
    data=pd.read_csv(filename,
                     sep=delimiter,
                     skiprows=s,
                     nrows=n,
                     header=header,
                     usecols=cols
                    )
    return data


# In[97]:


# 测试用, 测试开关使用and True: 
if __name__=="__main__" and True:
    fpath=os.path.join('..','testdata')
    fname='standard.csv'
    filename=os.path.join(fpath,fname)
    standard_data=pd.read_csv(filename,header=None,sep=';')
    data=dlmread(filename,';',1,2,4,2,header=None)
    print("原始表格")
    print(standard_data)
    print("部分读取")
    print(data)

    fname='pentacam.csv'
    filename=os.path.join(fpath,fname)
    data=dlmread(filename,';',313,1,317,2,header=None)
    print(data)


# ## 翻译单元格位置
# 比如给定A1, 应返回R=1,C=1

# In[103]:


def col_to_num(col_str):
    """ Convert base26 column string to number. """
    expn = 0
    col_num = 0
    for char in reversed(col_str):
        col_num += (ord(char) - ord('A') + 1) * (26 ** expn)
        expn += 1

    return col_num
def cell2num(cellname):
    col_letter="".join(re.findall('[A-Z][a-z]*',cellname))
    col=col_to_num(col_letter)
    row="".join(re.findall('[0-9]*',cellname))
    return (row,col)
    


# In[108]:


# 测试用, 测试开关使用and True: 
if __name__=="__main__" and True:
    (r,c)=cell2num('AA1')
    print("({0},{1})".format(r,c))


# ## 翻译单元格范围
# 例如: A1..B5->[1,1,5,2]

# In[113]:


def cell_block(cell_string):
    cell_name=re.split('\..',cell_string)
    (r1,c1)=cell2num(cell_name[0])
    (r2,c2)=cell2num(cell_name[1])
    return(r1,c1,r2,c2)    


# In[114]:


(r1,c1,r2,c2)=cell_block('A1..B5')
print("({0},{1},{2},{3})".format(r1,c1,r2,c2))


# ## 读取 Sirius  角膜地形图

# Sirius 角膜地形图. 数据存储为CSV文件. 
# 除Radii数据之外, 其他数据的描述以极座标方式描述角膜, 每一类数据共31行, 256列. 
# 
# read_sirius函数需要两个参数: 
# * filepath_or_buffer:  一般来说是文件名
# * catalog:  需要获取的数据类别. 包含的类别有: 
#   * 'Radii'                        
#   * 'CornealThickness'              
#   * 'ElevationAnterior'
#   * 'ElevationPosterior'
#   * 'RefractiveEquivalentPower'
#   * 'RefractiveFrontalPowerAnterior'
#   * 'RefractiveFrontalPowerPosterior'
#   * 'SagittalAnterior'
#   * 'SagittalPosterior'
#   * 'TangentialAnterior'
#   * 'TangentialPosterior'
#   
# ** 务必注意类别名称的大小写 **
# 

# In[7]:


def read_sirius(filepath_or_buffer,catalog):
    # based on Sirius CSV
    catalog_dict={
        'Radii':                           [2,1,],
        'CornealThickness':                {"skiprows":3, "nrows":31},
        'ElevationAnterior':               {"skiprows":35, "nrows":31},
        'ElevationPosterior':              {"skiprows":67, "nrows":31},
        'RefractiveEquivalentPower':       {"skiprows":99, "nrows":31},
        'RefractiveFrontalPowerAnterior':  {"skiprows":131, "nrows":31},
        'RefractiveFrontalPowerPosterior': {"skiprows":163, "nrows":31},
        'SagittalAnterior':                {"skiprows":195, "nrows":31},
        'SagittalPosterior':               {"skiprows":227, "nrows":31},
        'TangentialAnterior':              {"skiprows":259, "nrows":31},
        'TangentialPosterior':             {"skiprows":291, "nrows":31}
    }
    # extract skiprows and nrows from dict
    s=catalog_dict[catalog]["skiprows"]
    n=catalog_dict[catalog]["nrows"]
    
    # read CSV after skiprows and get nrows
    sirius_data=pd.read_csv(filepath_or_buffer,
                        skiprows=range(s),
                        header=None,
                        nrows=n,
                        sep=';')
    
    # delete the last column. Is there any better method?
    last_column_name= sirius_data.columns[-1]
    del sirius_data[last_column_name]
    
    return sirius_data


# In[8]:


# 测试用: 
if __name__=="__main__" and True:
    fpath=os.path.join('..','testdata')
    fname='sirius.csv'
    filename=os.path.join(fpath,fname)
    catalog='CornealThickness'
    data=read_sirius(filename,catalog)
    
    print(data)


# ## 读取PentaCam角膜地形图数据

# PentaCam 角膜地形图. 数据存储为CSV文件. 
# 
# * Front, Back以二维矩阵形式存储直角座标位置数据, 分别141行, 141列 
# * 其他数据一般标题在第一列, 数据放在第二列. 看起来非常凌乱. 于是读取很费力. 
# * 格式这么难看, 德国人真的好意思? ? ? 
# 
# read_pentacam函数需要两个参数: 
# * filepath_or_buffer:  一般来说是文件名
# * catalog:  需要获取的数据类别. 包含的类别有: 
#   * 'FRONT'
#   * 'BACK'
#   * 'Cornea'
#   * 'Pachy'
#   * 'Chamber'
#   * 'K'
#   * 'Pupil'
#   
# ** 务必注意类别名称的大小写 **
# 
# 列索引目前需要用字符串, 例如'7.000'

# In[46]:


def read_pentacam(filepath_or_buffer,catalog):
    # based on Sirius CSV
    catalog_dict={
        'FRONT':{"skiprows":0, "nrows":141, "header":0, "keepCol":141,"new_col_name":[]},
        'BACK':{"skiprows":142, "nrows":141, "header":0,"keepCol":141,"new_col_name":[]},
        'Cornea':{"skiprows":311, "nrows":4, "header":None,"keepCol":1,"new_col_name":['value']},
        'Pachy':{"skiprows":316, "nrows":4, "header":None,"keepCol":1,"new_col_name":['value']}, 
        'Chamber':{"skiprows":320, "nrows":2, "header":None,"keepCol":1,"new_col_name":['value']}, 
        'K':{"skiprows":325, "nrows":3, "header":None,"keepCol":1,"new_col_name":['value']},
        # 下面这个我也不知道为什么,329,330我都已经测试过了, header也试过不同的
        'Pupil':{"skiprows":328, "nrows":4, "header":0,"keepCol":1,"new_col_name":['value']} 
    }
    # extract skiprows and nrows from dict
    s=catalog_dict[catalog]["skiprows"]
    n=catalog_dict[catalog]["nrows"]
    h=catalog_dict[catalog]["header"]
    k=catalog_dict[catalog]["keepCol"]
    newname=catalog_dict[catalog]["new_col_name"]
    
    # read CSV after skiprows and get nrows
    pentacam_data=pd.read_csv(filepath_or_buffer,
                        skiprows=range(s),
                        header=h,
                        nrows=n,
                        sep=';'
                             )
    # set index and index name
    first_column_name= pentacam_data.columns[0]
    pentacam_data.set_index(first_column_name,inplace=True)
    pentacam_data.index.name=''
    
    # keep columns
    pentacam_data=pentacam_data.iloc[:,range(k)]
    
    # change column name
    newnameDict=dict(zip(pentacam_data.columns,newname))
    pentacam_data.rename(columns=newnameDict,inplace=True)    
    return pentacam_data


# In[50]:


# 测试用: 
if __name__=="__main__" and False:
    fpath=os.path.join('..','testdata')
    fname='pentacam.csv'
    filename=os.path.join(fpath,fname)
    catalog='Pupil'
#     catalog='Cornea'
    catalog='FRONT'

    data=read_pentacam(filename,catalog)
    
    print(data)
    print(data.shape)


# In[ ]:





# In[ ]:




