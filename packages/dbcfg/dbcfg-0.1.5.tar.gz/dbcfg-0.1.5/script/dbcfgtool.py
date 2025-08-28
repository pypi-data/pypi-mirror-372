import sys

from dbcfg import *
#import dbcfg
import os,json

def main():
    c=c_commandarg(globals(),"dbcfg工具、样例")
    c.main()

def 显示所有的配置文件():
    for cdir in cfgdir():
        if os.path.isdir(cdir):
            print(f"目录{cdir}下配置文件：")
        else:
            print(f"目录{cdir}不存在")
            continue
        文件清单=[]
        for f in os.listdir(cdir):
            if f.endswith(".cfg"):
                文件清单.append(f[:-4])
        文件清单.sort()
        print(" ".join(文件清单))

def info():
    '显示配置文件内容，可以用参数指定配置文件名（不用加.cfg）'
    if len(sys.argv)>2:
        配置名=sys.argv[2]
    else:
        配置名=sys.argv[1]
    dbc=dbcfg(配置名,ehm=1)    #读取指定的配置文件里的配置信息
    if dbc.rtcode!=0:
        print("参数需要指定配置文件名")
        显示所有的配置文件()
        return
#   dbc=dbcfg.use(sys.argv[1],ehm=1)    #如果使用import dbcfg引入包，就需要使用use函数
    cfg=dbc.cfg()           #返回指定名称的配置，不指定使用name为""的那一个
    print(f"配置文件 {dbc.cfgfilename}")
    print(f"cfg={cfg}")
    print(json.dumps(cfg,ensure_ascii=False,skipkeys=False,indent=2))

def test():
    '读配置文件，显示基础信息，调用相应的测试函数'
    if len(sys.argv)<3:
        print("需要附加一个参数指定配置文件名\n")
        显示所有的配置文件()
        return
    dbc=dbcfg(sys.argv[2],ehm=1)    #读取指定的配置文件里的配置信息
#   dbc=dbcfg.use(sys.argv[1],ehm=1)    #如果使用import dbcfg引入包，就需要使用use函数
    dbc.connect()
    print(f"dbc.dbname={dbc.dbname}")
    cfg=dbc.cfg()           #返回指定名称的配置，不指定使用name为""的那一个
    print(f"cfg={cfg}")
    dbc.test()
    tname=input("输入一个表名，查询表中的数据:")
    if tname:
        print("执行execute获取select的5条结果，返回的是列表")
        计数=0
        for i in dbc.execute(f"select * from {tname}"):
            print(i)
            计数=计数+1
            if 计数>=5:break
        print("执行execute2获取select的5条结果，返回的是字典")
        计数=0
        for i in dbc.execute2(f"select * from {tname}"):
            print(i)
            计数=计数+1
            if 计数>=5:break

def readdb():   #'读数据代码样例'
    字段=dbc.jg1("select 字段1 from 表 where 一些条件")  #返回结果只有一行数据用jg1

    字段1,字段2=dbc.jg1("select 字段1,字段2 from 表 where 一些条件") #jg1支持多字段

    结果=dbc.jg1("select 字段1,字段2 from 表 where 一些条件")  #jg1多字段另一种用法
    字段1,字段2=结果

    字段=dbc.jg1(f"select 字段1 from 表 where 字段2='{字段2筛选值}'")  #where条件可以用f格式串加入参数
    
    for 字段1,字段2 in dbc.execute("select 字段1,字段2 from 表 where 一些条件"): #循环读取多条数据
        print(字段1,字段2)

    for 字段1, in dbc.execute("select 字段1 from 表 where 一些条件"): #注意如果返回结果只有一个字段要加个逗号，不然返回的是数组
        print(字段1)

def wiki(): #wiki机器人读配置示例代码
    import mwclient
    dbc=dbcfg("wiki")
    cfg=dbc.cfg()
    site = mwclient.Site(cfg["d"]["server"], scheme=cfg["d"]["scheme"],path=cfg["d"]["path"])
    site.login(cfg["d"]["user"],cfg["d"]["password"])

if __name__ == "__main__":
    main()
