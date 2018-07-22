# -*- coding: utf-8 -*-
import web,time,datetime,re,json,random
import product.iconfig as icfg
import utility as uTools

class Tool:
    def __init__(self):
        templates_path =__file__.split(".py")[0]
        self.render = web.template.render(templates_path)

    def GET(self):
        data = web.input()
        self.env = icfg.getEnvObj()
        #openid = "twsh"
        act =uTools.get_act(data)
        #logstat.logAccessUrl(openid,act) #记录用户访问
        if(act =="ADD-UNIONID"):
            ret = self.relateUserId(data)
        return ret
    
    def POST(self):
        data = web.input()
        self.env = icfg.getEnvObj()
        act =uTools.get_act(data)
        ret = ""
        return ret
        
        
    def relateUserId(self,data):
        customers = icfg.db.query("SELECT * FROM Customer")
        for user in customers:
            wxuser = icfg.objWeixin.get_user_info(user.openid)
            openid = wxuser["openid"]
            icfg.db.update("Customer",where="openid=$openid",vars=locals(),unionid=wxuser["unionid"])
        return
    
