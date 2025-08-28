# dbcfg本身

dbcfg的python包。包含python的库以及dbcfg本身。

有关dbcfg的文档请参考

https://gitee.com/chenc224/dbcfg/blob/master/README.md

# 安装

使用

```
pip install dbcfg
```
即可下载安装

# 使用方法

```
import dbcfg
dbc=dbcfg.use("xxx",ehm=1)
db=dbc.connect()        #返回数据库连接
```
ehm参数表用于控制有问题、有异常时如何处理

|ehm|处理细节|
|:--|:--|
|0|默认值，不特殊处理。|
|1|如果调用的返回码为非0，则打印rtinfo的内容|
|2|如果调用的返回码为非0，则触发异常|
