# -*- coding: utf-8 -*-

import urllib2
import json

class MenuManager:
    #accessUrl = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=appid&secret=secret"
    delMenuUrl= "https://api.weixin.qq.com/cgi-bin/menu/delete?access_token="
    createUrl = "https://api.weixin.qq.com/cgi-bin/menu/create?access_token="
    getMenuUri= "https://api.weixin.qq.com/cgi-bin/menu/get?access_token="
    def __init__(self,userMsg):
        self.accessUrl = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=" + userMsg["appid"] + "&secret="+userMsg["secret"]
        self.accessToken = self.getAccessToken()
        self.menu = userMsg["menu"]
        
    def getAccessToken(self):
        req = urllib2.Request(self.accessUrl)
        response = urllib2.urlopen(req)
        accessT = response.read().decode("utf-8")
        jsonT = json.loads(accessT)
        return jsonT["access_token"]

    def delMenu(self):
        req  = urllib2.Request(self.delMenuUrl + self.accessToken)
        html = urllib2.urlopen(req)
        result = json.loads(html.read().decode("utf-8"))
        return result["errcode"]
        
    def createMenu(self):
        req  = urllib2.Request(self.createUrl + self.accessToken, self.menu)
        html = urllib2.urlopen(req)
        result = json.loads(html.read())
        return result["errcode"]
        #return 0

    def getMenu(self):
        html = urllib.request.urlopen(self.getMenuUri + self.accessToken)
        print(html.read().decode("utf-8"))
