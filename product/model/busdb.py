# -*- coding: utf-8 -*-
import web,csv
import datetime,time
import product.iconfig as icfg
import json
import utility as uTools
import ftp
import copy
from pyExcelerator import *

#座位状态定义
_seatStatus={3:"超时",2:"未知",1:"空座",0:"有人"}
end_distance_diff  = 0.1 #终点站误差范围
_seat_pkg_len      = 60

def getAllPlates():
    names = [{'number':'------------------------------', 'imei':''}]
    results = icfg.db.query("""SELECT Device.name,Device.imei FROM Device,DeviceGroup,GroupHasDevice
                                           WHERE Device.imei = GroupHasDevice.imei AND
                                                 GroupHasDevice.devicegroup_id = DeviceGroup.id
                                                 
    """)
    imeis = []
    for result in results:
        if result.name != "" and (result.imei not in imeis):
            names.append({"number":"%s (%s)"%(result.name, result.imei), "imei":result.imei})
            imeis.append(result.imei)
            
    return json.dumps(names)      

def getSeatMergeStrategys():
    strategys = [{"原始数据":"orign"},
                 {"时间碎片合并":"merge_chip"},
                 {"600米碎片合并":"merge_dist_600"},
                 {"800米碎片合并":"merge_dist_800"}]
    return json.dumps(strategys)
    
def getSeatsByImei(imei,fromTime,toTime,strategy="orign"):
        
    busline = getBusline(imei)
    #获取座位状态信息
    inSeats = getOrignSeatsStat(imei,fromTime,toTime)

    #策略合并
    inSeats1 = mergeDataByStrage(strategy,inSeats)
    #转换为数组模式
    seats = seatFormat2Array(inSeats1[0])
    
    #当策略不是 orign，统一进行格式化
    if strategy!="orign":
       seats = formatLineSites(busline,seats)
    #删除冗余的字段
    seats = delRedundancyFields(seats)
    return seats
    
def getSeatsByImei4BKTask(imei,fromTime,toTime,csv_file,ftp_addr=None,strategy=["orign","merge_dist_600","merge_service"]):
     
    sensor2seat = seat_template(imei)
    
    busline = getBusline(imei)
    #获取座位状态信息
    ret = getOrignSeatsStat3(imei,fromTime,toTime)
    if ret=={}:
        return
    inSeats,run_endsite_seq  = ret
    #策略合并
    listSeats = mergeDataByStrage(busline.id,strategy,inSeats,run_endsite_seq)
    
    #打印原始数据
    printStateFlow(imei,sensor2seat,fromTime,toTime,csv_file,ftp_addr)
    
    no = 0
    for seats in listSeats:
        #转换为数组模式
        seats1 = seatFormat2Array(seats)
        
        #对换座的情况进行合并
        #seats2 = mergeMoreSeats(busline,seats1,run_endsite_seq)
        
        seats3 = formatLineSites(busline,seats1,run_endsite_seq)
        
        #删除冗余的字段
        _seats = delRedundancyFields2(seats3,sensor2seat)
        writeSeats2cvs(_seats,csv_file+"_" +strategy[no]+".csv",4,ftp_addr)
        no+=1
    writeSeats2xls(_seats,busline.id,sensor2seat,csv_file+".xls",4,ftp_addr)
    return

#为每一个座位加入起始站点信息
def addRunEndSite2Seat(busline_id,inSeats,run_endsite_seq):
    for key in inSeats:
        for i in range(len(inSeats[key])):
            seat = inSeats[key][i]
            seat["endsite"]=getRunDirection(busline_id,seat,run_endsite_seq)
    return inSeats
            
def seat_template1(imei):
    #获取设备信息
    _ret = icfg.db.query("""SELECT * FROM Device WHERE imei='{0}'""".format(imei))
    dev = _ret[0]
    #{"midbus":33,"bed":54,"seat53":60,"seat39":41}
    inTemp = {}
    seats = dev.seat_template.split(";")
    for seat in seats:
        inSeat = seat.split(",")
        if len(inSeat) >1:
            sensor=inSeat[0]
            name = inSeat[1]
            if sensor=="":
                continue
        else:
            continue
        inTemp[sensor]=name
    return inTemp   

def seat_template(imei):
    #获取设备信息
    _ret = icfg.db.query("""SELECT * FROM Device WHERE imei='{0}'""".format(imei))
    dev = _ret[0]
    #{"midbus":33,"bed":54,"seat53":60,"seat39":41}
    inTemp = {}
    seats = dev.seat_template.split(";")
    for i in range(len(seats)):
        inSeat = seats[i].split(",")
        if len(inSeat) >1:
            sensor=inSeat[0]
            name = inSeat[1]
            if sensor=="":
                continue
        else:
            continue
        inTemp[str(i)]=name
    return inTemp    
    
def printStateFlow(imei,sensor2seat,fromTime,toTime,csv_file,ftp_addr):
    results = icfg.db.query("""SELECT * FROM HistoryTrack 
                                   WHERE imei='{0}' AND gpsTime >='{1}' AND gpsTime<='{2}' AND gmileage>0
                                   ORDER BY gpsTime
                                   """.format(imei,fromTime,toTime))
    inSeats = {} #内部暂时存储
    if len(results) == 0:
        return
    _csv_file =csv_file+"_flow.csv"
    objCsvfile = file(_csv_file, 'wb')
    writer = csv.writer(objCsvfile)
    
    keys=["座位号","蓝牙号","在位情况","地址","时间","速度","里程刻度"]
    writer.writerow(keys)
    for result in results:
        seatStatus = result.seatStatus
        if seatStatus == "":
            continue

        jsonSeat = json.loads(seatStatus)
        for seat in jsonSeat:
            val = []
            seatNo = (sensor2seat[seat]  if sensor2seat.has_key(seat) else "未编号")
            val.append(seatNo)
            val.append(seat)
            val.append(get_seatStatus(jsonSeat[seat]["sit"]))
            val.append(result.addr)
            val.append(result.gpsTime.strftime("%Y-%m-%d %H:%M:%S"))
            val.append(result.speed)
            val.append(result.gmileage)
            writer.writerow(val)
    objCsvfile.close()
    transfer2ftp(ftp_addr,_csv_file,4)            

def get_seatStatus(seat_sit):
    status = u"未知"
    if _seatStatus.has_key(seat_sit):
        status = _seatStatus[seat_sit]
    else:
        status = seat_sit
    return status
    
def writeSeats2cvs(seats,csv_file,level,ftp_addr=None):
    if len(seats)==0:
        return
    print("write2cvs...start")
    #删除已有文件
    csvfile = file(csv_file, 'wb')
    writer = csv.writer(csvfile)
    #keys = seats[0].keys()
    keys = ["班车线路","座位号","蓝牙号","在位情况","开始地址","开始站点","开始时间","开始速度","截止地址","截止站点","截止时间","截止速度","持续里程(公里)","价格","持续时间(分钟)","开始日期","截止日期","行程","运行时间","运行站点","全程里程(KM)","grain_num"]
    writer.writerow(keys)
    for seat in seats:
        #unicode(line, "cp866").encode("utf-8")
        val = []
        for key in keys:
            _val = (seat[key] if seat.has_key(key) else "")
            val.append(_val) 
        writer.writerow(val)
    csvfile.close()
    print("write2cvs...done")
    transfer2ftp(ftp_addr,csv_file,level)

def writeSeats2xls(seats,busline_id,sensor2seat,xls_file,level,ftp_addr):
    sites = getBuslineSites(busline_id)
    if len(seats)==0:
        return
    print("write2xls...start:{0}".format(xls_file))
    
    #删除已有文件
    wb = Workbook()
    #keys = ["班车线路","座位号","蓝牙号","在位情况","开始地址","开始站点","开始时间","开始速度","截止地址","截止站点","截止时间","截止速度","持续里程(公里)","价格","持续时间(分钟)","开始日期","截止日期","行程","运行时间","运行站点","全程里程(KM)"]
    sheets=[]
    #sheets=[{"name":"玉林-容县",
    #         "time":"8:30:33-10:30:33",
    #         "seats":{1:[{"开始站点":"玉林","开始时间":"12:33:00","截止站点":"容县","截止时间":"12:32:31"},
    #                     {"开始站点":"玉林","开始时间":"12:33:00","截止站点":"容县","截止时间":"12:32:31"}],
    #                  2:[{"开始站点":"玉林","开始时间":"12:33:00","截止站点":"容县","截止时间":"12:32:31"},
    #                     {"开始站点":"玉林","开始时间":"12:33:00","截止站点":"容县","截止时间":"12:32:31"}]
    #                  }
    #获取座位编号信息
    #print(sensor2seat)
    _seat_num = sensor2seat.values()
    
    try:#判定是否为数字型的
        int(_seat_num[0])
        _seat_type = "num"  #座位是数字型编号
        seat_num =sorted(_seat_num, key=lambda d: int(d))
    except:#按字符形式排序
        seat_num =sorted(_seat_num, key=lambda d: d)
        _seat_type = "str"  #座位是字符型编号
    for seat in seats:
        if seat["在位情况"]!="有人":
            continue
        #查找分组
        worksheet=None
        for sh in sheets:
            if (sh["name"]==seat["运行站点"] and sh["time"]==seat["运行时间"]):
                worksheet=sh
                
        if worksheet==None:
            worksheet={"name":seat["运行站点"],"time":seat["运行时间"],"seats":{}}
            sheets.append(worksheet)
        if worksheet["seats"].has_key(seat["座位号"])==False:
            worksheet["seats"][seat["座位号"]]=[]
        worksheet["seats"][seat["座位号"]].append(seat)
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
    #按发车时间排序
    _sheets =sorted(sheets, key=lambda d:d["time"])
    ws1 = wb.add_sheet(u"汇总报告")
    #pattern.set_pattern_back_colour("gray") #标题背景
    ws1.write(0,0,u'行程',style)    
    ws1.write(0,1,u'运行时间',style) 
    ws1.write(0,2,u'人数/票数',style)
    ws1.write(0,3,u'金额',style)
    
    sh_no     = 0
    total_fee = 0
    total_customer = 0 
    for sh in _sheets:
        sh_no += 1
        sheet_name = u"{0}-{1}".format(sh["name"],sh_no)
        link_url = u"#'{0}'!A1".format(sheet_name)
        ws = wb.add_sheet(sheet_name) 
        ws1.write(sh_no,0,sh["name"],style)
        ws1.set_link(sh_no,0,link_url,u"点击查看详情")
        ws1.write(sh_no,1,unicode(sh["time"], "utf-8"),style)
        fee      = 0
        customer = 0
        #pattern.set_pattern_back_colour("gray") #标题背景
        ws.write(0,0,u'座位号',style)
        #if len(sites)>3:
        ws.write(0,1,u'上车站点',style)
        ws.write(0,3,u'下车站点',style)
        #else:
        #    ws.write(0,1,u'上车地名',style)
        #    ws.write(0,3,u'下车地名',style)
        ws.write(0,2,u'上车时间',style)
        ws.write(0,4,u'下车时间',style)
        ws.write(0,5,u'持续里程(KM)',style)
        ws.write(0,6,u'金额',style)
        ws.write(0,7,u"抖动次数",style)
        ws.write(0,8,u"在位里程/抖动次数",style) 
        ws.write(0,9,u"在位里程/站点距离",style)
        ws.write(0,10,u"有效结论",style)
        ws.write(0,11,u"备注",style)
        #ws.write(0,7,u"在位里程",style)
        #ws.write(0,8,u"空座里程",style)
        #ws.write(0,11,u"<1KM次数",style) 
        #ws.write(0,12,u"1-2KM次数",style) 
        #ws.write(0,13,u"2-5KM次数",style)
        #ws.write(0,14,u"5-15KM次数",style)                        
        #ws.write(0,15,u"15-50KM次数",style)        
        #ws.write(0,16,u">50KM次数",style) 
        #ws.write(0,17,u"<1KM总里程",style)        
        #ws.write(0,18,u"1-2KM总里程",style)
        #ws.write(0,19,u"2-5KM总里程",style)                         
        #ws.write(0,20,u"5-15KM总里程",style)        
        #ws.write(0,21,u"15-50KM总里程",style)        
        #ws.write(0,22,u">50KM总里程",style)  
        #ws.write(0,23,u"<1KM次数比重",style)
        #ws.write(0,24,u"1-2KM次数比重",style) 
        #ws.write(0,25,u"2-5KM次数比重",style)                         
        #ws.write(0,26,u"5-15KM次数比重",style)            
        #ws.write(0,27,u"15-50KM次数比重",style)          
        #ws.write(0,28,u">50KM次数比重",style) 
        #ws.write(0,29,u"<1KM里程比重",style)
        #ws.write(0,30,u"1-2KM里程比重",style)                         
        #ws.write(0,31,u"2-5KM里程比重",style)          
        #ws.write(0,32,u"5-15KM里程比重",style)                        
        #ws.write(0,33,u"15-50KM里程比重",style)            
        #ws.write(0,34,u">50KM里程比重",style)            
        
        seats_keys = sh["seats"].keys()
        #_seats =sorted(sh["seats"].iteritems(), key=lambda d: (int(d[0]) if str(d[0])==d[0] else d[0]))
        row = 0
        for ist_num in seat_num:
            _ist_num = (str(ist_num) if _seat_type=="num" else ist_num)
            if sh["seats"].has_key(_ist_num)==False:
                row+=1
                ws.write(row,0,_ist_num,style)
                for i in range(10):
                    ws.write(row,i+1,"",style)
            else:
                _st =sorted(sh["seats"][_ist_num], key=lambda d:d["开始时间"])
                start_row = row+1
                start_row_valid=False #有有效输出，才能其作用
                for ist in _st:
                    if float(ist["持续里程(公里)"])>1:
                        start_row_valid=True
                        row+=1
                        #pattern.set_pattern_back_colour("white") #标题背景
                        style.num_format_str="general"
                        if len(sites)>3:
                            ws.write(row,1,ist['开始站点'],style)
                            ws.write(row,3,ist['截止站点'],style)
                        else:
                            ws.write(row,1,ist['开始地名'],style)
                            ws.write(row,3,ist['截止地名'],style)
                        
                        ws.write(row,2,ist['开始时间'],style)
                        
                        ws.write(row,4,ist['截止时间'],style)
                        style.num_format_str='0.00'
                        ws.write(row,9,ist["在位里程/站点距离"],style)
                        ws.write(row,5,ist['持续里程(公里)'],style)
                        #pattern.set_pattern_back_colour("aqua") #详细内容颜色
                        style.num_format_str='0'
                        ws.write(row,6,ist['价格'],style)
                        ws.write(row,7,ist["抖动次数"],style)
                        ws.write(row,8,ist["在位里程/抖动次数"],style)
                        
                        ws.write(row,10,ist["valid"],style)
                        if ist["valid"]=="有效" :
                            customer+=1
                        if ist.has_key("remark"):
                            ws.write(row,11,ist["remark"],style)
                        #ws.write(row,9,ist["在位里程"],style)
                        #ws.write(row,10,ist["空座里程"],style)
                        #ws.write(row,11,ist["<1KM次数"],style) 
                        #ws.write(row,12,ist["1-2KM次数"],style) 
                        #ws.write(row,13,ist["2-5KM次数"],style)
                        #ws.write(row,14,ist["5-15KM次数"],style)                        
                        #ws.write(row,15,ist["15-50KM次数"],style)        
                        #ws.write(row,16,ist[">50KM次数"],style) 
                        #ws.write(row,17,ist["<1KM总里程"],style)        
                        #ws.write(row,18,ist["1-2KM总里程"],style)
                        #ws.write(row,19,ist["2-5KM总里程"],style)                         
                        #ws.write(row,20,ist["5-15KM总里程"],style)        
                        #ws.write(row,21,ist["15-50KM总里程"],style)        
                        #ws.write(row,22,ist[">50KM总里程"],style) 
                        #style.num_format_str='0.00%'  
                        #ws.write(row,23,ist["<1KM次数比重"],style)
                        #ws.write(row,24,ist["1-2KM次数比重"],style) 
                        #ws.write(row,25,ist["2-5KM次数比重"],style)                         
                        #ws.write(row,26,ist["5-15KM次数比重"],style)            
                        #ws.write(row,27,ist["15-50KM次数比重"],style)          
                        #ws.write(row,28,ist[">50KM次数比重"],style) 
                        #ws.write(row,29,ist["<1KM里程比重"],style)
                        #ws.write(row,30,ist["1-2KM里程比重"],style)                         
                        #ws.write(row,31,ist["2-5KM里程比重"],style)          
                        #ws.write(row,32,ist["5-15KM里程比重"],style)                        
                        #ws.write(row,33,ist["15-50KM里程比重"],style)            
                        #ws.write(row,34,ist[">50KM里程比重"],style) 
                        
                        fee+=ist['价格']
                style.num_format_str=('0' if _seat_type=="num" else 'general')
                if start_row_valid==True:
                    ws.write_merge(start_row,row,0,0,ist_num,style)    
                else:
                    row+=1
                    ws.write(row,0,ist_num,style)
        #pattern.set_pattern_back_colour("aqua") #详细内容颜色
        style.num_format_str='general'
        ws.write(row+1,1,u'小计',style)
        style.num_format_str='0'
        ws.write(row+1,3,customer,style)
        ws.write(row+1,6,fee,style)
        #pattern.set_pattern_back_colour("white") #详细内容颜色
        ws1.write(sh_no,2,customer,style)
        ws1.write(sh_no,3,fee,style)
        total_customer += customer
        total_fee += fee
    #pattern.set_pattern_back_colour("aqua") #详细内容颜色
    style.num_format_str='0'
    ws1.write(sh_no+1,3,total_fee,style)
    ws1.write(sh_no+1,2,total_customer,style)
    
    printLinePrice(ws1,0,8,busline_id,style)
    wb.save(xls_file)
    transfer2ftp(ftp_addr,xls_file,level)
    
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
                price         = getLinePrice(busline_id,site.id,site1.id)
            #price =(prices[site.id][site1.id] if prices[site.id].has_key(site.id) else 0)
            
            ws.write(row,col,price,style)
    return
        
def getTotalLinePrice(busline_id):
    result={}
    _prices = icfg.db.query("""SELECT * FROM LinePrice WHERE BusLine_id={0}""".format(busline_id))
    for linePrice in _prices:
        if result.has_key(linePrice.from_site_id)==False:
            result[linePrice.from_site_id] ={}
        result[linePrice.from_site_id][linePrice.to_site_id]=linePrice.price
    return result    
    
def transfer2ftp(ftp_addr,csv_file,level): 
    if ftp_addr!=None:
        xfer = ftp.Xfer()  
        xfer.setFtpParams(ftp_addr["ip"], ftp_addr["user"], ftp_addr["pwd"])  
        xfer.uploadFile2(csv_file,level)
        print("ftp...done")
    return
    
def seatFormat2Array(inSeats): 
    seats = []
    #生成一个数据组
    for key in inSeats :
        seats +=  inSeats[key]
    return seats

def delRedundancyFields2(seats,sensor2seat): 
    #print seats
    for seat in seats:
        if isinstance(seat["status"],dict):
            seat["在位情况"] = seat["status"]["sit"]
        #将changedTime转化为字符串格式
        seat["座位号"]  = (sensor2seat[seat["num"]] if sensor2seat.has_key(seat["num"]) else "未编号")
        seat["蓝牙号"]  = seat["num"]
        
        seat["持续时间(分钟)"] = "%0.2f"%((seat["to_pos"].gpsTime-seat["from_pos"].gpsTime).total_seconds()/60.0)
        seat["持续里程(公里)"] = "%0.2f"%float(seat["to_pos"].gmileage-seat["from_pos"].gmileage)
        #if seat.has_key("flag"):
        #    seat.pop("flag")   #去掉临时字段
        #if seat.has_key("latLng"):
        #    seat.pop("latLng") #去掉临时字段
        #if seat.has_key("from_pos"):
        #    seat.pop("from_pos") #去掉临时字段
        #if seat.has_key("to_pos"):
        #    seat.pop("to_pos") #去掉临时字段
        #if seat.has_key("end_site"):
        #    seat.pop("end_site") #去掉临时字段
    return seats
    
def delRedundancyFields(seats): 
    #print seats
    for seat in seats:
        seat["status"] = str(seat["status"]["sit"])
        #将changedTime转化为字符串格式
        if isinstance(seat["changedTime"],datetime.datetime):
            seat["changedTime"] = seat["changedTime"].strftime("%Y-%m-%d %H:%M:%S")
        seat["持续时间(分钟)"] = "%0.2f"%seat["stayTime"]
        seat["持续里程(公里)"] = "%0.2f"%seat["mileage"]
        seat.pop("speed")
        seat.pop("flag") #去掉临时字段
        seat.pop("latLng") #去掉临时字段
        seat.pop("mileage") #去掉临时字段
        seat.pop("gmileage") #去掉临时字段
        seat.pop("from_pos") #去掉临时字段
        seat.pop("to_pos") #去掉临时字段
        seat.pop("end_site") #去掉临时字段
    return json.dumps(seats)


#2015-12-30之前的算法    
def getOrignSeatsStat2(imei,fromTime,toTime):
    results = icfg.db.query("""SELECT * FROM HistoryTrack 
                                   WHERE imei='{0}' AND gpsTime >='{1}' AND gpsTime<='{2}' AND gmileage>0
                                   ORDER BY gpsTime
                                   """.format(imei,fromTime,toTime))
    
    inSeats = {} #内部暂时存储
    if len(results) == 0:
        return inSeats
    busline = getBusline(imei)

    run_endsite_seq=[]
    #判定趟数
    for result in results:
        get_run_endsite_seq(busline.id,run_endsite_seq,result)
        seatStatus = result.seatStatus
        if seatStatus == "":
            continue
        
        jsonSeat  = json.loads(seatStatus)
        for seat in jsonSeat:
            #没有座位信息，首先进行初始化
            if inSeats.has_key(seat)==False:
                inSeats[seat] = []
                inSeats[seat].append(initSeat2(seat,result))
            else:
                #将数字符号修改为有意义的中文名字
                _seat_status =get_seatStatus(jsonSeat[seat]["sit"])
                
                status = {"sit":_seat_status}
                #状态发生改变，添加新的状态节点
                if inSeats[seat][-1]["status"]["sit"] != _seat_status: 
                    inSeats[seat].append(dict(
                        num         = seat,
                        status      = status,
                        grain       =[],#记录该区段分离数据的粒度
                        from_pos    =copy.deepcopy(result),
                        to_pos      =copy.deepcopy(result),
                    ))
                    inSeats[seat][-1]["grain"].append(inSeats[seat][-1])
                else:
                    if _seat_status=="空座":
                        inSeats[seat][-1]["to_pos"]=copy.deepcopy(result)
                    else:
                        is_end_site,offset = isEndSite2(busline.id,result)
                        if is_end_site and len(inSeats[seat])>1:
                            if offset<2:#探测距离
                                if inSeats[seat][-1].has_key("end_offset")==False:#还没有进入了终点站判定模式
                                    inSeats[seat].append(dict(
                                        num         = seat,
                                        status      = status,
                                        grain       =[],
                                        end_offset  = offset,#距离始发站的距离
                                        check_times = 0,#避免车辆曲折运营，导致逼近终点站出现反复的情况
                                        find_end    ="continue",#标志正在探索终点站位置
                                        from_pos    =copy.deepcopy(result),
                                        to_pos      =copy.deepcopy(result),
                                    )) 
                                    inSeats[seat][-1]["grain"].append(inSeats[seat][-1])
                                else:#已经进入终点站判定模式
                                    if inSeats[seat][-1].has_key("find_end") and inSeats[seat][-1]["find_end"]=="continue":#还在探索中
                                        if offset<=inSeats[seat][-1]["end_offset"]:#逼近终点站
                                            inSeats[seat][-1]["check_times"] =0  #逼近清零
                                            inSeats[seat][-1]["end_offset"]=offset
                                            inSeats[seat][-1]["from_pos"]  =copy.deepcopy(result)
                                            inSeats[seat][-1]["to_pos"]    =copy.deepcopy(result)
                                            inSeats[seat][-2]["to_pos"]    =copy.deepcopy(result)
                                        else:
                                            inSeats[seat][-1]["check_times"] -=1  #远离1次，当超过-3时，则认为大巴已经在离开
                                            if inSeats[seat][-1]["check_times"]<-3:#远离次数超过极限，则认为大巴已经离开终点站
                                                inSeats[seat][-1]["find_end"]=="break" #终点站已过
                                            inSeats[seat][-1]["to_pos"]=copy.deepcopy(result)
                                    else:#终点站已过,启动终点站远离模式
                                        inSeats[seat][-1]["to_pos"]=copy.deepcopy(result)                            
                            else:
                                inSeats[seat][-1]["to_pos"]=copy.deepcopy(result)
                        else:#刷新截止节点
                            inSeats[seat][-1]["to_pos"]=copy.deepcopy(result)    
    
    #将起始站点信息加入到每一个座位
    inSeats=addRunEndSite2Seat(busline.id,inSeats,run_endsite_seq)
    return [inSeats,run_endsite_seq]

#2016-01-14的算法    
def getOrignSeatsStat3(imei,fromTime,toTime):
    results = icfg.db.query("""SELECT * FROM HistoryTrack 
                                   WHERE imei='{0}' AND gpsTime >='{1}' AND gpsTime<='{2}' AND gmileage>0
                                   ORDER BY gpsTime
                                   """.format(imei,fromTime,toTime))
    
    inSeats = {} #内部暂时存储
    if len(results) == 0:
        return inSeats
    busline = getBusline(imei)

    run_endsite_seq=[]
    #判定趟数
    for result in results:
        get_run_endsite_seq(busline.id,run_endsite_seq,result)
        seatStatus = result.seatStatus
        if seatStatus == "":
            continue
        
        jsonSeat  = json.loads(seatStatus)
        for seat in jsonSeat:
            #没有座位信息，首先进行初始化
            if inSeats.has_key(seat)==False:
                inSeats[seat] = []
                inSeats[seat].append(initSeat2(seat,result))
            else:
                #将数字符号修改为有意义的中文名字
                _seat_status = get_seatStatus(jsonSeat[seat]["sit"])
                
                status = {"sit":_seat_status}
                #状态发生改变，添加新的状态节点
                if inSeats[seat][-1]["status"]["sit"] != _seat_status: 
                    inSeats[seat].append(dict(
                        num         = seat,
                        status      = status,
                        grain       =[],#记录该区段分离数据的粒度
                        from_pos    =copy.deepcopy(result),
                        to_pos      =copy.deepcopy(result),
                    ))
                    inSeats[seat][-1]["grain"].append(inSeats[seat][-1])
                else:
                    inSeats[seat][-1]["to_pos"]=copy.deepcopy(result)

    #对终点站有人座位进行分割处理
    inSeats1 = analyzeEndSite(inSeats,run_endsite_seq)
    #将起始站点信息加入到每一个座位
    inSeats2=addRunEndSite2Seat(busline.id,inSeats1,run_endsite_seq)
    return [inSeats2,run_endsite_seq]
    
#对终点站有人座位进行分割处理
def analyzeEndSite(inSeats,run_endsite_seq): 
    retInSeats={}
    for no in inSeats:
        if retInSeats.has_key(no)==False:
            retInSeats[no] =[]
        for seat in inSeats[no]:
            end_seat_procceed=False #标记是否完成始发站点分割
            for i in range(1,len(run_endsite_seq)):
                endsiteA = run_endsite_seq[i-1]
                endsiteB = run_endsite_seq[i]
                
                test_result = seat["from_pos"].gpsTime<endsiteA["end_site_t"].gpsTime and \
                              seat["to_pos"].gpsTime>endsiteA["end_site_t"].gpsTime
                #适用于所有状态
                print("""{4}-{0}:{1}<{2} and {3} > {2}""".format(test_result,
                        seat["from_pos"].gpsTime.strftime("%Y-%m-%d %H:%M:%S"), \
                        endsiteA["end_site_t"].gpsTime.strftime("%Y-%m-%d %H:%M:%S"),
                        seat["to_pos"].gpsTime.strftime("%Y-%m-%d %H:%M:%S"),
                        no
                ))
                if seat["from_pos"].gpsTime<endsiteA["end_site_t"].gpsTime and \
                   seat["to_pos"].gpsTime>endsiteA["end_site_t"].gpsTime:
                    end_seat_procceed =True
                    newNode =dict(
                        num         = no,
                        status      = seat["status"],
                        grain       =[],#记录该区段分离数据的粒度
                        from_pos    =copy.deepcopy(seat["from_pos"]),
                        to_pos      =copy.deepcopy(endsiteA["end_site_t"]),
                    )
                    newNode["grain"].append(newNode)
                    retInSeats[no].append(newNode)
                    
                    if seat["to_pos"].gpsTime>endsiteB["start_site_t"].gpsTime:
                        seat =dict(
                            num         = no,
                            status      = seat["status"],
                            grain       =[],#记录该区段分离数据的粒度
                            from_pos    =copy.deepcopy(endsiteB["start_site_t"]),
                            to_pos      =copy.deepcopy(seat["to_pos"]),
                        )
                    else:#座位状态已经分割完成
                        break
                
            if end_seat_procceed==False:
                retInSeats[no].append(seat)
    return retInSeats
                
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
    
#判定终点站模式    
def get_run_endsite_seq(busline_id,run_endsite_seq,pos):
    from_site,to_site=getBuslineEndSite(busline_id)
    #sites = getBuslineSites(busline_id)
    #from_site=sites[0]
    #to_site  =sites[-1]
    distance_of_ends =uTools.getDistance(from_site.gpsLat,from_site.gpsLng,to_site.gpsLat,to_site.gpsLng)
    if len(run_endsite_seq)==0:
        run_endsite_seq.append(dict(
            from_site     =from_site,
            to_site       =to_site,
            distance_of_ends = distance_of_ends,
            end_site_t    = None,
            end_accuracy  = 0.05,
            end_speed_trend =100,    #从车的速度趋势判定，速度越来越慢
            end_site_name  ="",#终点名称
            find_end      ="wait",#是否启动最终位置探索 ：waiting 等待 continue 进行中 complete 结束
            start_site_t  = None,
            start_accuracy= 0.05,
            start_speed_trend =0,  #从车的速度趋势判定，速度越来越快
            start_site_name   ="",  #终点名称
            find_start        ="finish",#是否启动最终位置探索 ：waiting 等待 continue 进行中 complete 结束
            left_endsite      =True,
            pass_sites        =[],#途径的中间节点
        ))
    #起始站点已经判定的终结点，离开起始点已经有1km了    
    if run_endsite_seq[-1]["find_start"]  =="finish" and \
       run_endsite_seq[-1]["find_end"]    =="wait" and \
       run_endsite_seq[-1]["start_site_t"]!=None:#探测结束位置
        #offset = (pos.gmileage-run_endsite_seq[-1]["start_site_t"].gmileage)
        #规避gmileage计算出现异常的情况
        offset = uTools.getDistance(pos.gpsLat,pos.gpsLng,run_endsite_seq[-1]["start_site_t"].gpsLat,run_endsite_seq[-1]["start_site_t"].gpsLng)
        offset_percent = offset/run_endsite_seq[-1]["distance_of_ends"]
        if offset_percent > 0.5:#至少要总行程1半以上，才可以认定已经离开出发站点
            run_endsite_seq[-1]["left_endsite"] = True
        #中点站判定
    
    for end_site in [from_site,to_site]:
        offset = uTools.getDistance(pos.gpsLat,pos.gpsLng,end_site.gpsLat,end_site.gpsLng)
        offset_percent = offset/run_endsite_seq[-1]["distance_of_ends"]
        if offset_percent < 0.1:
        #是否进入到了判定范围内，500米 #进入终点站范围，意味着上一趟的结束，下一趟的开始
            if run_endsite_seq[-1]["find_start"]=="finish"  and run_endsite_seq[-1]["left_endsite"]==True:#探测结束位置
                if run_endsite_seq[-1]["find_end"]=="wait": 
                    #进入新的结束站点探索状态
                    run_endsite_seq[-1]["find_end"]="search"
                if run_endsite_seq[-1]["find_end"]=="search":#截止点探索中
                    if offset_percent<run_endsite_seq[-1]["end_accuracy"]:
                        run_endsite_seq[-1]["end_site_t"]     =copy.deepcopy(pos)
                        run_endsite_seq[-1]["end_accuracy"]   =offset_percent
                        run_endsite_seq[-1]["end_speed_trend"]=pos.speed
                    
                    #两个站点间的距离，
                    if run_endsite_seq[-1]["end_site_t"]!=None and run_endsite_seq[-1]["start_site_t"]!=None:
                        #end_distance = run_endsite_seq[-1]["end_site_t"].gmileage-run_endsite_seq[-1]["start_site_t"].gmileage
                        #end_distance_percent = end_distance/run_endsite_seq[-1]["distance_of_ends"]
                        end_distance_percent = 1
                    else:
                        end_distance_percent = 0.5
                    
                    
                    print("{0}-{1}:{2}<10 and {3}<0.01 and {4}>0.4:{5}".format(pos.gpsTime.strftime("%H:%M:%S"),
                            (pos.speed<10 and offset_percent<0.01 and end_distance_percent>0.4),\
                             pos.speed,offset_percent,end_distance_percent,pos.addr))
                      
                    if pos.speed<10 and offset_percent<0.01 and end_distance_percent>0.4:#停止探索
                        near_name,far_name =getFromToSiteName(busline_id,pos)
                        run_endsite_seq[-1]["find_end"]="finish"
                        run_endsite_seq[-1]["end_site_name"]  =near_name
                        run_endsite_seq[-1]["start_site_name"]=far_name
                        run_endsite_seq.append(dict(
                            from_site       =from_site,
                            to_site         =to_site,
                            distance_of_ends = distance_of_ends,
                            start_site_t    = copy.deepcopy(pos),
                            start_accuracy  = offset_percent,
                            start_speed_trend =pos.speed,  #从车的速度趋势判定，速度越来越快
                            find_start      ="search",#是否启动最终位置探索 ：waiting 等待 continue 进行中 complete 结束
                            end_site_t      = None,                    
                            end_accuracy    = 0.05,            
                            find_end        ="wait",#是否启动最终位置探索 ：waiting 等待 continue 进行中 complete 结束
                            end_speed_trend =100,    #从车的速度趋势判定，速度越来越慢
                            left_endsite    =False,
                            start_site_name =near_name,
                            end_site_name   =far_name,
                        ))
                else:
                    pass
                    
            if run_endsite_seq[-1]["find_end"]=="wait"  and run_endsite_seq[-1]["left_endsite"]==False:#精度更高一点，进一步微调
                if run_endsite_seq[-1]["find_start"]=="search":#截止点探索中
                    print("{0}-{1}:{2}<0.01 and {3}>5 and {4}<{5}:{6}".format(pos.gpsTime.strftime("%H:%M:%S"),\
                            (offset_percent<0.01 and pos.speed>5 and run_endsite_seq[-1]["start_speed_trend"]<pos.speed),\
                            offset_percent,pos.speed, run_endsite_seq[-1]["start_speed_trend"],pos.speed,pos.addr))
                    
                    if offset_percent<0.01 and pos.speed>5 and run_endsite_seq[-1]["start_speed_trend"]<pos.speed:#停止探索
                        run_endsite_seq[-1]["find_start"]="finish"
                    else:   
                        if offset_percent<=run_endsite_seq[-1]["start_accuracy"] and pos.speed<5:
                            run_endsite_seq[-1]["start_site_t"]     =copy.deepcopy(pos)
                            run_endsite_seq[-1]["start_accuracy"]   =offset_percent
                            run_endsite_seq[-1]["start_speed_trend"]=pos.speed
                else:
                    pass
    return run_endsite_seq        

#根据末端站点的位置，判定行程方向，返回：[玉林,容县]    
def getFromToSiteName(busline_id,pos):
    #获取两端的节点
    from_site,to_site=getBuslineEndSite(busline_id)
    from_offset = uTools.getDistance(pos.gpsLat,pos.gpsLng,from_site.gpsLat,from_site.gpsLng)
    to_offset = uTools.getDistance(pos.gpsLat,pos.gpsLng,to_site.gpsLat,to_site.gpsLng)
    
    if from_offset<to_offset:
        ret =[from_site.name,to_site.name]
    else:
        ret =[to_site.name,from_site.name]
    return ret
    
    
def initSeat2(seat,pos):
    jsonSeat     = json.loads(pos.seatStatus)
    _seat_status =get_seatStatus(jsonSeat[seat]["sit"])

    status = {"sit":_seat_status}
    ret=dict(
        num         =seat,
        status      =status,
        grain       =[],
        from_pos    =copy.deepcopy(pos), 
        to_pos      =copy.deepcopy(pos),
    )
    ret["grain"].append(ret)
    return ret
    
#初始化座位2015-12-30之前   
def initSeat(seat,pos):
    nowTime  = pos.gpsTime
    jsonSeat     = json.loads(pos.seatStatus)
    _seat_status =get_seatStatus(jsonSeat[seat]["sit"])

    status = {"sit":_seat_status}
    ret=dict(
        num         = seat,
        status      = status,
        speed       = str(pos.speed),
        mileage     = 0,
        gmileage    = pos.gmileage,
        stayTime    = 0,
        address     = pos.addr,
        latLng      = [pos.gpsLat,pos.gpsLng],
        price       = "",
        busLine     = "",
        changedTime = nowTime,
        fromTime    = nowTime,
        fromAddr    = pos.addr,
        fromGmileage= pos.gmileage,
        flag        ="start",
        from_pos    =pos, 
        to_pos      =copy.deepcopy(pos),
    )
    return ret

#所有状态为 2 ，未初始化    
def is_init_data(inSeat):
    isInitData = True
    _seat1 = json.loads(inSeat)
    for seat in _seat1:
        if _seat1[seat]["sit"] != 2:
            isInitData = False
            break
    return isInitData    
    
#依据策略进行合并    
def mergeDataByStrage(busline_id,strategy,inSeats,run_endsite_seq):
    ret =[]
    if "orign" in strategy:
       ret.append(inSeats)
       #ret.append(mergeInseat(copy.deepcopy(inSeats)))
    inSeatsMerged = None   
    if "merge_chip" in strategy:
       merge_chip = seatBymergeByDistance(copy.deepcopy(inSeats),600)
       inSeatsMerged = copy.deepcopy(merge_chip)
       ret.append(merge_chip)
       #ret = seatBymergeByTime(inSeats)
    if "merge_dist_600" in strategy:
       inSeats600 = mergeByDistance2(copy.deepcopy(inSeats),run_endsite_seq,0.015)
       inSeatsMerged = copy.deepcopy(inSeats600)       
       ret.append(inSeats600)
    if "merge_dist_800" in strategy:
       inSeats800 = seatBymergeByDistance(copy.deepcopy(inSeats),800)
       inSeatsMerged = copy.deepcopy(inSeats800) 
       ret.append(inSeats800)
    #if "merge_exchange_site" in strategy and inSeatsMerged!=None:
    #    ret.append(merge_exchange_site(busline_id,inSeatsMerged,run_endsite_seq))
    if ("merge_service" in strategy) and inSeatsMerged!=None:
        ret.append(merge_service_site(busline_id,inSeatsMerged,run_endsite_seq))    
    return ret
#合并策略：前一个状态"有人",后一状态"空座",且速度>30公里/小时，则连城有人
#def mergeXseat(inSeats):
#    retInSeats = {}
#    for key in inSeats :
#        lenSeat = len(inSeats[key])
#        retInSeats[key]=[inSeats[key][0]]
#        for i in range(lenSeat-1):
#            if retInSeats[key][-1]["status"]["sit"]=="有人":
#                if inSeats[key][i]["status"]["sit"]=="空座" and inSeats[key][i]["to_pos"]["speed"]>30:
#                    retInSeats[key][-1]["to_pos"] = copy.deepcopy(inSeats[key][i]["to_pos"])
#                if retInSeats[key][-1].has_key("end_offset")==False and inSeats[key][i].has_key("end_offset"):
#    return inSeats

#针对两个站点的快线情况，对中间停车站点进行合并    
def merge_service_site(busline_id,inSeats,run_endsite_seq):
    sites = getBuslineSites(busline_id)
    distance_of_ends = run_endsite_seq[0]["distance_of_ends"]
    retInSeats = {}
    if len(sites)!=2:#只适用于两点快线班车
        return inSeats
   
    for key in inSeats:
        for i in range(len(inSeats[key])):
            seat = inSeats[key][i]
            if retInSeats.has_key(key)==False:
                retInSeats[key]=[]
                retInSeats[key].append(seat)
            else:
                lastSeat = retInSeats[key][-1]
                #与上一个座位的起始站相同
                if lastSeat["endsite"]!=seat["endsite"]:
                    retInSeats[key].append(seat)
                else:
                    if seat["status"]["sit"]==lastSeat["status"]["sit"]:#状态一致，直接合并
                        lastSeat["grain"] +=seat["grain"]
                        lastSeat["to_pos"] = seat["to_pos"]
                    else:
                        
                        gmileage_percent2 = (lastSeat["to_pos"].gmileage-lastSeat["from_pos"].gmileage)/distance_of_ends
                        if lastSeat["status"]["sit"]=="有人" and gmileage_percent2>0.03:#处理短暂空座的情况
                            seat_seconds = (seat["to_pos"].gpsTime  -seat["from_pos"].gpsTime).total_seconds()
                            seat_gmileage = seat["to_pos"].gmileage -seat["from_pos"].gmileage
                            seat_gmileage_percent = seat_gmileage/distance_of_ends
                            if (seat_seconds<900 and seat_gmileage<5 and seat["to_pos"].speed<15) or \
                               (seat_gmileage/lastSeat["endsite"]["total_km"]<0.2 and \
                                (lastSeat["endsite"]["total_seconds"]>0 and seat_seconds/lastSeat["endsite"]["total_seconds"]<0.2 or \
                                 lastSeat["endsite"]["total_seconds"]==0)) :
                                lastSeat["grain"] +=seat["grain"]
                                lastSeat["to_pos"] = seat["to_pos"]
                            else:
                                retInSeats[key].append(seat)
                        else:
                            retInSeats[key].append(seat)     
    return retInSeats

#对换座的情况进行合并 
def mergeMoreSeats(busline,seats,run_endsite_seq):
    sites =getBuslineSites(busline.id)
    if len(sites)>4:#只是针对长途车才进行合并
        return seats
    retInSeats=[]
    wait_seats = {}
    for seat in seats:
        if seat["status"]["sit"]!="有人":
            retInSeats.append(seat)
            continue
        seated_km_percent = (seat["to_pos"].gmileage - seat["from_pos"].gmileage)/seat["endsite"]["total_km"]
        print("seated_km_percent:{0}".format(seated_km_percent))
        if seated_km_percent > 0.6:
            retInSeats.append(seat)
        else:
            run_site_index = run_endsite_seq.index(seat["endsite"]["run_site"])
            if wait_seats.has_key(run_site_index)==False:
                wait_seats[run_site_index]=[]
            wait_seats[run_site_index].append(seat)
    for key in wait_seats:
        seat_size =len(wait_seats[key])
        if seat_size<2:
            retInSeats+=wait_seats[key]
        else:
            #考虑从A->B 的换座情况
            for i in range(seat_size):
                seatA = wait_seats[key][i]
                if seatA.has_key("merged"):
                    continue
                for j in range(seat_size):
                    seatB = wait_seats[key][j]
                    if i==j or seatB.has_key("merged"):
                        continue
                    BA_seconds = (seatB["from_pos"].gpsTime-seatA["to_pos"].gpsTime).total_seconds()
                    print("{4}-A:{0}-{1} B {2}-{3}".format(
                          seatA["from_pos"].gpsTime.strftime("%H:%M:%S"),
                          seatA["to_pos"].gpsTime.strftime("%H:%M:%S"),
                          seatB["from_pos"].gpsTime.strftime("%H:%M:%S"),
                          seatB["to_pos"].gpsTime.strftime("%H:%M:%S"),
                          (BA_seconds>=0 and BA_seconds<=1200)))
                    
                    if BA_seconds>=0 and BA_seconds<=1200: #换座间隔时间在20分钟以内
                        seatA["to_pos"] = copy.deepcopy(seatB["to_pos"])
                        seatA["grain"]  += seatB["grain"]
                        if seatA.has_key("remark")==False: 
                            seatA["remark"] =""
                        seatA["remark"] +=u"\r\n=>从座位:{0}，换到:{1}，换座时间 {2}-{3}".format(seatA["num"],
                                            seatB["num"],
                                            seatA["to_pos"].gpsTime.strftime("%H:%M:%S"),
                                            seatB["from_pos"].gpsTime.strftime("%H:%M:%S"))
                        if seatB.has_key["remark"]:
                            seatA["remark"]+=seatB["remark"]
                        seatB["merged"] =True #标记被合并
            for seat in wait_seats[key]:
                if seat.has_key("merged")==False:
                    retInSeats.append(seat)   
    return retInSeats


#对同一个行程的数据进行合并，
#前提，所有节点按时间顺序排列   
def mergeByDistance2(inSeats,run_endsite_seq,accuracy=0.015):
    distance_of_ends = run_endsite_seq[0]["distance_of_ends"]
    #运行中出现抖动的情况，数据进行拼接
    #1.速度>10km/h
    #2.在位距离 < 1分钟
    retInSeats = {}
    for key in inSeats :
        shortItems = []
        for i in range(len(inSeats[key])):
            
            if retInSeats.has_key(key)==False:
                retInSeats[key]=[]
                retInSeats[key].append(inSeats[key][0])
            else:
                if retInSeats[key][-1]["endsite"]!=inSeats[key][i]["endsite"]:
                    retInSeats[key].append(inSeats[key][i]) #终点站节点，不再合并
                else:#是同一个行程内的节点
                    gmileage  = inSeats[key][i]["to_pos"].gmileage-inSeats[key][i]["from_pos"].gmileage
                    gmileage2 = (retInSeats[key][-1]["to_pos"].gmileage-retInSeats[key][-1]["from_pos"].gmileage)
                    gmileage_percent2 = gmileage2/retInSeats[key][-1]["endsite"]["total_km"]
                    gmileage_percent  = gmileage /retInSeats[key][-1]["endsite"]["total_km"]
                    if retInSeats[key][-1]["status"]["sit"]==inSeats[key][i]["status"]["sit"]:
                        retInSeats[key][-1]["grain"] +=inSeats[key][i]["grain"]
                        retInSeats[key][-1]["to_pos"] = copy.deepcopy(inSeats[key][i]["to_pos"])
                    else:
                        #具有一定速度才进行合并
                        #1.空座 --开始、截止速度>30km/h
                        #2.前一个节点是有人，并且持续里程>2km
                        
                        if retInSeats[key][-1]["status"]["sit"]=="有人" and gmileage_percent2>0.03 and \
                            inSeats[key][i]["status"]["sit"]=="空座":
                            
                            span_seconds = (inSeats[key][i]["to_pos"].gpsTime-inSeats[key][i]["from_pos"].gpsTime).total_seconds()
                            span_km      =inSeats[key][i]["to_pos"].gmileage-inSeats[key][i]["from_pos"].gmileage
                            span_km_percent = span_km/distance_of_ends
                            if span_seconds<=30 or \
                                (inSeats[key][i]["to_pos"]["speed"]>20 and inSeats[key][i]["from_pos"]["speed"]>20 and \
                                (span_seconds<600 or span_km<10)):
                                retInSeats[key][-1]["grain"] +=inSeats[key][i]["grain"]
                                retInSeats[key][-1]["to_pos"] = copy.deepcopy(inSeats[key][i]["to_pos"])
                            else:
                                retInSeats[key].append(inSeats[key][i])
                        else:
                            if gmileage_percent<accuracy and retInSeats[key][-1]["to_pos"].speed>20 and inSeats[key][i]["to_pos"].speed>20:
                                retInSeats[key][-1]["grain"] +=inSeats[key][i]["grain"]
                                retInSeats[key][-1]["to_pos"] = copy.deepcopy(inSeats[key][i]["to_pos"])
                            else:
                                retInSeats[key].append(inSeats[key][i])
    return retInSeats 
    
def mergeByDistance(inSeats,run_endsite_seq,accuracy=0.015):
    distance_of_ends = run_endsite_seq[0]["distance_of_ends"]
    #运行中出现抖动的情况，数据进行拼接
    #1.速度>10km/h
    #2.在位距离 < 1分钟
    retInSeats = {}
    for key in inSeats :
        shortItems = []
        for i in range(len(inSeats[key])):
            gmileage_percent = (inSeats[key][i]["to_pos"].gmileage-inSeats[key][i]["from_pos"].gmileage)/distance_of_ends
            if retInSeats.has_key(key)==False:
                retInSeats[key]=[]
                retInSeats[key].append(inSeats[key][0])
            else:
                if retInSeats[key][-1].has_key("end_offset")==False and inSeats[key][i].has_key("end_offset"):
                    retInSeats[key].append(inSeats[key][i]) #终点站节点，不再合并
                else:
                    gmileage_percent2 = (retInSeats[key][-1]["to_pos"].gmileage-retInSeats[key][-1]["from_pos"].gmileage)/distance_of_ends
                    if retInSeats[key][-1]["status"]["sit"]==inSeats[key][i]["status"]["sit"]:
                        if inSeats[key][i]["status"]["sit"]=="有人" and (gmileage_percent+gmileage_percent2)>1.2:
                            retInSeats[key].append(inSeats[key][i])
                        else:
                            retInSeats[key][-1]["grain"] +=inSeats[key][i]["grain"]
                            retInSeats[key][-1]["to_pos"]= copy.deepcopy(inSeats[key][i]["to_pos"])
                    else:
                        #具有一定速度才进行合并
                        #1.空座 --开始、截止速度>30km/h
                        #2.前一个节点是有人，并且持续里程>2km
                        
                        if retInSeats[key][-1]["status"]["sit"]=="有人" and gmileage_percent2>0.03 and \
                            inSeats[key][i]["status"]["sit"]=="空座":
                            
                            span_seconds = (inSeats[key][i]["to_pos"].gpsTime-inSeats[key][i]["from_pos"].gpsTime).total_seconds()
                            span_km      =inSeats[key][i]["to_pos"].gmileage-inSeats[key][i]["from_pos"].gmileage
                            span_km_percent = span_km/distance_of_ends
                            if span_seconds<=30 or \
                                (inSeats[key][i]["to_pos"]["speed"]>20 and inSeats[key][i]["from_pos"]["speed"]>20 and \
                                (span_seconds<600 or span_km<10)):
                                retInSeats[key][-1]["grain"] +=inSeats[key][i]["grain"]
                                retInSeats[key][-1]["to_pos"] = copy.deepcopy(inSeats[key][i]["to_pos"])
                            else:
                                retInSeats[key].append(inSeats[key][i])
                        else:
                            if gmileage_percent<accuracy and retInSeats[key][-1]["to_pos"].speed>20 and inSeats[key][i]["to_pos"].speed>20:
                                retInSeats[key][-1]["grain"] +=inSeats[key][i]["grain"]
                                retInSeats[key][-1]["to_pos"] = copy.deepcopy(inSeats[key][i]["to_pos"])
                            else:
                                retInSeats[key].append(inSeats[key][i])
    return retInSeats    
    
def seatBymergeByDistance(inSeats,meters=500):
    #运行中出现抖动的情况，数据进行拼接
    #1.速度>10km/h
    #2.在位距离 < 1分钟
    retInSeats = {}
    for key in inSeats :
        shortItems = []
        for i in range(len(inSeats[key])):
            gmileage = (inSeats[key][i]["to_pos"].gmileage-inSeats[key][i]["from_pos"].gmileage)*1000
            if retInSeats.has_key(key)==False:
                retInSeats[key]=[]
                retInSeats[key].append(inSeats[key][0])
            else:
                if retInSeats[key][-1].has_key("end_offset")==False and inSeats[key][i].has_key("end_offset"):
                    if retInSeats[key][-1]["status"]["sit"]==inSeats[key][i]["status"]["sit"]:
                        if gmileage<=meters :#状态相同,理论上是有人，进行合并
                            retInSeats[key][-1]["grain"] +=inSeats[key][i]["grain"]
                            retInSeats[key][-1]["to_pos"] = copy.deepcopy(inSeats[key][i]["to_pos"])
                            
                            #将下一个节点，设置为终点节点
                            if i+1<len(inSeats[key]):
                                inSeats[key][i+1]["end_offset"]=0
                        else:
                            if retInSeats[key][-1]["status"]["sit"]=="空座":
                                retInSeats[key][-1]["grain"] +=inSeats[key][i]["grain"]
                                retInSeats[key][-1]["to_pos"] = copy.deepcopy(inSeats[key][i]["to_pos"])
                                #将下一个节点，设置为终点节点
                                if i+1<len(inSeats[key]):
                                    inSeats[key][i+1]["end_offset"]=0
                            else:# 
                                retInSeats[key].append(inSeats[key][i]) #终点站节点，不再合并
                    else:#状态不一致，
                        retInSeats[key].append(inSeats[key][i]) #终点站节点，不再合并
                else:
                    if retInSeats[key][-1]["status"]["sit"]==inSeats[key][i]["status"]["sit"]:
                        retInSeats[key][-1]["grain"] +=inSeats[key][i]["grain"]
                        retInSeats[key][-1]["to_pos"]= copy.deepcopy(inSeats[key][i]["to_pos"])
                    else:
                        #具有一定速度才进行合并
                        #1.空座 --开始、截止速度>30km/h
                        #2.前一个节点是有人，并且持续里程>2km
                        if retInSeats[key][-1]["status"]["sit"]=="有人" and \
                            (retInSeats[key][-1]["to_pos"].gmileage-retInSeats[key][-1]["from_pos"].gmileage)>1 and\
                            inSeats[key][i]["status"]["sit"]=="空座":
                            
                            span_seconds = (inSeats[key][i]["to_pos"].gpsTime-inSeats[key][i]["from_pos"].gpsTime).total_seconds()
                            span_km      =inSeats[key][i]["to_pos"].gmileage-inSeats[key][i]["from_pos"].gmileage
                            if (inSeats[key][i]["to_pos"]["speed"]>30 and inSeats[key][i]["from_pos"]["speed"]>30 and \
                                (span_seconds<300 or span_km<3)) or \
                                (inSeats[key][i]["to_pos"]["speed"]<=30 and inSeats[key][i]["from_pos"]["speed"]<=30 and \
                                span_seconds<=30):
                                retInSeats[key][-1]["grain"] +=inSeats[key][i]["grain"]
                                retInSeats[key][-1]["to_pos"] = copy.deepcopy(inSeats[key][i]["to_pos"])
                            else:
                                retInSeats[key].append(inSeats[key][i])
                        else:
                            if gmileage<meters and retInSeats[key][-1]["to_pos"].speed>30 and inSeats[key][i]["to_pos"].speed>30:
                                retInSeats[key][-1]["grain"] +=inSeats[key][i]["grain"]
                                retInSeats[key][-1]["to_pos"] = copy.deepcopy(inSeats[key][i]["to_pos"])
                            else:
                                retInSeats[key].append(inSeats[key][i])
    return retInSeats
def seatByMergeSite(busline_id,inSeats,run_endsite_seq):
    #getRunDirection(busline_id,)
    pass 

#def seatByMergeSite(busline_id,inSeats,run_endsite_seq):
#    getRunDirection(busline_id,)    
    
    
#获取线路起始站点
def getBuslineEndSite(busline_id):    
    #获取两端的节点
    sites = icfg.db.query("""SELECT * FROM LineSites,Sites 
                                      WHERE Sites.id=LineSites.site_id AND 
                                            LineSites.busline_id = {0} AND
                                            LineSites.is_end ="yes"
                                      ORDER BY LineSites.seq
                                      """.format(busline_id))
    if len(sites)==2:#配置了起始节点
        from_site = sites[0] #起点
        to_site   = sites[1]#终点
    else:#没有配置，自动指定
        sites = icfg.db.query("""SELECT * FROM LineSites,Sites 
                                      WHERE Sites.id=LineSites.site_id AND 
                                            LineSites.busline_id = {0} 
                                      ORDER BY LineSites.seq
                                      """.format(busline_id))
        if len(sites)==0:
            pass 
        elif len(sites)==1:
            from_site = sites[0] #起点
            to_site   = from_site
        else:
            from_site = sites[0]
            to_site   = sites[len(sites)-1]#终点
    return [from_site,to_site]

    
def isEndSite2(busline_id,pt):
    #获取两端的节点
    from_site,to_site=getBuslineEndSite(busline_id)
    
    site,offset = getLineSite2(busline_id,pt)
    if site=="":#没有做人工设定的线路
        isendSite = False
    else:
        isendSite = (site.name in [from_site.name,to_site.name]) 

    return [isendSite,offset]
    
def isEndSite(busline_id,pt):
    #获取两端的节点
    from_site,to_site=getBuslineEndSite(busline_id)
    
    site = getLineSite(busline_id,pt)
    if site=="":#没有做人工设定的线路
        isendSite = False
    else:
        isendSite = (site.name in [from_site.name,to_site.name]) 

    return isendSite
    
def formatLineSites(busline,seats,run_endsite_seq):
    for i in range(len(seats)):
        zone = getLineZone(busline.id,seats[i])
        seats[i]["开始站点"] = zone["upSite"]
        seats[i]["截止站点"] = zone["downSite"]
        seats[i]["zone"]     = zone
        #seats[i]["开始时间"] = zone["upTime"]
        #seats[i]["截止时间"] = zone["downTime"]
        #seats[i]["开始日期"] = zone["upDate"]
        #seats[i]["截止日期"] = zone["downDate"]
        from_pos = seats[i]["from_pos"]
        to_pos   = seats[i]["to_pos"]
        
        seats[i]["开始地名"] = (from_pos.local_addr if (from_pos.local_addr!=None and from_pos.local_addr.strip()!="") else  zone["upSite"])
        seats[i]["截止地名"] = (to_pos.local_addr   if (to_pos.local_addr!=None and to_pos.local_addr.strip()  !="") else  zone["downSite"]) 
        
        seats[i]["开始时间"] = from_pos.gpsTime.strftime("%H:%M:%S")
        seats[i]["开始日期"] = from_pos.gpsTime.strftime("%Y-%m-%d")
        seats[i]["开始地址"] = from_pos.addr
        seats[i]["开始速度"] = from_pos.speed
        seats[i]["截止时间"] = to_pos.gpsTime.strftime("%H:%M:%S")
        seats[i]["截止日期"] = to_pos.gpsTime.strftime("%Y-%m-%d")
        seats[i]["截止地址"] = to_pos.addr
        seats[i]["截止速度"] = to_pos.speed
        
        #endsite = getRunDirection(busline.id,seats[i],run_endsite_seq)
        endsite  = seats[i]["endsite"]
        start_time =(endsite["start_time"].strftime("%H:%M:%S") if  endsite["start_time"]!=None  else "未知")
        end_time   =(endsite["end_time"].strftime("%H:%M:%S") if  endsite["end_time"]!=None  else "未知")
        seats[i]["运行时间"] = start_time+"-"+end_time
        seats[i]["运行站点"] = endsite["start_name"]+"-"+endsite["end_name"]
        seats[i]["全程里程(KM)"] = endsite["total_km"]
        
        seats[i]["行程"] = zone["direction"]
        
        seats[i]["班车线路"] = "{0} 至 {1}".format(busline.from_name,busline.to_name)
        
        seats[i]["grain_num"] = len(seats[i]["grain"])
        stat  =statSeatStatus(busline.id,seats[i])
        seats[i]["stat"]    = stat
        seats[i]["在位里程"]=stat["seated_km"]
        seats[i]["空座里程"]=stat["unseated_km"]
        seats[i]["抖动次数"]=stat["grain_num"]
        seats[i]["在位里程/站点距离"]=stat["seated_km_percent"]
        seats[i]["在位里程/抖动次数"]=stat["seated_agv"]
        seats[i]["valid"]=stat["valid"]
        if stat["valid"]=="有效":
            seats[i]["价格"] = zone["price"]
        else:
            seats[i]["价格"] = 0
        
        seats[i]["<1KM次数"]    =stat["grain_num_below_1km"]
        seats[i]["1-2KM次数"]   =stat["grain_num_1t2km"]
        seats[i]["2-5KM次数"]   =stat["grain_num_2t5km"]
        seats[i]["5-15KM次数"]  =stat["grain_num_5t15km"]
        seats[i]["15-50KM次数"] =stat["grain_num_15t50km"]
        seats[i][">50KM次数"]   =stat["grain_num_above_50km"]
        
        seats[i]["<1KM总里程"]   =stat["grain_km_below_1km"]
        seats[i]["1-2KM总里程"]  =stat["grain_km_1t2km"]
        seats[i]["2-5KM总里程"]  =stat["grain_km_2t5km"]
        seats[i]["5-15KM总里程"] =stat["grain_km_5t15km"]
        seats[i]["15-50KM总里程"]=stat["grain_km_15t50km"]
        seats[i][">50KM总里程"]  =stat["grain_km_above_50km"]
        
        seats[i]["<1KM次数比重"]     =stat["grain_num_below_1km_percent"] 
        seats[i]["1-2KM次数比重"]    =stat["grain_num_1t2km_percent"] 
        seats[i]["2-5KM次数比重"]    =stat["grain_num_2t5km_percent"]     
        seats[i]["5-15KM次数比重"]   =stat["grain_num_5t15km_percent"]    
        seats[i]["15-50KM次数比重"]  =stat["grain_num_15t50km_percent"]   
        seats[i][">50KM次数比重"]    =stat["grain_num_above_50km_percent"]

        seats[i]["<1KM里程比重"]    =stat["grain_km_below_1km_percent"]
        seats[i]["1-2KM里程比重"]   =stat["grain_km_2t5km_percent"] 
        seats[i]["2-5KM里程比重"]   =stat["grain_km_2t5km_percent"]     
        seats[i]["5-15KM里程比重"]  =stat["grain_km_5t15km_percent"]    
        seats[i]["15-50KM里程比重"] =stat["grain_km_15t50km_percent"]   
        seats[i][">50KM里程比重"]   =stat["grain_km_above_50km_percent"]

    return seats
#对传感器的在位状态离散情况进行分析，以辨别数据的有效性 
def statSeatStatus(busline_id,seat):
    #有效里程
    grain_stat={
        "total_km":0  ,#总的里程
        "seated_km" :0,#在位里程
        "unseated_km":0,#非在位里程
        "grain_num" :0,#抖动频度
        "seated_agv":0,#在位状态分布里程
        "grain_num_below_1km":0,#持续时间在5公里以下的抖动
        "grain_km_below_1km":0, #持续时间在5公里以下的抖动，占的里程
        "grain_num_1t2km":0,#持续时间在5公里以下的抖动
        "grain_km_1t2km":0, #持续时间在5公里以下的抖动，占的里程
        "grain_num_2t5km":0,#持续时间在5公里以下的抖动
        "grain_km_2t5km":0, #持续时间在5公里以下的抖动，占的里程
        "grain_num_5t15km":0,#持续时间在5-15公里以下的抖动
        "grain_km_5t15km":0,#持续时间在5-15公里的抖动，占的里程
        "grain_num_15t50km":0,#持续时间在15-50公里的抖动
        "grain_km_15t50km":0,#持续时间在15-50公里的抖动，占的里程
        "grain_num_above_50km":0,#持续时间在50公里以上的抖动
        "grain_km_above_50km":0,#持续时间在50公里以上的抖动，占的里程
    }
    sites = getBuslineSites(busline_id)
    lenSites = len(sites)
    if lenSites==0:
        lenSites = 1 
    grain=[]
    for span in seat["grain"]:
        if span in grain:
            continue
        grain.append(span)
        
        if span["status"]["sit"] not in ["空座","有人"]:
            continue
        if ((seat["endsite"]["start_time"]!=None and seat["endsite"]["start_time"]>=span["from_pos"].gpsTime) or \
            (seat["endsite"]["end_time"]!=None and seat["endsite"]["end_time"]<=span["to_pos"].gpsTime)):
            continue
        span_km = span["to_pos"].gmileage - span["from_pos"].gmileage
        if span["status"]["sit"] =="有人":
            grain_stat["seated_km"]+=span_km
        else:
            grain_stat["unseated_km"]+=span_km
        if span_km<=1:
            grain_stat["grain_num_below_1km"]+=1
            grain_stat["grain_km_below_1km"] +=span_km
        elif span_km<=2:
            grain_stat["grain_num_1t2km"]+=1
            grain_stat["grain_km_1t2km"] +=span_km
        elif span_km<=5:
            grain_stat["grain_num_2t5km"]+=1
            grain_stat["grain_km_2t5km"] +=span_km
        elif span_km<=15:
            grain_stat["grain_num_5t15km"]+=1
            grain_stat["grain_km_5t15km"] +=span_km
        elif span_km<=50:
            grain_stat["grain_num_15t50km"]+=1
            grain_stat["grain_km_15t50km"] +=span_km
        else:
            grain_stat["grain_num_above_50km"]+=1
            grain_stat["grain_km_above_50km"] +=span_km
            
    grain_stat["grain_num"]  = len(grain)
    grain_stat["seated_km0"] = seat["to_pos"].gmileage-seat["from_pos"].gmileage
    grain_stat["seated_agv"] = grain_stat["seated_km0"]/grain_stat["grain_num"]
    if seat["zone"]["site_dist"]>0:
        grain_stat["seated_km_percent"]  =grain_stat["seated_km0"]/seat["zone"]["site_dist"]
    else:
        grain_stat["seated_km_percent"]  =0
    grain_stat["unseated_km_percent"]=grain_stat["unseated_km"]/seat["endsite"]["total_km"]
    
    #数据有效性判定
    #站点间的平均距离
    site_dist_avg = seat["endsite"]["total_km"]/lenSites
    #if grain_stat["seated_km_percent"]>0.6 and \
    #   ((site_dist_avg<=10 and grain_stat["seated_agv"] > 2) or \
    #    (site_dist_avg>10 and grain_stat["seated_agv"] >6)):
    #    grain_stat["valid"] =u"有效"
    #else:
    #    grain_stat["valid"] =u"无效"
    
    if grain_stat["seated_km_percent"]>0:
        grain_stat["valid"] =u"有效"
    else:
        grain_stat["valid"] =u"无效"
    
    grain_stat["grain_num_below_1km_percent"] =grain_stat["grain_num_below_1km"]/grain_stat["grain_num"]         
    grain_stat["grain_num_1t2km_percent"]     =grain_stat["grain_num_1t2km"]    /grain_stat["grain_num"]         
    grain_stat["grain_num_2t5km_percent"]     =grain_stat["grain_num_2t5km"]    /grain_stat["grain_num"]         
    grain_stat["grain_num_5t15km_percent"]    =grain_stat["grain_num_5t15km"]   /grain_stat["grain_num"]         
    grain_stat["grain_num_15t50km_percent"]   =grain_stat["grain_num_15t50km"]  /grain_stat["grain_num"]         
    grain_stat["grain_num_above_50km_percent"]=grain_stat["grain_num_above_50km"]/grain_stat["grain_num"]         

    grain_stat["grain_km_below_1km_percent"] =grain_stat["grain_num_below_1km"]/seat["endsite"]["total_km"]         
    grain_stat["grain_km_1t2km_percent"]     =grain_stat["grain_num_1t2km"]    /seat["endsite"]["total_km"]         
    grain_stat["grain_km_2t5km_percent"]     =grain_stat["grain_num_2t5km"]    /seat["endsite"]["total_km"]         
    grain_stat["grain_km_5t15km_percent"]    =grain_stat["grain_km_5t15km"]    /seat["endsite"]["total_km"]         
    grain_stat["grain_km_15t50km_percent"]   =grain_stat["grain_km_15t50km"]   /seat["endsite"]["total_km"]         
    grain_stat["grain_km_above_50km_percent"]=grain_stat["grain_km_above_50km"]/seat["endsite"]["total_km"]         
    
    return grain_stat    
        
#获取起始状态方向    isEndSite2
def getRunDirection(busline_id,seat,run_endsite_seq):
    from_pos = seat["from_pos"]
    to_pos   = seat["to_pos"]
    #确定所属区段
    run_site =None #所属行程区段

    
    #确定最近的一个区间
    for run_endsite in run_endsite_seq:
        if run_endsite["start_site_t"]!=None and run_endsite["end_site_t"]!=None:
            from_start_seconds= (from_pos.gpsTime-run_endsite["start_site_t"].gpsTime).total_seconds()
            end_to_seconds= (run_endsite["end_site_t"].gpsTime-to_pos.gpsTime).total_seconds()
            if (to_pos.gmileage  >run_endsite["start_site_t"].gmileage and \
               from_pos.gmileage<run_endsite["end_site_t"].gmileage and \
               from_pos.gmileage>run_endsite["start_site_t"].gmileage-5 and \
               to_pos.gmileage  <run_endsite["end_site_t"].gmileage+5) or \
               ((to_pos.gpsTime-run_endsite["start_site_t"].gpsTime).total_seconds()>0 and \
                (from_pos.gpsTime-run_endsite["end_site_t"].gpsTime).total_seconds()<0 and \
                from_start_seconds>=-1500 and end_to_seconds >=-1500):
                run_site = run_endsite
            else:
                continue
        if run_endsite["start_site_t"]!=None and run_endsite["end_site_t"]==None:
            if (to_pos.gmileage>run_endsite["start_site_t"].gmileage and \
               (from_pos.gmileage-run_endsite["start_site_t"].gmileage)>=-5) or \
               ((to_pos.gpsTime-run_endsite["start_site_t"].gpsTime).total_seconds()>0 and \
               (from_pos.gpsTime-run_endsite["start_site_t"].gpsTime).total_seconds()>=-900):
                run_site = run_endsite
            else:
                continue
        if run_endsite["end_site_t"]!=None and run_endsite["start_site_t"]==None:
            if (from_pos.gmileage<run_endsite["end_site_t"].gmileage and \
               (run_endsite["end_site_t"].gmileage+5)>=to_pos.gmileage) or \
               ((from_pos.gpsTime-run_endsite["end_site_t"].gpsTime).total_seconds()<0 and \
                (run_endsite["end_site_t"].gpsTime-to_pos.gpsTime).total_seconds()>=-900):
                run_site = run_endsite
            else:
                continue
    endsite ={"start_time":None,"end_time":None}
    
    if run_site==None:#没有设置终点站
        start_name=""
        end_name  =""
        total_km  =-1
    else:
        #优先运行起始距离判定
        if run_site["start_site_t"]!=None:
            endsite["start_time"] = run_site["start_site_t"].gpsTime
        if run_site["end_site_t"]  !=None:
            endsite["end_time"] = run_site["end_site_t"].gpsTime
    
        if  run_site["start_site_t"]  !=None and  run_site["end_site_t"]  !=None:
            total_km   = run_site["end_site_t"].gmileage - run_site["start_site_t"].gmileage
        else:
            total_km   = uTools.getDistance(run_site["to_site"].gpsLat,run_site["to_site"].gpsLng, run_site["from_site"].gpsLat,run_site["from_site"].gpsLng)
        start_name = run_site["start_site_name"]
        end_name   = run_site["end_site_name"]
    endsite["run_site"]   =  run_site
    endsite["start_name"] =  start_name
    endsite["end_name"]   =  end_name
    endsite["total_km"]   =  total_km
    if endsite["end_time"]!=None and endsite["start_time"]!=None:
        total_seconds = (endsite["end_time"]-endsite["start_time"]).total_seconds()
    else:
        total_seconds = 0
    endsite["total_seconds"]= total_seconds
    return endsite
    
    
#依据当前位置，判定该位置所属的站点    
def getLineZone(busline_id,zone):
    #获取站点：{名称,seq}
    from_site = getLineSite(busline_id,zone["from_pos"])
    to_site   = getLineSite(busline_id,zone["to_pos"])
    if isinstance(from_site,str) or isinstance(to_site,str):
        direction = ""
        upSite    = ""
        downSite  = ""
        price     = 0
    else:
        direction = ("去程" if to_site.seq -from_site.seq > 0 else "回程" )
        upSite    = from_site.name
        downSite  = to_site.name
        #依据站点查询价格
        price     = getLinePrice(busline_id,from_site.site_id,to_site.site_id)
    site_dist = uTools.getDistance(from_site.gpsLat,from_site.gpsLng,to_site.gpsLat,to_site.gpsLng)
    #上车点，下车点 ，方向，价格
    fZone ={"upSite"   :upSite,
            "downSite" :downSite,
            "direction":direction,
            "price"    :price,
            "from_site":from_site,
            "to_site"  :to_site,
            "site_dist":site_dist,
            #"upTime"   :zone["from_pos"].gpsTime.strftime("%H:%M:%S"),
            #"downTime" :zone["to_pos"].gpsTime.strftime("%H:%M:%S"),
            #"upDate"   :zone["from_pos"].gpsTime.strftime("%Y-%m-%d"),
            #"downDate" :zone["to_pos"].gpsTime.strftime("%Y-%m-%d")
    }
    return fZone

def getLineSite2(busline_id,pt):
    sites = icfg.db.query("""SELECT *,LineSites.id AS line_site_id,Sites.id AS site_id FROM LineSites,Sites
                                          WHERE LineSites.busline_id = {0} AND
                                                LineSites.site_id    = Sites.id AND
                                                Sites.setting_type= "manual"
                               """.format(busline_id))
    if len(sites)==0:
        sites = icfg.db.query("""SELECT *,LineSites.id AS line_site_id,Sites.id AS site_id FROM LineSites,Sites
                                          WHERE LineSites.busline_id = {0} AND
                                                LineSites.site_id    = Sites.id
                               """.format(busline_id))
    dstSite = ""  #目标站点
    shortDist = 100000 #当前最短距离
    for site in sites:
        gdist=uTools.getDistance(pt.gpsLat,pt.gpsLng,site.gpsLat,site.gpsLng)
        if gdist<shortDist:#获取最短的站点
            dstSite   =  site
            shortDist = gdist
    return [dstSite,shortDist]   
 
#判定规则：直线距离相比，距离最短的站点即为对应站点      
def getLineSite(busline_id,pt):
    sites = icfg.db.query("""SELECT *,LineSites.id AS line_site_id FROM LineSites,Sites
                                          WHERE LineSites.busline_id = {0} AND
                                                LineSites.site_id    = Sites.id AND
                                                Sites.setting_type= "manual"
                               """.format(busline_id))
    if len(sites)==0:
        sites = icfg.db.query("""SELECT *,LineSites.id AS line_site_id FROM LineSites,Sites
                                          WHERE LineSites.busline_id = {0} AND
                                                LineSites.site_id    = Sites.id
                               """.format(busline_id))
    dstSite = ""  #目标站点
    shortDist = 100000 #当前最短距离
    for site in sites:
        gdist=uTools.getDistance(pt.gpsLat,pt.gpsLng,site.gpsLat,site.gpsLng)
        if gdist<shortDist:#获取最短的站点
            dstSite   =  site
            shortDist = gdist
    return dstSite
    
#依据站点id获取价格    
def getLinePrice(busline_id,from_site_id,to_site_id):
    _price = icfg.db.query("""SELECT * FROM LinePrice
                                          WHERE busline_id   = {0} AND
                                                from_site_id = {1} AND
                                                to_site_id   = {2}
                               """.format(busline_id,from_site_id,to_site_id))
    if len(_price)==0:
        price = 0;
    else:
        price = _price[0].price
    return price
    
#依据imei获取BusLine   
def getBusline(imei):
    #获取该车所属车队
    _ret = icfg.db.query("""SELECT * FROM GroupHasDevice WHERE imei='{0}'""".format(imei))
    busgroup_id = _ret[0].devicegroup_id
    
    #依据车队查找对应的线路
    _ret = icfg.db.query("""SELECT * FROM BusLine WHERE busgroupid={0}""".format(busgroup_id))
    busline = _ret[0]  
    return busline

def getSeatStatus2(imei,his_datetime=None):
    #获取地址
    #_ret = icfg.db.query("SELECT * FROM HistoryTrack WHERE imei='{0}' ORDER BY gpsTime DESC LIMIT 0,2".format(imei))
    if his_datetime==None:#获取当前数据
        ret = getCurrentSeatStatus(imei)
    else:
        ret = getHistorySeatStatus(imei,his_datetime)
    
    pos      =ret["pos"]
    seatData =ret["seatData"] 
    
    if pos != None:
        if pos.seatStatus != "": #从当前位置可以取到有效座位信息
            if seatData==None:
                seatStatus = pos.seatStatus
                dataTime   = pos.gpsTime.strftime("%Y-%m-%d %H:%M:%S")
            else:
                if pos.gpsTime > seatData.report_at:
                    seatStatus = pos.seatStatus
                    dataTime   = pos.gpsTime.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    seatStatus = seatData.seatStatus
                    dataTime   = seatData.report_at.strftime("%Y-%m-%d %H:%M:%S")
        else:#无有效GPS数据
            if seatData==None:
                seatStatus = None
                dataTime   = "没有上报数据"
            else:
                seatStatus = seatData.seatStatus
                dataTime   = seatData.report_at.strftime("%Y-%m-%d %H:%M:%S")
    else:#以cachedata数据为准
        if seatData==None:
            seatStatus = None
            dataTime   = "没有上报数据"
        else:
            seatStatus = seatData.seatStatus
            dataTime   = seatData.report_at.strftime("%Y-%m-%d %H:%M:%S")
            
    #座位解析
    cfgPara = analyzeSeatStatus(seatStatus)
    cfgPara["addr"]    = ("" if pos is None else pos.addr)
    cfgPara["imei"]    = imei
    cfgPara["gpsTime"] = ("" if pos is None else pos.gpsTime.strftime("%Y-%m-%d %H:%M:%S"))
    cfgPara["dataTime"]= dataTime
    cfgPara["now_time"]= datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cfgPara["speed"]   = ("" if pos is None else pos.speed)
    return cfgPara
    
def getSeatStatus(imei,his_datetime=None):
    #获取地址
    #_ret = icfg.db.query("SELECT * FROM HistoryTrack WHERE imei='{0}' ORDER BY gpsTime DESC LIMIT 0,2".format(imei))
    if his_datetime==None:#获取当前数据
        ret = getCurrentSeatStatus(imei)
    else:
        ret = getHistorySeatStatus(imei,his_datetime)
    if ret==None:
        return None
    pos      =ret["pos"]
    seatData =ret["seatData"] 
    
    #查询板类型
    ret = icfg.db.query("""SELECT seat_num FROM SeatType 
                          WHERE enName IN (SELECT seat_type FROM Device WHERE imei='{0}')""".format(imei))
    seat_num = ret[0].seat_num
    
    if pos != None:
        if pos.seatStatus != "": #从当前位置可以取到有效座位信息
            if seatData==None:
                seatStatus = pos.seatStatus
                dataTime   = pos.gpsTime.strftime("%Y-%m-%d %H:%M:%S")
            else:
                if pos.gpsTime > seatData.report_at:
                    seatStatus = pos.seatStatus
                    dataTime   = pos.gpsTime.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    seatStatus = seatData.seatStatus
                    dataTime   = seatData.report_at.strftime("%Y-%m-%d %H:%M:%S")
        else:#无有效GPS数据
            if seatData==None:
                seatStatus = None
                dataTime   = "没有上报数据"
            else:
                seatStatus = seatData.seatStatus
                dataTime   = seatData.report_at.strftime("%Y-%m-%d %H:%M:%S")
    else:#以cachedata数据为准
        if seatData==None:
            seatStatus = None
            dataTime   = "没有上报数据"
        else:
            seatStatus = seatData.seatStatus
            dataTime   = seatData.report_at.strftime("%Y-%m-%d %H:%M:%S")
    cfgPara={}        
    #座位解析
    cfgPara["timely"]= analyzeSeatStatus(seatStatus,seat_num)
    cfgPara["region"]= getRegionSeatStatus(imei,seat_num)
    cfgPara["timer"] = getCustomerSeatStatus(imei,seat_num)
    cfgPara["param"] ={}
    cfgPara["param"]["addr"]    = ("" if pos is None else pos.addr)
    cfgPara["param"]["imei"]    = imei
    cfgPara["param"]["gpsTime"] = ("" if pos is None else pos.gpsTime.strftime("%Y-%m-%d %H:%M:%S"))
    cfgPara["param"]["dataTime"]= dataTime
    cfgPara["param"]["now_time"]= datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cfgPara["param"]["speed"]   = ("" if pos is None else pos.speed)
    #print cfgPara["param"]
    return cfgPara


    
    
def getRegionSeatStatus(imei,seat_num):
    valiTime = datetime.datetime.now() - datetime.timedelta(hours=8)
    _ret = icfg.db.query("""SELECT seatStatus FROM MonitorResult 
                     WHERE imei='{0}' AND duration_mileage>0 
                           AND to_time>= '{1}'""".format(imei,valiTime.strftime("%Y-%m-%d %H:%M:%S")))
    seatStatus = None
    if len(_ret)>0:
        seatStatus = analyzeRegionSeatStatus(_ret[0].seatStatus)
    
    return seatStatus

def getCustomerSeatStatus(imei,seat_num):
    valiTime = datetime.datetime.now() - datetime.timedelta(minutes=15)
    #validStamp = time.mktime(valiTime.timetuple())
    _ret = icfg.db.query("""SELECT seatstatus FROM CustomerSeat 
                     WHERE imei='{0}' AND update_at>= '{1}'
                      """.format(imei,valiTime.strftime("%Y-%m-%d %H:%M:%S")))
    seatStatus = None
    if len(_ret)>0:
        seatStatus = analyzeSeatStatus(_ret[0].seatstatus,seat_num)
        seatStatus["srcType"]="timer_analyze"
    return seatStatus
    
def getProceedHistorySeatStatus(imei,his_datetime):
    pass
    
def getCurrentSeatStatus(imei):
    _ret = icfg.db.query("SELECT * FROM CurrentLocation WHERE imei='{0}'".format(imei))
    if len(_ret)==0:
        return  None
    else:
        pos = _ret[0]
    #获取座位信息
    if pos.seatStatus==None or pos.seatStatus=="":
        seatData = getLastValidSeatData(imei)
    else:
        seatData = pos
    ret={"pos":pos,"seatData":seatData}
    return ret
    
def getHistorySeatStatus(imei,his_datetime):
    _ret = icfg.db.query("""SELECT * FROM HistoryTrack 
                                     WHERE imei='{0}' AND gpsTime>='{1}' AND seatStatus <>''
                                     ORDER BY  gpsTime
                                     LIMIT 0,2""".format(imei,his_datetime))
    if len(_ret)==0:
        ret = {"pos":None,"seatData":None}
    else:
        pos = _ret[0]
        ret ={"pos":pos,"seatData":pos}
    return ret
    
def getLastValidSeatData(imei):
    seatTable = "CacheSeat"
    seat_data = None
    _ret = icfg.db.query("SELECT * FROM {0} WHERE imei='{1}' ORDER BY report_at DESC LIMIT 0,10".format(seatTable,imei))
    for seat in _ret:
        temp = json.loads(seat.seatStatus)
        if len(temp.keys()) == _seat_pkg_len:
            seat_data = seat
            break
    return seat_data
    
    #for seat in _ret:
    #    if is_init_data(seat.seatStatus):
    #        continue
    #    else:
    #        seat_data = seat
    #        break 
        
    
def analyzeSeatStatus(seatStatus,seat_num=60):
    cfgPara ={"seats":{},"sum":{}}
    for key in _seatStatus:#初始化
            cfgPara["sum"][_seatStatus[key]]=0
    if seatStatus != None and seatStatus!="":
        jsonSeat = json.loads(seatStatus)
        for i in range(0,seat_num+1):
            seat = str(i)
            if jsonSeat.has_key(seat)==False:
                continue  
            _status = _seatStatus[jsonSeat[seat]["sit"]]
            cfgPara["sum"][_status]+=1
            cfgPara["seats"][i]=_status
    return cfgPara
    
def analyzeRegionSeatStatus(seatStatus):
    cfgPara ={"seats":{},"sum":{},"srcType":"region_monitor"}
    for key in _seatStatus:#初始化
            cfgPara["sum"][_seatStatus[key]]=0
            
    if seatStatus != None and seatStatus!="":
        stat = json.loads(seatStatus)
        for no in stat["checked_result"]:
            _status = stat["checked_result"][no]
            if  cfgPara["sum"].has_key(no):
                cfgPara["sum"][no]+=1
            else:
                cfgPara["sum"][no] = 0
            
            cfgPara["seats"][no]=_status
    return cfgPara

#查询最近运行的线路统计信息    
def getCurrentBusTravelStat(imei):
    items=[]
    sites_stat={}
    _ret = icfg.db.query("SELECT * FROM BusTravel WHERE imei='{0}' ORDER BY create_at DESC LIMIT 0,2")
    if len(_ret)==0:
        return None
    bustravel = _ret[0]
    _sites = icfg.db.query("SELECT * FROM SiteSeatStatus WHERE bustravel_id={0} ORDER BY from_time")
    for seat_site in _sites:
        _ret = icfg.db.query("SELECT * FROM Sites WHERE id ={0} ".format(seat_site.site_id))
        site =_ret[0]
        if len(items)==0:
            sites_stat={
                "start_site":site.addr,
                "start_date":seat_site.from_time.strftime("%m-%d"),
                "start_time":seat_site.from_time.strftime("%H:%M:%S"),
                "span_id"   :seat_site.next_span_id
            }
        items.append({
            "time"      :seat_site.from_time.strftime("%H:%M"),
            "stop_minutes":"%0.1f"%(seat_site.to_time - seat_site.from_time).total_seconds()/60.0,
            "site"      :site.name,
            "num_seated":seat_site.num_seated,
            "num_change":seat_site.num_change,
        })
    sites_stat["items"] = items
    return sites_stat

#依据span_id 查询该区段的详细座位情况    
def getDetailBusTravelStat(span_id):
    span_stat ={}
    items     =[]
    _ret = icfg.db.query("SELECT * FROM Span WHERE id={0}".format(span_id))
    span = _ret[0]
    _span_seats = icfg.db.query("SELECT * FROM SpanSeatStatus WHERE span_id={0}".format(span_id))
    for span_seat in _span_seats:
        items.append(uTools.dbItem2Dict(span_seat,format="string"))
    #起始位置
    _ret = icfg.db.query("""SELECT * FROM Sites,SiteSeatStatus
                            WHERE Sites.id=SiteSeatStatus.site_id AND
                                  SiteSeatStatus.id ={0}""".format(span.from_site_id))
    from_site = _ret[0]
    
    _ret = icfg.db.query("""SELECT * FROM Sites,SiteSeatStatus
                            WHERE Sites.id=SiteSeatStatus.site_id AND
                                  SiteSeatStatus.id ={0}""".format(span.to_site_id))
    to_site = _ret[0]
    
    #里程计算
    _ret = icfg.db.query("SELECT * FROM HistoryTrack WHERE imei='{0}' AND gpsTime='{1}'".format(span.imei,from_site.gpsTime))
    from_pos = _ret[0]
    _ret = icfg.db.query("SELECT * FROM HistoryTrack WHERE imei='{0}' AND gpsTime='{1}'".format(span.imei,to_site.gpsTime))
    to_pos = _ret[0]
    
    span_stat ={"items":items,
        "from_site":from_site.addr,
        "to_site"  :to_site.addr,
        "from_time":from_site.from_time.strftime("%m-%d %H:%M:%S"),
        "to_time"  :from_site.to_time.strftime("%m-%d %H:%M:%S"),
        "mileage_span":to_pos.gmileage -from_pos.gmileage,
        "num_seated"  :span.num_seated,
        "num_unseated":span.num_unseated,
        "num_idle"    :span.num_idle,
        "num_timeout" :span.num_timeout,
        "imei"        :span.imei,  
    }

    
