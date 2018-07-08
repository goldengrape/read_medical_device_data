
# coding: utf-8

# # 提取Octopus视野数据

# ## 设定文件路径参数

# In[15]:


if __name__=="__main__":
    input_path='../../testdata/Octopus'
    output_path="../../testdata/Octopus"
    fname="20130106动态视野(Octopus) .pdf" # for test


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


# In[102]:


filename=os.path.join(input_path,"o1.html")
with open(filename, 'rt') as f:
    data = f.read()


# In[142]:


span_left='<span style="position:absolute; color:black; left:(\d+)px; top:(\d+)px; font-size:\d+px;">'
span_right="</span>"
value=re.findall(span_left+"([\s\S]+?)"+span_right, data)
d1=DataFrame(value, columns=["X","Y","V"])
d1["X"]=d1["X"].astype(int);
d1["Y"]=d1["Y"].astype(int);


# In[141]:


block_span='<span style="position:absolute; border: black 1px solid; left:(\d+)px; top:(\d+)px; width:(\d{3})px; height:(\d{3})px;"></span>'
block=re.findall(block_span,data)


# In[139]:


def char_in_box(box, df):
    x0,y0,dx,dy=(int(u) for u in box)
    part=(df.where((df["X"]>x0) & (df["X"]<x0+dx) & 
                   (df["Y"]>y0) & (df["Y"]<y0+dy) )
            .dropna())
    return "".join(part["V"].tolist())


# In[140]:


char_in_box(block[1], d1)

