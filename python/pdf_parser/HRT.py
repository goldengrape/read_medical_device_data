
# coding: utf-8

# # 提取HRT数据
# ## 设定文件路径参数

# In[1]:


if __name__=="__main__":
    input_path='../../testdata/HRT'
    output_path="../../testdata/HRT"
    fname="HRT.pdf"


# ## 导入依赖包

# In[2]:


import sys
import os
import os.path

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import XMLConverter, HTMLConverter, TextConverter
from pdfminer.layout import LAParams
import io
import re
import pandas as pd
from pandas import Series,DataFrame

import numpy as np
from functools import reduce


# # 读取原始数据

# In[3]:


def pdfparser(input_path,fname):
    filename=os.path.join(input_path,fname)
    fp = open(filename, 'rb')
    rsrcmgr = PDFResourceManager()
    retstr = io.StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    # Create a PDF interpreter object.
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    # Process each page contained in the document.

    for page in PDFPage.get_pages(fp):
        interpreter.process_page(page)
        txt_string =  retstr.getvalue()

    return txt_string


# # 提取数据

# In[4]:


def extract_df(txt_str, pattern, data_index):
    info=list( re.findall(pattern,txt_str)[0])
    return DataFrame(info, index=data_index)
def common_pattern():
    global sth,float_number,p_hospital,p_name,p_DOB,p_ID,p_exam,p_diagnosis,p_comment,p_report
    global p_OCT_Q,p_sex,p_radius,p_T,p_N,p_S,p_I,p_ISNT
    sth="([\s\S]*?)"
    float_number="(\-*\d*\.*\d+?)"
    p_hospital=p_name=p_DOB=p_ID=p_exam=p_diagnosis=p_comment=p_report=sth
    p_OCT_Q="\s(\d+)\s"
    p_sex="([F|M])"
    p_radius=p_T=p_N=p_S=p_I=float_number
    p_ISNT= "T"+p_T+            "N"+p_N+            "S"+p_S+            "I"+p_S+            "G"+float_number+"\((\d+)\)"+            "T"+float_number+"\((\d+)\)"+            "TS"+float_number+"\((\d+)\)"+            "TI"+float_number+"\((\d+)\)"+            "N"+float_number+"\((\d+)\)"+            "NS"+float_number+"\((\d+)\)"+            "NI"+float_number+"\((\d+)\)"


# In[5]:


def get_basic_info(txt_str):
    basic_info_pattern=p_hospital+        "Patient:"+p_name+        "DOB:"+p_DOB+        "Sex:"+p_sex+        "Patient ID:"+p_ID+        "Exam.:"+p_exam+        "Diagnosis:"+p_diagnosis+        "Comment:"+p_comment+        "Software Version:"+"[\s\S]*"+"Report OU"+        p_report+        "OS200"
    basic_info_index=["Hospital",
        "Patient",
        "DOB",
        "Sex",
        "Patient_ID",
        "Exam_date",
        "Diagnosis",
        "Comment",
        "Report"]
    return extract_df(txt_str, basic_info_pattern, basic_info_index)


# In[6]:


def get_Asymmetry_data(txt_str):
    Asymmetry_pattern="AsymmetryOD - OS"+        "T"+p_T+        "N"+p_N+        "S"+p_S+        "I"+p_I+        "G"+float_number+        "T"+float_number+        "TS"+float_number+        "TI"+float_number+        "N"+float_number+        "NS"+float_number+        "NI"+float_number+        "[\s\S]*"+        "TMPSUPNASINFTMPRNFL Thickness"
    Asymmetry_index=["Asymmetry_T", 
        "Asymmetry_N",
        "Asymmetry_S",
        "Asymmetry_I",
        "Asymmetry_G",
        "Asymmetry_T",
        "Asymmetry_TS",
        "Asymmetry_TI",
        "Asymmetry_N",
        "Asymmetry_NS",
        "Asymmetry_NI"]
    return extract_df(txt_str, Asymmetry_pattern, Asymmetry_index)


# In[7]:


def get_ISNT_data(txt_str):
    OS_ISNT_pattern="OS200"+'[\s\S]*?'+p_radius+"\-*\d*\.*\d*?"+        "IR 30° ART \[HS\]"+"ILMILM"+"RNFLRNFL200"+'[\s\S]*?'+        "OCT Q:"+p_OCT_Q+        "\[HS\]TMPSUPNASINFTMPRNFL Thickness"+'[\s\S]*?'+        "Position"+'[\s\S]*?'+"\d+"+        p_ISNT+        "Classification OS"
    OD_ISNT_pattern=OS_ISNT_pattern.replace("OS","OD")
    OS_ISNT_index=[        
        "OS_radius",
        "OS_OCT Q",
        "OS_T",
        "OS_N",
        "OS_S",
        "OS_I",
        "OSR_G",
        "OSR_G_ref",
        "OSR_T",
        "OSR_T_ref",
        "OSR_TS",
        "OSR_TS_ref",
        "OSR_TI",
        "OSR_TI_ref",
        "OSR_N",
        "OSR_N_ref",
        "OSR_NS",
        "OSR_NS_ref",
        "OSR_NI",
        "OSR_NI_ref",]
    OD_ISNT_index=[OS.replace("OS","OD") for OS in OS_ISNT_index]
    OS_ISNT_data=extract_df(txt_str, OS_ISNT_pattern, OS_ISNT_index)
    OD_ISNT_data=extract_df(txt_str, OD_ISNT_pattern, OD_ISNT_index)
    return pd.concat([OS_ISNT_data,OD_ISNT_data])


# In[8]:


def get_Classification_data(txt_str):
    Classification_pattern="Classification OS"+sth+        "OD200"+"[\s\S]*?"+        "Classification OD"+sth+        "Asymmetry"
    Classification_index=["Classification OS","Classification OD"]
    return extract_df(txt_str, Classification_pattern,Classification_index)
    


# # 合并

# In[9]:


def get_HRT_df(input_path,fname):
    txt_str=pdfparser(input_path,fname)
    common_pattern()
    basic_info=get_basic_info(txt_str)
    ISNT_data=get_ISNT_data(txt_str)
    Asymmetry_data=get_Asymmetry_data(txt_str)
    Classification_data=get_Classification_data(txt_str)
    df=pd.concat([basic_info,ISNT_data,Asymmetry_data,Classification_data])
    df.columns=['Value']
    return df


# # 保存数据

# In[16]:


def get_out_name(output_path,fname):
    return os.path.join(output_path,"csv", "{}.csv".format(os.path.splitext(fname)[0]))

def save_to_csv(df,output_path,fname):
    df.to_csv(get_out_name(output_path,fname),sep=',',header=False)
    
    return True


# # 处理目录

# In[23]:


def convert_folder(input_path,output_path):
    pdffiles = [name for name in os.listdir(input_path)
            if name.endswith('.pdf')]

    df_list=[]
    for fname in pdffiles:
        print("Convert PDF file {} to CSV".format(fname))
        df=get_HRT_df(input_path,fname)
        save_to_csv(df,output_path,fname)
        print("done")

        df_list.append(df)
    print("Merge together")
    df_merged = reduce(lambda left,right: pd.merge(left,right,left_index=True,right_index=True), df_list)
    save_to_csv(df_merged,output_path,"together.csv")
    print("done")


        


# In[24]:


if __name__=="__main__":
    convert_folder(input_path,output_path)


# In[ ]:




