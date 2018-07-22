# -*- coding: utf-8 -*-
import sys,os
import importlib
curdir = os.path.abspath(__file__)
print("curdir:{0}".format(curdir))
root   = "/".join(curdir.split("\\")[0:-3])
print("root:{0}".format(root))
sys.path.append(root)
#weixin_name =  sys.argv[1]
#weixin_name = "gxsaiwei"
from MenuManager import WXManager

sys.modules["myDomain"] = "http://sw.gxsaiwei.com"
weixin = importlib.import_module('product.iweixin.config') 
wxMenu = WXManager(appid=weixin.appid,secret=weixin.secret)

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
#print(wxMenu.createMenu(weixin.menu))
#print(wxMenu.getMenu())
#r = wxMenu.getQR()
#t = r["ticket"]
#print(t)
#print(r["url"])
#
#print(wxMenu.getQRbyTicket(t))

#print(wxMenu.getGroups())
#print wxMenu.getGroups()
print wxMenu.createQcode("P4")['url']
#print wxMenu.createQcode(101)['url']
#import binascii
#outfile = file("out.amr","wb")
#ret = wxMenu.download_media("rHsPPwRNRD3H7qVTuNcAY6OQXqwm9u_0TQsxanQBGrjh8NMd4BJ6vjW85ntaZT9w")
#print ret.decode("utf-8","ignore")
#
#temp = "#AMR\n"
#for c in ret[7:]:
#    temp +=""hex(ord(c))
#print temp
    