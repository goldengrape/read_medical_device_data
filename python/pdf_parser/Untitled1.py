
# coding: utf-8

# # 根据位置提取PDF文件信息

# ## 设定文件路径参数

# In[ ]:


if __name__=="__main__":
    input_path='../../testdata/Octopus'
    output_path="../../testdata/Octopus"
    fname="20170406动态视野(Octopus) .pdf"

    #pageno=0 # for test


# ## 导入依赖包

# .2  导入依赖包
# 在使用notebook.azure.com在线运行时, 由于默认没有安装pdfminer.six这个包, 所以在首次运行时需要安装, 已经将安装代码加入

# 在使用notebook.azure.com在线运行时, 由于默认没有安装pdfminer.six这个包, 所以在首次运行时需要安装, 已经将安装代码加入到下面导入依赖包的代码内, 因此首次运行时速度会较慢. 
# 
# 同时, 在使用notebook.azure.com在线运行时, 服务器端不会保存曾经安装过的包, 因此在1小时没有操作之后, 服务器会关闭, 再次打开时就已经丢失了之前安装的包, 相当于首次运行. m
