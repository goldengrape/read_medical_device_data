
# coding: utf-8

# # WAM5500数据的清理器

# In[1]:


import pandas as pd
import numpy as np
import os


# In[2]:


if __name__=="__main__":
    from read_medical_data import read_medical_data
    dpath=os.path.join("..","testdata")
    dfname="WAM5500.csv"
    datafilename=os.path.join(dpath,dfname)
    
    jpath=os.path.join("..","medical_device_data")
    jname="GrandSeikoWAM5500.json"
    jsonfilename=os.path.join(jpath,jname)
    data=read_medical_data(datafilename,"all",jsonfilename)


# 按照时间裁剪
# 测量的时间通常比所需要的时间长, 因此需要按照裁剪出指定时长的数据. 由于有可能存在数据点丢失, 所以指定时长的数据可能数量并不相等, 需要补齐.

# In[35]:


def generate_df(data):
    df=pd.DataFrame()
    df["time"]=data["time"].values.flatten()
    df["power"]=data["power"].values.flatten()
    df["pupil"]=data["pupil"].values.flatten()
    return df.dropna()


# In[14]:


def cut_by_time(df,start_time=0, duration=5):
    # 获取一段时间内的数据
    # 测量时间通常长于所需要的时间, 因此需要截取
    start_timestamp=pd.to_datetime(start_time,unit='s')
    end_timestamp=pd.to_datetime(start_time+duration,unit="s")
    df= df.where((df.time>=start_timestamp) & (df.time<=end_timestamp)).dropna()
    
    #将时间格式转换回float
    df.time=pd.to_numeric(df.time)/10e8
    return df

def padding_time(df,duration=5,redundancy=5,padding_with="last"):
    # 将数据补齐
    # 通常每秒有4-5个数据. 
    # 默认以最后一项补齐,否则以padding_with补齐
    redundancy_length=duration*5+redundancy
    add_length=redundancy_length-len(df)
    if padding_with=="last":
        padding_item=df.tail(1)
    else:
        padding_item=pd.DataFrame(np.ones((1,df.shape[1]))*padding_with,columns=df.columns)
    df2=pd.concat([padding_item]*add_length)
    new_df=df.append(df2).reset_index()[df.columns]
    return new_df


# In[63]:


def clean_WAM5500_data(data):
    df=generate_df(data)
    df=cut_by_time(df,start_time=0, duration=5)
    df=padding_time(df,duration=5,redundancy=5,padding_with="last")
    df_dict={}
    for col in df.columns:
        df_dict[col]=df[col]
    return df_dict

