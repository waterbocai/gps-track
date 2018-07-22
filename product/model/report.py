# -*- coding: utf-8 -*-
import web,csv
import datetime 
import product.iconfig as icfg
import json
import utility as uTools
import ftp
import copy
from pyExcelerator import *
    
def genReportOnThreads(imei,fromTime,toTime,csv_file,ftp_addr=None):
     
    #打印原始数据
    writeOrigin2xls(imei,fromTime,toTime,csv_file+'_origin.xls',ftp_addr)
    writeCustomerReport2xls(imei,fromTime,toTime,csv_file+'_report.xls',ftp_addr)

    #writeSeats2xls(_seats,busline.id,sensor2seat,csv_file+".xls",4,ftp_addr)
    return

def order_seat2sensor(imei):
    sensor2seat =seat_template(imei)
    _seat2sensor={}
    for key in sensor2seat.keys():
        _seat2sensor[sensor2seat[key]]=key
    _seat_num = sorted(sensor2seat.values())
    seat2sensor={}
    for seat_name in _seat_num:
        if seat_name==u"未命名":
            continue
        seat2sensor[seat_name] = _seat2sensor[seat_name]
    return seat2sensor
        
        
def seat_template(imei):
    #获取设备信息
    _ret = icfg.db.query("""SELECT * FROM Device WHERE imei='{0}'""".format(imei))
    dev = _ret[0]
    #{"midbus":33,"bed":54,"seat53":60,"seat39":41}
    inTemp = {}
    seats = dev.seat_template.split(";")
    for seat in seats:
        inSeat = seat.split(",")
        if len(inSeat) ==2:
            sensor,name = inSeat
            if sensor=="":
                continue
        else:
            continue
        inTemp[long(sensor)]=name
    for i in range(long(60)):
        if inTemp.has_key(i)==False:
            inTemp[i]=u"未命名"
    return inTemp    
    
def writeOrigin2xls(imei,fromTime,toTime,xls_file,ftp_addr):
    #这里设置对齐方式
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
    wb = Workbook()
    
    sensor2seat = seat_template(imei)
    busline = getBusline(imei)
    prices  = getTotalLinePrice(busline.id)
    seats = icfg.db.query("""SELECT * FROM SeatStatus 
                                   WHERE imei='{0}' AND 
                                         from_time >='{1}' AND to_time<='{2}' AND 
                                         bustravel_id>0
                                   ORDER BY from_time
                            """.format(imei,fromTime,toTime))
    #删除已有文件
    keys = [u"班车线路",u"座位号",u"蓝牙号",u"在位情况",u"开始地址",u"开始站点",u"开始时间",u"开始速度",u"截止地址",u"截止站点",u"截止时间",u"截止速度",u"持续里程(公里)",u"价格",u"持续时间(分钟)",u"开始日期",u"截止日期",u"运行时间",u"运行站点",u"全程里程(KM)","grain_num"]
    ws_orign = wb.add_sheet(u"origin")
    for i in range(len(keys)):
        ws_orign.write(0,i,keys[i],style)
        
    travels = {}
    for i in range(len(seats)):
        seat = seats[i] 
        if travels.has_key(seat.bustravel_id)==False:
            travels[seat.bustravel_id]=getBusTravel(seat.bustravel_id)
        travel = travels[seat.bustravel_id]
        
        pos=[]
        site=[]
        for _dir in ["from","to"]:
            ret = icfg.db.query("SELECT * FROM HistoryTrack WHERE id={0}".format(seat[_dir+"_historytrack_id"]))
            pos.append(ret[0])
            ret = icfg.db.query("""SELECT * FROM TravelSites,Sites 
                                   WHERE TravelSites.manual_site_id=Sites.id AND
                                         TravelSites.id = {0}""".format(seat[_dir+"_travel_site_id"]))
            site.append(ret[0])
        busline_name = travel["busline"]["from_name"]+"-"+travel["busline"]["to_name"]
        ws_orign.write(i+1,0,busline_name,style)
        ws_orign.write(i+1,1,sensor2seat[seat.sensor_no],style)
        ws_orign.write(i+1,2,seat.sensor_no,style)
        ws_orign.write(i+1,3,seat.seat_state,style)
        ws_orign.write(i+1,4,pos[0].addr,style)
        ws_orign.write(i+1,5,site[0].name,style)
        ws_orign.write(i+1,6,pos[0].gpsTime.strftime("%H:%M:%S"),style)
        ws_orign.write(i+1,7,pos[0].speed,style)
        ws_orign.write(i+1,8,pos[1].addr,style)
        ws_orign.write(i+1,9,site[1].name,style)
        ws_orign.write(i+1,10,pos[1].gpsTime.strftime("%H:%M:%S"),style)
        ws_orign.write(i+1,11,pos[1].speed,style)
        ws_orign.write(i+1,12,seat.duration_gmileage,style)
# u"持续里程(公里)",u"价格",u"持续时间(分钟)",u"开始日期",u"截止日期",
        #print(prices)
        ws_orign.write(i+1,13,prices[site[0].manual_site_id][site[1].manual_site_id],style)
        ws_orign.write(i+1,14,seat.duration_seconds/60.0,style)
        ws_orign.write(i+1,15,pos[0].gpsTime.strftime("%Y-%m-%d"),style)
        ws_orign.write(i+1,16,pos[1].gpsTime.strftime("%Y-%m-%d"),style)
#u"行程",u"运行时间",u"运行站点",u"全程里程(KM)","grain_num"]
        runtime = travel["pos"][0].gpsTime.strftime("%H:%M")+"-"+travel["pos"][1].gpsTime.strftime("%H:%M")
        runname = travel["site"][0].name+"-"+travel["site"][1].name
        ws_orign.write(i+1,17,runtime,style)
        ws_orign.write(i+1,18,runname,style)
        ws_orign.write(i+1,19,travel["duration_gmileage"],style)
    wb.save(xls_file)
    #transfer2ftp(ftp_addr,xls_file,4)           
 
def writeCustomerReport2xls(imei,fromTime,toTime,xls_file,ftp_addr):
    #0.创建Excel文件
    wb = Workbook()
    #这里设置对齐方式
    al = Alignment()
    al.horz = Alignment.HORZ_CENTER
    al.vert = Alignment.VERT_CENTER
    borders = Borders()
    borders.left = 1  
    borders.right = 1  
    borders.top = 1  
    borders.bottom = 1 
    #borders.diag = borders.DOUBLE
    #borders.need_diag1 =borders.NEED_DIAG1  #设置是否显示 左上-右下 对角线
    #borders.need_diag2 =borders.NO_NEED_DIAG1  #设置是否显示 左下-右上 对角线
    style = XFStyle()
    style.alignment = al
    #pattern = Pattern()
    #pattern.pattern = pattern.SOLID_PATTERN
    #pattern.set_pattern_back_colour("aqua") #统计背景
    #pattern.set_pattern_back_colour("gray") #标题背景
    #pattern.set_pattern_back_colour("white") #详细内容颜色
    style.borders   = borders
    #style.pattern   = pattern
    seat2sensor = order_seat2sensor(imei)
    try:#判定是否为数字型的
        int(_seat_num[0])
        _seat_type = "num"  #座位是数字型编号
        seat_num =sorted(seat2sensor.keys(), key=lambda d: int(d))
    except:#按字符形式排序
        seat_num =sorted(seat2sensor.keys(), key=lambda d: d)
        _seat_type = "str"  #座位是字符型编号
        
    #keys = ["班车线路","座位号","蓝牙号","在位情况","开始地址","开始站点","开始时间","开始速度","截止地址","截止站点","截止时间","截止速度","持续里程(公里)","价格","持续时间(分钟)","开始日期","截止日期","行程","运行时间","运行站点","全程里程(KM)"]
    travels = icfg.db.query("""SELECT * FROM BusTravel WHERE imei='{0}' AND
                                       from_time>='{1}' AND from_time<'{2}'
                           """.format(imei,fromTime,toTime))
    
    #1.生成汇总报表
    sum_ws = wb.add_sheet(u"汇总报告")
    sum_ws.write(0,0,u'行程',style)    
    sum_ws.write(0,1,u'运行时间',style) 
    sum_ws.write(0,2,u'人数/票数',style)
    sum_ws.write(0,3,u'金额',style)
    sh_no     = 0
    total_fee = 0
    total_customer = 0
    busline_id     = -1
    for travel in travels:
        sh_no += 1
        bustravel = getBusTravel(travel)

        
        #2.生成单程座位状态表
        runtime = travel["pos"][0].gpsTime.strftime("%H:%M")+"-"+travel["pos"][1].gpsTime.strftime("%H:%M")
        runname = travel["site"][0].name+"-"+travel["site"][1].name
        sheet_name = u"{0}-{1}".format(runname,sh_no)
        link_url = u"#'{0}'!A1".format(sheet_name)
        
        #2.1 添加行程sheet页
        travel_ws = wb.add_sheet(sheet_name) 
        #2.2 刷新汇总表
        sum_ws.write(sh_no,0,runname,style)
        sum_ws.set_link(sh_no,0,link_url,u"点击查看详情")
        sum_ws.write(sh_no,1,runtime,style)
        
        #2.3 生成单程表头
        titles = [u'座位号',u'上车站点',u'上车时间',u'下车站点',u'下车时间',u'持续里程(KM)',u'金额',u"抖动次数",u"在位里程/抖动次数",u"在位里程/站点距离",u"有效结论",u"备注"]
        for i in range(len(titles)):
            travel_ws.write(0,i,titles[i],style)
        sites = getBuslineSites(travel.busline_id)
        if busline_id==-1:
            busline_id = travel.busline_id
        fee       = 0  #单程营收价格
        row       = 1
        customer  = 0
        for seat_name in seat_num:
            print("""SELECT * FROM SeatStatusDithering 
                             WHERE bustravel_id={0} AND 
                                   sensor_no   ={1}
                             ORDER BY from_time
                             """.format(travel.id,seat2sensor[seat_name]))
            seats =icfg.db.query("""SELECT * FROM SeatStatusDithering 
                             WHERE bustravel_id={0} AND 
                                   sensor_no   ={1}
                             ORDER BY from_time
                             """.format(travel.id,seat2sensor[seat_name]))
            lenSeats = len(seats)
            if lenSeats==0:#
                travel_ws.write(row,0,seat_name,style)
                for i in range(10):
                    travel_ws.write(row,i+1,"",style)
                row += 1
            else:
                if lenSeats==1:
                    travel_ws.write(row,0,seat_name,style)
                else:
                    travel_ws.write_merge(row,row+lenSeats-1,0,0,seat_name,style)
                for seat in seats:
                    seat = getSeatStatusDithering(seat)
                    style.num_format_str="general"
                    if len(sites)>3:
                        travel_ws.write(row,1,seat["site"][0].name,style)
                        travel_ws.write(row,3,seat["site"][1].name,style)
                    else:
                        travel_ws.write(row,1,seat["pos"][0].local_addr,style)
                        travel_ws.write(row,3,seat["pos"][1].local_addr,style)
                    travel_ws.write(row,2,seat["pos"][0].gpsTime.strftime("%Y-%m-%d %H:%M:%S"),style)
                    travel_ws.write(row,4,seat["pos"][1].gpsTime.strftime("%Y-%m-%d %H:%M:%S"),style)
                    
                    style.num_format_str='0.00'
                    travel_ws.write(row,9,seat["gmileage_sites_percent"],style)
                    travel_ws.write(row,5,seat['duration_gmileage'],style)
                    style.num_format_str='0'
                    travel_ws.write(row,6,seat['price'],style)
                    travel_ws.write(row,7,seat["dithering_num"],style)
                    travel_ws.write(row,8,seat["dither_km"],style)
                    style.num_format_str='general'
                    travel_ws.write(row,10,seat["seated_vote"],style)
                    if seat["seated_vote"]==u"有效" :
                        customer+=1
                    row += 1
                    fee +=seat['price']
        #pattern.set_pattern_back_colour("aqua") #详细内容颜色
        style.num_format_str='general'
        travel_ws.write(row,1,u'小计',style)
        style.num_format_str='0'
        travel_ws.write(row+1,2,customer,style)
        travel_ws.write(row+1,3,fee,style)
        #pattern.set_pattern_back_colour("white") #详细内容颜色
        sum_ws.write(sh_no,2,customer,style)
        sum_ws.write(sh_no,3,fee,style)
        total_customer += customer
        total_fee += fee
    #pattern.set_pattern_back_colour("aqua") #详细内容颜色
    style.num_format_str='0'
    sum_ws.write(sh_no+1,3,total_fee,style)
    sum_ws.write(sh_no+1,2,total_customer,style)
    
    printLinePrice(sum_ws,0,8,busline_id,style)
    wb.save(xls_file)
    #transfer2ftp(ftp_addr,xls_file,level)
    
def printLinePrice(ws,start_row,start_col,busline_id,style):
    _sites =icfg.db.query("""SELECT * FROM  LineSites,Sites
                              WHERE BusLine_id        ={0} AND
                                    LineSites.site_id =Sites.id AND
                                    Sites.setting_type="manual"
                              ORDER BY LineSites.seq""".format(busline_id))
    sites  = []
    prices = getTotalLinePrice(busline_id)
    
    borders1 = Borders()
    borders1.left   = 1  
    borders1.right  = 1  
    borders1.top    = 1  
    borders1.bottom = 1 
    
    borders2 = Borders()
    borders2.left   = 0  
    borders2.right  = 0  
    borders2.top    = 0  
    borders2.bottom = 0 
    
    ws.write(start_row,start_col,u"价格表",style)
    #ws = wb.add_sheet(u"价格表")
    #style.pattern.set_pattern_back_colour("gray")
    #prices = getTotalLinePrice(busline_id)
    row=start_row+1
    col=start_col
    for site in _sites:                   
        sites.append(site)
        col += 1 
        ws.write(row,col,site.name,style)
    for site in sites:
        row += 1
        #style.pattern.set_pattern_back_colour("gray")
        style.borders = borders1
        ws.write(row,start_col,site.name,style)
        col = start_col
        for site1 in sites:
            col += 1
            if (col-start_col)==(row-start_row-1):
                style.borders = borders1
                price ="-"
            else:
                style.borders = borders2
                price         = prices[site.id][site1.id]
            #price =(prices[site.id][site1.id] if prices[site.id].has_key(site.id) else 0)
            
            ws.write(row,col,price,style)
    return
 
#获取线路上所有站点信息
def getBuslineSites(busline_id):
    _sites = icfg.db.query("""SELECT *,Sites.id AS site_id FROM LineSites,Sites
                                           WHERE LineSites.busline_id ={0} AND
                                                 LineSites.site_id = Sites.id AND
                                                 Sites.setting_type='manual'
                                           ORDER BY seq""".format(busline_id))
    sites = []
    for site in _sites:
        sites.append(site)
    return sites
 
def getTotalLinePrice(busline_id):
    result={}
    sites = getBuslineSites(busline_id)
    
    _prices = icfg.db.query("""SELECT * FROM LinePrice WHERE BusLine_id={0}""".format(busline_id))
    for linePrice in _prices:
        if result.has_key(linePrice.from_site_id)==False:
            result[linePrice.from_site_id] ={}
        result[linePrice.from_site_id][linePrice.to_site_id]=linePrice.price
    for site1 in sites:
        for site2 in sites:
            if result.has_key(site1.id)==False:
                result[site1.id]={}
            if result[site1.id].has_key(site2.id)==False:
                result[site1.id][site2.id]=0
    return result    
    
def transfer2ftp(ftp_addr,csv_file,level): 
    if ftp_addr!=None:
        xfer = ftp.Xfer()  
        xfer.setFtpParams(ftp_addr["ip"], ftp_addr["user"], ftp_addr["pwd"])  
        xfer.uploadFile2(csv_file,level)
        print("ftp...done")
    return
    
#依据imei获取BusLine   
def getBusline(imei):
    #获取该车所属车队
    _ret = icfg.db.query("""SELECT * FROM GroupHasDevice WHERE imei='{0}'""".format(imei))
    busgroup_id = _ret[0].devicegroup_id
    
    #依据车队查找对应的线路
    _ret = icfg.db.query("""SELECT * FROM BusLine WHERE busgroupid={0}""".format(busgroup_id))
    busline = _ret[0]  
    return busline
    
def getBusTravel(bustravel):
    if isinstance(bustravel,long) or isinstance(bustravel,int):
        _ret = icfg.db.query("SELECT * FROM BusTravel WHERE id={0}".format(bustravel))
        bustravel = _ret[0]
        
    pos =[]
    site=[]
    _dirs = ["from","to"]
    for i in [0,1]:
        ret = icfg.db.query("""SELECT * FROM SiteSeatStatus,Sites 
                               WHERE SiteSeatStatus.manual_site_id=Sites.id AND
                                     SiteSeatStatus.id = {0}""".format(bustravel[_dirs[i]+"_site_id"]))
        site.append(ret[0])
        ret = icfg.db.query("""SELECT * FROM HistoryTrack 
                               WHERE id={0} """.format(site[i][_dirs[i^1]+"_historytrack_id"]))
        pos.append(ret[0])
    bustravel["pos"] =pos
    bustravel["site"]=site
    ret = icfg.db.query("""SELECT * FROM BusLine 
                               WHERE id= {0}""".format(bustravel.busline_id))
    bustravel["busline"]=ret[0]
    return bustravel
   
def getSeatStatusDithering(seat):
    site = []
    pos  = []

    for _dir in ["from","to"]:
        ret = icfg.db.query("""SELECT * FROM TravelSites,Sites 
                               WHERE TravelSites.manual_site_id=Sites.id AND
                                     TravelSites.id= {0}""".format(seat[_dir+"_travel_site_id"]))
        site.append(ret[0])
        ret = icfg.db.query("""SELECT * FROM HistoryTrack 
                               WHERE id={0} """.format(seat[_dir+"_historytrack_id"]))
        pos.append(ret[0])
    seat["site"]=site
    seat["pos"] =pos
    return seat
    
#获取线路上所有站点信息
def getBuslineSites(busline_id):
    _sites = icfg.db.query("""SELECT *,Sites.id AS site_id FROM LineSites,Sites
                                           WHERE LineSites.busline_id ={0} AND
                                                 LineSites.site_id = Sites.id AND
                                                 Sites.setting_type='manual'
                                           ORDER BY seq""".format(busline_id))
    sites = []
    for site in _sites:
        sites.append(site)
    return sites
    
    