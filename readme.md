# 医学数据读取工具

医疗设备导出的数据文件, 往往是整合在一起的CSV文件或EXCEL文件.
本工具包提供了读取数据文件中部分数据块的工具.

目前仅提供Python语言的函数:

目前支持的有医疗设备有:
* [Sirius角膜地形图](http://www.zeaomed.com/jmdxty/772.html)
* [PentaCam角膜地形图](https://www.pentacam.com/int/ophthalmologist-with-pentacam.html)
* [Grand Seiko WAM5500视调节力测量仪](http://www.wiskeymedical.com.cn/product/v1049)
* [Humphrey视野(PDF需预先处理)](https://www.zeiss.com.cn/meditec/products/ophthalmology-optometry/glaucoma/diagnostics/perimetry/humphrey-field-analyzer-3.html)
* [HRT(PDF需预先处理)](http://www.gvchina.com/product.aspx?t=1&c=12)
* [Octopus 900动态视野(PDF需预先处理)](https://www.haag-streit.com/haag-streit-diagnostics/products/perimetry/octopus-900/)

# 使用方法:

python版本依赖pandas,
* 如果在[Azure Notebooks](https://notebooks.azure.com/)或[CoCalc](https://cocalc.com/app)中运行, 该环境已经预装, 不需要再安装pandas.
* 如果在本地运行, 请事先安装[pandas](http://pandas.pydata.org/), 推荐使用Anaconda进行安装.

将[python目录](https://github.com/goldengrape/read_medical_device_data/tree/master/python)下的.py文件和[medical_device_data](https://github.com/goldengrape/read_medical_device_data/tree/master/medical_device_data)下所有的JSON文件复制到需要的文件夹中.

```python
from read_medical_data import read_medical_data

data=read_medical_data('patient01.csv','CornealThickness','sirius.json')
```

data以pandas DataFrame的类型存储, 该类型可以方便的索引/过滤/比较/计算, 也可以转换成numpy array进行运算.

## PDF预处理

PDF的预处理过程, 请参考教程[《octopus视野报告数据提取》](https://goldengrape.github.io/posts/python/octopus-data/)

# 随机森林

csv数据可以直接送进随机森林分类器进行机器学习训练, 请参考教程[《眼科数据随机森林》](https://goldengrape.github.io/posts/python/random-forest-for-ophthalmology-data/)
