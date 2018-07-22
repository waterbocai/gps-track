# _*_ coding:utf-8 _*_
import web,json,time,re
import product.iconfig as icfg 
import datetime,requests,random
import md5
import utility as uTools

def getFanBoxName(groupid):
    devs = icfg.db.query("""SELECT * FROM  Device WHERE imei IN (SELECT imei FROM GroupHasDevice WHERE devicegroup_id={0})""".format(groupid))
    area = []
    i = 0
    for dev in devs:
        i+=1
        name="机房{0}".format(i)
        area.append({"imei":dev.imei,
                     "name":name})
    return area
    
def getFanStateByArea(imeis):
    _imeis = json.dumps(imeis)
    _fans = icfg.db.query("SELECT * FROM FanState WHERE imei in ({0})".format(_imeis[1:-1]))
    fans  =[uTools.dbItem2Dict(fan,format="string") for fan in _fans]
    return fans
