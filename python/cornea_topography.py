
# coding: utf-8

# # 读取角膜地形图

# ## 必要的函数库

# In[1]:


import pandas as pd
from pandas import DataFrame, Series
import re
import os


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

# In[58]:


def read_sirius(filepath_or_buffer,catalog):
    # based on Sirius CSV
    catalog_dict={
        'Radii':                           {"skiprows":1, "nrows":1},
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


# In[61]:


# 测试用: 
if __name__=="__main__" and False:
    fpath=os.path.join('..','testdata')
    fname='sirius.csv'
    filename=os.path.join(fpath,fname)
    catalog='CornealThickness'
    data=read_sirius(filename,catalog)
    
    print(data)


# In[ ]:




