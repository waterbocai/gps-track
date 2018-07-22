# -*- coding: utf-8 -*-                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   # -*- coding: utf-8 -*-
import web,time,datetime
from product.iconfig import db,objWeixin
import product.iconfig as icfg
import product.model.devdb as devdb
import product.model.linedb as linedb
import utility as uTools
import logstat
import json
import re
from baidumap import BaiduMap

class  Security:
    def __init__(self):
        templates_path =__file__.split(".py")[0]
        self.render = web.template.render(templates_path)
        self.bdmap = BaiduMap();
        
    def GET(self):
        data = web.input()
        self.env = icfg.getEnvObj()
        act = uTools.get_act(data)

        ret = ""
        openid = objWeixin.getOpenid(data)
        accessLog = True #记录访问情况       
        if act == "HOME" :      
            ret = self.home(openid,data)
        elif act =="RESET-SF":
            ret = self.resetSF(openid,data)
        elif act =="SPEAKER-SUNG":           
            ret = self.speakerSung(openid,data.imei)
        elif act =="AUTO-MONITOR":#定时自动检测
            accessLog = False
            ret = self.autoMonitor()
        elif act =="OFFLINE-NOTIFY":#定时自动检测
            accessLog = False
            ret = self.offlineNotify(data)
        if accessLog == True:
            logstat.logAccessUrl(openid,act) #记录用户访问
        return ret
    
    def POST(self):
        data = web.input()
        self.env = icfg.getEnvObj()
        act = uTools.get_act(data)
        imei   = data.imei
        openid = objWeixin.getOpenid(data)
        if act == "HOME" :  
            ret = self.home(openid,data)
        elif act =="UPDATE-ITEMS":
            ret =self.updateSecurityItem(openid,data)
        elif act =="RESET-SF":
            ret = self.resetSF(openid,data)
        elif act =="SPEAKER-SUNG":
            ret = self.speakerSung(openid,imei)
        elif act =="MONITOR-SETUP":
            ret = self.monitorSetup(openid,imei,data.state)
        return ret
   
    def home(self,openid,data):
        _ret=db.query("SELECT * FROM Device WHERE imei='{0}'".format(data.imei))
        dev = _ret[0]
        fireMinutes    =15  if dev.fireMinutes==0  else dev.fireMinutes
        fireDistance   =200 if dev.fireDistance==0 else dev.fireDistance
        moveSpeaker    ="off"  if dev.moveSpeaker is None else dev.moveSpeaker
        poweroffSpeaker="off"  if dev.poweroffSpeaker is None else dev.poweroffSpeaker
        _ret = db.query("SELECT * FROM CurrentLocation WHERE imei='{0}'".format(data.imei))
        _devState = _ret[0]
        _cfgPara ={
            'openid'         :openid,
            'imei'           :data.imei,
            'fireMinutes'    :fireMinutes,
            'fireDistance'   :fireDistance,
            'moveSpeaker'    :moveSpeaker,
            'poweroffSpeaker':poweroffSpeaker,
            'monitorState'   :dev.monitorState,
            'alm_low_voltage'       :_devState.alm_low_voltage,
            'alm_power_off'         :_devState.alm_power_off,
            'lost_seconds'          :self.lost_seconds(data.imei),
            'lost_alm_after_minutes': (dev.lost_alm_after_minutes if dev.lost_alm_after_minutes>0 else 15)
        }
        if  web.ctx.method=='GET':
            jdkSign = objWeixin.get_jdk_sign(self.env["url"])
            cfgPara =json.dumps(_cfgPara,ensure_ascii=False)
            ret = self.render.security_item(cfgPara,jdkSign)
        else:
            ret = uTools.formatPostMsg(_cfgPara)
        return ret
        
    def updateSecurityItem(self,openid,data):
        imei =data.imei
        result = db.update("Device",where="imei=$imei",vars=locals(),
                                            fireMinutes    =data.fireMinutes,
                                            fireDistance   =data.fireDistance,
                                            moveSpeaker    =data.moveSpeaker,
                                            poweroffSpeaker=data.poweroffSpeaker,
                                            lost_alm_after_minutes =data.lost_alm_after_minutes
                            )
        cfgPara={"openid":openid,"result":"success"}
        ret =uTools.formatPostMsg(cfgPara)
        return ret
    
    def monitorAndNotifyRelations(self,imei):
        #判定是否失联
        lost_seconds = self.lost_seconds(imei)
        #设备信息
        _dev = db.query("SELECT * FROM Device WHERE imei='{0}'".format(imei))
        dev = _dev[0]
        
        #当前位置
        _pos = db.query("SELECT * FROM CurrentLocation WHERE imei='{0}'".format(imei))
        if len(_pos)==0:#还没有数据上报
            return;
        else:        
            pos = _pos[0]                
        i = 1
        eventMsg = "" #异常事件描述
        event    =[] #异常事件
        if dev.lost_state !="" :#检测对象已经失联，没有必要再进行进一步检查
            if dev.report_needed==1:
                eventMsg+= "{0} : GPS主机失去联系达:{1};".format(i,self.secondsFormat(lost_seconds))
                event.append("主机失联")
                i  +=1
        else:
            if dev.report_needed==1:
                event.append("主机上线")
                eventMsg+= "{0} : GPS主机回复上线！".format(i)
                i  +=1

            #获取上次上报的信息
            _hisPos = db.query("SELECT * FROM HistoryTrack WHERE imei='{0}' ORDER BY report_at DESC LIMIT 0,3".format(imei))
            if len(_hisPos)==0:#还没有数据上报
                return;
            hisPos = _hisPos[0]
            
            #车辆移动的位置距离设定位置距离
            ret = self.bdmap.routematrix([[dev.stopBaiduLat,dev.stopBaiduLng]],[[pos.baiduLat,pos.baiduLng]])
            try:
                movedDistance = (0 if ret =="" else int(ret[0]["distance"]["value"]))#移动距离
            except:
                movedDistance = 0
                print ret
            if movedDistance<1000:
                movedDistance="{0}米".format(movedDistance)
            else:
                movedDistance="%0.3f公里"%(movedDistance/1000.0)
            
            speaker = False         
            if pos.alm_power_off ==1 and hisPos.alm_power_off==0:
                eventMsg+= "{0} : GPS电源断了;".format(i)
                event.append("主机断电")
                i  +=1
                if dev.poweroffSpeaker=="on":#需要启动车辆上的报警
                    speaker = True
                    
            if pos.alm_power_off ==0 and hisPos.alm_power_off==1:
                event.append("主机恢复供电")
                eventMsg+= "{0} : GPS电源恢复正常;".format(i)
                i  +=1
                
                    
            if pos.alm_low_voltage ==1 and hisPos.alm_low_voltage==0:
                event.append("电压过低")
                eventMsg+= "{0} : 电瓶电压过低;".format(i)
                i  +=1
            if pos.alm_low_voltage ==0 and hisPos.alm_low_voltage==1:
                event.append("电压恢复正常")
                eventMsg+= "{0} : 电瓶电压回复正常;".format(i)
                i  +=1
                
            
        if eventMsg == "":#没有异常情况，直接返回
            return
        #合并消息接收人 车辆的朋友
        _swmgrs = db.query("""SELECT * FROM Customer WHERE openid IN(
                                 SELECT openid FROM CompanyHasEmployee
                                 WHERE company_id=1 AND privilege<>'invisible')""")
        msg = self.assumeNotifyExceptMsg(dev,pos,event,eventMsg)
        if msg ==None:
            return;
        #发送消息给朋友
        for mgr in _swmgrs:
            #发送台频繁，就不再发送了
            cmd = "monitorAndNotifyRelations_"+imei
            if objWeixin.customser_msg_is_frequent(mgr.openid,cmd):
                continue
            msg["url"]="{0}/m/device?act=seat-status-test&openid={1}&imei={2}".format(icfg.domain,mgr.openid,dev.imei)
            msg["touser"] = mgr.openid
            try:
                objWeixin.send_template_msg(msg)
            except Exception as e:
                print("openid:{0} -nickname:{1} -except:{2}".format(mgr.openid,mgr.nickname,e))
            
    def lost_seconds(self,imei):
        #设备信息
        _dev = db.query("SELECT * FROM Device WHERE imei='{0}'".format(imei))
        dev = _dev[0]
        #判定是否失联
        lost_alm_after_minutes =( 15 if dev.lost_alm_after_minutes ==0 else dev.lost_alm_after_minutes)
        lost_seconds = int((datetime.datetime.now()-dev.heardbeat_at).total_seconds()) 
        #print("lost_seconds:{0}".format(lost_seconds))
        if lost_seconds > 7*24*60*60:
            lost_state = "long"
        elif lost_seconds > lost_alm_after_minutes * 60 :
            lost_state ="short"
        else:
            lost_state = ""
            lost_seconds = 0
        _ret = db.query("SELECT * FROM Device WHERE imei='{0}'".format(imei))
        dev = _ret[0]
        if dev.lost_state==lost_state:#状态没有变化
            db.update("Device",where ='imei=$imei',vars=locals(),report_needed=0)
        else:
            db.update("Device",where ='imei=$imei',vars=locals(),lost_state=lost_state,report_needed=1)
        return lost_seconds
    
    def assumeNotifyExceptMsg(self,dev,pos,event,eventMsg):
        company = linedb.getCompanyByImei(dev.imei)
        if company==None:#还没有录入到公司，返回None
            return None
        busline = linedb.getBuslineByImei(dev.imei)
        exceptMsg = objWeixin.iconfig.exceptMsg
        exceptMsg["data"]["first"]["value"]    =company["company"]+" 设备异常提醒"
        exceptMsg["data"]["keyword1"]["value"] = "线路-"+busline["from_name"]+"<->" + busline["to_name"]
        exceptMsg["data"]["keyword2"]["value"] = "{0}({1})".format(dev.name,dev.imei)
        exceptMsg["data"]["keyword3"]["value"] = "\r\n".join(event)
        exceptMsg["data"]["keyword4"]["value"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        exceptMsg["data"]["remark"]["value"]   ="""异常描述:
{0}

最后检测到的情况:
-时间: {1}
-速度:{3}公里/小时
-位置:{2}
""".format(eventMsg,pos.gpsTime.strftime("%m-%d %H:%M:%S"),pos.addr,pos.speed)
        return exceptMsg
    
    def resetSF(self,openid,data):
        imei   = data.imei
        jdkSign = objWeixin.get_jdk_sign(self.env["url"])
        cfgPara={"openid":openid}
        #判定该用户对该imei具有管理权限
        if self.openidOwnerImei(openid,imei)==False:#不是管理者，不能解除告警
            cfgPara["result"]="fails"
        else:
            db.update("Device",where='imei=$imei',vars=locals(),
                stopTime     ="0000-00-00 00:00:00",
                stopBaiduLat =0,
                stopBaiduLng =0, 
                monitorState ='waiting0',
                monitor_at   ="0000-00-00 00:00:00",
            )
            cfgPara["result"]="success"
        if  web.ctx.method=='GET':
            ret = self.render.fire_alarm_result(cfgPara,jdkSign)
        else:
            ret =uTools.formatPostMsg(cfgPara)
        return ret
        
        
        
    def openidOwnerImei(self,openid,imei):
        #判定该用户对该imei具有管理权限
        
        _ret = db.query("""SELECT * FROM GroupHasDevice,DeviceGroup
                                    WHERE GroupHasDevice.imei = '{0}' AND
                                          GroupHasDevice.devicegroup_id = DeviceGroup.id AND
                                          DeviceGroup.Customer_openid   ='{1}' AND 
                                          DeviceGroup.type = '管理分组'
                        """.format(imei,openid))
        ret = (True if len(_ret)==1 else False)
        return ret
       
    def monitorSetup(self,openid,imei,state):
        #初始化返回值
        cfgPara={"openid":openid}
        if self.openidOwnerImei(openid,imei)==False:
            cfgPara["result"]="fails:owner is invalid"
        elif state in ["fired","waiting0"]:#满足条件，更新数据库
            db.update("Device",where='imei=$imei',vars=locals(),
                stopTime     ="0000-00-00 00:00:00",
                stopBaiduLat =0,
                stopBaiduLng =0, 
                monitorState =state,
                monitor_at   ="0000-00-00 00:00:00"
            )
            #从数据库中重新读取，确认数据正确
            _ret = db.query("SELECT * FROM Device WHERE imei='{0}'".format(imei))
            cfgPara["state"]=_ret[0].monitorState
            cfgPara["result"]="success"
        else:#不符合更新条件
            cfgPara["result"]="fails:state is invalid-{0}".format(state)
        ret =uTools.formatPostMsg(cfgPara)
        return ret
        
        
    def autoSecurity(self,imei):
        _ret =db.query("SELECT * FROM CurrentLocation WHERE imei ='{0}'".format(imei))
        pos = _ret[0]
        #获取设防条件
        _ret =db.query("SELECT * FROM Device WHERE imei='{0}'".format(imei))
        dev = _ret[0]
        if dev.monitorState in ['fired','going_out'] :#用户主动放弃监控
            return;
        elif dev.monitorState=='on': #已经启动监控  :
            if pos.speed<0.5:#车辆处于静止状态，安全范围内，
                return;
            else:#车辆在移动中！需要进一步确认是否在安全距离内
                ret = self.bdmap.routematrix([[dev.stopBaiduLat,dev.stopBaiduLng]],[[pos.baiduLat,pos.baiduLng]])
                movedDistance = int(ret[0]["distance"]["value"]) #移动距离
                #安全位置缺省为200米
                fireDistance = (200 if dev.fireDistance==0 else dev.fireDistance)
                if movedDistance<fireDistance:#在安全范围内，
                    return;
                else:#促发告警
                    db.update("Device",where='imei=$imei',vars=locals(),
                                    monitorState="going_out") 
        elif dev.monitorState=='waiting0': #等待监控
            if pos.speed>0:#车处于运行状态中
                return;#不需要监控
            else:#用户停车了，开始监控准备：设置开始时间以及停止位置 ,当停车时间超过设定值则会启动监控
                db.update("Device",where='imei=$imei',vars=locals(),
                                stopTime=datetime.datetime.now(),
                                stopBaiduLat=pos.baiduLat,
                                stopBaiduLng=pos.baiduLng,
                                monitorState ="waiting1")
        elif dev.monitorState=='waiting1': #等待监控
            #已经完成第一次的静止检测，需要考虑是否需要促发告警还是继续等待
            if pos.speed<0.5:#车处于静止状态
                #达到了促发设防条件，促发时间缺省为15分钟
                fireMinutes = (15 if dev.fireMinutes==0 else dev.fireMinutes)
                if (datetime.datetime.now()-dev.stopTime).total_seconds()>=fireMinutes*60:
                    db.update("Device",where='imei=$imei',vars=locals(),
                                       monitorState="on",
                                       monitor_at  =datetime.datetime.now())
                else:#没有达到监控条件，继续等待
                    return;
            else:#车处于运行状态中，没有达到监控条件，设防恢复为初始态
                db.update("Device",where    ='imei=$imei',vars=locals(),
                                stopTime    ="0000-00-00 00:00:00",
                                stopBaiduLat=0,
                                stopBaiduLng=0,
                                monitorState="waiting0")
        return;
        
    def offlineNotify(self,data):
        imei=data.imei
        dev =devdb.getDeviceByImei(imei,format="string")
        if dev["phone"]==None or dev["phone"]=="":
            dev["phone"]="未知手机卡"
        cfgPara={"dev":dev}
        jdkSign={}
        
        cfgPara = json.dumps(cfgPara,ensure_ascii=False)
        ret = self.render.offline_notify(cfgPara,jdkSign)
        return ret
        
    def autoMonitor(self,type="auto"):
        if type=="auto":#根据情况自动检测
            _devsReport=db.query("SELECT COUNT(*) AS sum FROM Device WHERE report_needed=1 ")
            if _devsReport[0].sum==0:#没有发生变化，不需要上报
                return
            
        _devs = db.query("SELECT * FROM Device")
        for dev in _devs:
            self.monitorAndNotifyRelations(dev.imei)
        
        _ret = db.query("SELECT COUNT(*) AS sum FROM Device WHERE lost_state='short'")
        shortSum = _ret[0].sum
        if shortSum==0:#没有短期失联的设备
            return
        #存在短期失联的设备，需要上报运维人员
        _ret = db.query("SELECT COUNT(*) AS sum FROM Device WHERE lost_state='long'")
        longSum = _ret[0].sum
        _ret = db.query("SELECT COUNT(*) AS sum FROM Device")
        sum = _ret[0].sum
        onlineSum = sum-shortSum-longSum
        shortPercent = "%0.1f"%(100.0*shortSum/sum)
        longPercent  = "%0.1f"%(100.0*longSum/sum)
        onlinePercent=100-float(longPercent)-float(shortPercent)

        _mgr = db.query("""SELECT * FROM Manager,Customer 
                                    WHERE Manager.openid=Customer.openid AND
                                          enRange='all'""")
        systemMsg = objWeixin.iconfig.systemMsg
        systemMsg["data"]["first"]["value"]    ="设备失联情况通报"
        systemMsg["data"]["keyword1"]["value"] ="在线状况统计"
        systemMsg["data"]["keyword2"]["value"] =datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        systemMsg["data"]["remark"]["value"]   ="""
在线:        {5}({6}%)
离线>15分钟：{0}({1}%)
离线>   7天：{2}({3}%)
设备总数：{4}""".format(shortSum,shortPercent,longSum,longPercent,sum,onlineSum,onlinePercent)
        cmd = "autoMonitor_{0}_{1}_{2}".format(onlineSum,shortSum,longSum)
        for mgr in _mgr:
            if objWeixin.customser_msg_is_frequent(mgr.openid,cmd):
                continue
            systemMsg["url"]="{0}/m/device?act=GET-ONLINE-STATE&openid={1}".format(icfg.domain,mgr.openid)
            systemMsg["touser"] = mgr.openid
            try:
                objWeixin.send_template_msg(systemMsg)
            except Exception as e:
                print("openid:{0} -nickname:{1} -except:{2}".format(mgr.openid,mgr.nickname,e))
            
         
    def secondsFormat(self,seconds):
        day = int(seconds/(60*60*24))
        hour =int((seconds%(60*60*24))/(60*60))
        min  =int(((seconds%(60*60*24))%(60*60))/60)
        ret = ""
        if day > 0:
            ret=ret+'{0}天'.format(day)
        if hour>0:
            ret=ret+'{0}时'.format(hour)
        ret=ret+'{0}分钟'.format(min)
        return ret
        