# -*- coding: utf-8 -*-
import web,time,datetime,re,json,random
import product.iconfig as icfg
import product.model.linedb as linedb
import product.model.devdb as devdb
import product.model.seat as seatdb
from product.model.historytrackmgr import historyTrackMgr
import gps2.gxsaiwei.lib.utool as swtool
import utility as uTools
import logstat


class Seat:
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
        if(act=='GET-LAYOUT'):
            ret =self.getSeatLayout(openid,data)
        elif(act=='GET-BUSTRAVEL'):
            ret =self.getBusTravel(openid,data)
        elif(act=='GET-SEAT-STATUS-DITHERING'):
            ret =self.getSeatStatusDithering(openid,data)
        elif(act=='GET-SEAT-STATUS'):
            ret =self.getSeatStatus(openid,data)
        elif(act=='GET-TRAVEL-SITE'):
            ret =self.getTravelSite(openid,data) 
        elif(act=='GET-REGION-MONITOR-RESULT'):
            ret =self.getRegionMonitorResult(openid,data) 
        elif(act=='GET-SEAT-TYPE'):
            ret =self.getSeatType(openid,data)    
        return ret
        
    def POST(self):
        data = web.input()
        self.env = icfg.getEnvObj()
        act =uTools.get_act(data)
        openid =icfg.objWeixin.getOpenid(data)
        if(act =='GET-LINEBUS'):
            ret =self.getLineBus(openid,data)
        elif(act=="UPDATE-CHECKED-TRAVEL"):
            ret =self.updateCheckedTravel(openid,data)
        elif(act=="ADD-MONITOR-REGION"):
            ret =self.addMonitorRegion(openid,data)
        elif(act=="ADD-LINE-SITE"):
            ret = self.addLineSite(openid,data)
        elif(act=="GET-LINE-SITE"):
            ret = self.getLineSite(openid,data)
        elif(act=="DEL-MONITOR-REGION"):
            ret =self.delMonitorRegion(openid,data)  
        elif(act=="GET-MONITOR-REGION-RESULT"):
            ret =self.getRegionMonitorResult(openid,data) 
        elif(act=="GET-REGION-RESULT-DETAIL"):
            ret =self.getRegionResultDetailById(openid,data)
        elif(act=="UPDATE-REGION-RESULT-DETAIL"):
            ret =self.updateRegionResultDetail(openid,data)
        elif(act=="NOTIFY-CUSTOMER-REGION-RESULT"):
            ret =self.notifyRegionResult2Customer(openid,data)
        elif(act=="GET-MSG-RECEIVER"):
            ret =self.getMsgReceiver(openid,data)
        return ret
        
        
    def getSeatLayout(self,openid,data):
        if data.has_key("company_id"):
            company_id =data.company_id
            company =linedb.getCompany(company_id,format="string")
        else:
            companys = linedb.getCompanyByOpenid(openid,format="string")
            company= companys[0]
        
        buslines=linedb.getBusLineByOpenid4pc(openid,company["id"])
        buses = linedb.getBusesByCompany4pc(company["id"])

        isMgr = devdb.isSuperManager(openid)
        fixPara ={"isMgr":isMgr}
        cfgPara={"buslines":buslines,"openid":openid,"buses":buses,"company":company}
        _cfgPara = json.dumps(cfgPara,ensure_ascii=False)
        ret = self.render.seated_layout(_cfgPara,fixPara)
        return ret
        
        
    def getBusTravel(self,openid,data):
        if data.has_key("from_time"):
            from_time = datetime.datetime.strptime(data.from_time,"%Y-%m-%d %H:%M:%S")
            to_time   = datetime.datetime.strptime(data.to_time,"%Y-%m-%d %H:%M:%S")
        else:
            now = datetime.datetime.now()
            from_time = datetime.datetime.strptime(now.strftime("%Y-%m-%d 00:00:00"),"%Y-%m-%d %H:%M:%S")
            to_time   = (from_time+datetime.timedelta(days=1))
        imei = data.imei
        seats = seatdb.getBusTravelByTimeSpan(imei,from_time,to_time)
        #添加编号，耗时
        footer =[]
        sum_fee    =0.0  #总金额
        sum_fee_check =0.0  #总金额
        sum_seated  =0  #乘客数
        sum_seated_check  =0  #乘客数
        for seat in seats:
            sum_fee += seat["fee"]
            sum_fee_check += seat["fee_checked"]
            sum_seated += seat["num_seated"]
            sum_seated_check += seat["seated_checked"]
        footer.append({"from_name":"合计:",
                        "num_seated":sum_seated,
                        "fee":sum_fee,
                        "seated_checked":sum_seated_check,
                        "fee_checked":sum_fee_check})    
        cfgPara ={"total":len(seats),
                  "rows":seats,
                  "footer":footer,
                  "openid":openid,
                  "from_time":from_time.strftime("%Y-%m-%d %H:%M:%S"),
                  "to_time":to_time.strftime("%Y-%m-%d %H:%M:%S"),
                  "imei":imei}
        
        if  web.ctx.method=='GET':
            fixPara={}
            _cfgPara = json.dumps(cfgPara,ensure_ascii=False)
            ret = self.render.bustravel(_cfgPara,fixPara)
        else:
            ret =uTools.formatPostMsg(cfgPara)
        return ret
       
    def updateCheckedTravel(self,openid,data):
        travel_id = data.travel_id
        icfg.db.update("BusTravel",where="id=$travel_id",vars=locals(),
                                   seated_checked = data.seated_checked,
                                   fee_checked    = data.fee_checked
        )
        ret = self.getBusTravel(openid,data)
        return ret
        
        
    def getSeatStatusDithering(self,openid,data):
        seats = seatdb.getSeatStatusDithering(data.travel_id)
        cfgPara ={"seats":seats}
        fixPara={}
        _cfgPara = json.dumps(cfgPara,ensure_ascii=False)
        ret = self.render.seat_status_dithering(_cfgPara,fixPara)
        return ret
        
    def getSeatStatus(self,openid,data):
        seats = seatdb.getSeatStatus(data.travel_id)
        cfgPara ={"seats":seats}
        fixPara={}
        _cfgPara = json.dumps(cfgPara,ensure_ascii=False)
        ret = self.render.seat_status(_cfgPara,fixPara)
        return ret
        
    def getTravelSite(self,openid,data):
        sites = seatdb.getTravelSite(data.travel_id)
        cfgPara ={"sites":sites}
        fixPara={}
        _cfgPara = json.dumps(cfgPara,ensure_ascii=False)
        ret = self.render.travel_site(_cfgPara,fixPara)
        return ret
        
        
    def addMonitorRegion(self,openid,data):
        busline = linedb.getBuslineByImei(data.imei)
        busline_id = busline["id"]
        from_historytrack_id = long(data.from_historytrack_id)
        to_historytrack_id   = long(data.to_historytrack_id)
        
        seatdb.addMonitorRegion(busline_id,from_historytrack_id,to_historytrack_id)
        rows = seatdb.getLineMonitorRegionByLineid(busline_id)
        
        cfgPara={"total":len(rows),"rows":rows}
        ret =uTools.formatPostMsg(cfgPara)
        return ret
        
        
    def delMonitorRegion(self,openid,data):
        monitor_region = seatdb.getMonitorRegionById(data.monitor_region_id)
        seatdb.delMonitorRegion(data.monitor_region_id)
        rows = seatdb.getLineMonitorRegionByLineid(monitor_region["busline_id"])
        
        cfgPara={"total":len(rows),"rows":rows}
        ret =uTools.formatPostMsg(cfgPara)
        return ret
        
        
        
    def addLineSite(self,openid,data):
        imei      = data.imei
        hispos_id =long(data.hispos_id)
        busline   = linedb.getBuslineByImei(imei)
        swtool.addBuslineSite(busline["id"],hispos_id,site_type="customer_site",setting_type="manual")

        sites = linedb.getSitesByLineid(busline["id"],setting_type="manual")
        rows = sites["manual"]
        ret =uTools.formatPostMsg({"result":"success","total":len(rows),"rows":rows})
        return ret
        
    def getLineSite(self,openid,data):
        imei = data.imei
        
        busline   = linedb.getBuslineByImei(imei)
        sites = linedb.getSitesByLineid(busline["id"],setting_type="manual")
        rows = sites["manual"]
        ret =uTools.formatPostMsg({"total":len(rows),"rows":rows})
        return ret
        
        
    def getRegionMonitorResult(self,openid,data):
        if data.has_key("from_time"):
            from_time = datetime.datetime.strptime(data.from_time,"%Y-%m-%d %H:%M:%S")
            to_time   = datetime.datetime.strptime(data.to_time,"%Y-%m-%d %H:%M:%S")
        else:
            now = datetime.datetime.now()
            from_time = datetime.datetime.strptime(now.strftime("%Y-%m-%d 00:00:00"),"%Y-%m-%d %H:%M:%S")
            to_time   = (from_time+datetime.timedelta(days=1))
        imei = data.imei
        cfgPara = seatdb.getMonitorRegionResultByImei(imei,from_time,to_time)
        cfgPara["total"] =len(cfgPara["rows"])
        cfgPara["from_time"] = from_time.strftime("%Y-%m-%d %H:%M:%S")
        cfgPara["to_time"]   = to_time.strftime("%Y-%m-%d %H:%M:%S")
        dev = devdb.getDeviceByImei(imei,format="string")
        
        if  web.ctx.method=='GET':
            cfgPara["openid"]=openid
            cfgPara["dev"]  =dev
            fixPara={"openid":openid}
            _cfgPara = json.dumps(cfgPara,ensure_ascii=False)
            ret = self.render.regionmonitor(_cfgPara,fixPara)
        else:
            ret =uTools.formatPostMsg(cfgPara)
        return ret
        
    #stat ={"sum":{"times":sum,"mileage":0},
    #       "mileage":{},"times":{}}   
    def getRegionResultDetailById(self,openid,data):
        region_result_id = data.region_result_id
        rows = seatdb.getRegionResultDetailById(region_result_id)
        cfgPara={"region_result_id":region_result_id,"total":len(rows),"rows":rows}
        return uTools.formatPostMsg(cfgPara)
        
        
    def getSeatType(self,openid,data):
        result = [{"seatid":"有人","seatName":"有人"},{"seatid":"空座","seatName":"空座"}]
        ret =uTools.formatPostMsg(result)
        return ret
        
    def updateRegionResultDetail(self,openid,data):
        region_result_id = data.region_result_id
        param            = data.param
        changeSeat ={}
        for item in param.split("_"):
            sensor_no,check_result =[val.strip() for val in param.split(":")]
            changeSeat[sensor_no]=check_result
        seatdb.updateRegionResultDetail(region_result_id,changeSeat)
        rows = seatdb.getRegionResultDetailById(region_result_id)
        cfgPara={"region_result_id":region_result_id,"total":len(rows),"rows":rows}
        return uTools.formatPostMsg(cfgPara)
        
            
    def getMsgReceiver(self,openid,data):
        imei = data.imei
        company  = linedb.getCompanyByImei(imei)
        employee = linedb.getEmployeeByid4pc(company["id"],with_manager=True)
        rows =[]
        for _type in employee:
            group = ("赛微" if _type=="saiwei" else "客户")
            for row in employee[_type]:
                row["group"] = group
                rows.append(row)
        cfgPara = {"total":len(row),"rows":rows}
        return uTools.formatPostMsg(cfgPara)
            
        
    def notifyRegionResult2Customer(self,openid,data):
        print(data)
        region_result_id = data.region_result_id
        param            = data.param
        msg              = data.msg
        openids          = data.openids.split(";")
        #先完成更新
        changeSeat ={}
        if param.strip()!="":
            for item in param.split("_"):
                sensor_no,check_result =[val.strip() for val in param.split(":")]
                changeSeat[sensor_no]=check_result
                seatdb.updateRegionResultDetail(region_result_id,changeSeat)
            
        #启动发送
        cmpHomeLink=icfg.objWeixin.getAuth2Url("{0}/m/manager?act=home".format(web.ctx.homedomain))
        systemMsg = icfg.objWeixin.iconfig.systemMsg
        systemMsg["url"]  =cmpHomeLink
        systemMsg["data"]["keyword2"]["value"] =datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        systemMsg["data"]["first"]["value"]   ="座位统计报告"
        systemMsg["data"]["keyword1"]["value"]="赛微消息"
        systemMsg["data"]["remark"]["value"]="\r\n   "+msg
        for iopenid in openids:
            systemMsg["touser"] = iopenid
            icfg.objWeixin.send_template_msg(systemMsg)
        
        return uTools.formatPostMsg({"result":"success"})
    
        
        
        
        