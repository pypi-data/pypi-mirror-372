__all__=["dbcfg","c_commandarg","cfgdir"]

import os,json
import inspect,sys

def cfgdir():   #返回配置目录列表
    配置目录=[]
    home_dir = os.path.expanduser("~")
    配置目录.append(os.path.join(home_dir,".dbcfg.d"))
    dh,_=os.path.splitdrive(os.getcwd())
    配置目录.append(os.path.join(dh,"/etc","dbcfg.d"))
    配置目录.append(os.path.join(dh,"/etc","dbconn.config.d"))
    return 配置目录

class dbcfg(object):    #dbcfg主类
    def __init__(self,连接名='',ehm=0):
        self.ehm=ehm
        self.connected=False
        self.读配置文件(连接名)

    def 读配置文件(self,连接名):
        self.rtcode=0
        配置目录=cfgdir()
        self.connectname=连接名
        for 目录 in 配置目录:
            配置文件=os.path.join(目录,f"{连接名}.cfg")
            if os.path.isfile(配置文件):
                self.cfgfilename=配置文件
                self.cfgdata=json.loads(open(配置文件).read())
                return
        self.q(-1,{"连接名":连接名})
        
    def cfg(self,实例=''):
        for 配置 in self.cfgdata:
            if not 实例 or 实例==配置.get("name",""):
                return 配置
        self.q(-2,{"实例":实例})
    def connect(self,实例=''):
        self.rtcode=0
        默认包={"oracle":"cx_Oracle","mysql":"pymysql","sqlserver":"pytds","tds":"pytds","opengauss":"py_opengauss.driver.dbapi20",
            "dm":"dmPython"}
        import importlib
        cfg=self.cfg(实例)
        self.dbname=cfg["db"]
        if "python" not in cfg or "import" not in cfg["python"]:
            包=默认包.get(cfg["db"],cfg["db"])
        else:
            包=cfg["python"]["import"]
        try:
            m=importlib.import_module(包)
        except:
            return self.q(-4,{"name":包})
        try:
            self.conn=m.connect(*cfg["t"],**cfg["d"])
            self.connected=True
        except:
            return self.q(-5)
        else:
            return self.conn

    def q(self,返回码,参数={}):
        消息表={
            -1: "未找到配置文件{连接名}.cfg",
            -2:"配置文件中未找到实例{实例}",
            -3:"配置文件中需要设置python相关内容",
            -4:"import {name}错误",
            -5:"连接到数据库错误"
        }
        self.rtcode=返回码
        self.rtinfo=消息表.get(返回码,"错误的返回码").format(**参数)
        if self.ehm==1:
            print(self.rtinfo)
        if self.ehm==2:
            raise Exception(self.rtinfo)
        return self.rtcode
    def commit(self):
        self.conn.commit()
    def execute(self,ssql,*args,**kwargs):
        c=self.conn.cursor()
        c.execute(ssql,*args,**kwargs)
        return c
    def execute2(self,ssql,*args,**kwargs):
        try:
            list = []
            c = self.conn.cursor()
            c.execute(ssql, kwargs)
            col = c.description
            for item in c.fetchall():
                dict = {}
                for i in range(len(col)):
                    dict[col[i][0]] = item[i]
                list.append(dict)
        except self.dbdriver.DatabaseError as e:
            self.connected = False
            print("oracle执行异常：%s" % (e))
            if self.raiseExp:
                raise  # 往上层抛
            return
        return list
    def jg1(self,ssql,*args,**kwargs):
        '''根据sql返回1条结果'''
        c=self.conn.cursor()
        c.execute(ssql,*args,**kwargs)
        jg=c.fetchone()
        c.close()
        if jg==None:
            return
        if len(jg)==1:
            return jg[0]
        else:
            return jg
    def xg(self,ssql,*args,**kwargs):
        '''主要用于修改，执行完后附加commit操作'''
        c=self.execute(ssql,*args,**kwargs)
        self.commit()
        return c
    def test(self):     #通过获取当前时间来测试数据库是否工作正常
        if self.dbname.lower()=="oracle":
            print(self.jg1("select sysdate from dual"))
    def __getattribute__(self,name):
        if name in ("读配置文件","connect"):
            self.code=0
            self.info=""
        if name in ("c","conn") and not self.connected:
            self.connect()
        return object.__getattribute__(self,name)
    def __del__(self):
        if self.connected:
            self.conn.close()

class c_commandarg: #根据命令行参数调用模块及显示相应help
    tcmd={}
    scriptname=""
    def __init__(self,gg,scriptname):
        c_commandarg.scriptname=scriptname
        for g in gg:
            if (inspect.isfunction(gg[g]) or inspect.isclass(gg[g])) and gg[g].__doc__!=None:
                c_commandarg.tcmd[g]=gg[g]
    def main(self):
        if len(sys.argv)>1:
            cmd=sys.argv[1]
        else:
            self.printhelp()
            return
        if cmd not in c_commandarg.tcmd:
            cmd="info"
        cf=c_commandarg.tcmd[cmd]
        if inspect.isfunction(cf):
            rtn=cf()
        else:
            c=cf()
            rtn=0
            if hasattr(c,"main"):
                rtn=c.main()
        return rtn
    
    @staticmethod
    def printhelp():
        '''显示程序说明及命令行、参数信息'''
        print(c_commandarg.scriptname)
        print("-"*len(c_commandarg.scriptname)*2)
        maxcmdsize=0
        scmd=[]
        for name in c_commandarg.tcmd:
            scmd.append(name)
            if len(name)>maxcmdsize:
                maxcmdsize=len(name)
        scmd.sort()
        for name in scmd:
            print("%-*s   %s" %(maxcmdsize,name,c_commandarg.tcmd[name].__doc__))
