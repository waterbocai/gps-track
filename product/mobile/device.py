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


class Device:
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
        ret = ""
        if act == 'SEAT-STATUS-AUTO':
            ret = self.getSeatsByImeiAuto("customer",openid,data)
        elif act == 'SEAT-STATUS-DEBUG':
            ret = self.getSeatsByImeiDebug("operator",openid,data)
        elif act =="SEAT-STATUS-TEST":
            #ret = self.getSeatsByImeiAuto("operator",openid,data)
            ret = self.getSeatsByImeiDebug("operator",openid,data)
        elif act =="SEAT-STATUS-HIS":
            ret = self.getSeatsByImeiAuto("operator-history",openid,data)
        elif act =="ABOUT" :
            ret = self.getBusConfigMsg(data)
        elif act =="BUS-CONFIG" :
            ret = self.getBusConfigMsg(data)
        elif act =='BIND-NEW-DEVICE':
            ret = self.bindNewDeviceMsg(openid,data)
        elif act == 'FRIEND-MANAGER':
            ret = self.friendManager(openid,data.imei)
        elif act =='ONLINE-TEST':
            ret = self.getOnlineTestViewMsg(openid)
        elif act =='GET-ONLINE-STATE':
            ret = self.getOnlineState(openid,data)
        return ret
        
    def POST(self):
        data = web.input()
        openid = objWeixin.getOpenid(data)
        act = data.act.upper()
        if act =="ABOUT" :
            ret = self.getAboutMsg(data)
        elif act == 'SEAT-STATUS-AUTO':
            ret = self.getSeatsByImeiAuto("customer",openid,data)
        elif act == 'SEAT-STATUS-DEBUG':
            ret = self.getSeatsByImeiDebug("operator",openid,data)
        elif act == 'SEAT-STATUS-TEST':
            #ret = self.getSeatsByImeiAuto("operator",openid,data)
            ret = self.getSeatsByImeiDebug("operator",openid,data)
        elif act == 'SEAT-BUSBOX-DEBUG':
            #ret = self.getSeatsByImeiAuto("operator",openid,data)
            ret = self.getSeatsBusboxDebug("operator",openid,data)
        elif act =='BIND-NEW-DEVICE':
            ret = self.bindNewDeviceMsg(openid,data)
        elif act =="UPDATE-DEVICE":
            ret = self.updateManagerDeviceGroup(openid,data)
        elif act =="UPDATE-DEVICE-CFG":
            ret = self.updateDeviceCfg(openid,data)
        elif act == 'FRIEND-MANAGER':
            return self.friendManager(openid,data.imei)
        elif act =='UPDATE-SHARE-PRIVILEGE':
            ret = self.updateSharePrivilege(openid,data)
        elif act =="CFG-BUS-SEAT":
            ret = self.cfgBusSeat(openid,data)
        elif act =='ONLINE-TEST':
            ret = self.getOnlineTestViewMsg(openid)
        elif act =='GET-ONLINE-STATE':
            ret = self.getOnlineState(openid,data)
        return ret
   
    #roleType:指示Customer，Operator
    def getSeatsByImeiAuto(self, roleType,openid,data):
        if data.has_key("imei"):
            imei = data.imei
        else:
            imei = devdb.getDemoDeviceImei() #演示大巴
        #判定该用户对imei的可视权限--暂缺
        if data.has_key("his_datetime") or roleType=="operator-history":
            if data.has_key("his_datetime"):
                his_datetime = data.his_datetime  
            else:
                his_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                seatStatus= busdb.getSeatStatus(imei,his_datetime)  
        else:
            seatStatus  = busdb.getSeatStatus(imei)
            
        cfgPara=seatStatus["param"]
        
        _typeMap = {"region":"区间检测","timer":"定时分析","timely":"及时数据"}
        if seatStatus["region"]!=None:
            _type="region"
        elif seatStatus["timer"]!=None:
             _type="timer"
        else:
            _type="timely"
        
        cfgPara["srcType"] =_typeMap[_type]
        for key in seatStatus[_type]:
            cfgPara[key] = seatStatus[_type][key]
        
        
        dev      = devdb.getDeviceByImei(imei,format="string")
        company  = linedb.getCompanyByImei(imei)
        
        cfgPara["name"]        =dev["name"]
        cfgPara["dev"]         =dev
        cfgPara["company_id"]  =company["id"]
        cfgPara["heartbeat_at"]=dev["heardbeat_at"]
        cfgPara["openid"]      =openid
        #修正统计座位数
        seat_num = 0
        for seat in dev["seat_template"].split(";"):
            if seat.split(",")[0]!="":
                seat_num+=1
        cfgPara["seat_num"] = seat_num
        cfgPara["sum"]["空座"] = seat_num -cfgPara["sum"]["有人"]
        
        
        cfgPara["openid"]      =openid        
        if  web.ctx.method=='POST':
            ret =uTools.formatPostMsg(cfgPara)
        else:
            if dev["seat_template"]==None or dev["seat_template"]=="":
                ret = web.seeother('/device?act=bus-config&imei={0}&openid={1}'.format(imei,openid))
            else:
                jdksign = objWeixin.get_jdk_sign(self.env["url"])
                sharePara=tradeObj.genPreSharePara("share-view",openid,cfgPara["dev"]['imei'])
                
                sharePara["seat_template"] = self.seat_template(dev["seat_template"])
                sharePara["blank_color"]="#C0C0C0"
                sharePara["manager"] = linedb.getManageEmployee(openid)
                sharePara["company_id"]  =company["id"]
                cfgPara = json.dumps(cfgPara,ensure_ascii=False)
                if roleType=="operator":
                    ret = self.render.seat_status_auto(cfgPara,jdksign,sharePara)
                elif roleType=="operator-history":
                    ret = self.render.seat_status_his(cfgPara,jdksign,sharePara)
                else:
                        
                    if dev["seat_type"]=="bed":
                        ret = self.render.bed_status_auto(cfgPara,jdksign,sharePara)
                    elif  dev["seat_type"]=="midbus":
                        ret = self.render.seat_midbus_status_auto(cfgPara,jdksign,sharePara)
                    elif  dev["seat_type"]=="seat53":
                        if imei=='681501000179443':
                            print("sharePara----sharePara")
                            print(sharePara)
                        ret = self.render.seat53_status_auto(cfgPara,jdksign,sharePara)
                    elif  dev["seat_type"]=="seat39":
                        ret = self.render.seat39_status_auto(cfgPara,jdksign,sharePara)
                    else:
                        ret = web.seeother('/device?act=bus-config&imei={0}&openid={1}'.format(imei,openid))
        return ret   
        
    #roleType:指示Customer，Operator
    def getSeatsByImeiDebug(self,roleType,openid,data):
        if data.has_key("imei"):
            imei = data.imei
        else:
            imei = devdb.getDemoDeviceImei() #演示大巴
        #判定该用户对imei的可视权限--暂缺
        if data.has_key("his_datetime") or roleType=="operator-history":
            if data.has_key("his_datetime"):
                his_datetime = data.his_datetime  
            else:
                his_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                seatStatus= busdb.getSeatStatus(imei,his_datetime)  
        else:
            seatStatus  = busdb.getSeatStatus(imei)
        cfgPara=seatStatus["param"]
        for key in seatStatus["timely"]:
            cfgPara[key] = seatStatus["timely"][key]
        cfgPara["srcType"] ="及时数据"
        
        dev      = devdb.getDeviceByImei(imei,format="string")
        company  = linedb.getCompanyByImei(imei)
        
        cfgPara["name"]        =dev["name"]
        cfgPara["dev"]         =dev
        cfgPara["company_id"]  =company["id"]
        cfgPara["heartbeat_at"]=dev["heardbeat_at"]
        cfgPara["openid"]      =openid
        #修正统计座位数
        seat_num = 0
        for seat in dev["seat_template"].split(";"):
            if seat.split(",")[0]!="":
                seat_num+=1
        cfgPara["seat_num"] = seat_num
        cfgPara["sum"]["空座"] = seat_num -cfgPara["sum"]["有人"]
        
        
        cfgPara["openid"]      =openid        
        if  web.ctx.method=='POST':
            ret =uTools.formatPostMsg(cfgPara)
        else:
            if dev["seat_template"]==None or dev["seat_template"]=="":
                ret = web.seeother('/device?act=bus-config&imei={0}&openid={1}'.format(imei,openid))
            else:
                jdksign = objWeixin.get_jdk_sign(self.env["url"])
                sharePara=tradeObj.genPreSharePara("share-view",openid,cfgPara["dev"]['imei'])
                
                sharePara["seat_template"] = self.seat_template(dev["seat_template"])
                sharePara["blank_color"]="#C0C0C0"
                sharePara["manager"] = linedb.getManageEmployee(openid)
                sharePara["company_id"]  =company["id"]
                cfgPara = json.dumps(cfgPara,ensure_ascii=False)
                if roleType=="operator":
                    ret = self.render.seat_status_auto(cfgPara,jdksign,sharePara)
                elif roleType=="operator-history":
                    ret = self.render.seat_status_his(cfgPara,jdksign,sharePara)
                else:
                        
                    if dev["seat_type"]=="bed":
                        ret = self.render.bed_status_auto(cfgPara,jdksign,sharePara)
                    elif  dev["seat_type"]=="midbus":
                        ret = self.render.seat_midbus_status_auto(cfgPara,jdksign,sharePara)
                    elif  dev["seat_type"]=="seat53":
                        ret = self.render.seat53_status_auto(cfgPara,jdksign,sharePara)
                    elif  dev["seat_type"]=="seat39":
                        ret = self.render.seat39_status_auto(cfgPara,jdksign,sharePara)
                    else:
                        ret = web.seeother('/device?act=bus-config&imei={0}&openid={1}'.format(imei,openid))
        return ret 
        
    def getSeatsBusboxDebug(self,roleType,openid,data):
        if data.has_key("imei"):
            imei = data.imei
        else:
            imei = devdb.getDemoDeviceImei() #演示大巴
        #判定该用户对imei的可视权限--暂缺
        if data.has_key("his_datetime") or roleType=="operator-history":
            if data.has_key("his_datetime"):
                his_datetime = data.his_datetime  
            else:
                his_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                seatStatus= busdb.getSeatStatus(imei,his_datetime)  
        else:
            seatStatus  = busdb.getSeatStatus(imei)
        cfgPara=seatStatus["param"]
        for key in seatStatus["timely"]:
            cfgPara[key] = seatStatus["timely"][key]
        cfgPara["srcType"] ="及时数据"
        
        dev      = devdb.getDeviceByImei(imei,format="string")
        company  = linedb.getCompanyByImei(imei)
        
        cfgPara["name"]        =dev["name"]
        cfgPara["dev"]         =dev
        cfgPara["company_id"]  =company["id"]
        cfgPara["heartbeat_at"]=dev["heardbeat_at"]
        cfgPara["openid"]      =openid
        #修正统计座位数
        seat_num = 0
        for seat in dev["seat_template"].split(";"):
            if seat.split(",")[0]!="":
                seat_num+=1
        cfgPara["seat_num"] = seat_num
        cfgPara["sum"]["空座"] = seat_num -cfgPara["sum"]["有人"]
        
        
        cfgPara["openid"]      =openid        
        if  web.ctx.method=='POST':
            ret =uTools.formatPostMsg(cfgPara)
        else:
            if dev["seat_template"]==None or dev["seat_template"]=="":
                ret = web.seeother('/device?act=bus-config&imei={0}&openid={1}'.format(imei,openid))
            else:
                #jdksign = objWeixin.get_jdk_sign(self.env["url"])
                sharePara=tradeObj.genPreSharePara("share-view",openid,cfgPara["dev"]['imei'])
                
                sharePara["seat_template"] = self.seat_template(dev["seat_template"])
                sharePara["blank_color"]="#C0C0C0"
                sharePara["manager"] = linedb.getManageEmployee(openid)
                sharePara["company_id"]  =company["id"]
                cfgPara = json.dumps(cfgPara,ensure_ascii=False)
                if dev["seat_type"]=="bed":
                     ret = self.render.port_state_bed(cfgPara,sharePara)
                elif  dev["seat_type"]=="midbus":
                    ret = self.render.port_state_midbus(cfgPara,sharePara)
                elif  dev["seat_type"]=="seat53":
                    ret = self.render.port_state_seat39(cfgPara,sharePara)
                elif  dev["seat_type"]=="seat39":
                    ret = self.render.port_state_seat53(cfgPara,sharePara)
                else:
                    ret = web.seeother('/device?act=bus-config&imei={0}&openid={1}'.format(imei,openid))
        return ret
        
    def seat_template(self,template):
        #{"midbus":33,"bed":54,"seat53":60,"seat39":41}
        inTemp = []
        if template!=None:
            seats = [item.strip()  for item in template.split(";")]
            for seat in seats:
                inSeat = seat.split(",")
                if len(inSeat) ==2:
                    sensor,name = inSeat
                    port = ""
                elif len(inSeat) ==3:
                    sensor,name,port = inSeat
                else:
                    sensor=""
                    name  =seat
                    port  = ""
                inTemp.append([sensor,name,port])
        lenSeat = len(inTemp)
        for i in range(lenSeat,60):
            inTemp.append([str(i),str(i),i])
            
        return inTemp
        
    
    def bindNewDeviceMsg(self,openid,data):
        if  web.ctx.method=='GET':
            jdkSign = objWeixin.get_jdk_sign(self.env['url'])
            busline =linedb.getBuslineByid(data.busline_id,format="string")
            #company = linedb.getCompanyByBusline(data.busline_id)
            _cfgPara={"openid" :openid,"busline":busline}
            cfgPara = json.dumps(_cfgPara,ensure_ascii=False)
            ret = self.render.bind_new_devices(cfgPara,jdkSign)
        else:
            imei = self.updateManagerDeviceGroup(openid,data)
            #产品被卖出，更新卖出时间
            db.update("Device",where="imei=$imei",vars=locals(),saled_at=web.SQLLiteral('NOW()'))
            ret =  uTools.formatPostMsg({"result":"success","msg":"bind  succeed"})           
        return ret
        
        #更新设备所属分组视图：
    def updateManagerDeviceGroup(self,openid,data):
        imei = data.imei
        _ret = db.query("SELECT * FROM BusLine WHERE id={0}".format(data.busline_id))
        busline =_ret[0]
        #更新分组信息
        self.changeDeviceGroup(openid,imei,busline.busgroupid)
        
        db.update("Device",where         = "imei=$imei",vars=locals(),
                           Distributor_id= 6, #何秋文的账号
                           name          = data.name,
                           phone         = data.phone,
                           arm_type      = (data.arm_type if data.has_key("arm_type") else "bus"))
        return imei
        
    def updateDeviceCfg(self,openid,data):
        imei = data.imei
        #更新服务期限
        if data.has_key("service_start") and devdb.isSuperManager(openid):
                db.update("Device",where     ="imei=$imei",vars=locals(),
                           name          = data.name,
                           phone         = data.phone,
                           service_start = data.service_start,
                           expired_at    = data.expired_at)
        else:
            db.update("Device",where     ="imei=$imei",vars=locals(),
                           name          = data.name,
                           phone         = data.phone)
        return imei
    def changeDeviceGroup(self,openid,imei,groupid): 
        #更新设备的现有分组信息
        db.update("GroupHasDevice",where='imei = $imei',vars=locals(),
                               devicegroup_id=groupid,
                               created_at   =web.SQLLiteral('NOW()'))
        return
    
    def getBusConfigMsg(self,data):
        openid = objWeixin.getOpenid(data)
        imei   = data.imei
        
        _ret = db.query('SELECT * FROM Device WHERE imei="{0}"'.format(imei))
        
        cfgPara = {
            "result":"failed"
        }
        seat_type = "seat39"
        seat_t    =[]
        if len(_ret)>0:
            dev = _ret[0]
            seat_t  = self.seat_template(dev.seat_template)
            #查询该imei所属的管理分组
            _group = db.query("""SELECT *,DeviceGroup.id AS grpId FROM DeviceGroup,GroupHasDevice 
                                         WHERE GroupHasDevice.imei ='{0}' AND
                                               GroupHasDevice.devicegroup_id =DeviceGroup.id AND
                                               DeviceGroup.type = "管理分组"
                                         """.format(imei))
            if len(_group)>0:
                grp = _group[0]
                grpName = grp.name
                grpId   = grp.grpId
                _ret = db.query("SELECT * FROM BusLine WHERE busgroupid={0}".format(grpId))
                busline = _ret[0]
                company_id = busline.company_id
            else:
                grpName = "未知"
                grpId   = -1
                company_id = 0

            cfgPara = {
                "result"       :"success",
                "name"         :dev.name,
                "openid"       :openid,
                "busline_id"   :busline.id,
                "grpName"      :grpName,
                "grpId"        :grpId,
                "seat_t"       :seat_t,
                "devType"      :("天网1代" if dev.devType=="" else dev.devType),
                "manufacturer" :dev.manufacturer,
                "imei"         :dev.imei,
                "phone"        :dev.phone,
                "arm_type"     :dev.arm_type,
                "seat_type"    :dev.seat_type,
                "create_at"    :dev.regedit_at.strftime("%Y-%m-%d"), 
                "warehouse_id" :dev.warehouse_id,
                "company_id"   :company_id,
            }  
        if  web.ctx.method=='GET':
            sharePara=tradeObj.genPreSharePara("transfer",openid,imei)
            #设定缺省车型
            sharePara["sel"]={"midbus":"","bed":"","seat53":"","seat39":""}
            sharePara["sel"][seat_type]='selected = "selected"'
            sharePara["seat_t"]  = seat_t
            sharePara["manager"] = objWeixin.getManager(openid)
            sharePara["company_id"]= company_id
            jdkSign = objWeixin.get_jdk_sign(self.env['url'])
            _cfgPara=json.dumps(cfgPara,ensure_ascii=False)
            ret = self.render.bus_config(_cfgPara,jdkSign,sharePara)
        else:
            ret = uTools.formatPostMsg(cfgPara)
        return ret        
    
    def getAboutMsg(self,data):
        openid = objWeixin.getOpenid(data)
        imei = data.imei
        _ret = db.query('SELECT * FROM Device WHERE imei="{0}"'.format(imei))
        
        cfgPara = {
            "result":"failed"
        }
        if len(_ret)>0:
            dev = _ret[0]
            
            #查询该imei所属的管理分组
            _group = db.query("""SELECT *,DeviceGroup.id AS grpId FROM DeviceGroup,GroupHasDevice 
                                         WHERE GroupHasDevice.imei ='{0}' AND
                                               GroupHasDevice.devicegroup_id =DeviceGroup.id AND
                                               DeviceGroup.type = "管理分组"
                                         """.format(imei))
            if len(_group)>0:
                grp = _group[0]
                grpName = grp.name
                grpId   = grp.grpId
                _ret = db.query("SELECT * FROM BusLine WHERE busgroupid={0}".format(grpId))
                busline = _ret[0]
                busline_id = busline.id
                company_id = busline.company_id
            else:
                grpName = "未知"
                grpId   = -1
                company_id = 0
                busline_id = -1
            
            cfgPara = {
                "result"       :"success",
                "name"         :dev.name,
                "openid"       :openid,
                "busline_id"   :busline_id,
                "grpName"      :grpName,
                "grpId"        :grpId, 
                "devType"      :("天网1代" if dev.devType=="" else dev.devType),
                "manufacturer" :dev.manufacturer,
                "imei"         :dev.imei,
                "phone"        :dev.phone,
                "arm_type"     :dev.arm_type,
                "seat_type"    :dev.seat_type,
                "create_at"    :dev.regedit_at.strftime("%Y-%m-%d"), 
                "warehouse_id" :dev.warehouse_id,
                "company_id"   :company_id,
            }  
        if  web.ctx.method=='GET':
            sharePara=tradeObj.genPreSharePara("transfer",openid,imei)
            #设定缺省车型
            sharePara["sel"]={"midbus":"","bed":"","test":""}
            sharePara["sel"][dev.seat_type]='selected = "selected"'
            sharePara["company_id"]= company_id
            jdkSign = objWeixin.get_jdk_sign(self.env['url'])
            _cfgPara=json.dumps(cfgPara,ensure_ascii=False)
            ret = self.render.single_device_mgr(_cfgPara,jdkSign,sharePara)
        else:
            ret = uTools.formatPostMsg(cfgPara)
        return ret
        
    def friendManager(self,openid,imei):
        items =[]
        #权限验证
        company  = linedb.getCompanyByImei(imei)
        employee = linedb.getCompanyEmployeeByOpenid(openid,company["id"])             
        if employee["privilege"]=="manager":#是设备主人   
            _grps = db.query("""SELECT *,GroupHasDevice.created_at AS received_at,GroupHasDevice.id AS ghdId
                                        FROM GroupHasDevice,DeviceGroup
                                        WHERE GroupHasDevice.imei='{0}' AND
                                          GroupHasDevice.devicegroup_id = DeviceGroup.id AND
                                          DeviceGroup.type ='视图分组'""".format(imei))

            for grp in _grps:
                _user = db.query("SELECT * FROM Customer WHERE openid='{0}'".format(grp.Customer_openid))
                for user in _user:
                    items.append({
                        "nickname"   :user.nickname,
                        "received_at":grp.received_at.strftime("%Y-%m-%d %H:%M:%S"),
                        "ghdId"      :grp.ghdId, 
                        "openid"     :grp.Customer_openid,
                        "privilege"  :grp.privilege
                    })
        _dev = db.query("SELECT * FROM Device WHERE imei='{0}'".format(imei))
        cfgPara={"openid" :openid,
             "items"  :items,
             "imei"   :imei,
             "devName":_dev[0].name
        }
        if  web.ctx.method=='GET':
            jdkSign = objWeixin.get_jdk_sign(self.env["url"])
            sharePara=tradeObj.genPreSharePara("share-view",openid,imei)
            _cfgPara =json.dumps(cfgPara,ensure_ascii=False)
            ret = self.render.friend_manager(_cfgPara,jdkSign,sharePara)
        else:
            ret =uTools.formatPostMsg(cfgPara)
        return ret
    
    def updateSharePrivilege(self,openid,data):
        ghdId   = data.ghdId
        result = "fail"
        if data.has_key("ghd_act") and data.ghd_act == "delete":#删除操作，具有最高权限
            db.delete("GroupHasDevice",where="id=$ghdId",vars=locals())
            result = "success"
        else:
            if data.has_key("privilege") and  data.privilege in ["visible","invisible"]:
                db.update("GroupHasDevice",where="id=$ghdId",vars=locals(),privilege=data.privilege)
                result = "success"
            if data.has_key("no_help_theft") and  data.no_help_theft in [0,1]: 
                db.update("GroupHasDevice",where="id=$ghdId",vars=locals(),no_help_theft=data.no_help_theft)
                result = "success"
        ret = self.friendManager(openid,data.imei)
        return ret 
    
    #座位模板配置
    def cfgBusSeat(self,openid,data):
        imei = data.imei
        
        db.update("Device",where="imei=$imei",vars=locals(),seat_type=data.seat_type,
                                  seat_template=data.seat_template)
        ret =uTools.formatPostMsg({"result":"success"})
        return ret
        
    def getOnlineTestViewMsg(self,openid):
        if openid not in ["vk","zongheng"]:
            return
        openid = "online-test"
        cfgPara = devdb.getDeviceDistrubtorView(openid)
        cfgPara["openid"]=openid
        #iUrl = "&".join(self.env["qrcode_url"].split("&")[0:2])+"&grpType={0}&grpName={1}".format(grpType,grpName)
        
        _cfgPara = json.dumps(cfgPara,ensure_ascii=False)
        if  web.ctx.method=='GET':
            jdkSign = objWeixin.get_jdk_sign(self.env["url"])
            fixPara = icfg.getFixPara(openid)
            ret = self.render.online_test(_cfgPara,jdkSign,fixPara)
        else:
            ret =_cfgPara
        return ret
        
    def getOnlineState(self,openid,data):
        #查询纳入
        buses = devdb.getCompanyBusSate()
        if  web.ctx.method=='GET': 
            jdkSign = objWeixin.get_jdk_sign(self.env["url"])
            fixPara = icfg.getFixPara(openid)
            cfgPara = {"buses":buses,"openid":openid}
            _cfgPara =json.dumps(cfgPara,ensure_ascii=False)
            ret     = self.render.online_state(_cfgPara,jdkSign,fixPara)
        else:
            ret =uTools.formatPostMsg({"buses":buses})
        return ret
        
        

