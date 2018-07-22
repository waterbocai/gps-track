# -*- coding: utf-8 -*-
import string
import urllib2,json
from common import myHomeUrl
from message import GetMessage,PostMessage
class Chick:
    def __init__(self,index):
        self.index = index
        self.mc = pylibmc.Client()      #初始化一个memcache实例用来保存用户的操作
        self.bye_pic_url   ="http://g.hiphotos.bdimg.com/album/scrop%3D120%3Bq%3D90/sign=ef7d37423bdbb6fd2105a27979199a2a/caef76094b36acaf907a15457ed98d1000e99cf5.jpg"
        self.hello_pic_url ="http://b.hiphotos.bdimg.com/album/s%3D1100%3Bq%3D90/sign=c3745497aad3fd1f3209a63b007e1e6e/279759ee3d6d55fbf304b19f6f224f4a21a4dd4d.jpg"    
    
    def run(self,msg,extMsg=""):
        #获取用户当前状态
        if msg.msgType == "text" and msg.content.strip() == "bye" :
            self.mc.delete(msg.fromUser)
            news =[{
            "title"       : "小主，下次再来玩啊",
            "description" : "请输入任意内容获取服务列表 ",
            "picurl"      : self.bye_pic_url,
            "url"         : myHomeUrl,
            }]
            retmsg = msg.reply_news(news)
        else :
            if self.index == 0 :
                news =[{
                "title"       : "小主，等你好久了",
                "description" : "不想和我玩，请输入:bye",
                "picurl"      : self.hello_pic_url,
                "url"         : myHomeUrl,
                }]
                retmsg = msg.reply_news(news)
            else :
                retmsg = msg.reply_text(self.talk(msg.content))
            self.mc.set(msg.fromUser,"Chick-"+"%d"%(self.index+1))
        return retmsg
        
    def talk(self,msg):
        msg = msg.encode('UTF-8')
        enmsg = urllib2.quote(msg)
        baseurl = r'http://www.simsimi.com/func/req?msg='
        url = baseurl+enmsg+'&lc=ch&ft=0.0'
        resp = urllib2.urlopen(url)
        reson = json.loads(resp.read())
        return reson["response"]
    