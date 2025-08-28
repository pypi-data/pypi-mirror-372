from .dbcfgmain import *

__all__=dbcfgmain.__all__

def use(连接名="",ehm=0):
    return dbcfg(连接名,ehm)
