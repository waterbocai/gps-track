# -*- coding: utf-8 -*-
import web
import time
import datetime
import json
import re
import utility as uTools
import logstat
from product.mobile.tradeorder import tradeObj
from product.model.historytrackmgr import historyTrackMgr
import product.model.devdb as devdb
import product.model.linedb as linedb
import product.iconfig as iconfig
from product.iconfig import db,objWeixin

class BusTrack:
    def __init__(self):
        templates_path =__file__.split(".py")[0]
        self.render = web.template.render(templates_path)

        
    def GET(self):
        data = web.input()
        #print web.ctx.env['REQUEST_METHOD']
        self.env = iconfig.getEnvObj()
        self.url =self.env['url']
        openid =objWeixin.getOpenid(data)

        if data.has_key('act'):
            act = data.act.upper()
        else:
            act = "MINE_TRACK"
        logstat.logAccessUrl(openid,act) #记录用户访问
        if(act =="MINE_TRACK"):
            #处理2种情况：
            #1.初次打开时，依据openid自动获取imei
            #2.指定imei的情况
            ret = self.getMineTrackMsg(openid,data)
        elif(act =="TEST"):
            ret = self.getTest(openid,data)
        elif(act =="HISTORY-TRACK"):
            ret =  self.getHistoryTrackMsg(openid,data)
        elif(act =="HISTORY-STAT"):
            ret = self.getHistoryStatMsg(openid,data)
        elif(act =="BAIDU-HISTORY-TRACK"):
            ret = self.getHistoryTrackMsg(openid,data,"BAIDU")
        return ret
        
    def POST(self):
        data = web.input()
        if not data.has_key('act'):
            return
        act = data.act.upper()
        openid =objWeixin.getOpenid(data)
        if act == 'GET-GROUP-BY-IMEI':
            ret = self.getGroupByImeiMsg(openid,data)
        elif(act =="HISTORY-TRACK"):
            ret =  self.getHistoryTrackMsg(openid,data)
        elif(act =="BAIDU-HISTORY-TRACK"):
            ret =  self.getHistoryTrackMsg(openid,data,"BAIDU")
        elif(act =="HISTORY-STAT"):
            ret = self.getHistoryStatMsg(openid,data)
        elif(act=='MINE_TRACK'):
            ret = self.getMineTrackMsg(openid,data)
        return ret
    #找到一个可以展示的设备，
    #1.优先选择自己管理的设备
    #2.其次选择朋友分享的
    #3.
    def getValidDev(self,openid,imei):
        _dev = devdb.validAuthDev(openid,imei)
        #print("_dev:{0}".format(_dev))
        if _dev =="":
           _dev =  devdb.getOneDevByOpenid(openid)
        if _dev =="":
           _dev =  devdb.getDemoDev()
        return   _dev  
     
    def getMineTrackMsg(self,openid,data):
        #jdkSign = objWeixin.get_jdk_sign(self.url)
        company_id = data.company_id
        jdkSign={}
        dev = devdb.getDevice(data.imei)
        
        if dev !="":
            #查询设备位置信息
            arm = historyTrackMgr.getMineTrack(dev['imei'])
            _ret = db.query("SELECT * FROM BusLine WHERE busgroupid={0}".format(dev["groupid"]))
            busline=_ret[0]

            sites = linedb.getSitesByLineid(busline.id,"manual")
            cfgPara = {
                "pt"    :arm,
                'openid':openid,
                'dev'   :dev,
                'busline_id':busline.id,
                'sites'     :sites["manual"],
                'url'       :"gxsaiwei/m/bustrack?act=MINE_TRACK&openid={0}&imei=".format(openid),
                'imei'      :dev['imei'],
                "company_id":company_id,
            }
        else:
            cfgPara = {
                "pt" :"",
                'openid':openid,
                'dev':"",
                'url':"#",
                'imei':"",
                'sites':[],
                'busline_id':-1,
                "company_id":company_id,
            }   
        if  web.ctx.method=='GET':
            jdkSign = objWeixin.get_jdk_sign(self.url)
            sharePara=tradeObj.genPreSharePara("share_view",openid,cfgPara['imei'])
            _cfgPara = json.dumps(cfgPara,ensure_ascii=False)
            ret = self.render.mytrackqq_v2(_cfgPara,jdkSign,sharePara)
            #ret = self.render.mytrackqq_v1(cfgPara,_cfgPara)
        else:
            ret =uTools.formatPostMsg(cfgPara)
        return ret 
    

    
    def getRefreshPosMsg(self,openid,data):
        imeis = data.imeis.encode('utf-8').split(',')
        #openid = data.openid.encode('utf-8')
        openid = ""
        arms = self.getArmPos(imeis,openid)
        ret ={'arms':arms}
        web.header('Content-Type', 'application/json')
        return json.dumps(ret,ensure_ascii=False)
    
    def getArmPos(self,imeis,openid=""):
        arms = []
        for imei in imeis:
            _ret= db.query("SELECT * FROM CurrentLocation WHERE imei='{0}'".format(imei))
            arm = _ret[0]
            arms.append({'lat':arm.qqLat,
                        'lng':arm.qqLng,
                        'addr':arm.addr,
                        'speed':arm.speed})
        return arms
        
    
    def getHistoryStatMsg(self,openid,data):
        imei      =data.imei
        startTime =data.startTime
        endTime   =data.endTime
        
        statRet = historyTrackMgr.getHistoryStat(imei,startTime,endTime)
        _dev = db.query("SELECT * FROM Device WHERE imei='{0}'".format(imei))
        dev = _dev[0]
        cfgPara={
            'imei':imei,
            'name':dev.name,
            'pts':statRet,
            'url':"/m/bustrack?act=HISTORY-STAT&strict=y&openid={0}&startTime={1}&endTime={1}&imei=".format(openid,data.startTime,data.endTime),
        }
        if  web.ctx.env['REQUEST_METHOD']=='GET':
            ret = self.render.historystat(json.dumps(cfgPara,ensure_ascii=False))
        else:
            ret = uTools.formatPostMsg(cfgPara)
        return ret
        
    
    def getHistoryTrackMsg(self,openid,data,mapType="QQ"):
        imei = data.imei

        fromTime =datetime.datetime.strptime(data.startTime, "%Y-%m-%d %H:%M:%S")
        toTime   =datetime.datetime.strptime(data.endTime, "%Y-%m-%d %H:%M:%S")
        _pts = historyTrackMgr.getHistoryTrack(imei,fromTime,toTime)
        pts =[]
        start_gmileage=-1
        for pt in _pts:
            if start_gmileage==-1:
                start_gmileage = pt.gmileage
            pts.append(uTools.dbItem2Dict(pt,format="string"))
            pts[-1]["dist"] = float("%0.2f"%(pt["gmileage"] - start_gmileage))
            
        dev = devdb.getDevice(imei)
        sites = linedb.getHistorySitesByImei(imei,fromTime,toTime)
        cfgPara = {
            'dev':dev,
            'pts':pts,
            'sites':sites,
            'openid':openid,
            'startTime':fromTime.strftime("%m/%d %H:%M"),
            'endTime': toTime.strftime("%m/%d %H:%M"),
            'url':"/m/bustrack?act=HISTORY-TRACK&strict=y&openid={0}&startTime={1}&endTime={1}&imei=".format(openid,data.startTime,data.endTime),
        }
        
        if  web.ctx.method=='GET':
            if mapType=="QQ":
                ret = self.render.historytrackqq(json.dumps(cfgPara,ensure_ascii=False))
            elif mapType=="BAIDU":
                #print cfgPara
                ret = self.render.historytrackbaidu(json.dumps(cfgPara,ensure_ascii=False))
        else:
            ret =self._formatPostMsg(cfgPara)
        return ret 

        #对post消息进行统一标准化为json格式
    def _formatPostMsg(self,cfgPara):
        web.header('Content-Type', 'application/json')
        ret =json.dumps(cfgPara,ensure_ascii=False)
        return ret
        

       

    def secondsFormat(self,seconds):
        day = int(seconds/(60*60*24))
        hour =int((seconds%(60*60*24))/(60*60))
        min  =int(((seconds%(60*60*24))%(60*60))/60)
        ret = ""
        if day > 0:
            ret=ret+'{0}d'.format(day)
        if hour>0:
            ret=ret+'{0}h'.format(hour)
        ret=ret+'{0}m'.format(min)
        return ret
    

    def getGroupByOpenid(self,openid):
        #获取该用户下的所有可见的分组信息
        _grps = db.query("""SELECT * FROM CustomerHasDeviceGroup,DeviceGroup 
                                          WHERE CustomerHasDeviceGroup.Customer_openid ='{0}' AND
                                                DeviceGroup.id = CustomerHasDeviceGroup.DeviceGroup_id
                                          """.format(openid))
        if len(_grps)==0: #该用户还没有设备，取演示分组的设备
            _grps = db.query("SELECT *,id AS DeviceGroup_id FROM DeviceGroup WHERE id =1")
        
        grpRet = []
        for grp in _grps:
            _grp = []
            _devs = db.query("""SELECT *,Device.heardbeat_at AS lastTIme FROM Device,CurrentLocation
                                         WHERE CurrentLocation.imei  = Device.imei    AND
                                               Device.DeviceGroup_id  ={0}""".format(grp.DeviceGroup_id))
            for dev in _devs:
                timeDiff = (datetime.datetime.now()-dev.lastTIme).seconds
                online = ("离线" if (timeDiff>600) else "在线")
                _grp.append({
                    'name':dev.name,
                    'speed':dev.speed,
                    'online':online,
                    'addr'  :dev.province[0:2]+dev.city,
                    'imei'  :dev.imei
                })
            grpRet.append({
                'name':grp.name,
                'devs':_grp
            })
        return grpRet
        
        
    def getGroupByImeiMsg(self,openid,data):
        imei    = data.imei
        grps    = devdb.getDeviceGroup(openid)
        
        #将原来的url中的imei替换成新的，以实现场景的平滑切换
        #for grp in grps:
        #    for dev in grp['devs']:
        #        #result,n = re.subn(r'imei=\d+','imei={0}'.format(dev['imei']),fromUrl)
        #        dev['url']="/m/bustrack?act=MINE_TRACK&imei={0}".format(dev['imei'])
        #ret = self.render.devicegroup4share(fromUrl,json.dumps(grps,ensure_ascii=False))
        return uTools.formatPostMsg(grps)
        

        
        
        
