# -*- coding: utf-8 -*-
import web
import time
import datetime 
import product.model.busdb as busdb

class SeatStat:
    def __init__(self):
        pass
    
    def GET(self):
        data = web.input()
        act = data.act.upper()
        if  act  == 'PLATES':
            return busdb.getAllPlates()
        elif act == 'SEATS':
            return self.getSeatsByImei(data)
        elif act == 'SEATS-MERGE-STRATEGYS':
            return busdb.getSeatMergeStrategys()
        else:
            pass
        return        
     
    def POST(self):
        data = web.input()
      

    def getSeatsByImei(self, data):
        imei    =data.imei
        if len(imei)< 5:#非法的imei号
            return []
        if data.has_key("toTime")==False:
            toTime0 = datetime.datetime.now()
            toTime = datetime.datetime.strftime(toTime0,"%Y-%m-%d %H:%M:%S")
        else:
            toTime = data.toTime
            
        if data.has_key("fromTime")==False:#缺省取24小时前
            fromTime0 = toTime0 - datetime.timedelta(hours=24)
            fromTime  = datetime.datetime.strftime(fromTime0,"%Y-%m-%d %H:%M:%S")
        else:
            fromTime = data.fromTime
            
        strategy=data.strategy
        
        ret = busdb.getSeatsByImei(imei,fromTime, toTime,strategy)
        return ret
        
    
 