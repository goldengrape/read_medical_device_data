
# coding: utf-8

# # 读取角膜地形图

# 从数据文件中读取所需要的数据, 并转换成Pandas DataFrame的形式. 
# 
# Pandas DataFrame支持多种索引方式, 并且能够方便转换成numpy array进行运算. 

# ## 必要的函数库
# 
# * pandas: 常用数据读写处理的工具包, 如果未安装应考虑使用anaconda安装
# 

# In[1]:


import pandas as pd
# import numpy as np
from pandas import DataFrame, Series
import re
import os

# 仿照matlab构造了dlmread
from dlm import dlmread


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

# In[2]:


def read_sirius(filepath_or_buffer,catalog):
    # based on Sirius CSV
    catalog_dict={
        'Radii':'A2..AE2',
        'CornealThickness':'A4..IV34',
        'ElevationAnterior':'A36..IV66',
        'ElevationPosterior':'A68..IV98',
        'RefractiveEquivalentPower':'A100..IV130',
        'RefractiveFrontalPowerAnterior':'A132..IV162',
        'RefractiveFrontalPowerPosterior':'A164..IV194',
        'SagittalAnterior':'A196..IV226',
        'SagittalPosterior':'A228..IV258',
        'TangentialAnterior':'A260..IV290',
        'TangentialPosterior':'A292..IV322',
    }
    # read CSV with dlmread
    data=dlmread(filepath_or_buffer,';',catalog_dict[catalog])
    
    return data


# In[3]:


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

# In[4]:


def read_pentacam(filepath_or_buffer,catalog):
    # based on pentaCam CSV
    catalog_dict={
        'FRONT':'B2..EL142',
        'BACK':'B144..EL284',
        'Cornea':'B313..B317',
        'Pachy':'B318..B321',
        'Chamber':'B322..B323',
        'K':'B327..B329',
        'Pupil':'B332..B334',
        'X':'A337..A592',
        'Y':'B337..B592',
    }
    # read CSV with dlmread
    data=dlmread(filepath_or_buffer,';',catalog_dict[catalog])
    return data


# In[5]:


# 测试用: 
if __name__=="__main__" and True:
    fpath=os.path.join('..','testdata')
    fname='pentacam.csv'
    filename=os.path.join(fpath,fname)
    catalog='Pupil'
#     catalog='Cornea'
#     catalog='FRONT'

    data=read_pentacam(filename,catalog)
    
    print(data)
    print(data.shape)

