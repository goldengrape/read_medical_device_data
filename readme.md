# 医学数据读取工具

医疗设备导出的数据文件, 往往是整合在一起的CSV文件或EXCEL文件.
本工具包提供了读取数据文件中部分数据块的工具.

目前提供MatLab和Python这两种常用语言的函数(其他我也不会):

目前支持的有医疗设备有:
* Sirius角膜地形图
* PentaCam角膜地形图

# 使用方法:

## MatLab版本

### 简单快速使用版本:
将[matlab目录](https://github.com/goldengrape/read_medical_device_data/tree/master/MatLab)下的文件复制到所需要的文件夹中, 调用函数即可:
* read_sirius.m: 读取Sirius角膜地形图的数据.
  * data=read_sirius(data_file_name,catalog)
  * 示例: data=read_sirius('patient01.csv','CornealThickness')
  data中记录的是来自'patient01.csv'中的角膜厚度数据.

* read_pentacam.m: 读取PentaCam角膜地形图的数据.
    * data=read_pentacam(data_file_name,catalog)
    * 示例: data=read_pentacam('patient01.csv','FRONT')
    data中记录的是来自'patient01.csv'中的角膜前表面高度数据.

### 通用读取器版本
需要事先安装[JSONLab](https://cn.mathworks.com/matlabcentral/fileexchange/33381-jsonlab--a-toolbox-to-encode-decode-json-files), 打开页面, 在Download->Toolbox, 然后点击安装即可.

* 将[matlab目录](https://github.com/goldengrape/read_medical_device_data/tree/master/MatLab)下read_medical_data.m复制到所需要的文件夹中,
* 将[medical_device_data](https://github.com/goldengrape/read_medical_device_data/tree/master/medical_device_data)下所有的JSON文件复制到需要的文件夹中,

调用方法:
* data=read_medical_data(data_file_name,catalog,json_file_name)
* 示例:
  data=read_medical_data('patient01.csv','CornealThickness','sirius.json')
  data中记录的是Sirius角膜地形图的角膜厚度数据.

# Python版本

python版本依赖pandas,
* 如果在[Azure Notebooks](https://notebooks.azure.com/)或[CoCalc](https://cocalc.com/app)中运行, 该环境已经预装, 不需要再安装pandas.
* 如果在本地运行, 请事先安装[pandas](http://pandas.pydata.org/), 推荐使用Anaconda进行安装.

将[python目录](https://github.com/goldengrape/read_medical_device_data/tree/master/python)下的.py文件和[medical_device_data](https://github.com/goldengrape/read_medical_device_data/tree/master/medical_device_data)下所有的JSON文件复制到需要的文件夹中.

```python
from read_medical_data import read_medical_data

data=read_medical_data('patient01.csv','CornealThickness','sirius.json')
```

data以pandas DataFrame的类型存储, 该类型可以方便的索引/过滤/比较/计算, 也可以转换成numpy array进行运算.
