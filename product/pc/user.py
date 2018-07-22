# -*- coding: utf-8 -*-
import web,time,datetime,re,json,random
import product.iconfig as icfg
import product.iweixin.config as wxcfg
import utility as uTools
import logstat
from weixin.client import WeixinAPI
from weixin.oauth2 import OAuth2AuthExchangeError

class User:
    def __init__(self):
        templates_path =__file__.split(".py")[0]
        self.render = web.template.render(templates_path)

    def GET(self):
        data = web.input()
        self.env = icfg.getEnvObj()
        #openid =objWeixin.getOpenid(data)
        openid = "twsh"
        act =uTools.get_act(data)
        #logstat.logAccessUrl(openid,act) #记录用户访问
        if(act =="LOGIN"):
            ret = self.login(data)

        return ret
        
    def POST(self):
        data = web.input()
        self.env = icfg.getEnvObj()
        act =uTools.get_act(data)
        #openid =objWeixin.getOpenid(data)
        if act == 'GET-GROUP-BY-IMEI':
            pass
        return ret
        
    def login(self,data):
        redirect_uri = icfg.objWeixin.openapi.get_authorize_login_url(scope=("snsapi_login",),state=("pcweb_login",))
        return web.seeother(redirect_uri)
        

        
