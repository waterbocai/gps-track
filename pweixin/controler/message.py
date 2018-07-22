# -*- coding: utf-8 -*-
import hashlib
import web
import lxml
import time
import os
import urllib2,json
from lxml import etree
import traceback
import datetime
from common import templates_root

class GetMessage:
    def __init__(self,data):
        self.signature=data.signature
        self.timestamp=data.timestamp
        self.nonce    =data.nonce
        self.echostr  =data.echostr
    
    def is_from_weixin(self,token):
        #字典序排序
        list=[token,self.timestamp,self.nonce]
        list.sort()
        sha1=hashlib.sha1()
        map(sha1.update,list)
        #sha1加密算法 
        hashcode=sha1.hexdigest()
        return hashcode == self.signature       
        
class PostMessage:
    def __init__(self,xmlMsg):
        self.render = web.template.render(templates_root)
        self.xml = etree.fromstring(xmlMsg)
        self.xmlMsg = xmlMsg  
        self.msgType   =self.xml.find("MsgType").text.strip()
        self.fromUser  =self.xml.find("FromUserName").text.strip()
        self.toUser    =self.xml.find("ToUserName").text.strip()
        self.CreateTime=datetime.datetime.fromtimestamp(int(self.xml.find("CreateTime").text.strip()))
        if self.msgType.lower() == "event" :
            try :
                self.eventKey=self.xml.find("EventKey").text
            except :
                self.eventKey =""
            
        #define message parser class
        parser = {
          'text'    : self.parse_text ,
          "image"   : self.parse_image ,
          "voice"   : self.parse_voice,
          "video"   : self.parse_video,
          "location": self.parse_location,
          "LOCATION": self.parse_LOCATION,
          "link"    : self.parse_link,
          "event"   : self.parse_event,
        }
        self.event_parser = {
            "subscribe"  : self.evParse_subscribe,
            "scan"       : self.evParse_subscribe,
            "location"   : self.evParse_location,
            "click"      : self.evParse_subscribe,
            "view"       : self.evParse_subscribe,
        }
        
        if  parser.has_key(self.msgType) :
            parser[self.msgType]()
       
    
    def auto_reply(self):
        auto_replyer = {
              'text'    : self.reply_text ,
              "image"   : self.reply_image,
              "voice"   : self.reply_voice,
              "video"   : self.reply_video,
              "link"    : self.reply_news,
              "location": self.reply_location, 
        }
        if auto_replyer.has_key(self.msgType):
            retmsg = auto_replyer[self.msgType]() 
        else :
            retmsg = self.reply_text("消息类型为:  "+self.msgType)       
        return retmsg
        
    #<xml>
    #<ToUserName><![CDATA[toUser]]></ToUserName>
    #<FromUserName><![CDATA[fromUser]]></FromUserName> 
    #<CreateTime>1348831860</CreateTime>
    #<MsgType><![CDATA[text]]></MsgType>
    #<Content><![CDATA[this is a test]]></Content>
    #<MsgId>1234567890123456</MsgId>
    #</xml>   
    def parse_text(self):
        self.content=self.xml.find("Content").text
        
    def reply_text(self,content=""):  
        #缺省回复消息
        if content == "":
            content = self.content
        return self.render.reply_text(self.fromUser,self.toUser,int(time.time()),content)  
        
    #<xml>
    #<ToUserName><![CDATA[toUser]]></ToUserName>
    #<FromUserName><![CDATA[fromUser]]></FromUserName>
    #<CreateTime>1348831860</CreateTime>
    #<MsgType><![CDATA[image]]></MsgType>
    #<PicUrl><![CDATA[this is a url]]></PicUrl>
    #<MediaId><![CDATA[media_id]]></MediaId>
    #<MsgId>1234567890123456</MsgId>
    #</xml>  
    def parse_image(self):
        self.picUrl=self.xml.find("PicUrl").text
        self.mediaId=self.xml.find("MediaId").text
        
    def reply_image(self,mediaId=""):
        if mediaId=="" :
            mediaId = self.mediaId
        return self.render.reply_image(self.fromUser,self.toUser,int(time.time()),mediaId)  
    
    #<xml>
    #<ToUserName><![CDATA[toUser]]></ToUserName>
    #<FromUserName><![CDATA[fromUser]]></FromUserName>
    #<CreateTime>1357290913</CreateTime>
    #<MsgType><![CDATA[voice]]></MsgType>
    #<MediaId><![CDATA[media_id]]></MediaId>
    #<Format><![CDATA[Format]]></Format>
    #<MsgId>1234567890123456</MsgId>
    #</xml>        
    def parse_voice(self):
        self.format=self.xml.find("Format").text
        self.mediaId=self.xml.find("MediaId").text
    
    def reply_voice(self,mediaId=""):
        if mediaId=="" :
            mediaId = self.mediaId
        return self.render.reply_voice(self.fromUser,self.toUser,int(time.time()),mediaId)   
        
    #<xml>
    #<ToUserName><![CDATA[toUser]]></ToUserName>
    #<FromUserName><![CDATA[fromUser]]></FromUserName>
    #<CreateTime>1357290913</CreateTime>
    #<MsgType><![CDATA[video]]></MsgType>
    #<MediaId><![CDATA[media_id]]></MediaId>
    #<ThumbMediaId><![CDATA[thumb_media_id]]></ThumbMediaId>
    #<MsgId>1234567890123456</MsgId>
    #</xml>
    def parse_video(self):
        self.thumbMediaId=self.xml.find("ThumbMediaId").text
        self.mediaId=self.xml.find("MediaId").text

    def reply_video(self,mediaId="",title="",description=""):
        if mediaId=="" :
            mediaId       = self.mediaId
        return self.render.reply_video(self.fromUser,self.toUser,int(time.time()),mediaId,title,description)   
        
    #<xml>
    #<ToUserName><![CDATA[toUser]]></ToUserName>
    #<FromUserName><![CDATA[fromUser]]></FromUserName>
    #<CreateTime>1351776360</CreateTime>
    #<MsgType><![CDATA[location]]></MsgType>
    #<Location_X>23.134521</Location_X>
    #<Location_Y>113.358803</Location_Y>
    #<Scale>20</Scale>
    #<Label><![CDATA[位置信息]]></Label>
    #<MsgId>1234567890123456</MsgId>
    #</xml>     
    def parse_location(self):
        self.Latitude=self.xml.find("Location_X").text
        self.Longitude=self.xml.find("Location_Y").text   
        self.scale=self.xml.find("Scale").text   
        self.label=self.xml.find("Label").text   
 
    def parse_LOCATION(self):
        self.Latitude=self.xml.find("Latitude").text
        self.Longitude=self.xml.find("Longitude").text   
        self.Precision=self.xml.find("Scale").text   
 
    def reply_location(self):
        content  = "location_X : " +self.location_X
        content += "\r\nlocation_Y : " +self.location_Y
        content += "\r\nscale : " +self.scale
        content += "\r\naddress: " +self.label
        return self.render.reply_text(self.fromUser,self.toUser,int(time.time()),content)           
    #<xml>
    #<ToUserName><![CDATA[toUser]]></ToUserName>
    #<FromUserName><![CDATA[fromUser]]></FromUserName>
    #<CreateTime>1351776360</CreateTime>
    #<MsgType><![CDATA[link]]></MsgType>
    #<Title><![CDATA[公众平台官网链接]]></Title>
    #<Description><![CDATA[公众平台官网链接]]></Description>
    #<Url><![CDATA[url]]></Url>
    #<MsgId>1234567890123456</MsgId>
    #</xml> 
    def parse_link(self):
        self.title=self.xml.find("Title").text
        self.description=self.xml.find("Description").text
        self.url=self.xml.find("Url").text

    def reply_news(self,news=[]):
        if len(news) == 0 :
            news =[{
                "title"       : self.title,
                "description" : self.description,
                "picurl"      : "",
                "url"         : self.url,
                }]
        return self.render.reply_news(self.fromUser,self.toUser,int(time.time()),news)
        
    
    def reply_music(self,media_id="",description="",music_url="",hq_music_url=""):
        if media_id=="" :
            media_id       = self.mediaId
        return self.render.reply_video(self.fromUser,self.toUser,int(time.time()),description,music_url,hq_music_url,media_id)       
        
       
    def parse_event(self):
        self.event = self.xml.find("Event").text.lower()
        if  self.event_parser.has_key(self.event) :
            self.event_parser[self.event]()
    #<xml>
    #<ToUserName><![CDATA[toUser]]></ToUserName>
    #<FromUserName><![CDATA[FromUser]]></FromUserName>
    #<CreateTime>123456789</CreateTime>
    #<MsgType><![CDATA[event]]></MsgType>
    #<Event><![CDATA[subscribe]]></Event>
    #</xml> 
    
    #<xml><ToUserName><![CDATA[toUser]]></ToUserName>
    #<FromUserName><![CDATA[FromUser]]></FromUserName>
    #<CreateTime>123456789</CreateTime>
    #<MsgType><![CDATA[event]]></MsgType>
    #<Event><![CDATA[subscribe]]></Event>
    #<EventKey><![CDATA[qrscene_123123]]></EventKey>
    #<Ticket><![CDATA[TICKET]]></Ticket>
    #</xml>           
    
    #<xml>
    #<ToUserName><![CDATA[toUser]]></ToUserName>
    #<FromUserName><![CDATA[FromUser]]></FromUserName>
    #<CreateTime>123456789</CreateTime>
    #<MsgType><![CDATA[event]]></MsgType>
    #<Event><![CDATA[SCAN]]></Event>
    #<EventKey><![CDATA[SCENE_VALUE]]></EventKey>
    #<Ticket><![CDATA[TICKET]]></Ticket>
    #</xml>
    
    #<xml>
    #<ToUserName><![CDATA[toUser]]></ToUserName>
    #<FromUserName><![CDATA[FromUser]]></FromUserName>
    #<CreateTime>123456789</CreateTime>
    #<MsgType><![CDATA[event]]></MsgType>
    #<Event><![CDATA[CLICK]]></Event>
    #<EventKey><![CDATA[EVENTKEY]]></EventKey>
    #</xml>    
    
    #<xml>
    #<ToUserName><![CDATA[toUser]]></ToUserName>
    #<FromUserName><![CDATA[FromUser]]></FromUserName>
    #<CreateTime>123456789</CreateTime>
    #<MsgType><![CDATA[event]]></MsgType>
    #<Event><![CDATA[VIEW]]></Event>
    #<EventKey><![CDATA[www.qq.com]]></EventKey>
    #</xml>    
    def evParse_subscribe(self):
        self.ticket = ""
        self.eventKey = ""   
        try:
            self.eventKey = self.xml.find("EventKey").text
        except Exception,ex:
            print(ex)
    
        try:
            self.ticket = self.xml.find("Ticket").text 
        except Exception,ex:
            print(ex)
        
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
    def evParse_location(self):
        self.latitude = self.xml.find("Latitude").text
        self.longitude = self.xml.find("Longitude").text 
        self.precision = self.xml.find("Precision").text 
        
    #<xml>
    # <ToUserName><![CDATA[touser]]></ToUserName>
    # <FromUserName><![CDATA[fromuser]]></FromUserName>
    # <CreateTime>1399197672</CreateTime>
    # <MsgType><![CDATA[transfer_customer_service]]></MsgType>
    #</xml>    
    def reply_transfer_customer_service(self,kfcount=None):
        ret =  self.render.reply_transfer_customer_service(self.fromUser,self.toUser,self.CreateTime,kfcount)
        return ret
    