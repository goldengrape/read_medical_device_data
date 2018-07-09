
# coding: utf-8

# # 提取Octopus视野数据

# ## 设定文件路径参数

# In[1]:


if __name__=="__main__":
    input_path='../../testdata/Octopus'
    output_path="../../testdata/Octopus"
    fname="20170316动态视野(Octopus) .pdf"
    #pageno=0 # for test


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


# # 提取相关信息

# 各个信息是基于字符位置进行提取的, 因此只要指定每个信息所在的位置box即可, 位置box的定义为(left, top, width, height)

# ## 提取基本信息
# 包含:
# "name", "birthday","exam_date","eye", "Programs_type", "RF","Pupil","MS","MD","sLV"

# In[7]:


def get_basic_info(char_df):
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
    Programs_type=char_in_box(location_dict["Programs"],char_df)
    if "G Standard" in Programs_type:
        Eye_and_exam_date_time=          char_in_box(location_dict["Eye and exam date time in G Standard"],char_df)
    elif "LVC Standard" in Programs_type:
        Eye_and_exam_date_time=         char_in_box(location_dict["Eye and exam date time in LVC Standard"],char_df)
#     print(Eye_and_exam_date_time.split("/"))
    eye, exam_date, exam_time =(x.strip() for x in Eye_and_exam_date_time.split("/"))
    
    name_and_birthday=char_in_box(location_dict["name and birthday"],char_df)
    name, birthday=(x.strip() for x in name_and_birthday.split(","))
    
    RF, Pupil, MS, MD, sLV=(char_in_box(location_dict[key],char_df)
        for key in ["RF","Pupil","MS","MD","sLV"])
    
    s=Series([name, birthday,exam_date+"/"+exam_time,eye, Programs_type,RF,Pupil,MS,MD,sLV ],
             index=["name", "birthday","exam_date","eye", "Programs_type",
                    "RF","Pupil","MS","MD","sLV"] )
    s.birthday=pd.to_datetime(s.birthday)
    s.exam_date=pd.to_datetime(s.exam_date)
    s.iloc[5:]=pd.to_numeric(s.iloc[5:])
    return s


# ## 提取视野的原始数据
# 数据从中心按照顺时针渐开线的方式排列成一维数组:
# 
# ![](https://i.loli.net/2018/07/08/5b421fb0a922a.png)
# 

# In[8]:


def get_VF_value(char_df):
    value_c_x=445
    value_c_y=290
    value_location=[
    #     (371,216,164,164), # 最大范围
        (value_c_x,value_c_y,10,10), # 中心

        (value_c_x+5,value_c_y+5,10,10), # 顺时针渐开螺线, 第1圈
        (value_c_x-5,value_c_y+5,10,10), 
        (value_c_x-5,value_c_y-5,10,10), 
        (value_c_x+5,value_c_y-5,10,10),
        ##第2圈
        (value_c_x+15,value_c_y+10,10,10),
        (value_c_x-10,value_c_y+10,10,10),
        (value_c_x-10,value_c_y-10,10,10), 
        (value_c_x+15,value_c_y-10,10,10),

        ##第3圈
        (value_c_x+25,value_c_y+5,10,10),
        (value_c_x+25,value_c_y+20,10,10), # 第3圈, 下横(从右到左)
        (value_c_x+10,value_c_y+20,10,10),
        (value_c_x-5,value_c_y+20,10,10),
        (value_c_x-20,value_c_y+20,10,10), # 第3圈, 左竖,从下到上
        (value_c_x-20,value_c_y+5,10,10),
        (value_c_x-20,value_c_y-5,10,10),
        (value_c_x-20,value_c_y-20,10,10), # 上横
        (value_c_x-5,value_c_y-20,10,10),
        (value_c_x+5,value_c_y-20,10,10),
        (value_c_x+25,value_c_y-20,10,10), #第3圈, 右竖
        (value_c_x+25,value_c_y-5,10,10),

        ## 第4圈,
        (value_c_x+40,value_c_y+10,10,10),
        (value_c_x+35,value_c_y+35,10,10),
        (value_c_x+15,value_c_y+35,10,10),
        (value_c_x-10,value_c_y+35,10,10), 
        (value_c_x-30,value_c_y+35,10,10),  
        (value_c_x-35,value_c_y+10,10,10),
        (value_c_x-35,value_c_y-10,10,10),
        (value_c_x-30,value_c_y-35,10,10),  
        (value_c_x-10,value_c_y-35,10,10), 
        (value_c_x+15,value_c_y-35,10,10),
        (value_c_x+35,value_c_y-35,10,10),
        (value_c_x+40,value_c_y-10,10,10),    

        # 第5圈
        (value_c_x+55,value_c_y+10,15,10),
        (value_c_x+55,value_c_y+30,10,10),
        (value_c_x+55,value_c_y+50,10,10),
        (value_c_x+35,value_c_y+50,10,10),
        (value_c_x+15,value_c_y+50,10,10),
        (value_c_x-10,value_c_y+50,10,10),
        (value_c_x-30,value_c_y+50,10,10),
        (value_c_x-50,value_c_y+50,10,10),
        (value_c_x-50,value_c_y+30,10,10),
        (value_c_x-55,value_c_y+10,15,10), # 左右眼略有差别, 宽度加大一些,增加冗余
        (value_c_x-55,value_c_y-10,15,10),
        (value_c_x-50,value_c_y-30,10,10), # 这圈好大
        (value_c_x-50,value_c_y-50,10,10), 
        (value_c_x-30,value_c_y-50,10,10),
        (value_c_x-10,value_c_y-50,10,10),
        (value_c_x+10,value_c_y-50,15,10),
        (value_c_x+30,value_c_y-50,15,10),
        (value_c_x+55,value_c_y-50,10,10),
        (value_c_x+55,value_c_y-30,10,10),
        (value_c_x+55,value_c_y-10,15,10),

        ## 最外8个
        (value_c_x+70,value_c_y+10,20,20),
        (value_c_x+20,value_c_y+70,20,20),
        (value_c_x-20,value_c_y+70,20,20),
        (value_c_x-80,value_c_y+15,20,20),
        (value_c_x-80,value_c_y-20,20,20),
        (value_c_x-20,value_c_y-70,10,10), 
        (value_c_x+20,value_c_y-70,20,10),  
        (value_c_x+70,value_c_y-20,20,20),
    ]
    VF_values=[(char_in_box(v,char_df).strip()) for v in value_location]
    VF_s=Series(VF_values)
    return pd.to_numeric(VF_s)


# # 处理单个文件

# In[9]:


def process_single_file(input_path,fname, output_path, save=False):
    print("process the file: ", os.path.join(input_path,fname))
    total_page=get_pdf_page(input_path,fname)
    series_list=[]
    for p_number in range(total_page):
        t_data=pdf_parser(input_path,fname,p_number)
        c_df= get_all_char(t_data)
        s1=get_basic_info(c_df)
        if "G Standard" in s1.Programs_type:
            s2=get_VF_value(c_df)
        else:
            s2=Series()
        s=pd.concat([s1, s2])
        series_list.append(s)
        if save:
            df=DataFrame(s)
            output_fname=os.path.join(output_path, 
                                      "{}_p{}.csv".format(os.path.splitext(fname)[0],p_number+1))
            df.to_csv(output_fname)
            print("save to "+output_fname)
    
    return series_list


# In[10]:


process_single_file(input_path,fname, output_path, save=True);


# # 处理目录

# In[11]:


def process_file_list(input_path, output_path, filename_list, save=False):
    series_list=[]
    for fname in filename_list:
        s_list=process_single_file(input_path,fname, output_path, save=save)
        for s in s_list:
            series_list.append(s)
    return DataFrame(series_list) 


# In[12]:


def process_folder(input_path, output_path, save_together=True, save_individual=False):
    pdffiles = [name for name in os.listdir(input_path)
            if name.endswith('.pdf')]
    df= process_file_list(input_path, output_path, pdffiles, save=save_individual)
    if save_together:
        df.to_csv(os.path.join(output_path, "octopus_data.csv"))
    print("DONE")
    return df


# # 保存数据

# In[13]:


if __name__=="__main__":    
    df=process_folder(input_path, output_path, save_together=True, save_individual=True)

