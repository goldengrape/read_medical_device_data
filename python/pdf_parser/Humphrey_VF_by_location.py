
# coding: utf-8

# # 提取Humphrey视野数据
# 
# 使用新的方式重构

# # 设定文件路径参数

# In[1]:


if __name__=="__main__":
    input_path='../../testdata/Humphrey'
    output_path="../../testdata/Humphrey"
    fname="huangzeyuan13.pdf"
    info_location_path='../../medical_device_data/'
    info_basic_fname="humphrey_basic_location.csv"
    info_30_2_fname="humphrey_30-2_location.csv"
    info_24_2_fname="humphrey_24-2_location.csv"
    info_fname_dict={"basic": info_basic_fname, "30-2":info_30_2_fname, "24-2":info_24_2_fname}
#     fname="右眼-sfa_zh.pdf" # for test


# ## 导入依赖包

# 在使用notebook.azure.com在线运行时, 由于默认没有安装pdfminer.six这个包, 所以在首次运行时需要安装, 已经将安装代码加入到下面导入依赖包的代码内, 因此首次运行时速度会较慢. 
# 
# 同时, 在使用notebook.azure.com在线运行时, 服务器端不会保存曾经安装过的包, 因此在1小时没有操作之后, 服务器会关闭, 再次打开时就已经丢失了之前安装的包, 相当于首次运行. 

# In[2]:


import sys
import os
import os.path
import io
import re
import pandas as pd
from pandas import Series,DataFrame
import numpy as np

try:
    from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
    from pdfminer.pdfpage import PDFPage
    from pdfminer.converter import XMLConverter, HTMLConverter, TextConverter
    from pdfminer.layout import LAParams
except:
    get_ipython().system('conda install pdfminer.six --yes')
    from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
    from pdfminer.pdfpage import PDFPage
    from pdfminer.converter import XMLConverter, HTMLConverter, TextConverter
    from pdfminer.layout import LAParams


# ## 导入 PDF_parser_by_location 
# PDF_parser_by_location 中将所有PDF转换成带有html, 其中每个字符均有定位, 通过选取一个方框来对一个数据或者单词进行选择. 各个数据的定位数据放置在相应的csv文件中, 由info_lation_path和info_fname保存

# In[3]:


from PDF_parser_by_location import read_data_from_location, pdf_parser


# # 读取

# In[4]:


def read_one_Humphrey_data(input_path, fname, info_location_path, info_fname):
    page_number=0
    df=read_data_from_location(input_path, fname, info_location_path, info_fname, page_number)
    df=df.set_index("item_name")
    return df.T


# In[5]:


def get_humphrey_test_method(input_path, fname, info_location_path, info_fname_dict):
    df=read_one_Humphrey_data(input_path, fname, info_location_path, info_fname_dict["basic"])
    return df.Test.values[0]


# In[6]:


def get_full_humphrey_data(input_path, fname, info_location_path, info_fname_dict):
    humphrey_test_method=get_humphrey_test_method(input_path, fname, info_location_path, info_fname_dict)
    for key in info_fname_dict.keys():
        if key in humphrey_test_method: 
            info_fname=info_fname_dict[key]
    df=read_one_Humphrey_data(input_path, fname, info_location_path, info_fname)
    return df


# In[7]:


# if __name__=="__main__":
#     df=get_full_humphrey_data(input_path, fname, info_location_path, info_fname_dict)


# ## 处理目录

# In[32]:


if __name__=="__main__":

    pdffiles = [name for name in os.listdir(input_path)
            if name.endswith('.pdf')]
    df=DataFrame()
    for fname in pdffiles:
        newdf=get_full_humphrey_data(input_path, fname, info_location_path, info_fname_dict)
        df=df.append(newdf, sort=False)
        


# In[37]:


# df.iloc[:,24:34]
df
