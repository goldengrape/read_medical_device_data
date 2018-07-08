
# coding: utf-8

# # 提取Octopus视野数据

# ## 设定文件路径参数

# In[1]:


if __name__=="__main__":
    input_path='../../testdata/Octopus'
    output_path="../../testdata/Octopus"
    fname="20170406动态视野(Octopus) .pdf" # for test


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
    from pdfminer.image import ImageWriter
except:
    get_ipython().system('conda install pdfminer.six --yes')
    from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
    from pdfminer.pdfpage import PDFPage
    from pdfminer.converter import XMLConverter, HTMLConverter, TextConverter
    from pdfminer.layout import LAParams
    from pdfminer.image import ImageWriter


# # 读取原始数据

# 使用导出成html文本的方式, 将PDF文件中的每一个字符定位后导出.
# 由于对字符位置高度依赖, 所以文件必须以A4形式导出.

# In[3]:


def pdf_prepare(input_path,fname):
    filename=os.path.join(input_path,fname)
    fp = open(filename, 'rb')
    rsrcmgr = PDFResourceManager()
    retstr = io.BytesIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = HTMLConverter(rsrcmgr, retstr, codec=codec, layoutmode="exact", laparams=laparams)
    # Create a PDF interpreter object.
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    # Process each page contained in the document.
    all_pages=[p for p in PDFPage.get_pages(fp)]
    pdftool=(interpreter,retstr)
    return pdftool, all_pages

def pdf_parser(pdftool, page):
    interpreter,retstr=pdftool
    interpreter.process_page(page)
    txt_string =  retstr.getvalue()
    return  txt_string.decode("utf-8")


# In[4]:


pdftool, all_pages=pdf_prepare(input_path,fname)
txt_data=pdf_parser(pdftool, all_pages[1])


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


# In[6]:


char_df= get_all_char(txt_data)
# char_df1= get_all_char(txt_data[1])


# 从一个box内取出所包含的字符, 并拼接成字符串

# In[7]:


def char_in_box(box, df):
    '''
    读取box范围内的字符, 并且拼接成字符串
    '''
    x0,y0,dx,dy=(int(u) for u in box)
    part=(df.where((df["X"]>x0) & (df["X"]<x0+dx) & 
                   (df["Y"]>y0) & (df["Y"]<y0+dy) )
            .dropna())
    return "".join(part["V"].tolist())


# In[8]:


location_dict={
    "name and birthday":(50,130,200,50), # 有不同的检查方式, 位置需要有一定的冗余
    "Eye and exam date time in G Standard":(50,175,200,20), # 有不同的检查方式, 后面再切换
    "Eye and exam date time in LVC Standard":(50,175,200,30), # 简单粗暴有效
    "Programs":(120,700,130,4),
    "RF":(300,720,100,10),
    "Pupil":(100,745,100,10),   
    "MS":(507,710,50,10),
    "MD":(507,720,50,10),
    "sLV":(507,720,50,10),
}


# In[9]:


for k,v in location_dict.items():
    print("{} : {}".format(k,char_in_box(v,char_df)))


# In[10]:


value_c_x=450-5
value_c_y=295-5
value_location=[
#     (371,216,164,164), # 最大范围
#     (value_c_x,value_c_y,10,10), # 中心
#     (value_c_x-5,value_c_y-5,10,10), # 顺时针渐开螺线, 第一圈
#     (value_c_x+5,value_c_y-5,10,10),
#     (value_c_x+5,value_c_y+5,10,10), 
#     (value_c_x-5,value_c_y+5,10,10), 
    (value_c_x-10,value_c_y-10,10,10), #第2圈
    (value_c_x+15,value_c_y-10,10,10),
    (value_c_x+15,value_c_y+10,10,10),
    (value_c_x-10,value_c_y+10,10,10),

]

for loc in value_location:
    print(char_in_box(loc,char_df))

