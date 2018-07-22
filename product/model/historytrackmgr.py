# _*_ coding:utf-8 _*_
import web
from config import db
import datetime
import random
from baidumap import BaiduMap
import md5
import utility as uTools
from pyExcelerator import *

_max_db_num    = 100
_max_order_num = 500000
_max_start_num = 500000  #支持926(=5556/6)个GPS同时在线
class HistoryTrackMgr:
    #查询当前历史数据库数据流入速度
    def getCurrentInputSpeed(self):
        now = datetime.datetime.now()
        past_minites = now - datetime.timedelta(minutes=5)
        _ret  = db.query("SELECT COUNT(*) AS sum FROM HistoryTrack WHERE report_at>'{0}' AND report_at<'{1}'".format(past_minites.strftime("%y-%m-%d %H:%M:%S"),now.strftime("%y-%m-%d %H:%M:%S")))
        incrNum = _ret[0].sum
        return incrNum
    
    #查询历史数据流入的目标库    
    def getInput2Table(self,incrSum):
        #查询最近一个可用的历史数据库
        for i in range(_max_db_num):
            _ret = db.query("SELECT * FROM HistoryTrackTable WHERE id={0}".format(i+1))
            selTable = _ret[0]
            if selTable.sum+incrSum<_max_order_num:
                selTable = selTable
                break
        return selTable 
        
    def moveData2History(self):
        #step0: 判定是否需要启动数据搬迁>_max_start_num
        _ret = db.query("SELECT COUNT(*) AS sum FROM HistoryTrack")
        if _ret[0].sum<_max_start_num:
            return 0
        #step1：确定当前流入历史库的速度
        incrNum   = self.getCurrentInputSpeed()
        #step2: 确定迁移的目标数据库
        selTable =self.getInput2Table(incrNum)
        selTableId = selTable.id
        #step3: 确定选定要迁移的数据
        items = db.query("SELECT * FROM HistoryTrack ORDER BY report_at LIMIT {0}".format(incrNum))
        for i in range(incrNum):
            item = items[i]
            if selTable.sum==0:
                db.update("HistoryTrackTable",where='id=$selTableId',
                                             from_time=item.report_at.strftime("%Y-%m-%d %H:%M:%S"),
                                             vars=locals())
            #将数据移入新的数据库
            db.insert(selTable.tableName,imei   =  item.imei,          
                                report_at       =  item.report_at,     
                                gpsLat    	    =  item.gpsLat,    	  
                                gpsLng          =  item.gpsLng,        
                                speed     	    =  item.speed,     	  
                                realState       =  item.realState,     
                                lngType         =  item.lngType,       
                                latType         =  item.latType,       
                                direction       =  item.direction,     
                                addr            =  item.addr,          
                                province        =  item.province,     
                                city            =  item.city,          
                                gpsReport       =  item.gpsReport,     
                                reportMode      =  item.reportMode,    
                                ACC             =  item.ACC,           
                                CellID          =  item.CellID,        
                                LAC             =  item.LAC,           
                                MNC             =  item.MNC,           
                                MCC             =  item.MCC,           
                                satNum          =  item.satNum,        
                                locatedState    =  item.locatedState,  
                                gpsTime         =  item.gpsTime,       
                                qqLat           =  item.qqLat,         
                                qqLng           =  item.qqLng,         
                                baiduLat        =  item.baiduLat,      
                                baiduLng        =  item.baiduLng,      
                                country         =  ('中国' if item.country is None else item.country),       
                                alarm           =  ('' if item.alarm is None else item.alarm),        
                                height          =  item.height,        
                                battery         =  item.battery,       
                                gsm_intensity   =  item.gsm_intensity,      
                                seatStatus      =  item.seatStatus,    
                                mileage         =  item.mileage,      
            )               
            #删除原来库的数据
            db.query("DELETE FROM HistoryTrack WHERE id={0}".format(item.id))
        #刷新截至时间与最新数据
        db.update("HistoryTrackTable",where='id=$selTableId',
                                      sum = selTable.sum+incrNum,
                                      to_time=item.report_at.strftime("%Y-%m-%d %H:%M:%S"),vars=locals())
        return incrNum

    
    def getHistoryTrack(self,imei,from_time,to_time):
        ponits = []
        hisTables  = []
        strFrom = from_time.strftime("%Y-%m-%d %H:%M:%S")
        strTo   = to_time.strftime("%Y-%m-%d %H:%M:%S")
        #规避gps重启的历史数据
        gpsTime = (from_time - datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        
        #搜索可能存在的历史库
        _hisTables = db.query("""SELECT * 
                                    FROM HistoryTrackTable 
                                    WHERE from_time<='{0}' AND to_time>='{0}'  
                                    ORDER BY from_time""".format(strTo,strFrom))
        for tbl  in _hisTables:
            hisTables.append(tbl.tableName)
        hisTables.append("HistoryTrack")
        #在所有可能数据库中查找满足要求的数据
        for tblName in hisTables:
            _ret = db.query("""SELECT * FROM {3} 
                                    WHERE imei='{2}' AND 
                                    gpsTime >='{0}' AND gpsTime <='{1}' AND gmileage>0
                                    ORDER BY gpsTime""".format(strFrom,strTo,imei,tblName))
            for pt in _ret:
                ponits.append(pt)          
        return ponits
        
    def getHistoryTrack4b(self,imei,startTime,endTime,mapType):
        if isinstance(startTime,datetime.datetime):
            fromTime = startTime
            toTime   = endTime
        else:
            fromTime = datetime.datetime.strptime(startTime,"%Y-%m-%d %H:%M:%S")
            toTime   = datetime.datetime.strptime(endTime,"%Y-%m-%d %H:%M:%S")
        #根据同步时区,中国属于东8区
        fromTime = fromTime-datetime.timedelta(hours=0)
        toTime   = toTime-datetime.timedelta(hours=0)
        pts = []
        pts1 = []
        _pts =self.getHistoryTrack(imei,fromTime,toTime)
        initMileage =  -1

        #规避sae  slq  order by 65536的限制
        lastDist = 0
        for pt in _pts:
            if initMileage ==-1:#初始化里程
                initMileage =(0 if pt["gmileage"] is None else pt["gmileage"])
            if pt["qqLat"] ==0 or pt["qqLng"]==0:#抛弃异常节点
                continue

            dist =(lastDist if pt["gmileage"]==0 else "%0.2f"%(pt["gmileage"]-initMileage))
            
            lastDist = dist
            pts.append({'gpsTime':pt["report_at"].strftime("%Y-%m-%d %H:%M:%S"),
                        'addr':pt["addr"],
                        'speed':pt["speed"],
                        'dist':float(dist)})
            pts[-1]['id'] =pt["id"]            
            pts[-1]['direction']=pt["direction"]
            pts[-1]['lat']=pt["qqLat"]
            pts[-1]['lng']=pt["qqLng"]
            pts[-1]['baiduLat']=pt["baiduLat"]
            pts[-1]['baiduLng']=pt["baiduLng"] 
            pts[-1]['qqLat']=pt["qqLat"]
            pts[-1]['qqLng']=pt["qqLng"]
            pts[-1]['img_path']  =("" if pt["img_path"]  ==None else pt["img_path"])
            pts[-1]['video_path']=("" if pt["video_path"]==None else pt["video_path"])            
            #pts1.append([pt["baiduLat,pt["baiduLng])
        #如果没有历史数据，直接取当前数据
        if len(pts)==0:
            pt  = self.getMineTrack(imei)
            for i in range(2):
                pts.append(pt)
                pts[-1]['dist']=0
        return pts
    
            
    def getHistoryStat(self,imei='86304020537125',startTime='2015-3-09',endTime='2015-3-10',stopMinutes=5,reqType="mobile"):
        #时区平移
        if isinstance(startTime,datetime.datetime)==False:
            startTime = datetime.datetime.strptime(startTime,"%Y-%m-%d %H:%M:%S")
            endTime = datetime.datetime.strptime(endTime,"%Y-%m-%d %H:%M:%S")
        #startTime = startTime-datetime.timedelta(hours=8)
        #endTime = endTime-datetime.timedelta(hours=8)
        
        sites = self.getHistoryTrack(imei,startTime,endTime)
        if reqType=="mobile" :
            timeFormat ="%H:%M"
            dateFormat ="%m/%d"
            splitStr   ="<br>"
        else:
            timeFormat = "%H:%M:%S"
            dateFormat = "%Y-%m-%d"
            splitStr   =" - "
        pts = []
        pts1 = [] #用于计算路程
        stopStart =""
        stopEnd   =""
        addr     =""
        daySplit =""
        lenth = len(sites)
        if lenth <2:#没有历史数据，直接取当前
            pt  = self.getMineTrack(imei)
            sites = db.query("SELECT * FROM CurrentLocation WHERE imei='{0}'".format(imei))
            site=sites[0]
            for i in range(2):
                pts.append({'report_at':'{0}'.format(site.report_at.strftime("%H:%M")),
                    'speed':site.speed,
                    'duration':0,
                    'addr':'{0}{1}'.format(site.city,site.addr),
                    'dist':0,
                    'seated_num':0,
                    "seat_status"  :"",
					 "date":"",
                })
        else:
            daySplitArr = []
            initMileage = -1
            i = 0
            lastDist = 0
            for site in sites:
                i+=1 #计数
                if (initMileage == -1):
                    initMileage =site.gmileage
                
                #获取座位信息
                seatStatus =site.seatStatus
                if (seatStatus is None):
                    seatStatus =""
                 
                day  = site.gpsTime.strftime(dateFormat) 
                if daySplit!=day:#日期发生改变了
                    daySplit = day
                    #print(site.gpsTime.strftime("%m/%d %H:%M:%S") )
                    #记录正常行进值
                    dist =(lastDist if site.gmileage==0 else "%0.2f"%(site.gmileage-initMileage))
                    lastDist = dist
                    pts.append({'report_at':'{0}'.format(daySplit),
                        'speed':"-",
                        'duration':"-",
                        'addr':'-',
                        'dist':dist,
                        'seated_num':seatStatus.count("0},"),
                        "seat_status"  :seatStatus,
                        "date":day
                    }) 
                    
                if site.speed<5 and i<lenth:
                    if stopStart=="":#记录停止开始时间
                        stopStart = site.gpsTime
                        addr      ='{0}{1}'.format(site.city,site.addr)
                        stopEnd = site.gpsTime
                    else:
                        stopEnd = site.gpsTime
                else:
                    if stopStart !="":#记录之前停止信息
                        duSeconds = (stopEnd-stopStart).total_seconds()
                        if duSeconds>60:#对短时间停车值进行修正 
                            stopStartS = stopStart.strftime(timeFormat)
                            stopEndS = stopEnd.strftime(timeFormat)
                            dist =(lastDist if site.gmileage==0 else "%0.2f"%(site.gmileage-initMileage))
                            lastDist = dist
                            pts.append({'report_at':'{0}{2}{1}'.format(stopStartS,stopEndS,splitStr),
                                'speed':0,
                                'duration':uTools.secondsFormat(duSeconds),
                                'addr':addr,
                                'dist':dist,
                                'seated_num':seatStatus.count("0},"),
                                "seat_status"  :seatStatus,
                                "date":day
                            })
                        stopStart=""
                        stopEnd  =""
                        addr     =""
                    #记录正常行进值
                    dist =(lastDist if site.gmileage==0 else "%0.2f"%(site.gmileage-initMileage))
                    lastDist = dist
                    pts.append({'report_at':'{0}'.format(site.gpsTime.strftime(timeFormat)),
                        'speed':site.speed,
                        'duration':0,
                        'addr':'{0}{1}'.format(site.city,site.addr),
                        'dist':dist,
                        'seated_num':seatStatus.count("0},"),
                        "seat_status"  :seatStatus,
                        "date":day
                    })
            
        #查询距离
        #print "开始：{0}".format(datetime.datetime.now().strftime("%H:%M:%S"));
        #print "pts1 len:{0}".format(len(pts1))
        #dist = self.routematrix(pts1)
        #print "结束：{0}".format(datetime.datetime.now().strftime("%H:%M:%S"));
        #for i in range(len(pts)):
        #    pts[i]['dist'] = "%0.2f"%(dist[i]/1000.0)                
        return pts
    #统计停车位置列表    
    def getHistorySite(self,imei,startTime,endTime):
        _sites = db.query("""SELECT * FROM SiteSeatStatus,Sites 
                             WHERE imei='{0}' AND 
                                   from_time>='{1}' AND from_time<='{2}' AND 
                                   SiteSeatStatus.manual_site_id = Sites.id
                            ORDER BY from_time
                """.format(imei,startTime,endTime))
        sites = []
        for site in _sites:
            sites.append(uTools.dbItem2Dict(site,format="string"))
        return sites
    
    def getMineTrack(self,imei):
        ret = []
        #获取路线信息
        _arms = db.query("SELECT * FROM CurrentLocation WHERE imei='{0}'".format(imei))
        try :
            arm =_arms[0]
        except:
            raise("异常：getMineTrack(self,imei)---IMEI:{0}".format(imei))
        myArm = { 'gpsTime':(arm.gpsTime+datetime.timedelta(hours=8)).strftime("%m-%d %H:%M"),
                  'lat':arm.qqLat,
                  'lng':arm.qqLng,
                  'qqLat':arm.qqLat,
                  'qqLng':arm.qqLng,
                  'baiduLat':arm.baiduLat,
                  'baiduLng':arm.baiduLng,
                  'addr' :arm.addr,
                  'speed':arm.speed,
                }
        return  myArm
    def getHistoryStatXls(self,imei,fromTime,toTime,xls_file=None):
        if xls_file==None:
            ret  = db.query("SELECT * FROM Device WHERE imei='{0}'".format(imei))
            dev = ret[0]
            if isinstance(fromTime,datetime.datetime)==False:
                fromTime = datetime.datetime.strptime(fromTime,"%Y-%m-%d %H:%M:%S")
                toTime = datetime.datetime.strptime(toTime,"%Y-%m-%d %H:%M:%S")
            xls_relfile = "/files/histat/{0}_{1}_{2}.xls".format(imei,fromTime.strftime("%Y%m%d%H%M%S"),toTime.strftime("%Y%m%d%H%M%S"))
            xls_file = "{0}{1}".format(uTools.public_path,xls_relfile)
        pts = self.getHistoryStat(imei,fromTime,toTime)
        
        wb = Workbook()
        al = Alignment()
        al.horz = Alignment.HORZ_CENTER
        al.vert = Alignment.VERT_CENTER
        borders = Borders()
        borders.left = 1  
        borders.right = 1  
        borders.top = 1  
        borders.bottom = 1 
        style = XFStyle()
        style.alignment = al
        style.borders   = borders
        sum_ws = wb.add_sheet(u"运营统计")
        titles=[u'日期',u'时间',u'速度',u'持续时长',u'详细地址',u'里程(公里)']
        col = 0
        for title in titles:
            sum_ws.write(0,col,title,style)
            col +=1
        row = 1 
        for pt in pts:
            style.alignment.horz = Alignment.HORZ_CENTER
            sum_ws.write(row,0,pt['date'].decode('utf-8'),style)
            sum_ws.write(row,1,pt['report_at'].replace("<br>"," - ").decode('utf-8'),style)
            sum_ws.write(row,2,pt['speed'],style)
            sum_ws.write(row,3,pt['duration'].decode('utf-8'),style)
            sum_ws.write(row,5,pt['dist'],style)
            style.alignment.horz = Alignment.HORZ_LEFT
            sum_ws.write(row,4,pt['addr'].decode('utf-8'),style)
            row +=1
        wb.save(xls_file)
        return xls_relfile
            
historyTrackMgr = HistoryTrackMgr()