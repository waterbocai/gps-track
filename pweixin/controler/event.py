# -*- coding: utf-8 -*-
import importlib
import product.iconfig as icfg 
import string
from message import GetMessage,PostMessage
from tencent_map import TencentMap
from baidumap import BaiduMap
import time
import datetime
import re
import web
import json
import requests

        
#事件处理基类
class EventBase:
    def __init__(self):
        pass
        
    def run(self,msg,objWeixin):
        self.objWeixin   = objWeixin
        #获取文本配置信息
        self.tradeorder  = self.objWeixin.tradeorder
        #获取产品文本配置信息       
        return ""

    def broadcast2Manager(self,user,msg,op):
        openid = msg.fromUser
        _ret = icfg.db.query("""SELECT * FROM Manager WHERE openid='{0}' AND report='no'""".format(openid))
        if (len(_ret)>0):#是特定管理者自己，不用上报
            return
        _ret = icfg.db.query("""SELECT * FROM Customer 
                                    WHERE openid='{2}' AND 
                                          {0}_at ='{1}'""".format(op,msg.CreateTime.strftime("%Y-%m-%d %H:%M:%S"),openid))
        if len(_ret)>0:#已经有记录
            return
        
        
        sum = self.objWeixin.get_followers()["total"]
        
        #发送广播消息
        managers = icfg.db.query("""SELECT * FROM Manager,Customer 
                                        WHERE Manager.openid = Customer.openid AND
                                              Manager.enRange ='all'""")
        #textMsg ={
        #    'unsubscribe':"用户离开:{0}\r\n注册地：{1}{2}\r\n当前位置:\r\n-{3}\r\n现有用户:{4}".format(user.nickname,user.province,user.city,user.address,sum),
        #    'subscribe':"新增用户:{0}\r\n注册地：{1}{2}\r\n当前位置:\r\n-{3}\r\n现有用户:{4}".format(user.nickname,user.province,user.city,user.address,sum)
        #}
        systemMsg = self.objWeixin.iconfig.systemMsg
        systemMsg["url"]=""
        systemMsg["data"]["first"]["value"]="关注用户变化提醒"
        if op=="unsubscribe":
            systemMsg["data"]["keyword1"]["value"]="用户离开"
        else:
            systemMsg["data"]["keyword1"]["value"]="用户关注"
        systemMsg["data"]["keyword2"]["value"]=msg.CreateTime.strftime("%Y-%m-%d %H:%M:%S")
        systemMsg["data"]["remark"]["value"]="""
***用户信息***
用户昵称: {0}
所在城市: {1}{2}

用户总数: {3}\r\n""".format(user["nickname"],user["province"],user["city"],sum)
        sent_openids = [] #记录已经发送的用户
        for mgr in managers:
            if mgr.privilege=="invisible" or mgr.openid in sent_openids: #已经发送过
                continue
            #发送太频繁，就不再发送了
            #cmd = "broadcast2Manager_"+openid+"_"+op
            #if self.objWeixin.customser_msg_is_frequent(mgr.openid,cmd,continue_decide="no",minutes_span=0.3):
            #    continue
                
            systemMsg["touser"] = mgr.openid
            try:
                ret = self.objWeixin.send_template_msg(systemMsg)
                sent_openids.append(mgr.openid)
                #objWeixin.send_text_message(mgr.openid,textMsg[op])
            except Exception as e:
                print "{1}-管理员：{0} openid:{2}的消息无法送达".format(mgr.nickname,self.objWeixin.weixinName,mgr.openid)
                print e
                print systemMsg


#---关注事件
#<xml>
#<ToUserName><![CDATA[toUser]]></ToUserName>
#<FromUserName><![CDATA[FromUser]]></FromUserName>
#<CreateTime>123456789</CreateTime>
#<MsgType><![CDATA[event]]></MsgType>
#<Event><![CDATA[subscribe]]></Event>
#</xml> 

#---二维码扫描关注
#<xml><ToUserName><![CDATA[toUser]]></ToUserName>
#<FromUserName><![CDATA[FromUser]]></FromUserName>
#<CreateTime>123456789</CreateTime>
#<MsgType><![CDATA[event]]></MsgType>
#<Event><![CDATA[subscribe]]></Event>
#<EventKey><![CDATA[qrscene_123123]]></EventKey>
#<Ticket><![CDATA[TICKET]]></Ticket>
#</xml>         
class Subscribe(EventBase):
    def __init__(self):
        pass

        
    def run(self,msg,objWeixin):
        EventBase.run(self,msg,objWeixin)
        user = objWeixin.get_user_info2(msg.fromUser)
        EventBase.broadcast2Manager(self,user,msg,'subscribe')    

        if msg.eventKey != "" :
            retmsg=self.tradeorder.procWeixinScene(msg)
            #retmsg = EventBase.getSceneMsg(self,msg)
        else :
            #retmsg = msg.reply_text(msg.xmlMsg)
            #firsteye[1]['url']=firsteye[1]['url']+msg.fromUser
            firsteye = objWeixin.firsteye
            for i in range(len(firsteye)):
                if firsteye[i]['url'].find("openid=") >=0:
                    firsteye[i]['url']=firsteye[i]['url']+msg.fromUser
            retmsg = msg.reply_news(firsteye)    
        return retmsg
        
class UnSubscribe(EventBase):
    def __init__(self):
        pass
    
    def run(self,msg,objWeixin):
        EventBase.run(self,msg,objWeixin)
        user = objWeixin.get_user_info2(msg.fromUser,format="string")
        EventBase.broadcast2Manager(self,user,msg,'unsubscribe')
        #新用户，首先进行注册
        _ret = icfg.db.query("SELECT * FROM Customer WHERE openid='{0}'".format(msg.fromUser))
        if len(_ret)==0:
            icfg.db.insert("Customer",openid = msg.fromUser,
                                 unsubscribe_at = msg.CreateTime.strftime("%Y-%m-%d %H:%M:%S")
            )           
        else:
            w = "openid ='{0}'".format(msg.fromUser)
            icfg.db.update("Customer",where=w,unsubscribe_at = datetime.datetime.now())

        retmsg = msg.reply_text(msg)
        return retmsg

#---场景扫描事件
#<xml>
#<ToUserName><![CDATA[toUser]]></ToUserName>
#<FromUserName><![CDATA[FromUser]]></FromUserName>
#<CreateTime>123456789</CreateTime>
#<MsgType><![CDATA[event]]></MsgType>
#<Event><![CDATA[SCAN]]></Event>
#<EventKey><![CDATA[SCENE_VALUE]]></EventKey>
#<Ticket><![CDATA[TICKET]]></Ticket>
#</xml>         
class Scan(EventBase):
    def __init__(self):
        pass
    
    def run(self,msg,objWeixin):
        EventBase.run(self,msg,objWeixin)
        #print(msg.xmlMsg)
        ret = self.tradeorder.procWeixinScene(msg)
        return ret

#---地里位置上报事件
#<xml>
#<ToUserName><![CDATA[toUser]]></ToUserName>
#<FromUserName><![CDATA[fromUser]]></FromUserName>
#<CreateTime>123456789</CreateTime>
#<MsgType><![CDATA[event]]></MsgType>
#<Event><![CDATA[LOCATION]]></Event>
#<Latitude>23.137466</Latitude>
#<Longitude>113.352425</Longitude>
#<Precision>119.385040</Precision>
#</xml>        
class Location(EventBase):
    def __init__(self):
        pass
    
    def run(self,msg,objWeixin):
        EventBase.run(self,msg,objWeixin)
        self.updateUserLaction(msg,objWeixin)
        return
    
    #更新用户的当前位置
    def updateUserLaction(self,msg,objWeixin):
        _uploadtime = msg.CreateTime.strftime('%Y-%m-%d %H:%M:%S')
        ret = icfg.db.query("SELECT COUNT(*) as _sum FROM Customer where openid='%s'" %(msg.fromUser))
        times = ret[0]._sum
        user = objWeixin.update_user_info(msg.fromUser)
        #print(user)
        lat =msg.latitude
        lng =msg.longitude
        coords        ="{1},{0}".format(lat,lng)
        url           ="{0}/baidumap?act=translate".format(icfg.iwaiter_service_url)
        rLatLng =requests.get(url,params = dict( _from ='gpsAngle',_to='baiduAngle',
                                             coords = coords)).json()
        
        url = "{0}/baidumap?act=geocoder".format(icfg.iwaiter_service_url)
        addr =requests.get(url,params = dict(lat =lat,lng=lng,type='bd09ll')).json()
        
        qqLat,qqLng =requests.get("{0}/qqmap?act=translate".format(icfg.iwaiter_service_url), 
                               params = dict(lat =lat,lng=lng)).json()
        #addr = qqMap.geocoder(str(msg.latitude)+","+str(msg.longitude))
        
        icfg.db.update("Customer",where="openid=$msg.fromUser",vars =locals(),
                                     upload_time = _uploadtime,
                                     gpsLat = msg.latitude,
                                     gpsLng = msg.longitude,
                                     nickname = user["nickname"],
                                     address  = addr['formatted_address']+"({0})".format(addr['sematic_description']),
                                     city     =addr["addressComponent"]["city"],
                                     baiduLat    =rLatLng[0]['y'],
                                     baiduLng    =rLatLng[0]['x'],
                                     qqLat       =qqLat,
                                     qqLng       =qqLng,)
        return ""
#---菜单点击事件
#<xml>
#<ToUserName><![CDATA[toUser]]></ToUserName>
#<FromUserName><![CDATA[FromUser]]></FromUserName>
#<CreateTime>123456789</CreateTime>
#<MsgType><![CDATA[event]]></MsgType>
#<Event><![CDATA[CLICK]]></Event>
#<EventKey><![CDATA[EVENTKEY]]></EventKey>
#</xml>        
class Click(EventBase):
    def __init__(self):
        pass
    
    def run(self,msg,objWeixin):
        EventBase.run(self,msg,objWeixin)
        retmsg = msg.reply_news(firsteye)
        return retmsg
 
#---点击菜单跳转链接时的事件推送
#<xml>
#<ToUserName><![CDATA[toUser]]></ToUserName>
#<FromUserName><![CDATA[FromUser]]></FromUserName>
#<CreateTime>123456789</CreateTime>
#<MsgType><![CDATA[event]]></MsgType>
#<Event><![CDATA[VIEW]]></Event>
#<EventKey><![CDATA[www.qq.com]]></EventKey>
#</xml>  
class View(EventBase):
    def __init__(self):
        pass
    
    def run(self,msg,objWeixin):
        EventBase.run(self,msg,objWeixin)
        retmsg = msg.reply_text(msg.xmlMsg)
        return retmsg

        