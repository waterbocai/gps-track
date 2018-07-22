# -*- coding: utf-8 -*-
import os
import sys
#add parent directory to sys.path
sys.path.append(os.path.split(os.path.dirname(__file__))[0])

#import pylibmc
from common import templates_root
from message import GetMessage,PostMessage
from event import Subscribe

subscribe_xml="""
  <xml>
  <ToUserName><![CDATA[toUser]]></ToUserName>
  <FromUserName><![CDATA[FromUser]]></FromUserName>
  <CreateTime>123456789</CreateTime>
  <MsgType><![CDATA[event]]></MsgType>
  <Event><![CDATA[subscribe]]></Event>
  </xml>""" 
msg = PostMessage(subscribe_xml) 
print Subscribe("test").run(msg)

#subscribe_xml="""
#    <xml><ToUserName><![CDATA[toUser]]></ToUserName>
#    <FromUserName><![CDATA[FromUser]]></FromUserName>
#    <CreateTime>123456789</CreateTime>
#    <MsgType><![CDATA[event]]></MsgType>
#    <Event><![CDATA[subscribe]]></Event>
#    <EventKey><![CDATA[qrscene_123123]]></EventKey>
#    <Ticket><![CDATA[TICKET]]></Ticket>
#    </xml> """
#msg = PostMessage(subscribe_xml) 
#print msg.event=="subscribe" 
#print msg.eventKey=="qrscene_123123"  
#print msg.ticket=="TICKET"  
#subscribe_xml ="""   
#    <xml>
#    <ToUserName><![CDATA[toUser]]></ToUserName>
#    <FromUserName><![CDATA[FromUser]]></FromUserName>
#    <CreateTime>123456789</CreateTime>
#    <MsgType><![CDATA[event]]></MsgType>
#    <Event><![CDATA[SCAN]]></Event>
#    <EventKey><![CDATA[SCENE_VALUE]]></EventKey>
#    <Ticket><![CDATA[TICKET]]></Ticket>
#    </xml>"""
#msg = PostMessage(subscribe_xml) 
#print msg.event=="SCAN".lower()      
#print msg.eventKey=="SCENE_VALUE"  
#print msg.ticket=="TICKET" 
#subscribe_xml ="""       
#    <xml>
#    <ToUserName><![CDATA[toUser]]></ToUserName>
#    <FromUserName><![CDATA[FromUser]]></FromUserName>
#    <CreateTime>123456789</CreateTime>
#    <MsgType><![CDATA[event]]></MsgType>
#    <Event><![CDATA[CLICK]]></Event>
#    <EventKey><![CDATA[EVENTKEY]]></EventKey>
#    </xml>    """
#msg = PostMessage(subscribe_xml) 
#print msg.event=="CLICK".lower()      
#print msg.eventKey=="EVENTKEY" 
#subscribe_xml ="""       
#    <xml>
#    <ToUserName><![CDATA[toUser]]></ToUserName>
#    <FromUserName><![CDATA[FromUser]]></FromUserName>
#    <CreateTime>123456789</CreateTime>
#    <MsgType><![CDATA[event]]></MsgType>
#    <Event><![CDATA[VIEW]]></Event>
#    <EventKey><![CDATA[www.qq.com]]></EventKey>
#    </xml>"""
#msg = PostMessage(subscribe_xml) 
#print msg.event=="VIEW".lower()      
#print msg.eventKey=="www.qq.com"  
#subscribe_xml ="""   
#    <xml>
#    <ToUserName><![CDATA[toUser]]></ToUserName>
#    <FromUserName><![CDATA[fromUser]]></FromUserName>
#    <CreateTime>123456789</CreateTime>
#    <MsgType><![CDATA[event]]></MsgType>
#    <Event><![CDATA[LOCATION]]></Event>
#    <Latitude>23.137466</Latitude>
#    <Longitude>113.352425</Longitude>
#    <Precision>119.385040</Precision>
#    </xml>  """ 
#msg = PostMessage(subscribe_xml) 
#print msg.event=="LOCATION".lower()      
#print msg.latitude=="23.137466" 
#print msg.longitude=="113.352425" 
#print msg.precision=="119.385040" 