# -*- coding: utf-8 -*-
import web,csv
import datetime 
import product.iconfig as icfg
import product.model.devdb as devdb
import product.model.linedb as linedb

import json
import gps2.gxsaiwei.lib.utool as swtool
import utility as uTools
import ftp
import copy
seatState={"seated":"有人","idle":"空座","timeout":"超时","unkown":"未知"}
#查询座位信息
def getBusTravelByTimeSpan(imei,from_time,to_time):
    _travels = icfg.db.query("""SELECT * FROM BusTravel
                              WHERE imei='{0}' AND
                                    from_time>='{1}' AND from_time<='{2}'                              
             """.format(imei,from_time,to_time))
    travels =[]
    for travel in _travels:
        travel["duration_time"] = uTools.secondsFormat2((travel.to_time - travel.from_time).total_seconds())
        travels.append(uTools.dbItem2Dict(travel,format="string"))
        
        for _dir in ["from","to"]:
            _ret = icfg.db.query("""SELECT * FROM SiteSeatStatus,Sites  
                                             WHERE SiteSeatStatus.id={0}  AND
                                                   SiteSeatStatus.manual_site_id =  Sites.id                                           
                                 """.format(travel[_dir+"_site_id"]))
            travels[-1][_dir+"_name"]=_ret[0].name
    return travels
    
    
#查询座位信息
def getSeatStatus(bustravel_id):
    _ret = icfg.db.query("SELECT * FROM BusTravel WHERE id={0}".format(bustravel_id))
    bustravel = _ret[0]
    #按座位号进行排序
    seat2sensor = devdb.seat2sensor(bustravel.imei)
    rows =[]
    merges =[]
    no = 0
    for seat_name in sorted(seat2sensor.keys()):
        _seatStatus = icfg.db.query("""SELECT * FROM SeatStatus
                                    WHERE bustravel_id={0}  AND sensor_no ={1}
                                    ORDER BY from_time""".format(bustravel_id,seat2sensor[seat_name]))
        if len(_seatStatus)==0:
            rows.append({"seat_name":seat_name})
            no += 1
            continue
        if len(_seatStatus)>1:
            merges.append({"index":no,"rowspan":len(_seatStatus)}) 
        for seatstatus in _seatStatus:
            no += 1
            rows.append(uTools.dbItem2Dict(seatstatus,format="string"))
            for _dir in ["from","to"]:
                _ret = icfg.db.query("""SELECT * FROM TravelSites,Sites  
                                                WHERE TravelSites.id={0}  AND
                                                    TravelSites.manual_site_id =  Sites.id                                           
                                    """.format(seatstatus[_dir+"_travel_site_id"]))
                rows[-1][_dir+"_name"]=_ret[0].name
            rows[-1]["seat_name"]=seat_name
            rows[-1]["seat_state_ch"]=seatState[rows[-1]["seat_state"]]
    seats={"total":no,"rows":rows,"merges":merges}
    return seats

def getSeatStatusDithering(bustravel_id):
    _ret = icfg.db.query("SELECT * FROM BusTravel WHERE id={0}".format(bustravel_id))
    bustravel = _ret[0]
    #按座位号进行排序
    seat2sensor = devdb.seat2sensor(bustravel.imei)
    rows =[]
    merges =[]
    no = 0
    for seat_name in sorted(seat2sensor.keys()):
        _seatStatus = icfg.db.query("""SELECT * FROM SeatStatusDithering
                                    WHERE bustravel_id={0} AND seat_state='seated' AND
                                          sensor_no ={1}
                                    ORDER BY from_time""".format(bustravel_id,seat2sensor[seat_name]))
        if len(_seatStatus)==0:
            rows.append({"seat_name":seat_name})
            no += 1
            continue
        if len(_seatStatus)>1:
            merges.append({"index":no,"rowspan":len(_seatStatus)})
        for seatstatus in _seatStatus:
            no += 1
            rows.append(uTools.dbItem2Dict(seatstatus,format="string"))
            for _dir in ["from","to"]:
                _ret = icfg.db.query("""SELECT * FROM TravelSites,Sites  
                                                WHERE TravelSites.id={0}  AND
                                                    TravelSites.manual_site_id =  Sites.id                                           
                                    """.format(seatstatus[_dir+"_travel_site_id"]))
                rows[-1][_dir+"_name"]=_ret[0].name
            rows[-1]["seat_name"]=seat_name
            rows[-1]["seat_state_ch"]=seatState[rows[-1]["seat_state"]]
    seats={"total":no,"rows":rows,"merges":merges}
    return seats
    
def getTravelSite(bustravel_id):
    rows = []
    _sites = icfg.db.query("SELECT * FROM TravelSites WHERE id={0} ORDER BY from_time".format(bustravel_id))
    for site in _sites:
        _ret = icfg.db.query("""SELECT * FROM Sites WHERE id ={0}""".format(site.manual_site_id))
        manual_site = _ret[0]
        rows.append(uTools.dbItem2Dict(site,format="string"))
        rows[-1]["site_name"] = manual_site.name
        rows[-1]["address"]   = manual_site.address
        
        _ret = icfg.db.query("""SELECT * FROM SiteSeatStatus WHERE id ={0}""".format(site.site_seatstatus_id))
        seatstatu_site = _ret[0]
        rows[-1]["duration_time"] =uTools.secondsFormat2((site.to_time-site.from_time).total_seconds())
        rows[-1]["from_seated_num"]=seatstatu_site.from_seated_num
        rows[-1]["to_seated_num"]=seatstatu_site.to_seated_num 
        rows[-1]["num_change"]=seatstatu_site.num_change
    sites={"total":len(rows),"rows":rows}
    return sites
    
    
def addMonitorRegion(busline_id,from_historytrack_id,to_historytrack_id):
    
    #添加到sites库
    from_site_id =swtool.addSite(from_historytrack_id,"monitor_region_site")
    to_site_id   =swtool.addSite(to_historytrack_id,"monitor_region_site")
    gmileage     =swtool.getSitesGmileage(from_site_id,to_site_id)
    id = icfg.db.insert("MonitorRegion", busline_id=busline_id,
                      from_site_id=from_site_id,
                      to_site_id=to_site_id,
                      gmileage  = gmileage,
                      receiver  ="manager")
    return id
    
def getLineMonitorRegionByImei(imei):
    busline = linedb.getBuslineByImei(imei)
    rows = getLineMonitorRegionByLineid(busline["id"])
    return rows
    
def getLineMonitorRegionByLineid(busline_id):
    rows =[]
    _regions = icfg.db.query("SELECT * FROM MonitorRegion WHERE busline_id={0}".format(busline_id))
    
    for row in _regions:
        row = getMonitorRegionInfoById(row.id)
        rows.append(row)
    return rows

def getMonitorRegionInfoById(region_id):
    region = getMonitorRegionById(region_id,format="string")
    for dir in ["from","to"]:
        _ret = icfg.db.query("""SELECT name,address,gpsLat,gpsLng,qqLat,qqLng,baiduLat,baiduLng 
                                FROM Sites WHERE id={0}""".format(region[dir+"_site_id"]))
        site = _ret[0]
        region[dir+"_name"] =site.name
        if site.name=="":
            region[dir+"_name"] = site.address
        region[dir+"_gpsLat"] =site.gpsLat
        region[dir+"_gpsLng"] =site.gpsLng
        region[dir+"_qqLat"] =site.qqLat
        region[dir+"_qqLng"] =site.qqLng
        region[dir+"_baiduLat"] =site.baiduLat
        region[dir+"_baiduLng"] =site.baiduLng
        region[dir+"_addr"] =site.address
    return region
            
def delMonitorRegion(id):
    _ret = icfg.db.query("DELETE FROM MonitorRegion WHERE id={0}".format(id))
    return
    
    
def getMonitorRegionById(monitor_region_id,format="origion"):
    _ret = icfg.db.query("SELECT * FROM MonitorRegion WHERE id={0}".format(monitor_region_id))
    ret  = uTools.dbItem2Dict(_ret[0],format)
    return ret
        
        
def getMonitorRegionResultByImei(imei,from_time,to_time):
    rows =[]
    _ret = icfg.db.query("""SELECT * FROM MonitorResult WHERE imei='{0}' AND 
                                from_time >='{1}' AND to_time<='{2}'
                     """.format(imei,from_time.strftime("%Y-%m-%d %H:%M:%S"),to_time.strftime("%Y-%m-%d %H:%M:%S")))
    region  = {}
    
    for item in _ret:
        if region.has_key(item.monitor_region_id)==False:
            region[long(item.monitor_region_id)] = getMonitorRegionInfoById(item.monitor_region_id)
        rows.append(uTools.dbItem2Dict(item,format="string"))

    for row in rows:
        row["from_name"] = region[row["monitor_region_id"]]["from_name"]
        row["to_name"]   = region[row["monitor_region_id"]]["to_name"]
        row["times_percent"]   = "{0}%".format(region[row["monitor_region_id"]]["times_percent"])
        row["mileage_percent"] = "{0}%".format(region[row["monitor_region_id"]]["mileage_percent"])
        del row["seatStatus"]
        
    ret = {"region":region,"rows":rows}
    return ret
    
    
def getRegionResultDetailById(id):
    _ret = icfg.db.query("""SELECT * FROM MonitorResult WHERE id={0}
                         """.format(id))
    regionResult =_ret[0]
    stat = json.loads(regionResult.seatStatus)
    sensor2seat = devdb.seat_template(regionResult.imei)
    rows = []
    for no in stat["mileage"]:
        if sensor2seat.has_key(long(no))==False:
            continue;
        row={"sensor_no"      :no,"seat_no":sensor2seat[long(no)],
             "checked_result" :stat["checked_result"][no],
             "times_result"   :stat["times"][no]["result"],
             "times_percent"  :stat["times"][no]["percent"],
             "mileage_percent":stat["mileage"][no]["percent"],
             "mileage_result" :stat["mileage"][no]["result"],
             }
        for _type in ["times","mileage"]:
            for _state in ["seated","idle","unkonwn","outtime"]:
                row[_type+"_"+_state] = (stat[_type][no][_state] if stat[_type][no].has_key(_state) else 0)
        rows.append(row)
    return rows
    
    
def updateRegionResultDetail(region_result_id,changeSeat):
    _ret = icfg.db.query("""SELECT seatStatus FROM MonitorResult WHERE id={0}
                         """.format(region_result_id))
    regionResult =_ret[0]
    seatStatus = json.loads(regionResult.seatStatus)
    for sensor_no in changeSeat:
        seatStatus["checked_result"][sensor_no]=changeSeat[sensor_no]
    checked_sum =0
    for no in seatStatus["checked_result"]:
        if seatStatus["checked_result"][no]=="有人":
            checked_sum+=1
    
    _seatStatus = json.dumps(seatStatus)
    icfg.db.update("MonitorResult",where="id=$region_result_id",vars=locals(),
                                   seatStatus=_seatStatus,
                                   checked_sum=checked_sum)
    return
    
    
    
        
        
    
