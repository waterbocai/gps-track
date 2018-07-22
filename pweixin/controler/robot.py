# -*- coding: utf-8 -*-
import string
from common import myHomeUrl
from message import GetMessage,PostMessage
class Robot:
    def __init__(self,index):
        self.index = index
        self.mc = pylibmc.Client()      #初始化一个memcache实例用来保存用户的操作
        self.bye_pic_url   = "http://b.hiphotos.bdimg.com/album/scrop%3D120%3Bq%3D90/sign=2a1f350bd358ccbf1fe2f26569e58d0c/d6ca7bcb0a46f21f27c8c2eaf4246b600d33ae8f.jpg"
        self.hello_pic_url ="http://f.hiphotos.bdimg.com/album/s%3D1100%3Bq%3D90/sign=298a9d215cdf8db1b82e78653913e625/a8014c086e061d957f91ab8179f40ad163d9cab0.jpg"    
    
    def run(self,msg,extMsg=""):
        #获取用户当前状态
        if msg.msgType == "text" and msg.content.strip() == "bye" :
            self.mc.delete(msg.fromUser)
            news =[{
            "title"       : "小主，下次再来玩啊",
            "description" : "请输入任意内容获取服务列表 ",
            "picurl"      : self.hello_pic_url,
            "url"         : myHomeUrl,
            }]
            retmsg = msg.reply_news(news)
        else :
            if self.index == 0 :
                news =[{
                "title"       : "小主，等你好久了",
                "description" : "不想和我玩，请输入:bye",
                "picurl"      : self.bye_pic_url,
                "url"         : myHomeUrl,
                }]
                retmsg = msg.reply_news(news)
            else :
                retmsg = msg.auto_reply()
            self.mc.set(msg.fromUser,"Robot-"+"%d"%(self.index+1))
        return retmsg
    