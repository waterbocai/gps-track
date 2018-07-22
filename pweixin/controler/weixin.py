# -*- coding: utf-8 -*-
import web
import string 
from message import GetMessage,PostMessage
from robot   import Robot
from chick   import Chick
from event   import Subscribe,UnSubscribe,Scan,Location,Click,View

from userdb import userdb
import product.iconfig as icfg
import importlib
import re
import datetime

class Weixin:
    def __init__(self):
        #注册消息事件处理类
        #self.activities = {
        #    "1"  : Robot,
        #    "000": BusBoss,
        #}
        #注册事件处理类
        self.eventies = {
            "subscribe"  : Subscribe,
            "unsubscribe": UnSubscribe,
            "scan"       : Scan,
            "location"   : Location,
            "LOCATION"   : Location,
            "click"      : Click,
            "view"       : View,
        }
    
    def GET(self):
        #获取输入参数
        data = web.input()
        #从WeixinService中获取该服务号的相关信息
        fwh = userdb.get_weixin_obj(weixin_name=data.name)
        msg = GetMessage(data)
        if msg.is_from_weixin(fwh.token):
            return msg.echostr
        else :
            return msg.signature
        
    def POST(self):
        str_xml = web.data() #获得post来的数据
        msg = PostMessage(str_xml) #解析消息信息
        #retmsg =msg.reply_text(str_xml)
        self.initConfig(msg)
        if msg.msgType.lower() == "event" :
            self.logAccessUrl(msg)
            retmsg = self.event_handler(msg)
        else :
		    retmsg = self.transferDialogue(msg)
            #1.优先进入对话状态
            
            #2.其次选择通话对象
            
            #3.最后进入服务咨询状态
            #retmsg = msg.reply_transfer_customer_service()
        return retmsg
    
    
    
    def msg_handler(self,msg):
        #获取用户当前状态
        if msg.msgType =="text" and self.activities.has_key(msg.content.strip()):
            #进入设定好的服务状态，并直接运行
            retmsg = self.activities[msg.content.strip()](0).run(msg)
        else:
            for i in range(len(self.firsteye)):
                if self.firsteye[i]['url'].find("openid=") >=0:
                    self.firsteye[i]['url']=self.firsteye[i]['url']+msg.fromUser
            retmsg = msg.reply_news(self.firsteye)
        return retmsg
        
    def event_handler(self,msg):
        #retmsg = msg.reply_text(msg.xmlMsg)
        if self.eventies.has_key(msg.event) :
            #retmsg = self.eventies[msg.event]().run(msg,self.userMsg)
            retmsg = self.eventies[msg.event]().run(msg,self.objWeixin)
        else :
            retmsg = msg.reply_news(self.firsteye) 
        return retmsg
        
        
    def logAccessUrl(self,msg):
        auth_pattern =  re.compile("^https://open.weixin.qq.com", re.IGNORECASE)
        mall_pattern =  re.compile("^http://mp.weixin.qq.com/bizmall/mallshelf", re.IGNORECASE)
        now = datetime.datetime.now()

        fullpath =msg.eventKey
        if msg.event=="view":
            if auth_pattern.match(msg.eventKey):#内部链接，已经有计算，不再记录
                return
            elif(mall_pattern.match(msg.eventKey)):#微信小店
                pathinfo ="http://mp.weixin.qq.com/bizmall/mallshelf"
            else:
                pathinfo =msg.eventKey
        elif msg.event=="click":
            pathinfo ="weixin_"+msg.eventKey
        else:
            return
        icfg.db.insert("UserAccess",domain   =web.ctx.homedomain,
                               fullpath =web.ctx.fullpath,
                               pathinfo =pathinfo,
                               openid   =msg.fromUser,
                               weixin_orign_id   =msg.toUser,
                               access_at    =now,
                               access_month =now.strftime("%Y-%m"),
                               access_week =(now+datetime.timedelta(days=6-now.weekday())).strftime("%Y-%m-%d"),
                               access_date =now.strftime("%Y-%m-%d"),
                               access_hour = now.hour)
        return
    
    #初始化微信配置信息
    def initConfig(self,msg):
        self.objWeixin =icfg.objWeixin
        self.firsteye  = icfg.objWeixin.firsteye
        self.menuMap   = icfg.objWeixin.menuMap
        #获取文本配置信息
        self.objWeixin.product     = importlib.import_module('product.iconfig')
        tradeorderModule = importlib.import_module('product.mobile.tradeorder')
        self.objWeixin.tradeorder  = tradeorderModule.TradeOrder()

        return
        
    def transferDialogue(self,msg):
        openid = msg.fromUser
        #获取用户对象
        user=self.objWeixin.get_user_info2(openid)
        retmsg = msg.reply_transfer_customer_service()
        return retmsg
