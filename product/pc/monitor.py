# -*- coding: utf-8 -*-
import web,time,datetime,re,json,random,requests
import product.iconfig as icfg
import product.model.linedb as linedb
import product.model.devdb as devdb
import product.model.demo as demo
from product.model.historytrackmgr import historyTrackMgr
import utility as uTools
import product.model.seat as seatdb
import logstat
#from weixin.client import WeixinAPI
#from weixin.oauth2 import OAuth2AuthExchangeError

class Monitor:
    def __init__(self):
        templates_path =__file__.split(".py")[0]
        self.render = web.template.render(templates_path)

    def GET(self):
        data = web.input()
        self.env = icfg.getEnvObj()
        openid = icfg.objWeixin.getOpenid(data)
        if openid=="error":#没有登录
            raise web.seeother('/user?act=login')
        #openid = "twsh"
        act =uTools.get_act(data)
        #logstat.logAccessUrl(openid,act) #记录用户访问
        if(act =="CAR-ONLINE"):
            ret = self.getCarOnline(openid,data)
        elif(act =='GET-BUSLINE'):
            ret = self.getBusLine(openid,data)
        elif(act =='GET-LINEBUS'):
            ret =self.getLineBus(openid,data)
        elif(act=="GET-DEVICES-TABLE"):
            ret =self.getDevicesTable(openid,data)
        elif(act=='GET-BUS-SEATTYPE'):
            ret =self.getBusSeatType(openid,data)
        elif(act in ['GET-HISTORYTRACK','GET-HISTORYTRACK-ONLY']):
            ret =self.getHistoryTrackMsg(act,openid,data)
        elif(act=='GET-HISTORY-SITE'):
            ret =self.getHistorySite(openid,data)
        elif(act=='GET-SEAT-LAYOUT'):
            ret =self.getSeatLayout(openid,data)
        elif(act=='GET-BOXCMD-RESULT'):
            ret =self.getBoxCmdResult(openid,data)
        elif(act=='GET-BOX-MONITOR'):
            ret =self.getBoxMonitor(openid,data)
        elif(act=="GET-FAN-DEMO"):
            ret =self.getFanDemo(openid,data)
        else:
            ret  = self.getCarOnline(openid,data)
        return ret
    
    def POST(self):
        data = web.input()
        self.env = icfg.getEnvObj()
        act =uTools.get_act(data)
        openid =icfg.objWeixin.getOpenid(data)
        if(act =='GET-LINEBUS'):
            ret =self.getLineBus(openid,data)
        elif(act=="BUS-POSITION"):
            ret = self.getBusPostion(openid,data)
        elif(act =='GET-BUSLINE'):
            ret = self.getBusLine(openid,data)
        elif(act =='GET-BUSCFG'):
            ret = self.getBusConfig(openid,data)
        elif(act=='GET-HISTORYTRACK'):
            ret = self.getHistoryTrackMsg(act,openid,data)
        elif(act=='GET-HISTORY-SITE'):
            ret =self.getHistorySite(openid,data)
        elif(act=='SEND-BOX-CMD'):
            ret =self.exeBoxCmd(openid,data)
        elif(act=='GET-BOXCMD-RESULT'):
            ret =self.getBoxCmdResult(openid,data)
        elif(act=="GET-FAN-STATE"):
            ret =self.getFanState(openid,data)
        return ret
        
        
    def wxOpenAuth(self,data):
        code = request.args.get('code')
        api = WeixinAPI(appid=wxcfg.appid,
                        app_secret=wxcfg.appid,
                        redirect_uri=wxcfg.redirect_uri)
        auth_info = api.exchange_code_for_access_token(code=code)
        api = WeixinAPI(access_token=auth_info['access_token'])
        resp = api.user(openid=auth_info['openid'])
        return jsonify(resp) 
    
    def getCarOnline(self,openid,data):
        if data.has_key("company_id"):
            company_id =data.company_id
            company =linedb.getCompany(company_id,format="string")
        else:
            companys = linedb.getCompanyByOpenid(openid,format="string")
            if len(companys)==0:
                company = {"id":-1,"company":"未知"}
            else:
                company = companys[0]
        if company["id"]==-1:
            raise web.seeother(icfg.urlHome)
        else:
            buslines=linedb.getBusLineByOpenid4pc(openid,company["id"])
            buses = linedb.getBusesByCompany4pc(company["id"])
            isMgr = devdb.isSuperManager(openid)
            fixPara ={"isMgr":isMgr}
            cfgPara={"buslines":buslines,"openid":openid,"buses":buses,"company":company}
            _cfgPara = json.dumps(cfgPara,ensure_ascii=False)
            ret = self.render.caronline(_cfgPara,fixPara)
        return ret
        
    #获取大巴车位置
    def getBusPostion(self,openid,data):
        if data.bus_type=="imei":
            buses = devdb.getDeviceByImei4pc([data.value])
        elif data.bus_type=="groupid":
            buses = devdb.getDeviceByGroupid4pc(data.value)
        elif data.bus_type=="company_id":
            buses = linedb.getBusesByCompany4pc(data.value)
        else:
            buses = linedb.getBusesByOpenid4pc(openid)
        cfgPara={"buses":buses}
        cfgPara=uTools.formatPostMsg(cfgPara)
        return cfgPara
            
    def getBusLine(self,openid,data):
        busline = linedb.getBuslineByid(data.busline_id,format="string")
        ret = {"total":1,"rows":[busline]}
        ret = uTools.formatPostMsg(cfgPara)
        return ret
        
    def getLineBus(self,openid,data):
        #jdkSign = icfg.objWeixin.get_jdk_sign(self.env["url"])
        cfgPara ={'openid' :openid,"appid":icfg.objWeixin.appid,"homedomain":self.env["homedomain"]}
        #stat = linedb.statCompany(self.env,openid)
        cfgPara['buses']=devdb.getDeviceByGroupid4pc(data.busgroupid)
        ret = uTools.formatPostMsg(cfgPara)
        return ret
        
        
    def getBusConfig(self,openid,data):
        dev = devdb.getDeviceByImei(data.imei,format="string")
        ret = {"total":0,"rows":[]}
        ret["rows"].append({"name" :"IMEI"     ,"db_name":"imei"   ,"value":dev["imei"]})
        ret["rows"].append({"name" :"车牌号"   ,"db_name":"name"   ,"value":dev["name"],"editor":"text"})
        ret["rows"].append({"name" :"SIM卡号"  ,"db_name":"phone"  ,"value":dev["phone"],"editor":"text"})
        ret["rows"].append({"name" :"设备类型" ,"db_name":"devType","value":dev["devType"]})
        ret["rows"].append({"name" :"注册日期" ,"db_name":"regedit_at","value":dev["regedit_at"]})
        ret["rows"].append({"name" :"座位类型" ,"db_name":"seat_type","value":dev["seat_type"],"editor":{
                            "type":'combobox',
                            "options":{
                                "valueField":'seatid',
                                "textField":'seatname',
                                "method":'get',
                                "url":'/pc/monitor?act=get-bus-seattype',
                                "required":True
                            },
                }              
        })
        
        ret["total"] = len(ret["rows"])
        ret = uTools.formatPostMsg(ret)
        return ret
        
    def getBusSeatType(self,openid,data):
        seat_types = devdb.getBusSeatType()
        ret = json.dumps(seat_types,ensure_ascii=False)
        return ret
        
    def getHistoryTrackMsg(self,act,openid,data,mapType="QQ"):
        imei = data.imei
        fromTime =data.startTime
        toTime   =data.endTime
        pts = historyTrackMgr.getHistoryTrack4b(imei,fromTime,toTime,mapType)  
        dev = devdb.getDevice(imei)
        sites = linedb.getHistorySitesByImei(imei,fromTime,toTime)
        #统计位置中心
        centerQQLat=0
        centerQQLng=0
        centerBaiduLat=0
        centerBaiduLng=0
        for pt in pts:
            centerQQLat += pt["qqLat"]/len(pts)
            centerQQLng += pt["qqLng"]/len(pts)
            centerBaiduLat += pt["baiduLat"]/len(pts)
            centerBaiduLng += pt["baiduLng"]/len(pts)
        
        _toTime = datetime.datetime.strptime(toTime,"%Y-%m-%d %H:%M:%S")
        _fromTime = datetime.datetime.strptime(fromTime,"%Y-%m-%d %H:%M:%S")
        monitors = seatdb.getLineMonitorRegionByImei(imei)       
        history_sites = historyTrackMgr.getHistorySite(imei,fromTime,toTime)
        no = 1
        for site in history_sites:
            site["no"]=no
            no+=1
            site["duration_time"] = uTools.secondsFormat2(site["duration_seconds"])
            
        cfgPara = {
            'dev':dev,
            'pts':pts,
            'sites':sites,
            'hisSites':history_sites,
            'monitor_regions':monitors,
            'openid'  :openid,
            'centerQQLat':centerQQLat,
            'centerQQLng':centerQQLng,
            'centerBaiduLat':centerBaiduLat,
            'centerBaiduLng':centerBaiduLng,
            'startTime':_fromTime.strftime("%Y-%m-%dT%H:%M"),
            'endTime': _toTime.strftime("%Y-%m-%dT%H:%M"),
        }
        
        
        fixPara={}
        if  web.ctx.method=='GET':
            cfgPara = json.dumps(cfgPara,ensure_ascii=False)
            if act=="GET-HISTORYTRACK-ONLY":
                ret = self.render.history_track_only(cfgPara,fixPara)
            else:
                ret = self.render.history_track(cfgPara,fixPara)
        else:
            ret =uTools.formatPostMsg(cfgPara)
        return ret 
        
    def getHistorySite(self,openid,data):
        rows = historyTrackMgr.getHistorySite(data.imei,data.startTime,data.endTime)
        cfgPara={"total":len(rows),"rows":rows}
        cfgPara = json.dumps(cfgPara,ensure_ascii=False)
        return cfgPara
        
    def getSeatLayout(self,openid,data):
        if data.has_key("company_id"):
            company_id =data.company_id
        else:
            companys = linedb.getCompanyByOpenid(openid)
            company_id = companys[0]["id"]

        buslines=linedb.getBusLineByOpenid4pc(openid,company_id)
        buses = linedb.getBusesByCompany4pc(company_id)
        fixPara={}
        cfgPara={"buslines":buslines,"openid":openid,"buses":buses,"company_id":company_id}
        _cfgPara = json.dumps(cfgPara,ensure_ascii=False)
        ret = self.render.seated_layout(_cfgPara,fixPara)
        return ret
        
    def getDevicesTable(self,openid,data):
        if data.qtype=="groupid":
            devices =devdb.getDeviceByGroupid4pc(data.value)
        else:
            imeis = data.value.split(",")
            devices =devdb.getDeviceByImei4pc(imeis)
        cfgPara={"devices" :devices,
                 "openid"  :openid}
        _cfgPara=json.dumps(cfgPara,ensure_ascii=False)
        isMgr = devdb.isSuperManager(openid)
        fixPara ={"isMgr":isMgr}
        ret = self.render.devicemanager(_cfgPara,fixPara)
        return ret
        
    def exeBoxCmd(self,openid,data):
        if data.has_key("cmd")==False:
            ret={}
        else:
            args=dict(act='EXE-BOX-CMD',imei=data.imei,cmd=data.cmd)
            print(icfg.adapter["busbox"])
            ret = requests.post(icfg.adapter["busbox"], params = args).json()
        cfgPara =uTools.formatPostMsg(ret)
        return cfgPara
        
        
    def getBoxCmdResult(self,openid,data):
        args=dict(act='GET-BOXCMD-RESULT',imei=data.imei,cmd=data.cmd)
        ret = requests.get(icfg.adapter["busbox"], params = args).json()
        cfgPara =uTools.formatPostMsg(ret)
        return cfgPara
        
    def getBoxMonitor(self,openid,data):
        imei = data.imei
        ret = devdb.getBoxMonitor(imei)
        cfgPara =uTools.formatPostMsg(ret)
        return cfgPara
        
        
    def getFanDemo(self,openid,data):
        groupid = 42
        area = demo.getFanBoxName(groupid)
        imeis = [item["imei"] for  item in area]
        fans = demo.getFanStateByArea(imeis)
        _cfgPara={
            "area":{"rows":area,"total":len(area)},
            "fans":{"rows":fans,"total":len(fans)}
        }
        cfgPara=json.dumps(_cfgPara,ensure_ascii=False)
        fixPara={}
        ret = self.render.fan_demo(cfgPara,fixPara)
        return ret
        
    #获取大巴车位置
    def getFanState(self,openid,data):
        groupid = 42
        imei = data.imei
        if imei=="":
            area = demo.getFanBoxName(groupid)
            imeis = [item["imei"] for  item in area]
        else:
            imeis = [imei]
            
        fans = demo.getFanStateByArea(imeis)
        _cfgPara={
            "fans":{"rows":fans,"total":len(fans)}
        }
        cfgPara=uTools.formatPostMsg(_cfgPara)
        return cfgPara
        
        
        