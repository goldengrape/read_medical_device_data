
# coding: utf-8

# # 提取Humphrey视野数据
# 
# 使用新的方式重构

# # 设定文件路径参数

# In[1]:


if __name__=="__main__":
    input_path='../../testdata/o2'
    output_path="../../testdata/o2"
    fname="dec_83\303\317\225F20131106\266\257\314\254\312\323\322\260(Octopus) .pdf"

    info_location_path='../../medical_device_data/'
    info_basic_fname="octopus_basic_location.csv"
    info_LVC_fname="octopus_LVC_location.csv"
    info_G_fname="octopus_G_location.csv"
    info_fname_dict={"basic": info_basic_fname, "LVC":info_LVC_fname, "G":info_G_fname}


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
import timeit

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


def get_pdf_page(input_path,fname):
    '''
    取得页面个数
    '''
    filename=os.path.join(input_path,fname)
    fp = open(filename, 'rb')
    return len([p for p in PDFPage.get_pages(fp)])


# In[5]:


def read_one_data(input_path, fname, info_location_path, info_fname,page_number):
    '''
    处理一页内容
    '''
    df=read_data_from_location(input_path, fname, info_location_path, info_fname, page_number)
    df=df.set_index("item_name")
    return df.T


# In[6]:


def get_test_method(input_path, fname, info_location_path, info_fname_dict, page_number):
    df=read_one_data(input_path, fname, info_location_path, info_fname_dict["basic"],page_number)
    return df.Programs.values[0]


# In[7]:


def get_full_data(input_path, fname, info_location_path, info_fname_dict, page_number):
    test_method=get_test_method(input_path, fname, info_location_path, info_fname_dict,page_number)
    for key in info_fname_dict.keys():
        if key in test_method: 
            info_fname=info_fname_dict[key]
    df=read_one_data(input_path, fname, info_location_path, info_fname, page_number)
    return df


# ## 清洗数据

# In[8]:


def clean_data(df):
    df["Name"]=df["name and birthday"].str.extract('([\s\S]+),').astype("str")
    df["Birthday"]=df["name and birthday"].str.extract('(\d+-\d+-\d+)').astype("str")
    df.drop("name and birthday", axis=1, inplace=True)
    
    df["Eye"]=df["Eye and exam date time"].str.extract('(O[D|S])').astype("str")
    df["Date"]=df["Eye and exam date time"].str.extract('(\d+-\d+-\d+)').astype("str")
    df["Time"]=df["Eye and exam date time"].str.extract('(\d+:\d+:\d+)').astype("str")
    df.drop("Eye and exam date time", axis=1, inplace=True)
    df["Refraction"]=df["Refraction"].astype("str")
    
    # re-order
    cols = df.columns
    t=np.asarray(["_value_" in x for x in cols])
    df.columns=np.concatenate([cols[~t],cols[t]])
    
    
#     df["patient"]=df["patient"].str.replace(",","")
#     df["date of birth"]=pd.to_datetime(df["date of birth"])
#     df["gender"]=(df["gender"]
#                   .str.replace("其他","Other")
#                   .str.replace("女性","Female")
#                   .str.replace("男性","Male")
#                  )
#     df["Date"]=pd.to_datetime(df["Date"])
#     # Fixation Losses不知为何有可能在excel里被解析成日期, 但csv以纯文本打开不会
#     df["Fixation Losses"]=df["Fixation Losses"].str.extract('(\d+\/\d+)').astype("str")
#     df["False POS Errors"]=df["False POS Errors"].str.extract('(\d+\%)').astype("str") 
#     df["False NEG Errors"]=df["False NEG Errors"].str.extract('(\d+\%)').astype("str")
#     df["Background"]=df["Background"].str.extract('(\-{,1}\d+\.{,1}\d*)').astype("float")
#     df["Pupil Diameter"]=df["Pupil Diameter"].str.extract('(\-{,1}\d+\.{,1}\d*)').astype("float")
    
#     # 将字符串转换为数字
#     # 带有最多一个负号, 跟至少一个数字, 带有最多一个小数点, 小数点后有或者没有数字
#     for col in df.iloc[:,24:]:
#         df[col]=df[col].str.extract('(\-{,1}\d+\.{,1}\d*)').astype("float") 
    return df


# ## 处理单个文件

# In[9]:


def deal_with_one_file(input_path, fname, info_location_path, info_fname_dict):
    pages=get_pdf_page(input_path,fname)
    df=DataFrame()
    for page_number in range(pages):
        newdf=get_full_data(input_path, fname, info_location_path, info_fname_dict,page_number)
        newdf=clean_data(newdf)
        df=df.append(newdf, sort=False)
    return df


# # 处理目录

# In[10]:


def deal_with_folder(input_path, fname, info_location_path, info_fname_dict):
    pdffiles = [name for name in os.listdir(input_path)
            if name.endswith('.pdf')]
    df=DataFrame()
    N=len(pdffiles)
    i=0
    start_time = timeit.default_timer()
    for fname in pdffiles:
        newdf=deal_with_one_file(input_path, fname, info_location_path, info_fname_dict)
        df=df.append(newdf, sort=False)
        print(os.path.join(input_path,fname)+" Done!")
        elapsed = timeit.default_timer() - start_time
        i+=1
        print(str(int(i/N*100))+"%")
        print("each file time ~={}sec".format(int(elapsed/i)))
        print("total time ~={}sec".format(int(elapsed/i*N)))
    return df


# In[11]:


if __name__=="__main__":
    df=deal_with_folder(input_path, fname, info_location_path, info_fname_dict)
    df.to_csv(os.path.join(output_path,"Octopus_data.csv"))

