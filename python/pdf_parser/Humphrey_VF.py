
# coding: utf-8

# # 提取Humphrey视野数据

# ## 设定文件路径参数

# In[1]:


if __name__=="__main__":
    input_path='../../testdata/Humphrey'
    output_path="../../testdata/Humphrey"


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
        
    ori_df=DataFrame(re.split("\n",txt_string))
    ori_df.columns=["value"]

    return ori_df


# # 读取视野测量原始数据
# 
# 注意设定中英文和眼别

# In[4]:


def check_eye(ori_df):
    '''
    确认眼别, 返回"OD"或"OS"
    '''
    if (ori_df['value']
     .where(ori_df['value'].str.contains('^O[D|S] '))
     .dropna()
     .str.match("OD")
     .iloc[0]
    ):
        return "OD"
    elif (ori_df['value']
     .where(ori_df['value'].str.contains('^O[D|S] '))
     .dropna()
     .str.match("OS")
     .iloc[0]
    ):
        return "OS"
    
def get_version(ori_df):
    '''
    确认版本
    '''
    if ord(ori_df.iloc[0,0][0])<=ord('z'):
        return "en"
    elif ord(ori_df.iloc[0,0][0])>ord('z'):
        return "zh"
    
def reformat_vf_data(data,eye):
    data=data.where(data["value"]!="").dropna().replace("<0",-1).reset_index()["value"]

    OD_index  =np.asarray([0, 0, 0,24,32,40,48, 0, 0,
                           0, 0,17,25,33,41,49,57, 0,
                           0,10,18,26,34,42,50,58,66,
                           3,11,19,27,35,43,51,59,67,
                           4,12,20,28,36,44,52,60,68,
                           0,13,21,29,37,45,53,61,69,
                           0, 0,22,30,38,46,54,62, 0,
                           0, 0, 0,31,39,47,55, 0, 0]).reshape(8,9).T.reshape(-1)
    OS_index =np.asarray([  0,0,16,24,32,40,0,0,0,
                            0,9,17,25,33,41,49,0,0,
                            2,10,18,26,34,42,50,58,0,
                            3,11,19,27,35,43,51,59,67,
                            4,12,20,28,36,44,52,60,68,
                            5,13,21,29,37,45,53,61,0,
                            0,14,22,30,38,46,54,0,0,
                            0,0,23,31,39,47,0,0,0]).reshape(8,9).T.reshape(-1)
    if eye=="OD":
        index=OD_index[OD_index>0]
    elif eye=="OS":
        index=OS_index[OS_index>0]
        
    two_D_data=np.zeros(72)
    for i in range(len(index)):
        two_D_data[index[i]]=data[i]
    df=DataFrame(two_D_data.reshape(9,8).T)
    return df


# In[5]:


def get_vf_data(ori_df):
    eye=check_eye(ori_df)
    ver=get_version(ori_df)
    if ver=="en":
        data_pos=ori_df.where(ori_df["value"]=="30°").dropna().index
        data=ori_df.iloc[data_pos[0]+1:data_pos[1]]
    elif ver=="zh":
        data=pd.concat([ori_df[25:44],ori_df[58:145]])
        
    return reformat_vf_data(data,eye)


# # 读取病人信息

# In[6]:


def get_patient_info(ori_df):
    basic_info=[re.split("[：|:]",x) for x in ori_df.iloc[0:4,0] ]
    basic_info.append(["eye", check_eye(ori_df)])
    basic_info.append(
        ['exam date',
         (ori_df['value']
             .where(ori_df['value'].str.contains('/[\s\S]*:'))
             .dropna()
             .str.findall("\d+/\d+/\d+")
             .apply(lambda x: x[0])
            ).iloc[0]]
    )

    
    df=DataFrame(basic_info,columns=["item",'value'])
    return df


# # 读取统计值
# 
# 包含
# * 假阳性率：
# * 假阴性率：
# * VFI: 
# * MD
# * PSD

# In[7]:


def get_stat(ori_df):
    df=(ori_df['value']
     .where(ori_df['value'].str.contains('%'))
     .dropna()
     .iloc[0:5]
     )
    df.index=["False POS Errors %","False NEG Errors %","VFI %","MD","PSD"]
    
    df.iloc[0:3]=df.iloc[0:3].str.findall("(\d+)%").apply(lambda x:float(x[0])/100)
    
    df.loc[["MD", "PSD"]]=(df.loc[["MD", "PSD"]]
       .str.findall("(\-*\d.*\d*)(\sdB)")
       .apply(lambda x: float(x[0][0]))
                          )
#     df=df.apply(float)
    return df


# # 保存数据
# 

# In[8]:


def get_out_name(output_path,fname,cat):
    return os.path.join(output_path,"csv", "{}_{}.csv".format(os.path.splitext(fname)[0],cat))

def save_to_csv(input_path,output_path,fname):
    ori_df=pdfparser(input_path,fname)
    
    data=get_vf_data(ori_df)
    data.to_csv(get_out_name(output_path,fname,"data"),sep=',',header=False, index=False)
    
    patient_info=get_patient_info(ori_df)
    patient_info.to_csv(get_out_name(output_path,fname,"info"),sep=',',header=False,index=False)
    
    stat=get_stat(ori_df)
    stat.to_csv(get_out_name(output_path,fname,"statistics"),sep=',',header=False)
    
    return True


# # 处理目录

# In[9]:


def convert_folder(input_path,output_path):
    pdffiles = [name for name in os.listdir(input_path)
            if name.endswith('.pdf')]
    for fname in pdffiles:
        print("Convert PDF file {} to CSV".format(fname))
        save_to_csv(input_path,output_path,fname)
        print("done")



# In[10]:


if __name__=="__main__":    
    convert_folder(input_path,output_path)


# In[ ]:




