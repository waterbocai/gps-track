#----- -*- coding: utf-8 -*-
import web
import os
import sys
import time
import datetime
from product.iconfig import db,objWeixin,urlHome
import product.iconfig as icfg
from pweixin.userdb import userdb
import product.model.devdb as devdb
import urllib
import utility as uTools
import logstat
import product.model.linedb as linedb

import json

#应用程序的根路径


class Manager:
    def __init__(self):
        templates_path =__file__.split(".py")[0]
        self.render = web.template.render(templates_path)
        #print(templates_path)

    def GET(self):
        data = web.input()
        act = uTools.get_act(data)
        self.env = icfg.getEnvObj()
        self.url =self.env['url']
        openid = objWeixin.getOpenid(data)
        logstat.logAccessUrl(openid,act) #记录用户访问
        ret = ""
        if act   =='BUSLINE-HOME':
            ret = self.getCompanyBusLines(openid,data)
        elif act =='LINE-BUSES':
            ret = self.getLineBuses(openid,data)
        elif act =='HOME':
            ret = self.getCompanyBusLines(openid,data)
        elif act =='COMPANY-BUSES':
            ret = self.getCompanyBuses(openid,data)
        elif act =='DESIGN-LINE-SITE':
            ret = self.designLineSite(openid,data)
        elif act =='DESIGN-LINE-SITE-QQ':
            ret = self.designLineSiteQQ(openid,data)
        elif act =='DESIGN-LINE-PRICE':
            ret = self.designLinePrice(openid,data)
        elif act =='START-LINE-STAT':
            ret = self.startLineStat(openid,data)
        return ret

    def POST(self):
        data = web.input()
        if not data.has_key('act'):
            return
        act = data.act.upper()
        openid =objWeixin.getOpenid(data)
        if linedb.isEmployee(openid)==False:
            return web.seeother(urlHome)    
        if act == 'USER-POS':
            ret = self.postUserPos(openid,data)
        elif act == 'LINE-BUSES':
            ret = self.getLineBuses(openid,data)
        elif act =='COMPANY-BUSES':
            ret = self.getCompanyBuses(openid,data)
        elif act == 'SET-LINE-NAME':
            ret = self.setLineName(openid,data)
        elif act =='DELETE-LINE':
            ret = self.delLine(openid,data)
        elif act =='SET-LINE-SITE':
            ret = self.setLineSite(openid,data)
        elif act =='DEL-LINE-SITE':
            ret = self.delLineSite(openid,data)
        elif act =='UPDATE-LINE-SITE':
            ret = self.updateLineSite(openid,data)
        elif act =='UPDATE-ONE-SITE':
            ret = self.updateOneLineSite(openid,data)
        elif act =='UPDATE-LINE-PRICE':
            ret = self.updateLinePrice(openid,data)
        elif act =='SEND-MSG-COMPANY':
            return self.sendMsg2Company(openid,data)
        return ret
   
    
    def getCompanyBusLines(self,openid,data):
        jdkSign = objWeixin.get_jdk_sign(self.url)
        user = objWeixin.get_user_info2(openid,format="string")
        #获取openid对应的公司
        manager     = objWeixin.getManager(openid)
        company_mgr = linedb.getManageEmployee(openid)
        company_id  = uTools.get_data_value(data,"company_id",default=0)
        
        ret   = linedb.getBusLineByOpenid(openid,company_id)
        
        if len(ret["company_ids"])==0:#不是有效员工
            if manager!=None:#是管理员
                return web.seeother("/company?act=manager-home&openid={0}".format(openid))
            else:
                return web.seeother(icfg.urlHome)
        else:    
            company_id = ret["company_ids"][0]
            company    = linedb.getCompany(company_id,format="string")
            employee = linedb.getEmployeeByid(company_id,with_manager=True)
            cfgPara={"openid":openid,
                    "user"  :user,
                    "items" :ret["items"],
                    "company":company,
                    "employee":employee}
            #生成分享链接
            share_app_link = "{0}/m/company?act=cert-company&company_id={1}".format(self.env["homedomain"],company_id)
            share_app_title="扫一扫，成为-{0}-运营管理员 ".format(company["company"])
            mgr = ("manager" if manager!=None or company_mgr!=None else None) 
            fixPara = icfg.getFixPara(openid,manager=mgr,
                                            share_app_link=share_app_link,
                                            share_app_title = share_app_title,
                                            company_id = company_id)
            _cfgPara = json.dumps(cfgPara,ensure_ascii=False)
            ret = self.render.company_buslines(_cfgPara,jdkSign,fixPara)
        return ret
    
    def getCompanyBuses(self,openid,data):
        #manager = objWeixin.getManager(openid)
        #判定是否为赛维员工
        manager = linedb.getManageEmployee(openid)
        
        user = objWeixin.get_user_info2(openid,format="string")
        #获取公司信息
        company_id = uTools.get_data_value(data,"company_id",default=0)
        if company_id==0:
            companys = linedb.getCompanyByOpenid(openid,format="string")
            company  = companys[0]
            company_id=company["id"]
        else:
            company_id = int(company_id)
            company    = linedb.getCompany(company_id,format="string")
            
        items   = devdb.getBusesByCompany(openid,company["id"])
        
        if  web.ctx.method=='GET':
            jdkSign = objWeixin.get_jdk_sign(self.url)
            cfgPara={"openid":openid,
                     "devs"  :items,
                     "company":company,
                     "user"  :user}
            #生成分享链接
            share_app_link = "{0}/m/company?act=cert-company&company_id={1}".format(self.env["homedomain"],company_id)
            share_app_title="扫一扫，成为-{0}-运营管理员 ".format(company["company"])
            fixPara = icfg.getFixPara(openid,manager=manager,
                                                company_id=company["id"],
                                                company_name=company["company"],
                                                share_app_link=share_app_link,
                                                share_app_title = share_app_title,)
            _cfgPara = json.dumps(cfgPara,ensure_ascii=False)
            ret = self.render.company_buses(_cfgPara,jdkSign,fixPara)
        else:
            cfgPara={"devs":items,"result":"succuss"}
            ret = uTools.formatPostMsg(cfgPara)
        return ret 
        
    def getLineBuses(self,openid,data):
        _ret = db.query("SELECT * FROM BusLine WHERE id={0}".format(data.busline_id))
        busline =_ret[0]
        #判定是否为赛维员工
        manager = linedb.getManageEmployee(openid)
        items = devdb.getDeviceByGroupid(openid,busline.busgroupid)
        line_name = busline.from_name+" "+ busline.to_name
        if  web.ctx.method=='GET':
            jdkSign = objWeixin.get_jdk_sign(self.url)
            cfgPara={"openid":openid,
                     "items"  :items,
                     "busline_id"  :data.busline_id,
                     "busgroupid":busline.busgroupid,
                     "company_id":data.company_id,
                     "line_name" :line_name}
            fixPara = icfg.getFixPara(openid,manager=manager,
                                                busline_id=data.busline_id,
                                                busgroupid=busline.busgroupid,
                                                company_id=busline.company_id)
            _cfgPara = json.dumps(cfgPara,ensure_ascii=False)
            ret = self.render.line_buses(_cfgPara,jdkSign,fixPara)
        else:
            cfgPara={"items":items,"result":"succuss"}
            ret = uTools.formatPostMsg(cfgPara)
        return ret  
        
    def designLineSite(self,openid,data):
        jdkSign = objWeixin.get_jdk_sign(self.url)
        sites = [{"name":"无菊","addr":"云南省红河州金平县无菊酒吧","lat":223.1455,"lng":109.1231},{"name":"蒙自","addr":"云南省红河州蒙自县无菊酒吧","lat":223.1455,"lng":109.1231}]
        cfgPara={"openid":openid,"sites":sites}
        _cfgPara = json.dumps(cfgPara,ensure_ascii=False)
        ret = self.render.line_sites(_cfgPara,jdkSign,icfg.getFixPara(openid))
        return ret

    def designLineSiteQQ(self,openid,data):
        jdkSign = objWeixin.get_jdk_sign(self.url)
        #对站点进行排序
        
        if data.has_key('busline_id'):#已有的线路重新调整
            sites = linedb.getSitesByLineid(data.busline_id,"manual")
            busline = linedb.getBuslineByid(data.busline_id,format="string")
            linedb.orderLineSiteSeq(busline["id"])
        else:#创建新的线路 
            sites = {"manual":[],"auto":[]}
            busline ={"id":-1,"from_name":"","to_name":""}
        user = userdb.getUserByOpenid(objWeixin.weixinName,openid)

        cfgPara={"openid":openid,
                 "sites":sites,
                 "user":user,
                 "busline":busline,
                 "company_id":data.company_id}
        fixPara = icfg.getFixPara(openid,busline = busline,company_id=data.company_id)
        _cfgPara = json.dumps(cfgPara,ensure_ascii=False)
        ret = self.render.line_sites_qq(_cfgPara,jdkSign,fixPara)
        return ret

    def postUserPos(self,openid,data):
        user = userdb.getUserByOpenid(objWeixin.weixinName,openid)
        cfgPara = uTools.formatPostMsg({"user":user})
        return cfgPara
        
        
    def setLineName(self,openid,data):
        busline_id=int(data.busline_id)
        company_id=int(data.company_id)
        if busline_id==-1:#新线路
            busgroupid=db.insert("DeviceGroup",belong_to="company",
                                                   type="管理分组",
                                                   created_at     =datetime.datetime.now(),
                                                   Customer_openid=openid,
                                                   description    ="gxsaiwei",
                                                   name = 'dengchewang')
            
            busline_id = db.insert("BusLine",from_name =data.src,
                                         to_name   =data.dst,
                                         busgroupid=busgroupid,
                                         created_at=datetime.datetime.now(),
                                         company_id=company_id)
        else:
            db.update("BusLine",where="id=$data.busline_id",vars=locals(),
                                         from_name =data.src,
                                         to_name   =data.dst,
                                         created_at=datetime.datetime.now(),
                                         company_id=company_id)
        buslines=linedb.getBusLineByOpenid4pc(openid,company_id)
        cfgPara = uTools.formatPostMsg({"result":"success","buslines":buslines})
        return cfgPara
        
    def delLineSite(self,openid,data):
        busline_id = data.busline_id
        site_seq    = data.site_seq
        #获取站点信息
        #print("SELECT * FROM LineSites WHERE busline_id={0} AND seq={1}".format(busline_id,data.site_seq))
        _ret = db.query("SELECT * FROM LineSites WHERE busline_id={0} AND seq={1}".format(busline_id,site_seq))
        linesite = _ret[0]
        
        #删除LineSite的站点
        db.query("DELETE FROM LineSites WHERE id={0}".format(linesite.id))
        #删除Sites站点信息
        db.query("DELETE FROM Sites WHERE id={0}".format(linesite.site_id))
        linedb.orderLineSiteSeq(busline_id)
        sites = linedb.getSitesByLineid(busline_id)
        cfgPara = uTools.formatPostMsg({"result":"success","msg":"busline delete succeed！","sites":sites})
        return cfgPara
        
    def setLineSite(self,openid,data):
        busline_id = data.busline_id
        _ret = db.query("SELECT MAX(seq)  AS max_seq FROM LineSites WHERE busline_id = {0}".format(busline_id))
        max_seq = _ret[0].max_seq
        changeType = data.changeType
        #新加入的站点
        if changeType=="add-new":
            #依据微信上报信息获取位置信息
            _ret = db.query("SELECT * FROM Customer WHERE openid='{0}'".format(openid))
            user = _ret[0]
            site_id = db.insert("Sites",gpsLat=user.gpsLat,gpsLng=user.gpsLng,
                                       baiduLat=user.baiduLat,baiduLng=user.baiduLng,
                                       qqLat=user.qqLat,qqLng=user.qqLng,
                                       name = data.name,address=user.address,
                                       setting_type="manual")
            db.insert("LineSites",site_id=site_id,seq = max_seq+1,busline_id=busline_id)
            
        else:
            _ret = db.query("SELECT * AS sum FROM LineSites WHERE busline_id = {0} AND seq={1}".format(busline_id,data.old_seq))
            linesite =_ret[0]
            site_id = linesite.site_id
            db.update("Sites",where="id=$site_id",
                                       name = data.name,vars=locals())
            db.update("LineSites",where="id=$site_id",vars=locals(),seq = data.new_seq)
        linedb.orderLineSiteSeq(busline_id)
        sites = linedb.getSitesByLineid(busline_id)
        cfgPara = uTools.formatPostMsg({"result":"success","msg":"busline config succeed！","sites":sites})
        return cfgPara 
    

        
    
    def setLineSite2(self,openid,data):
        busline_id = data.busline_id
        _ret = db.query("SELECT COUNT(*) AS sum FROM LineSites WHERE busline_id = {0}".format(busline_id))
        site_sum = _ret[0]
        #新加入的站点
        if (site_sum<data.old_seq):
            changeType ="add-new" #缺省是增加新站点
        else:
            changeType="renew-old"
            _ret = db.query("SELECT * AS sum FROM LineSites WHERE busline_id = {0} AND seq={1}".format(busline_id,data.old_seq))
            linesite =_ret[0]
        
        #调整现有站点顺序
        if (data.new_seq < data.old_seq):#站点向前调整顺序
            changeSites = db.query("SELECT * FROM LineSites WHERE seq>={0} AND seq<{1}".format(data.new_seq,data.old_seq))
            for site in changeSites:
                db.update("LineSites",where="id=$site.id",seq=site.seq+1,vars=locals())
        else: 
            changeSites = db.query("SELECT * FROM LineSites WHERE seq>{0} AND seq<={1}".format(data.old_seq,data.new_seq))
            for site in changeSites:
                db.update("LineSites",where="id=$site.id",seq=site.seq-1,vars=locals())
        
        if changeType=="add-new":
            #依据微信上报信息获取位置信息
            _ret = db.query("SELECT * FROM Customer WHERE openid='{0}'".format(openid))
            user = _ret[0]
            site_id = db.insert("Sites",gpsLat=user.gpsLat,gpsLng=user.gpsLng,
                                       baiduLat=user.baiduLat,baiduLng=user.baiduLng,
                                       qqLat=user.qqLat,qqLng=user.qqLng,
                                       name = data.name,address=user.address,
                                       setting_type="manual")
            db.insert("LineSites",site_id=site_id,seq = data.new_seq,busline_id=busline_id)
        else:
            site_id = linesite.site_id
            db.update("Sites",where="id=$site_id",
                                       name = data.name,vars=locals())
            db.update("LineSites",where="id=$linesite,id",seq = data.new_seq)
        sites = linedb.getSitesByLineid(busline_id)
        cfgPara = uTools.formatPostMsg({"result":"success","msg":"busline config succeed！","sites":sites})
        return cfgPara   
    
    def delLine(self,openid,data):
        busline_id = data.busline_id
        _ret = db.query("SELECT * FROM BusLine WHERE id = {0}".format(busline_id))
        busline = _ret[0]
        #确认该线路下没有班车队
        ret = db.query("""SELECT COUNT(*) AS sum FROM GroupHasDevice WHERE devicegroup_id={0}""".format(busline.busgroupid))
        if ret[0].sum > 0:#还有车队，不能删除
            cfgPara ={"result":"fail","msg":"busgroup is not empty!"}
        else:
            lineSites = db.query("SELECT * FROM LineSites WHERE busline_id={0}".format(busline.id))
            for lineSite in lineSites:
                db.query("DELETE FROM Sites WHERE id={0}".format(lineSite.site_id))
            #删除该线路的站点信息
            db.query("DELETE FROM LineSites WHERE busline_id={0}".format(busline.id))
            #删除该线路信息
            db.query("DELETE FROM BusLine WHERE id={0}".format(busline.id))
            cfgPara ={"result":"success","msg":"busline delete succeed！"}
        cfgPara = uTools.formatPostMsg(cfgPara)
        return cfgPara
        
    def designLinePrice(self,openid,data):
        jdkSign = objWeixin.get_jdk_sign(self.url)
        busline_id = data.busline_id
        company_id =data.company_id
        #获取相关数据
        sites = linedb.getSitesByLineid(busline_id)
        prices= linedb.getLinePrice(busline_id)
        _ret = db.query("SELECT * FROM BusLine WHERE id = {0}".format(busline_id))
        busline = _ret[0]
        line_name = busline.from_name +"-" + busline.to_name
        #结果拼装
        cfgPara={"openid":openid,
                 "sites":sites,
                 "prices":prices,
                 "line_name":line_name,
                 "busline_id":busline_id,
                 "company_id":company_id}

        fixPara = icfg.getFixPara(openid,busline_id = busline_id,company_id=company_id)
        _cfgPara = json.dumps(cfgPara,ensure_ascii=False)
        ret = self.render.design_line_price(_cfgPara,jdkSign,fixPara)
        return ret
        
    def updateLinePrice(self,openid,data):
        busline_id = data.busline_id
        price      = data.price
        site_ids   = data.site_id.split("-")
        from_site_id =int(site_ids[0])
        to_site_id   =int(site_ids[1])
        _ret = db.query("""SELECT * FROM LinePrice 
                                             WHERE BusLine_id={0} AND 
                                                   from_site_id={1} AND 
                                                   to_site_id  ={2} """.format(busline_id,from_site_id,to_site_id))
        if len(_ret)==1:
            db.update("LinePrice",where="id=$_ret[0].id",price=price,vars=locals())
        else:
            db.insert("LinePrice",price=price,BusLine_id=busline_id,from_site_id=from_site_id,to_site_id=to_site_id)
        cfgPara = uTools.formatPostMsg({"result":"success","msg":"lineprice update succeed！"})
        return cfgPara
    
    def updateLineSite(self,openid,data):
        busline_id = int(data.busline_id)
        name_change  = data.name_change.split(";")
        end_change  = data.end_change.split(";")
        #名称修改
        
        for site_name in name_change:
            if site_name=="":
                continue
            site_id,name =site_name.split(":")
            site_id = int(site_id)
            db.update("Sites",where="id=$site_id",name=name,vars=locals())
        #序号变更
        for endchange in end_change:
            if endchange=="":
                continue
            seq,is_end =endchange.split(":")
            seq = int(seq)
            db.update("LineSites",where="busline_id=$busline_id AND seq=$seq",is_end=is_end,vars=locals())
            
        sites = linedb.getSitesByLineid(busline_id)
        cfgPara = uTools.formatPostMsg({"result":"success","msg":"busline config succeed！","sites":sites})
        return cfgPara 
        
    def updateOneLineSite(self,openid,data):
        site_id      =data.site_id
        name         =(data.name if data.has_key("name")  else None)
        setting_type =(data.setting_type if data.has_key("setting_type")  else None)
        if name !=None and setting_type!=None:
            if setting_type!="manual":
                setting_type = None
            
            db.update("Sites",where="id=$site_id",name=name,setting_type=setting_type,vars=locals())
        if name ==None and setting_type!=None:
            if setting_type!="manual":
                setting_type = None
            db.update("Sites",where="id=$site_id",setting_type=setting_type,vars=locals())
        if name !=None and setting_type==None:
            db.update("Sites",where="id=$site_id",name=name,vars=locals())
        cfgPara = uTools.formatPostMsg({"result":"success","msg":"update site succeed!"})
        return cfgPara    
            
            
    #启动线路批量统计    
    def startLineStat(self,openid,data):
        busline_id = data.busline_id
        company_id = data.company_id
        
        _ret = db.query("SELECT * FROM BusLine WHERE id={0}".format(busline_id))
        busline =_ret[0]
        
        items = devdb.getDeviceByGroupid(openid,busline.busgroupid)
        line_name = busline.from_name+" "+ busline.to_name
        
        jdkSign = objWeixin.get_jdk_sign(self.url)
        fixPara = icfg.getFixPara(openid,busline_id = busline_id,company_id=company_id)
        
        cfgPara={"openid"    :openid,
                 "buses"     :items,
                 "busline_id":busline_id,
                 "company_id":company_id,
                 "line_name":line_name}
        _cfgPara = json.dumps(cfgPara,ensure_ascii=False)
        ret = self.render.start_busline_stat(_cfgPara,jdkSign,fixPara)
        return ret
        
    #启动线路批量统计    
    def startSingleBusStat(self,openid,data):
        busline_id = data.busline_id
        company_id = data.company_id
        imei       = data.imei
        
        
        jdkSign = objWeixin.get_jdk_sign(self.url)
        fixPara = icfg.getFixPara(openid,busline_id = busline_id,company_id=company_id)
        
        cfgPara={"openid"    :openid,
                 "busline_id":busline_id,
                 "company_id":company_id,
                 "imei"      :imei}
        _cfgPara = json.dumps(cfgPara,ensure_ascii=False)
        ret = self.render.start_bus_stat(_cfgPara,jdkSign,fixPara)
        return ret
        
    def sendMsg2Company(self,openid,data):
        company_id = data.company_id
        msg     = data.msg
        employee = linedb.getEmployeeByid(company_id,with_manager=True)
        
        cmpHomeLink=objWeixin.getAuth2Url("{0}/m/manager?act=home".format(web.ctx.homedomain))
        systemMsg = objWeixin.iconfig.systemMsg
        systemMsg["url"]  =cmpHomeLink
        systemMsg["data"]["keyword2"]["value"] =datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        systemMsg["data"]["first"]["value"]   ="座位统计报告"
        systemMsg["data"]["keyword1"]["value"]="赛微消息"
        systemMsg["data"]["remark"]["value"]="\r\n   "+msg
 
        systemMsg["touser"] = openid
        openids =[openid]
        objWeixin.send_template_msg(systemMsg)
        
        for item in employee:
            if item["privilege"]=="manager" and (item["openid"] not in openids):
                systemMsg["touser"] = item["openid"]
                openids.append(item["openid"])
                objWeixin.send_template_msg(systemMsg)
        return
        