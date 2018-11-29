
# coding: utf-8

# # 根据位置提取PDF文件信息

# ## 设定文件路径参数

# In[1]:


if __name__=="__main__":
#     input_path='../../testdata/Octopus'
#     output_path="../../testdata/Octopus"
#     fname="20170406动态视野(Octopus) .pdf"
#     info_location_path='../../medical_device_data/'
#     info_fname="octopus_location.csv"
#     #pageno=0 # for test
    
    input_path='../../testdata/Humphrey'
    output_path="../../testdata/Humphrey"
    fname="huangzeyuan13.pdf"
    info_location_path='../../medical_device_data/'
    info_fname="humphrey_basic_location.csv"
    page_number=0


# ## 导入依赖包

# .2  导入依赖包
# 在使用notebook.azure.com在线运行时, 由于默认没有安装pdfminer.six这个包, 所以在首次运行时需要安装, 已经将安装代码加入

# 在使用notebook.azure.com在线运行时, 由于默认没有安装pdfminer.six这个包, 所以在首次运行时需要安装, 已经将安装代码加入到下面导入依赖包的代码内, 因此首次运行时速度会较慢. 
# 
# 同时, 在使用notebook.azure.com在线运行时, 服务器端不会保存曾经安装过的包, 因此在1小时没有操作之后, 服务器会关闭, 再次打开时就已经丢失了之前安装的包, 相当于首次运行. m

# In[2]:


import sys
import os
import os.path
import io
import re
import pandas as pd
from pandas import Series,DataFrame
import numpy as np
from collections import OrderedDict

try:
    from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
    from pdfminer.pdfpage import PDFPage
    from pdfminer.converter import XMLConverter, HTMLConverter, TextConverter
    from pdfminer.layout import LAParams
    from pdfminer.image import ImageWriter
    import numba

except:
    get_ipython().system('conda install pdfminer.six --yes')
    from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
    from pdfminer.pdfpage import PDFPage
    from pdfminer.converter import XMLConverter, HTMLConverter, TextConverter
    from pdfminer.layout import LAParams
    from pdfminer.image import ImageWriter
    get_ipython().system('conda install numba --yes')


# # 读取原始数据

# 使用导出成html文本的方式, 将PDF文件中的每一个字符定位后导出.
# 由于对字符位置高度依赖, 所以文件必须以A4形式导出.

# In[3]:


def get_pdf_page(input_path,fname):
    '''
    取得页面个数
    '''
    filename=os.path.join(input_path,fname)
    fp = open(filename, 'rb')
    return len([p for p in PDFPage.get_pages(fp)])


# In[4]:


def pdf_parser(input_path,fname,page_number):
    '''
    取得转换为html的字符
    '''
    filename=os.path.join(input_path,fname)
    fp = open(filename, 'rb')
    rsrcmgr = PDFResourceManager()
    retstr = io.BytesIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = HTMLConverter(rsrcmgr, retstr, 
                           codec=codec, layoutmode="exact", laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    all_pages=[p for p in PDFPage.get_pages(fp)]
    interpreter.process_page(all_pages[page_number]) # 无法分成多个函数处理, 目前只能重新读取并处理
    txt_string =  retstr.getvalue()
    retstr.truncate(0)
    return  txt_string.decode("utf-8")


# 每个字符的位置

# In[5]:


def get_all_char(txtdata):
    span_left='<span style="position:absolute; color:black; left:(\d+)px; top:(\d+)px; font-size:\d+px;">'
    span_right="</span>"
    value=re.findall(span_left+"([\s\S]+?)"+span_right, txtdata)
    char_df=DataFrame(value, columns=["X","Y","V"])
    char_df["X"]=char_df["X"].astype(int);
    char_df["Y"]=char_df["Y"].astype(int);
    return char_df


# 从一个box内取出所包含的字符, 并拼接成字符串

# In[6]:


def char_in_box(box, df):
    '''
    读取box范围内的字符, 并且拼接成字符串
    '''
    x0,y0,dx,dy=(int(u) for u in box)
    part=(df.where((df["X"]>x0) & (df["X"]<x0+dx) & 
                   (df["Y"]>y0) & (df["Y"]<y0+dy) )
            .dropna())
    return "".join(part["V"].tolist())


# # 读取位置信息文件

# In[7]:


def read_data_from_location(input_path, fname, info_location_path, info_fname, page_number):
    txt_data=pdf_parser(input_path,fname,page_number)
    c_df=get_all_char(txt_data)
    info_loc_df=pd.read_csv(os.path.join(info_location_path, info_fname))
    df_dict=OrderedDict()
    for index, row in info_loc_df.iterrows():
        df_dict[row[0]]=(char_in_box((row.left, row.top, row.width, row.height),c_df ))
    df=DataFrame(df_dict, index=[0]).T.reset_index()
    df.columns=["item_name","string_value"]
    return df


# ## 处理目录

# In[8]:


def treat_folder(input_path, fname, info_location_path, info_fname):
    pdffiles = [name for name in os.listdir(input_path)
            if name.endswith('.pdf')]
    df=DataFrame()

    for fname in pdffiles:
        newdf=read_data_from_location(input_path, fname, info_location_path, info_fname, 0)
        df=df.append(newdf, sort=False)
        print(os.path.join(input_path,fname)+" Done!")
    return df


# In[9]:


if __name__=="__main__":
    import timeit
    start_time = timeit.default_timer()
    treat_folder(input_path, fname, info_location_path, info_fname)
    elapsed = timeit.default_timer() - start_time
    print(elapsed)

