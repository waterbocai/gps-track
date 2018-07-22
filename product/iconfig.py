# _*_ coding:utf-8 _*_
import sys,os
from config import getEnvObj,myDomain
from pweixin.userdb import userdb
from model.config import db

#获取微信服务号对象
weixin_name = __file__.split("/")[-2]
objWeixin = userdb.get_weixin_obj(weixin_name=weixin_name)  
weixin    = objWeixin

urlHome='http://www.iwaiter.cn'
domain ='http://twsh2.iwaiter.cn'
db_gxsaiwei = db
owner_db    = db

qrcode_root_dir = "/".join(__file__.split("/")[:-2])+"/public/qrcode"
iwaiter_service_url = "http://service.iwaitercn.localhost:901"
adapter_bus = "http://192.168.56.11:906"
adapter={"vk"    :adapter_bus+"/vkclient",
         "busbox":adapter_bus+"/busboxapi"
        }
file_server="http://171.111.153.186:8090/"
file_server_api =file_server+"fileapi"

catchword        ='赛微——智慧客运探路人'
advertising_word ='赛微——赛出新颖 微动未来'
logo_url = "http://sw.gxsaiwei.com/static/img/gxsaiwei/logo.jpg"
def getFixPara(openid,**args):
    env = getEnvObj()
    fixPara ={"openid"   :openid,
              "catchword":catchword,
              "advertising_word":advertising_word,
              "homedomain": env["homedomain"],
              "show_url":urlHome,
              "logo_url"      : logo_url
    }
    for key in args:
        fixPara[key] =args[key]
    return fixPara

