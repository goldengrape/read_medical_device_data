
# coding: utf-8

# # 提取Humphrey视野数据

# ## 设定文件路径参数

# In[1]:


if __name__=="__main__":
    input_path='../../testdata/Humphrey'
    output_path="../../testdata/Humphrey"
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


# In[4]:


# if __name__=="__main__":
#     ori_df=pdfparser(input_path,fname)


# # 读取视野测量原始数据
# 
# 注意设定中英文和眼别

# In[5]:


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


# In[6]:


# if __name__=="__main__":
#     print(check_eye(ori_df))
#     print(get_version(ori_df))


# In[7]:


def get_vf_data(ori_df):
    eye=check_eye(ori_df)
    ver=get_version(ori_df)
    if ver=="en":
        data_pos=ori_df.where(ori_df["value"]=="30°").dropna().index
        data=ori_df.iloc[data_pos[0]+1:data_pos[1]]
    elif ver=="zh":
#         data=pd.concat([ori_df[25:44],ori_df[58:145]])
        data=(ori_df.where(ori_df.value.str.match("(<*\d+)$")) #有<0或者整数
                   .dropna()
#                    .reset_index()
                   .iloc[:56,:])
        if eye=="OD": # 右眼+中文的时候, 貌似把年龄数据混进来了
            data.loc[70,:]="" # 改法虽然难看, 但暂时可用
            
    return reformat_vf_data(data,eye)


# In[8]:


# if __name__=="__main__":
#     print(get_vf_data(ori_df))


# # 读取病人信息

# In[9]:


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


# In[10]:


# if __name__=="__main__":
#     print(get_patient_info(ori_df))


# # 读取统计值
# 
# 包含
# * 假阳性率：
# * 假阴性率：
# * VFI: 
# * MD
# * PSD

# In[11]:


def get_stat(ori_df):
    df1=(ori_df['value']
     .where(ori_df['value'].str.contains('%'))
     .dropna()
     .iloc[0:3]
     .str.findall("(\d+)%")
     .apply(lambda x:float(x[0])/100)
     )
    
#     df.iloc[0:3]=df.iloc[0:3].str.findall("(\d+)%").apply(lambda x:float(x[0])/100)
    
    df2=(ori_df['value']
     .where(ori_df['value'].str.contains('dB'))
     .dropna()
     .str.findall("(\-*\d.*\d*)\sdB")
     .apply(lambda x: float(x[0]))
     )
    df=pd.concat([df1,df2])
    df.index=["False POS Errors %","False NEG Errors %","VFI %","MD","PSD"]
    return df


# In[12]:


# if __name__=="__main__":
#     print(get_stat(ori_df))


# # 保存数据
# 

# In[13]:


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
    
    together=pd.concat([patient_info,stat,data])
    together.to_csv(get_out_name(output_path,fname,""),sep=',',header=False)

    return True


# # 处理目录

# In[14]:


def convert_folder(input_path,output_path):
    pdffiles = [name for name in os.listdir(input_path)
            if name.endswith('.pdf')]
    for fname in pdffiles:
        print("Convert PDF file {} to CSV".format(fname))
        save_to_csv(input_path,output_path,fname)
        print("done")



# In[15]:


if __name__=="__main__":    
    convert_folder(input_path,output_path)

