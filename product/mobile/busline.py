# -*- coding: utf-8 -*-
import web
import os
import sys
import time
import datetime
import urllib
from product.iconfig import db,objWeixin,db
import product.iconfig as icfg
from product.mobile.tradeorder import tradeObj
import product.model.devdb as devdb
import product.model.busdb as busdb
import product.model.linedb as linedb

import utility as uTools
import logstat
import json

#应用程序的根路径


class BusLine:
    def __init__(self):
        templates_path =__file__.split('.py')[0]
        self.render = web.template.render(templates_path)
        self.env = icfg.getEnvObj()

    def GET(self):
        data = web.input()
        act = uTools.get_act(data)
        
        self.env = icfg.getEnvObj()
        openid = objWeixin.getOpenid(data)
        logstat.logAccessUrl(openid,act) #记录用户访问
        ret = None
        if act == 'BUSTRAVEL-CURRENT':
            ret = self.get_bustravel_current(openid,data)
        elif act =='BUSTRAVEL-DETAIL':
            ret = self.get_bustravel_detail(openid,data)
        return ret
        
    def POST(self):
        data = web.input()
        openid = objWeixin.getOpenid(data)
        act = data.act.upper()
        ret = None
        return ret
   
    def get_bustravel_current(self,openid,data):
        imei     = data.imei
        company  = linedb.getCompanyByImei(imei)
        dev      = devdb.getDeviceByImei(imei,format="string")
        
        cfgPara = busdb.getCurrentBusTravelStat(imei)
        if cfgPara==None:#暂时没有数据
            ret = web.seeother("/device?act=seat-status-auto&openid={0}&imei={1}&company_id={2}".format(openid,imei,company["id"]))
        else:
            cfgPara["name"]       =dev["name"]
            cfgPara["imei"]       =imei
            cfgPara["company_id"] =company["id"]
            
            jdksign  = objWeixin.get_jdk_sign(self.env["url"])
            sharePara=tradeObj.genPreSharePara("share-view",openid,imei)
            sharePara["manager"] = objWeixin.getManager(openid)
            sharePara["company_id"]  =company["id"]
            cfgPara = json.dumps(cfgPara,ensure_ascii=False)
            
            ret = self.render.bustravel_current(cfgPara,jdksign,sharePara)
        return ret
        
    def get_bustravel_detail(self,openid,data):
        span_id  = data.span_id
        cfgPara  = busdb.getDetailBusTravelStat(span_id)
        imei     = cfgPara["imei"]
        company  = linedb.getCompanyByImei(imei)
        dev      = devdb.getDeviceByImei(imei,format="string")


        cfgPara["name"]        =dev["name"]
        cfgPara["company_id"] =company["id"]
        cfgPara["openid"]     =openid        
        jdksign  = objWeixin.get_jdk_sign(self.env["url"])
        
        sharePara=tradeObj.genPreSharePara("share-view",openid,imei)
        sharePara["blank_color"]="#C0C0C0"
        sharePara["manager"]     = objWeixin.getManager(openid)
        sharePara["company_id"]  =company["id"]
        sharePara["openid"]      =openid
        cfgPara = json.dumps(cfgPara,ensure_ascii=False)
        
        ret = self.render.bustravel_detail(cfgPara,jdksign,sharePara)
        return ret