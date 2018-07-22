# -*- coding: utf-8 -*-
import web,time,datetime,re,json,random
import product.iconfig as icfg
import product.model.linedb as linedb
import product.model.devdb as devdb
from product.model.historytrackmgr import historyTrackMgr
import utility as uTools
import logstat


class Manager:
    def __init__(self):
        templates_path =__file__.split(".py")[0]
        self.render = web.template.render(templates_path)

    def GET(self):
        data = web.input()
        self.env = icfg.getEnvObj()
        openid = icfg.objWeixin.getOpenid(data)
        #openid = "twsh"
        act =uTools.get_act(data)
        #logstat.logAccessUrl(openid,act) #记录用户访问
        if(act=='GET-MANAGER-CENTER'):
            ret =self.getManagerCenter(openid,data)
        return ret
        
    def POST(self):
        data = web.input()
        self.env = icfg.getEnvObj()
        act =uTools.get_act(data)
        openid =icfg.objWeixin.getOpenid(data)
        if(act=='GET-MANAGER-CENTER'):
            ret =self.getManagerCenter(openid,data)
        return ret
        
    def getManagerCenter(self,openid,data):
        country  =None
        province =None
        city     =None
        district =None
        if data.has_key("country") and  data.country!="":
            country = data.country
        if data.has_key("province") and  data.province!="":
            province = data.province
        if data.has_key("city") and  data.city!="":
            city = data.city
        if data.has_key("district") and  data.district!="":
            district = data.district
         
        cfgPara = linedb.getCompanyRegion(country,province,city,district)
        
        if  web.ctx.method=='GET':
            user   = icfg.objWeixin.get_user_info2(openid,format="string")
            fixPara={}
            cfgPara["openid"]=openid
            cfgPara["user"]  =user
            _cfgPara = json.dumps(cfgPara,ensure_ascii=False)
            ret = self.render.manager_center(_cfgPara,fixPara)
        else:
            ret =uTools.formatPostMsg(cfgPara)
        return ret
