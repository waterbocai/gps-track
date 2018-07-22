# -*- coding: utf-8 -*-
import sys
sys.path.append("../site-packages")
sys.path.append("..")
reload(sys)
sys.setdefaultencoding('utf-8')
import importlib
import requests
from config import myDomain
from pweixin.controler.MenuManager import WXManager
#获取微信号数据
weixinName = sys.argv[1]
url = "{0}/manage?act=weixin-id".format(myDomain)
fwh = requests.get(url, params = {"enname":weixinName}).json()

#微信对象初始化
wxMenu = WXManager({"appid":fwh["appid"],"secret":fwh["secret"]})

#动态加载微信数据
weixin = importlib.import_module("fuwuhao.{0}".format(weixinName))
weixin.menu.replace("__APPID__",fwh['appid'])
weixin.menu.replace("__MYDOMAIN__",myDomain)

#urls = [
#  "http://m.wsq.qq.com/263529217",
#  "https://www.jinshuju.net/f/4qc62V",
#  "http://lightapp.baidu.com/?appid=967755",
# "http://lightapp.baidu.com/?pageId=pg21023827250137584&appid=967755",
# "http://lightapp.baidu.com/?pageId=pg21037040745337296&appid=967755",
# "http://lightapp.baidu.com/?pageId=pg21022913242476964&appid=967755",
# "http://hao.uc.cn/bst/index?uc_param_str=prdnfrpfbivelabtbmntpvsscp"]
#for e in  urls :
#    print(wxMenu.url2short(e))
#print(wxMenu.delMenu())
#print menu
#print(wxMenu.createMenu(menu))
print(wxMenu.getMenu())
#r = wxMenu.getQR()
#t = r["ticket"]
#print(t)
#print(r["url"])
#
#print(wxMenu.getQRbyTicket(t))

#print(wxMenu.getGroups())
#print wxMenu.getGroups()
#print wxMenu.createQcode(1)['url']
#print wxMenu.createQcode(101)['url']