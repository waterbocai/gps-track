# -*- coding: utf-8 -*-
import hashlib
import web
#import lxml
import time
import os
import urllib2,json
import sys
#add parent directory to sys.path
sys.path.append(os.path.split(os.path.dirname(__file__))[0])

#from lxml import etree
#import pylibmc
from common import templates_root
from message import GetMessage,PostMessage
class Data :
    def __init__(self):
        self.signature="62f883efec0de69cac4cb4f23c706b36db1ce28a"
        self.echostr="5990745519727602978"
        self.timestamp="1394634018"
        self.nonce="1394829133"
    
data =Data()
print data.signature
msg = GetMessage(data)
if msg.is_from_weixin():
    print msg.echostr