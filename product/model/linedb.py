# _*_ coding:utf-8 _*_
import web,json
import product.iconfig  as icfg
import datetime
import requests
import utility as uTools
import devdb

#从数据库中查询站点信息，返回形式：[{},{}]
def getSitesByLineid(busline_id,setting_type="manual"):
    if setting_type=="all":#所有的
        _sites = icfg.db.query("""SELECT *,Sites.id AS site_id FROM LineSites,Sites
                                           WHERE LineSites.busline_id ={0} AND
                                                 LineSites.site_id = Sites.id 
                                           ORDER BY seq""".format(busline_id))
                                           
    elif setting_type =="manual":  #人工设置                                     
        _sites = icfg.db.query("""SELECT *,Sites.id AS site_id FROM LineSites,Sites
                                           WHERE LineSites.busline_id ={0} AND
                                                 LineSites.site_id = Sites.id AND
                                                 Sites.setting_type='manual'
                                           ORDER BY seq""".format(busline_id))
    else:#获取自动分析的停车点
        _sites = icfg.db.query("""SELECT *,Sites.id AS site_id FROM LineSites,Sites
                                           WHERE LineSites.busline_id ={0} AND
                                                 LineSites.site_id = Sites.id AND
                                                 Sites.setting_type<>'manual'
                                           ORDER BY seq""".format(busline_id))
                                           
    ret = statSites(_sites)
    return ret 
    
def getHistorySitesByImei(imei,fromTime,toTime):
    sites = {"manual":[],"auto":[]}
    _run_sites = icfg.db.query("""SELECT *,Sites.id AS site_id 
                              FROM Sites,SiteSeatStatus
                              WHERE SiteSeatStatus.imei ='{0}'        AND
                                    SiteSeatStatus.site_id = Sites.id AND
                                   (SiteSeatStatus.from_time>='{1}' AND SiteSeatStatus.to_time<='{2}')""".format(imei,fromTime,toTime))         
    for site in _run_sites:
        site = uTools.dbItem2Dict(site,format="string")
        site["seated_num"] =site["to_seated_num"]
        sites["auto"].append(site)
        
        
    busline = getBuslineByImei(imei)
    _manual_sites = icfg.db.query("""SELECT *,Sites.id AS site_id FROM LineSites,Sites
                                           WHERE LineSites.busline_id ={0} AND
                                                 LineSites.site_id = Sites.id AND
                                                 Sites.setting_type='manual'
                                           ORDER BY seq""".format(busline["id"]))                                 
    for site in _manual_sites:
        site = uTools.dbItem2Dict(site,format="string")
        sites["manual"].append(site)
    return sites 
    
def statSites(_sites):
    sites = {"manual":[],"auto":[]}
    stat_sites =[];#防止重复统计
    for _site in _sites:
        if _site.site_id in stat_sites:
            continue
        setting_type = ("auto" if _site.setting_type is None else _site.setting_type)
        site = uTools.dbItem2Dict(_site,format="string")
        sites[setting_type].append(site)
    return sites
    
#items = []
#    items.append({"line_id":29,"src":"灵山","dst":"深圳"})
#    items.append({"line_id":12,"src":"灵山","dst":"大坪"}) 
def getBusLineByOpenid(openid,company_id=0):
    #权限校验。。。
    lines = []
    company_ids =[]
    if company_id==0:
        _company = icfg.db.query("""SELECT * FROM CompanyHasEmployee WHERE openid='{0}' AND company_id>0 ORDER BY company_id""".format(openid))
        for company in _company:
            company_ids.append(company.company_id)
            _lines = icfg.db.query("""SELECT * FROM BusLine WHERE company_id={0}""".format(company.company_id))
            for line in _lines:
                lines.append(line) 
    else:
        _lines = icfg.db.query("""SELECT * FROM BusLine WHERE company_id={0}""".format(company_id))  
        company_ids.append(company_id)
        for line in _lines:
                lines.append(line) 
        
    retLines =[]
    for line in lines:
        temp ={}
        for k in line:
            if isinstance(line[k],datetime.datetime):
                temp[k] = line[k].strftime("%Y-%m-%d %H:%M:%S")
            else:
                temp[k] = line[k]
        _lineBusNum = icfg.db.query("""SELECT COUNT(imei) AS sum FROM GroupHasDevice 
                                       WHERE devicegroup_id={0}""".format(line.busgroupid))
        temp["bus_num"] = _lineBusNum[0].sum;
        retLines.append(temp)
    cfgPara ={"items":retLines,"company_ids":company_ids}
    return cfgPara

def getBusLineByOpenid4pc(openid,company_id=0):
    cfgPara = getBusLineByOpenid(openid,company_id)
    cfgPara["total"]=len(cfgPara["items"])
    cfgPara["rows"] =cfgPara["items"]
    no = 1
    for row in cfgPara["rows"]:
        row["no"] =no
        no += 1
    del cfgPara["items"]
    del cfgPara["company_ids"]
    return cfgPara
    
def isEmployee(openid):
    _company = icfg.db.query("""SELECT * FROM CompanyHasEmployee WHERE openid='{0}' """.format(openid))
    return len(_company)>0

def getEmployeeByid(company_id,with_manager=False):
    rows = []
    openids =[]
    _employee = icfg.db.query("""SELECT * FROM CompanyHasEmployee WHERE company_id={0}
                              """.format(company_id))
    receivers = [employee for employee in _employee]
    if with_manager==True:
        _mgrs = icfg.db.query("""SELECT * FROM Manager WHERE privilege<>'invisible'
                              """.format(company_id))
        for mgr in _mgrs:
            receivers.append(mgr)
            
    for employee in receivers:
        if employee.openid in openids:
            continue
        openids.append(employee.openid)
        _ret = icfg.db.query("""SELECT * FROM Customer WHERE openid ='{0}'
                             """.format(employee.openid))
        if len(_ret)>0:
            nickname = _ret[0].nickname
            rows.append(uTools.dbItem2Dict(employee,format="string"))
            rows[-1]["nickname"] = nickname
            if rows[-1]["remark"]=="":
                rows[-1]["remark"]=nickname
    return rows  

def getEmployeeByid4pc(company_id,with_manager=False):
    rows = []
    openids = []
    rows = {"saiwei":[],"customer":[]}
    _employee = icfg.db.query("""SELECT * FROM CompanyHasEmployee WHERE company_id={0}
                              """.format(company_id))
    for employee in _employee:
        openids.append(employee.openid)
        _employee = uTools.dbItem2Dict(employee,format="string")
        rows["customer"].append(formatEmployeeInfo(_employee))
    
    
    if with_manager==True:
        _mgrs = icfg.db.query("""SELECT * FROM Manager WHERE privilege<>'invisible'
                              """.format(company_id))
        for employee in _mgrs:
            if employee.openid in openids:
                continue
            openids.append(employee.openid)
            _employee = uTools.dbItem2Dict(employee,format="string")
            rows["saiwei"].append(formatEmployeeInfo(_employee))
            
    return rows 

def formatEmployeeInfo(employee):
    _ret = icfg.db.query("""SELECT * FROM Customer WHERE openid ='{0}'
                             """.format(employee["openid"]))
    if len(_ret)>0:
        nickname = _ret[0].nickname
        employee["nickname"] = nickname
        if employee["remark"]=="":
            employee["remark"]=nickname
    return employee
    
def getLinePrice(busline_id):
    result={}
    _prices = icfg.db.query("""SELECT * FROM LinePrice WHERE BusLine_id={0}""".format(busline_id))
    for linePrice in _prices:
        if result.has_key(linePrice.from_site_id)==False:
            result[linePrice.from_site_id] ={}
        result[linePrice.from_site_id][linePrice.to_site_id]=linePrice.price
    return result
        
def isManager(openid):
    _ret = icfg.db.query("SELECT * FROM Manager WHERE openid='{0}' AND weixinname='gxsaiwei'".format(openid))
    return (len(_ret)==1)

#判定该openid是imei的管理者    
def isManager2(openid,imei):
    #判定是否为赛微公司员工
    _ret = icfg.db.query("SELECT * FROM CompanyHasEmployee WHERE openid='{0}' and company_id=1".format(openid))
    if len(_ret)==1:
        ret = True
    else:#按普通公司进行审核权限
        #所属的车队
        _ret = icfg.db.query("SELECT * FROM GroupHasDevice WHERE imei='{0}'".format(imei))
        busgroup=_ret[0]
        #所属的线路
        _ret = icfg.db.query("SELECT * FROM BusLine WHERE busgroupid={0}".format(busgroup.devicegroup_id))
        busline=_ret[0]
        
        #所属公司
        _ret = icfg.db.query("""SELECT * FROM CompanyHasEmployee 
                                        WHERE openid='{0}' AND  
                                            company_id={1} AND 
                                            privilege='manager'""".format(openid,busline.company_id))
        
        
        ret = False if len(_ret)==0 else True
    return ret
        
#注册公司
def regeditCompany(**param):
    id = icfg.db.insert("Company",name   =param["name"],
                            weixin      =param["weixin"], 
                            qq          =param["qq"], 
                            phone       =param["phone"], 
                            workAddr    =param["addr"],
                            province    =param["province"],
                            city        =param["city"],
                            district    = param["district"],
                            created_at  =web.SQLLiteral('NOW()'),
                            valid       =param["valid"],
                            regedit_openid=param["regedit_openid"],
                            company=param["company"],
    )
    qrcode_id = getQrcodeLimitUrl("Company",id)
    icfg.db.update("Company",where="id=$id", WeixinQRcodeScene_id=qrcode_id,vars=locals())
    return id
    
def getQrcodeLimitUrl(tableName,id):
    env = icfg.getEnvObj()
    #生成文件名
    title = "{0}01{1}".format(datetime.datetime.now().strftime("%Y%m%d%H%M%S"),id)
    _qrcode_url="{0}{1}.jpg".format(env["qrcode_url"],title)
    file_name  = "{0}/{1}.jpg".format(icfg.qrcode_root_dir,title)
    #判定scene_id是否合法
    _ret = icfg.db.query("SELECT * FROM QrsceneAllocation WHERE tableName = '{0}'".format(tableName))
    scene = _ret[0]
    
    WeixinQRcodeScene_id =-1 #标记失败的id值
    
    _ret = icfg.db.query("SELECT COUNT(*) AS sum FROM QrsceneAllocation")
    if _ret[0].sum > 100000:
        raise("{0}：scene_id{1} 大于 最大值：{2} ".format(tableName,scene.start_scene+id,scene.end_scene))
    else:
        #1.将二维码记录WeixinQRcodeScene数据库
        WeixinQRcodeScene_id = icfg.db.insert("WeixinQRcodeScene",tableName=tableName,table_id=id,qrcode_url=_qrcode_url)
        
        #2.将二维码生成任务加入并发队列
        #qrUrl = '{2}/utility/cronday00?act=GEN_LIMIT_QRCODE&file_name={0}&scene_id={1}&weixinname=gxsaiwei'.format(title,WeixinQRcodeScene_id,web.ctx.homedomain)
        ##print(qrUrl)
        #requests.get(qrUrl)
        scene_str ="P{0}".format(WeixinQRcodeScene_id)
        icfg.objWeixin.create_perm_qrcode2(scene_str,_qrcode_url,file_name)
        #add_task('QRCodeSeq', qrUrl, '')
    
    return WeixinQRcodeScene_id

def statCompany(env,openid):
    employee = getManageEmployee(openid)
    stat = []
    if employee!=None:
        if employee.range=="所有":
            _companies = icfg.db.query("SELECT * FROM Company ORDER BY id")
        else:
            _companies = icfg.db.query("SELECT * FROM Company WHERE province like '{0}%' ORDER BY id".format(employee.range))
        
        for _company in _companies:
            company = {}
            for key in _company.keys():
                if type(_company[key]) is datetime.datetime:
                    company[key] = _company[key].strftime("%Y-%m-%d %H:%M:%S")
                else:
                    company[key] = _company[key]
            company["url"]=icfg.objWeixin.getAuth2Url("{0}/m/manager?act2=home_companyid_{1}".format(env["homedomain"],company["id"]))
            company["regedit_url"]=icfg.objWeixin.getAuth2Url("{0}/m/manager?act2=home_companyid_{1}".format(env["homedomain"],company["id"]))
            stat.append(company)
    return stat
 
def getManageEmployee(openid):
    _ret = icfg.db.query("SELECT * FROM CompanyHasEmployee WHERE company_id=1 AND openid='{0}'".format(openid))
    if len(_ret)==0:
        ret= None
    else:
        ret = _ret[0]
    return ret

def getBuslineByImei(imei,format="orign"):
    _ret = icfg.db.query("SELECT * FROM GroupHasDevice WHERE imei='{0}'".format(imei))
    if len(_ret)==0:
        return None
    _ret = icfg.db.query("SELECT * FROM BusLine WHERE busgroupid={0}".format(_ret[0].devicegroup_id))

    busline = (None if len(_ret)==0 else uTools.dbItem2Dict(_ret[0],format))
    return busline
    
    
def getCompanyByImei(imei):
    _ret = icfg.db.query("SELECT * FROM GroupHasDevice WHERE imei='{0}'".format(imei))
    if len(_ret)==0:
        return None
    _ret = icfg.db.query("SELECT * FROM BusLine WHERE busgroupid={0}".format(_ret[0].devicegroup_id))
    if len(_ret)==0:
        return None
    _ret = icfg.db.query("SELECT * FROM Company WHERE id={0}".format(_ret[0].company_id))
    company = uTools.dbItem2Dict(_ret[0])
    return company

def getCompanyByBusline(busline_id):
    _ret = icfg.db.query("SELECT * FROM BusLine WHERE id={0}".format(busline_id))
    if len(_ret)==0:
        return None
    _ret = icfg.db.query("SELECT * FROM Company WHERE id={0}".format(_ret[0].company_id))
    company = uTools.dbItem2Dict(_ret[0])
    return company    
 
def getCompany(company_id,format="orign"):
    _ret = icfg.db.query("SELECT * FROM Company WHERE id={0}".format(company_id))
    if len(_ret)==0:
        return None
    company = uTools.dbItem2Dict(_ret[0],format)
    return company
    
def getCompanyByOpenid(openid,format="orign"):
    companys = []
    _ret = icfg.db.query("SELECT * FROM CompanyHasEmployee WHERE openid='{0}' ORDER BY company_id".format(openid))
    for item in _ret:
        companys.append(getCompany(item.company_id,format))
    return companys
    
def getCompanyEmployeeByOpenid(openid,company_id,format="orign"):
    _ret = icfg.db.query("SELECT * FROM CompanyHasEmployee WHERE openid='{0}' AND company_id={1}".format(openid,company_id))
    employee = None
    if len(_ret)>0:
        employee = uTools.dbItem2Dict(_ret[0],format)
    return employee
    
def getBuslineByid(busline_id,format="orign"):
    _ret = icfg.db.query("SELECT * FROM BusLine WHERE id={0}".format(busline_id))
    if len(_ret)==0:
        return None
    busline = uTools.dbItem2Dict(_ret[0],format)
    return busline
    
def orderLineSiteSeq(busline_id):
    endSites = icfg.db.query("""SELECT * FROM LineSites,Sites 
                                      WHERE Sites.id=LineSites.site_id AND 
                                            LineSites.busline_id = {0} AND
                                            LineSites.is_end ="yes"
                                      ORDER BY LineSites.seq
                                      """.format(busline_id))
    if len(endSites)<2:
        return
    fromSite = endSites[0]
    toSite   = endSites[1]
    
    
    _Sites = icfg.db.query("""SELECT * FROM LineSites,Sites 
                                      WHERE Sites.id=LineSites.site_id AND 
                                            LineSites.busline_id = {0} AND
                                            (LineSites.is_end <> "yes" OR LineSites.is_end IS NULL)
                                      ORDER BY LineSites.seq
                                      """.format(busline_id))
    lenSites = len(_Sites)
    
    if fromSite.seq!=1:
        site_id = fromSite.site_id
        icfg.db.update("LineSites",where="busline_id=$busline_id AND site_id=$site_id",vars=locals(),seq=1)
    
    if toSite.seq!=2+lenSites:
        site_id = toSite.site_id
        icfg.db.update("LineSites",where="busline_id=$busline_id AND site_id=$site_id",vars=locals(),seq=2+lenSites)
    
    
    #保存站点信息,#距离排序
    distances ={}
    sites     ={}
    for i in range(lenSites):
        sites[i]    =_Sites[i]
        distances[i]=uTools.getDistance(fromSite.gpsLat,fromSite.gpsLng,sites[i].gpsLat,sites[i].gpsLng)
    
    #站点排序
    dist = sorted(distances.iteritems(), key=lambda d:d[1])
    for i in range(lenSites):
        site_id = sites[dist[i][0]].site_id
        icfg.db.update("LineSites",where="busline_id=$busline_id AND site_id=$site_id",vars=locals(),seq=1+i)
    return
    
    
def getBusesByCompany4pc(company_id):
    _imeis= icfg.db.query("""SELECT imei FROM GroupHasDevice 
                          WHERE devicegroup_id IN ( 
                           SELECT busgroupid FROM BusLine WHERE company_id={0})
                        """.format(company_id))
    imeis = [item.imei for item in _imeis]
    buses = devdb.getDeviceByImei4pc(imeis)
    return buses
    
def getBusesByOpenid4pc(openid):
    _ret = icfg.db.query("""SELECT * FROM CompanyHasEmployee 
                            WHERE openid='{0}' AND privilege<>'invisible'
                         """.format(openid))
    if len(_ret)==0:
        buses = {"total":0,"rows":[]}
    else:
        company_id = _ret[0].company_id
        buses = getBusesByCompany4pc(company_id)
    return buses
    
def getBusesByBusline4pc(busline_id):
    grps =[]
    _ret = icfg.db.query("SELECT * FROM BusLine WHERE id={0}".format(busline_id))
    busline =_ret[0]
    _grps= icfg.db.query("""SELECT *
                        FROM CurrentLocation,GroupHasDevice 
                        WHERE GroupHasDevice.devicegroup_id={0} AND
                              CurrentLocation.imei = GroupHasDevice.imei""".format(busline.busgroupid))
    for grp in _grps:
        grps.append(uTools.dbItem2Dict(grp,format="string"))
    buses = {"total":len(grps),"rows":grps}
    return buses
    
def getBusesByImei4pc(imei):
    grps =[]
    _grps= icfg.db.query("""SELECT *
                        FROM CurrentLocation 
                        WHERE imei = '{0}'
                    """.format(imei))
    for grp in _grps:
        grps.append(uTools.dbItem2Dict(grp,format="string"))
    buses = {"total":len(grps),"rows":grps}
    return buses
    
    
    
def getCompanyRegion(country=None,province=None,city=None,district=None):
    where =[]
    group_region = "province"
    if country!=None:
       where.append("country='{0}'".format(country))
       group_region = "province"
    if province!=None:
       where.append("province='{0}'".format(province))
       group_region = "city"
    if city!=None:
       where.append("city='{0}'".format(city))
       group_region = "district"
    if district!=None:
       where.append("district='{0}'".format(district))
       group_region = None

    #查询下级信息
    group_cond = ("" if group_region==None else "GROUP BY {0}".format(group_region))
    where_sql = ("" if where==[] else "WHERE " +" AND ".join(where))
    regions = []
    if group_region != None:
        _ret = icfg.db.query("""SELECT {0},COUNT(id) AS sum 
                       FROM Company {1} {2}
                    """.format(group_region,where_sql,group_cond))
        for item in _ret:
            regions.append({"id":-1,
                             "text":item[group_region],
                             "iconCls":"icon-tip",
                             "state":"close",
                             "region":group_region,
                             "name":item[group_region],
                             "sum":item["sum"]})
    
    #查询企业信息
    companys = icfg.db.query("""SELECT * FROM Company {0}""".format(where_sql))
    items = []
    locations = []
    no = 0
    for comp in companys:
        items.append(uTools.dbItem2Dict(comp,format="string"))
        
        _buslines = icfg.db.query("SELECT id FROM BusLine WHERE company_id={0}".format(comp.id))
        items[-1]["line_sum"]=len(_buslines)
        for busline in _buslines:
            _lineSites = icfg.db.query("""SELECT * FROM Sites 
                                          WHERE id IN (
                                            SELECT site_id FROM LineSites 
                                            WHERE busline_id={0} AND is_end='yes' AND seq = 1)
                                         """.format(busline.id))
            for site in _lineSites:
                locations.append(uTools.dbItem2Dict(site,format="string"))
                locations[-1]["company"] = items[-1] 

        _ret = icfg.db.query("""SELECT COUNT(imei) AS sum FROM GroupHasDevice 
                           WHERE devicegroup_id IN (SELECT busgroupid FROM BusLine WHERE company_id={0})
                           """.format(comp.id))
        items[-1]["bus_sum"]=_ret[0].sum
        
        no += 1
    #查询公司所在位置信息

    company={"total":len(items),"rows":items}
    ret ={"regions":regions,"company":company,"locations":locations}
    return ret
    
    
    

        
        
    
    