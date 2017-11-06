
# coding: utf-8

# # 一组与MatLab类似的csv读取工具

# ## 翻译单元格位置
# 比如给定A1, 应返回R=1,C=1

# In[1]:


import pandas as pd
import re


# In[2]:


def col2num(col_str):
    """ Convert base26 column string to number. """
    expn = 0
    col_num = 0
    for char in reversed(col_str):
        col_num += (ord(char) - ord('A') + 1) * (26 ** expn)
        expn += 1

    return col_num
def cell2num(cellname):
    col_letter="".join(re.findall('[A-Z][a-z]*',cellname))
    col=int(col2num(col_letter))
    row=int("".join(re.findall('[0-9]*',cellname)))
    return (row,col)


# ## 翻译单元格范围
# 例如: A1..B5->[1,1,5,2]

# In[3]:


def cellblock2num(cell_string):
    cell_name=re.split('\..',cell_string)
    (r1,c1)=cell2num(cell_name[0])
    (r2,c2)=cell2num(cell_name[1])
    return(r1,c1,r2,c2)   


# ## 构造dlmread
# 仿照MatLab里面的dlmread
# ```matlab
# M = dlmread(filename,delimiter,[R1 C1 R2 C2])
# ```
# 注意其中行列数字按照excel表格中的形式写, 首行=1, 首列=1. 否则一个大的表格数起来太麻烦了. 

# In[4]:


def dlmread(filename,delimiter,cell_block,header=None):
    (R1,C1,R2,C2)=cellblock2num(cell_block)
    s=range(R1-1)
    n=R2-R1+1
    cols=range(C1-1,C2)
    data=pd.read_csv(filename,
                     sep=delimiter,
                     skiprows=s,
                     nrows=n,
                     header=header,
                     usecols=cols
                    )
    return data


# In[5]:


# 测试用, 测试开关使用and True: 
if __name__=="__main__" and True:
    import os
    fpath=os.path.join('..','testdata')
    fname='standard.csv'
    filename=os.path.join(fpath,fname)
    standard_data=pd.read_csv(filename,header=None,sep=';')
    data=dlmread(filename,';',"B1..C4",header=None)
    print("原始表格")
    print(standard_data)
    print("部分读取")
    print(data)


# In[ ]:




