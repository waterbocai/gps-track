# -*- coding: utf-8 -*-

import urllib  
import urllib2  
from urllib import urlencode 
import json  
import sys
import web 
import time
import random
import string
import hashlib
from config import db
import datetime 

def getOpenid(userMsg,data):
    if data.has_key("openid"):
        openid = data.openid
    else:
        openid = oauth2_openid(userMsg,data.code)
    return openid
        
def oauth2_openid(userMsg,code,come_from=""):
    accessUrl = "https://api.weixin.qq.com/sns/oauth2/access_token?grant_type=authorization_code&appid=" + userMsg["appid"] + "&secret="+userMsg["secret"]+"&code="+code
    f = urllib2.urlopen(accessUrl)
    stringjson = json.loads(f.read().decode("utf-8"))
    try:
        openid =  stringjson['openid']
    except:
        print stringjson
        openid = "error_openid"
    #print "%s -stringjson:%s"%(come_from,stringjson)
    #print "code:"+code
    #print stringjson
    return openid
    
def post(url, data): 
    #data = urllib.urlencode(data)
    jdata = json.dumps(data,ensure_ascii=True)
    req = urllib2.Request(url,jdata)
    response = urllib2.urlopen(req)
    the_page = response.read()
    print the_page
    ret = urllib.unquote(the_page)
    return ret
    
class WXManager:
    comUrl   = "https://api.weixin.qq.com/cgi-bin/"
    comToken = "?access_token="
    def __init__(self,userMsg):
        self.userMsg = userMsg
        self.accessToken = self.getAccessToken()
    
    def cmdUrl(self,cmd):
        comUrl = "https://api.weixin.qq.com/cgi-bin/"+cmd+ "?access_token=" + self.accessToken
        return comUrl
         
    def getAccessToken(self):
        accessUrl = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=" + self.userMsg["appid"] + "&secret="+self.userMsg["secret"]
        f = urllib2.urlopen(accessUrl)
        stringjson = f.read()   
        access_token = json.loads(stringjson)['access_token']
        return access_token

    def delMenu(self):
        req  = urllib2.Request(self.cmdUrl("menu/delete"))
        html = urllib2.urlopen(req)
        result = json.loads(html.read().decode("utf-8"))
        return result["errcode"]
        
    def createMenu(self,menu):
        f  = urllib2.urlopen(url = self.cmdUrl("menu/create"), data = menu.encode('utf-8'))
        return f.read()
        #return 0
    def getMenu(self):
        html  = urllib2.urlopen(self.cmdUrl("menu/get"))
        return html.read().decode("utf-8")
    
    def getGroups(self):
        html  = urllib2.urlopen(self.cmdUrl("groups/get"))
        return html.read().decode("utf-8")
    
    def createGroup(self,name,id):
        group = '''
          {
            "group": {
                "id": ''' + id +''',
                "name" :"'''+name+ '''
            }
        }'''
         
        html  = urllib2.urlopen(self.cmdUrl("groups/create"),group.encode('utf-8'))
        return html.read().decode("utf-8")
    
    def moveMember2Group(self,openid,to_groupid):
        sto_groupid = '%d' %to_groupid
        group = '''{"openid":"''' + openid +'''","to_groupid":'''+sto_groupid +"}"
        html  = urllib2.urlopen(self.cmdUrl("groups/members/update"),group.encode('utf-8'))
        return html.read().decode("utf-8")
     
    def createQcode(self,scene_id,expire_seconds=0):
        sscene_id= '%d' %scene_id 
        if expire_seconds == 0:
            args = '''{"action_name": "QR_LIMIT_SCENE", "action_info": {"scene": {"scene_id":'''+ sscene_id +'}}}'
        else :
            args = '''{"expire_seconds":'''+ expire_seconds+''', "action_name": "QR_SCENE", "action_info": {"scene": {"scene_id":'''+ sscene_id+'''}}}'''
        html  = urllib2.urlopen(self.cmdUrl("qrcode/create"),args.encode('utf-8'))
        result =  json.loads(html.read().decode("utf-8"))
        return result

    def getUser(self,openid,lang="zh_CN"):
        html  = urllib2.urlopen(self.cmdUrl("user/info")+"&openid="+openid+"&lang="+lang)
        result =  json.loads(html.read().decode("utf-8"))
        if result.has_key('nickname')==False:
            #print result
            #print openid
            raise web.seeother(self.userMsg['home'])
        else:
            return result
        
    def sendText2Customer(self,openid,content):
        openid = openid.decode('utf-8')
        openid = openid.encode('ascii')
        content = content.decode('utf-8')
        content = content.encode('ascii')
        message = {"text": 
                    {
                        "content": content
                    }, 
                   "msgtype": "text", 
                   "touser": openid
        }
        print "sendText2Customer:----"
        print message
        print self.cmdUrl("message/custom/send")
        
        ret = post(self.cmdUrl("message/custom/send"),message)
        return ret
        
    def getJsapiTicket(self):
        _ret = db.query("SELECT * FROM GlobalPara WHERE name='jsapi_ticket'")
        if len(_ret) == 0:
            html  = urllib2.urlopen(self.cmdUrl("ticket/getticket")+"&type=jsapi")
            ret =  json.loads(html.read().decode("utf-8"))
            ticket = ret['ticket']
            db.insert("GlobalPara",name = 'jsapi_ticket',value=ticket,create_at=datetime.datetime.now())
        else:
            jsapi_ticket = _ret[0]
            ticket     =jsapi_ticket.value
            create_at  =jsapi_ticket.create_at
            if time.time()>=time.mktime(create_at.timetuple())+7200:
                html  = urllib2.urlopen(self.cmdUrl("ticket/getticket")+"&type=jsapi")
                ret =  json.loads(html.read().decode("utf-8"))
                ticket = ret['ticket']
                db.insert("GlobalPara",name = 'jsapi_ticket',value=ticket,create_at=datetime.datetime.now())
        return ticket
        

class JSJDKSign:
    def __init__(self,appid):
        self.appid = appid

    def __create_nonce_str(self):
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(15))

    def __create_timestamp(self):
        return int(time.time())

    def jdkSign(self,jsapi_ticket, url,nonceStr="",timestamp=""):
        test = True
        if nonceStr== "":
            test = False
            nonceStr  = self.__create_nonce_str()
        if timestamp=="":
            timestamp = self.__create_timestamp()
        #处理url中#字符情况
        temp= url.split("#")[0]
        ret = {
            'nonceStr': nonceStr,
            'jsapi_ticket': jsapi_ticket,
            'timestamp': timestamp,
            'url': temp
        }
        string = '&'.join(['%s=%s' % (key.lower(), ret[key]) for key in sorted(ret)])
        ret['signature'] = hashlib.sha1(string).hexdigest()
        ret['appid'] = self.appid
        ret['url'] = url
        #ret['string'] = string
        return ret
    
    def paySign(self,prepay_id,nonceStr="",timestamp="",appid="",package=""):
        test = True
        if nonceStr== "":
            test = False
            nonceStr  = self.__create_nonce_str()
        if timestamp=="":
            timestamp = self.__create_timestamp()
        if appid =="" :
            appid = self.appid
        if package=="":
            package = 'prepay_id={0}'.format(prepay_id)
        if appid =="":
            appid = self.appid
        
        ret = {
            'appId'    :appid,
            'timestamp': timestamp,
            'nonceStr' : nonceStr,
            'package'  : package,
            'signType' :'MD5',
        }
        string = '&'.join(['%s=%s' % (key.lower(), ret[key]) for key in sorted(ret)])
        ret['paySign'] = hashlib.sha1(string).hexdigest().upper()
        if test:
            ret['string'] = string
        return ret
        
