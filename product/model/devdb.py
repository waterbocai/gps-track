# _*_ coding:utf-8 _*_
import web,json,time,re
import product.iconfig as icfg 
db = icfg.db
import datetime,requests,random
import md5
import utility as uTools

#为了确保id暴露，对id采用md5进行编号
def getMd5ById(id):
    #查询是否存在对应id的md5
    _ret = db.query("SELECT *  FROM Md5ID WHERE id={0}".format(id))
    if len(_ret)>0:
        retMd5 =  _ret[0].md5
    else:
        _retMd5 = bytes(md5.new(str(id)).digest())
        retMd5 ="".join(["%02X" % ord( x ) for x in _retMd5])
        _ret = db.insert("Md5ID",id=id,md5=retMd5)
    return retMd5

#为了确保id暴露，对id采用md5进行编号
def getIdByMd5(md5id):
    #查询是否存在对应id的md5
    _ret = db.query("SELECT *  FROM Md5ID WHERE md5='{0}'".format(md5id))
    id = _ret[0].id
    return id
#获取该用户下的所有分组,以及分组下的设备imei    
def getDeviceGroup(openid,with_formated=True):
    grpImeis = db.query("""SELECT *,name AS grpName,type AS grpType,DeviceGroup.id AS grpId
                            FROM DeviceGroup,GroupHasDevice 
                            WHERE DeviceGroup.id = GroupHasDevice.devicegroup_id AND
                                  Customer_openid='{0}'""".format(openid))
    ret = grpImeis
    #需要格式化
    if with_formated == True:
        ret = genFormDeviceGroup(grpImeis,openid) 
    return ret

#获取该用户下的所有分组,以及分组下的设备imei
def getDeviceSpecial(openid,grpId,with_formated=True):
    if grpId==-1:#获取该用户下的所有设备
        grpImeis = db.query("""SELECT *,name AS grpName,type AS grpType,DeviceGroup.id AS grpId
                            FROM DeviceGroup,GroupHasDevice 
                            WHERE DeviceGroup.Customer_openid='{0}' AND
                                  DeviceGroup.type='管理分组' AND
                                  DeviceGroup.id = GroupHasDevice.devicegroup_id AND
                                  DeviceGroup.id > 0 
                                  """.format(openid))
    else:
        #获取该用户下的所有分组,以及分组下的设备imei
        grpImeis = db.query("""SELECT *,name AS grpName,type AS grpType,DeviceGroup.id AS grpId
                            FROM DeviceGroup,GroupHasDevice 
                            WHERE DeviceGroup.id = GroupHasDevice.devicegroup_id AND
                                  DeviceGroup.id ={0}
                                  """.format(grpId))
    ret = grpImeis
    #需要格式化
    if with_formated == True:
        ret = genFormDeviceGroup(grpImeis,openid,grpId) 
    return ret
    
def getDeviceTypeStat(openid,grptype):
    _mgr = db.query("""SELECT COUNT(*) AS sum 
                            FROM GroupHasDevice,DeviceGroup
                            WHERE DeviceGroup.Customer_openid='{0}' AND
                                  DeviceGroup.type='{1}' AND
                                  DeviceGroup.id= GroupHasDevice.devicegroup_id AND
                                  DeviceGroup.id>0
                    """.format(openid,grptype))
    ret = {"sum":_mgr[0].sum}
    return ret
    
def getGroupStat(openid,grptype):
    if grptype =="朋友分享":
        _mgr = db.query("""SELECT COUNT(*) AS sum 
                            FROM CustomerHasDeviceGroup
                            WHERE Customer_openid='{0}' AND
                                  privilege      ='visible' """.format(openid))
    else:
        _mgr = db.query("""SELECT COUNT(*) AS sum  FROM DeviceGroup
                                                WHERE Customer_openid='{0}' AND 
                                                type='{1}'""".format(openid,grptype))
    ret = {"sum":_mgr[0].sum}
    return ret

def getSpecialGroupStat(openid,grptype):
    if grptype =="朋友分享":
        _mgr = db.query("""SELECT *,DeviceGroup_id AS grpId 
                            FROM CustomerHasDeviceGroup,DeviceGroup
                            WHERE CustomerHasDeviceGroup.Customer_openid ='{0}' AND
                                  CustomerHasDeviceGroup.privilege       ='visible' AND
                                  DeviceGroup.id  =CustomerHasDeviceGroup.DeviceGroup_id""".format(openid))
    else:
        _mgr = db.query("""SELECT *,id AS grpId  FROM DeviceGroup
                                WHERE Customer_openid='{0}' AND 
                                type='{1}'""".format(openid,grptype))
    grps = []
    for mgr in _mgr: #统计每一个分组的设备数
        _ret = db.query("""SELECT COUNT(*) AS sum FROM GroupHasDevice WHERE devicegroup_id={0}""".format(mgr.grpId))
        devs =_ret[0]
        grps.append({"name"  :mgr.name.encode("utf-8"),
                     "id"    :getMd5ById(mgr.id),
                     "sum"   :devs.sum
                    })
    return grps

#查询改名用户名下可以看的设备
def getDeviceViewStat(openid):
    #获取该用户下的所有分组,以及分组下的设备imei
    grpImeis = db.query("""SELECT *,name AS grpName,type AS grpType,DeviceGroup.id AS grpId
                            FROM DeviceGroup,GroupHasDevice 
                            WHERE DeviceGroup.id = GroupHasDevice.devicegroup_id AND
                                  DeviceGroup.type ="管理分组" AND
                                  Customer_openid='{0}'""".format(openid))
    grpShare = db.query("""SELECT *,name AS grpName,type AS grpType,DeviceGroup.id AS grpId
                            FROM DeviceGroup,CustomerHasDeviceGroup,GroupHasDevice
                            WHERE CustomerHasDeviceGroup.Customer_openid='{0}' AND
                                  DeviceGroup.id = CustomerHasDeviceGroup.DeviceGroup_id AND
                                  GroupHasDevice.devicegroup_id = DeviceGroup.id AND
                                  CustomerHasDeviceGroup.privilege='visible' """.format(openid))
    grps =[]
    for grp in grpImeis:
        grps.append(grp)
    for grp in grpShare:
        grps.append(grp)
    
    ret = grps
    #需要格式化
    if with_formated == True:
        ret = genFormDeviceGroup(grpImeis,openid) 
    return ret 

def getDeviceView(openid,with_formated=True):
    #获取该用户下的所有分组,以及分组下的设备imei
    grpImeis = db.query("""SELECT *,name AS grpName,type AS grpType,DeviceGroup.id AS grpId
                            FROM DeviceGroup,GroupHasDevice 
                            WHERE DeviceGroup.id = GroupHasDevice.devicegroup_id AND
                                  DeviceGroup.type ="管理分组" AND
                                  Customer_openid='{0}' AND
                                  DeviceGroup.id > 0 """.format(openid))
    grpShare = db.query("""SELECT *,name AS grpName,type AS grpType,DeviceGroup.id AS grpId
                            FROM DeviceGroup,CustomerHasDeviceGroup,GroupHasDevice
                            WHERE CustomerHasDeviceGroup.Customer_openid='{0}' AND
                                  DeviceGroup.id = CustomerHasDeviceGroup.DeviceGroup_id AND
                                  GroupHasDevice.devicegroup_id = DeviceGroup.id AND
                                  CustomerHasDeviceGroup.privilege='visible' """.format(openid))
    grps =[]
    for grp in grpImeis:
        grps.append(grp)
    for grp in grpShare:
        grps.append(grp)
    
    ret = grps
    #需要格式化
    if with_formated == True:
        ret = genFormDeviceGroup(grps,openid) 
    return ret  

def getDeviceView2(openid,with_formated=True):
    #获取该用户下的所有分组,以及分组下的设备imei
    grpImeis = db.query("""SELECT *,name AS grpName,type AS grpType,DeviceGroup.id AS grpId
                            FROM DeviceGroup,GroupHasDevice 
                            WHERE DeviceGroup.id = GroupHasDevice.devicegroup_id AND
                                  DeviceGroup.type ="管理分组" AND
                                  Customer_openid='{0}' AND
                                  DeviceGroup.id > 0 """.format(openid))
    grpShare = db.query("""SELECT *,DeviceGroup.name AS grpName,DeviceGroup.type AS grpType,DeviceGroup.id AS grpId
                            FROM DeviceGroup,GroupHasDevice 
                            WHERE Customer_openid='{0}' AND DeviceGroup.type ="视图分组" AND
                                  DeviceGroup.id = GroupHasDevice.devicegroup_id AND
                                  GroupHasDevice.privilege = 'visible' AND
                                  DeviceGroup.id > 0 """.format(openid))
    grps =[]
    for grp in grpImeis:
        grps.append(grp)
    for grp in grpShare:
        grps.append(grp)
    
    ret = grps
    #需要格式化
    if with_formated == True:
        ret = genFormDeviceGroup(grps,openid) 
    return ret        

def getDeviceDistrubtorView(openid,with_formated=True):
    if openid=="online-test":#是上线测试查询
        grpImeis = db.query("""SELECT *
                                FROM GroupHasDevice,Device
                                WHERE Device.imei = GroupHasDevice.imei AND 
                                      GroupHasDevice.devicegroup_id = 0                                    
                                ORDER BY  Device.heardbeat_at DESC""".format(openid))
    else:
        _ret = db.query("SELECT * FROM Manager WHERE openid='{0}' AND enRange='all'".format(openid))
        if len(_ret)==0:
            #获取该用户下的所有分组,以及分组下的设备imei
            grpImeis = db.query("""SELECT *
                                FROM Device,Distributor
                                WHERE Device.Distributor_id = Distributor.id AND
                                    Distributor.Customer_openid='{0}'
                                ORDER BY  heardbeat_at DESC  """.format(openid))
        else:
            grpImeis = db.query("""SELECT *
                                FROM Device
                                WHERE Device.Distributor_id >0 
                                ORDER BY  heardbeat_at DESC""".format(openid))
    grps =[]
    for grp in grpImeis:
        grps.append(grp)
    
    ret = grps
    #需要格式化
    if with_formated == True:
        ret = genFormDevice(grps,openid) 
    return ret          

def getDeviceGroupByImei(imeis,with_formated=True):
    grpImeis = []
    #获取该用户下的所有分组,以及分组下的设备imei
    for imei in imeis:
        _imei = db.query("""SELECT *,name AS grpName,type AS grpType,DeviceGroup.id AS grpId
                            FROM DeviceGroup,GroupHasDevice 
                            WHERE DeviceGroup.id = GroupHasDevice.devicegroup_id AND
                                  imei='{0}'""".format(imei))            
        grpImeis.append(_imei[0])
    ret =grpImeis 
    #需要格式化
    if with_formated == True:
        ret = genFormDeviceGroup(grpImeis)         
    return ret

def genFormDevice(grpImeis,openid="",id=-1):
    #该用户名下的设备列表
    retDevs = []
    grpDev  ={}
    grpMgr  ={} 
    imeis   =[]  
    #获取该用户管理分组下的设备
    for imei in grpImeis:
        if (imei.imei in imeis): #过滤重复的设备
            continue
        else: #进入imei队列
            imeis.append(imei.imei)
        #在gps注册初期，存在Device /CurrentLocation 表不一致的情况
        try:
            imeiNo = imeis.index(imei.imei)
        except:
            imeiNo = -1
            
        _devs = db.query("""SELECT * FROM Device,CurrentLocation 
                                 WHERE Device.imei = CurrentLocation.imei AND
                                       Device.imei='{0}'""".format(imei.imei))
        if len(_devs)==1:#位置信息已经上报
            dev = _devs[0]
            #如果是管理分组，计入到设备列表序列中;避免重复，其他分组的设备不计入设备列表
            node = {
                    'name'          :dev.name,
                    'speed'         :dev.speed,
                    'ver'           :dev.ver,
                    'phone'         :dev.phone,
                    'satNum'        :dev.satNum,
                    'expired_at'    :(dev.expired_at.strftime("%Y-%m-%d") if dev.expired_at is not None else "0000-00-00"),
                    'last_time'     :dev.heardbeat_at.strftime("%m-%d %H:%M"),
                    'addr'          :dev.province[0:2]+dev.city,
                    'imei'          :dev.imei.encode("utf-8"),
                }
        else:#位置还没有上报
            _devs = db.query("""SELECT * FROM Device
                                 WHERE imei='{0}'""".format(imei.imei))
            dev = _devs[0]
            node = {
                    'name'          :dev.name,
                    'speed'         :"-1",
                    'satNum'        :"-1",
                    'ver'           :dev.ver,
                    'expired_at'    :("" if dev.expired_at==None else dev.expired_at.strftime("%Y-%m-%d")),
                    'last_time'     :("" if dev.heardbeat_at==None else dev.heardbeat_at.strftime("%m-%d %H:%M")),
                    'addr'          :"未知",
                    'imei'          :dev.imei,
                }
        _ret = db.query("""SELECT * FROM GroupHasDevice,DeviceGroup
                                    WHERE  GroupHasDevice.imei = '{0}'  AND
                                           GroupHasDevice.devicegroup_id = DeviceGroup.id AND 
                                           DeviceGroup.type ='管理分组' AND 
                                           DeviceGroup.id > 0 
                                    """.format(node["imei"]))
        node["owner_openid"] = ""
        if len(_ret)==1:
            node["owner_openid"] =  _ret[0].Customer_openid
        retDevs.append(node)         

        
    if openid!="" and id!=-1:
        #判定该openid是否为owner 还是 customer
        _ret = db.query("""SELECT COUNT(*) AS sum FROM DeviceGroup 
                                WHERE Customer_openid  ='{0}' AND
                                    id = {1}
                                    """.format(openid,id))
        role = ("owner" if _ret[0].sum==1 else "customer")
    else:
        role = "owner"
    
    cfgPara = {
        "items":retDevs,
        "imeis":imeis,
        "role" :role,
    }
    return cfgPara


#格式化设备信息    
def genFormDeviceGroup2(grpImeis,openid="",id=-1):
    #该用户名下的设备列表
    retDevs = []
    grpDev  ={}
    grpMgr  ={} 
    imeis   =[]  
    #获取该用户管理分组下的设备
    for imei in grpImeis:
        _devs = db.query("""SELECT * FROM Device,CurrentLocation 
                                 WHERE Device.imei = CurrentLocation.imei AND
                                       Device.imei='{0}'""".format(imei.imei))
        for dev in _devs:
            #如果是管理分组，计入到设备列表序列中;避免重复，其他分组的设备不计入设备列表
            if (dev.imei not in imeis):
                retDevs.append({
                    'groupName'     :imei.grpName,
                    'name'          :dev.name,
                    'speed'         :dev.speed,
                    'phone'         :dev.phone,
                    'satNum'        :dev.satNum,
                    'expired_at'    :("0000-00-00" if dev.expired_at is None else dev.expired_at.strftime("%Y-%m-%d")),
                    'last_time'     :dev.heardbeat_at.strftime("%m-%d %H:%M"),
                    'addr'          :dev.province[0:2]+dev.city,
                    'arm_type'      :(dev.arm_type if dev.arm_type!="" else "motor"),
                    'imei'          :dev.imei.encode("utf-8"),
                })
                imeis.append(dev.imei)
        #分组对应的设备列表
        if (imei.grpType not in grpDev):
            grpDev[imei.grpType]={}
        if (imei.grpName not in grpDev[imei.grpType]):
            grpDev[imei.grpType][imei.grpName]=[]
        
        #在gps注册初期，存在Device /CurrentLocation 表不一致的情况
        try:
            imeiNo = imeis.index(imei.imei)
        except:
            imeiNo = -1
        if imeiNo >-1:
            #保存该分组所包含的imei在retDevs的序号
            grpDev[imei.grpType][imei.grpName].append(imeiNo)
        
        #分组相关的人员列表
        if (imei.grpType not in grpMgr):
            grpMgr[imei.grpType]={}                
        if (imei.grpName not in grpMgr[imei.grpType]):
            #获取分组对应的owner信息
            grpMgr[imei.grpType][imei.grpName]=getUserByGrpId(imei.grpId)
    if openid!="" and id!=-1:
        #判定该openid是否为owner 还是 customer
        _ret = db.query("""SELECT COUNT(*) AS sum FROM DeviceGroup 
                                WHERE Customer_openid  ='{0}' AND
                                    id = {1}
                                    """.format(openid,id))
        role = ("owner" if _ret[0].sum==1 else "customer")
    else:
        role = "owner"
    
    cfgPara = {
        "grp"  :grpDev,
        "mgr"  :grpMgr,
        "items":retDevs,
        "imeis":imeis,
        "role" :role,
    }
    return cfgPara
    
#格式化设备信息    
def genFormDeviceGroup(grpImeis,openid="",id=-1):
    #该用户名下的设备列表
    retDevs = []
    grpDev  ={}
    grpMgr  ={} 
    imeis   =[]  
    #获取该用户管理分组下的设备
    for imei in grpImeis:
        _devs = db.query("""SELECT * FROM Device 
                                 WHERE imei='{0}'""".format(imei.imei))
        dev = _devs[0]
        _pos = db.query("""SELECT * FROM CurrentLocation 
                                 WHERE imei='{0}'""".format(imei.imei))
        pos = (_pos[0] if len(_pos)==1 else  None)
        
        if (dev.imei not in imeis):
            imeis.append(dev.imei)
            if pos!=None:
            #如果是管理分组，计入到设备列表序列中;避免重复，其他分组的设备不计入设备列表
                retDevs.append({
                    'groupName'     :imei.grpName,
                    'name'          :dev.name,
                    'speed'         :pos.speed,
                    'phone'         :dev.phone,
                    'satNum'        :pos.satNum,
                    'expired_at'    :("0000-00-00" if dev.expired_at is None else dev.expired_at.strftime("%Y-%m-%d")),
                    'last_time'     :dev.heardbeat_at.strftime("%m-%d %H:%M"),
                    'addr'          :pos.province[0:2]+pos.city,
                    'arm_type'      :(dev.arm_type if dev.arm_type!="" else "motor"),
                    'imei'          :dev.imei.encode("utf-8"),
                })
            else:
                retDevs.append({
                    'groupName'     :imei.grpName,
                    'name'          :dev.name,
                    'speed'         :-1,
                    'phone'         :dev.phone,
                    'satNum'        :-1,
                    'expired_at'    :("0000-00-00" if dev.expired_at is None else dev.expired_at.strftime("%Y-%m-%d")),
                    'last_time'     :dev.heardbeat_at.strftime("%m-%d %H:%M"),
                    'addr'          :"未知",
                    'arm_type'      :(dev.arm_type if dev.arm_type!="" else "motor"),
                    'imei'          :dev.imei.encode("utf-8"),
                })
            
    return retDevs
#获取imei对应的用户名字  
def getOwnerByImei(imei):
    _ret = db.query("""SELECT *,DeviceGroup.id AS grpId
                         FROM GroupHasDevice,DeviceGroup,Customer
                         WHERE GroupHasDevice.imei='{0}' AND
                               GroupHasDevice.devicegroup_id = DeviceGroup.id AND
                               DeviceGroup.Customer_openid = Customer.openid
                    """.format(imei))
    if len(_ret)==0:
        owner = ""
    else:
        dev = _ret[0]
        if dev.grpId == 0:#属于库存设备
            owner = ""
        else:
            owner = dev.nickname
    return owner

#获取imei对应的用户名字  
def getOwnerByImei2(imei):
    _ret = db.query("""SELECT *,DeviceGroup.id AS grpId
                         FROM GroupHasDevice,DeviceGroup
                         WHERE GroupHasDevice.imei='{0}' AND
                               GroupHasDevice.devicegroup_id = DeviceGroup.id AND
                               DeviceGroup.type = '管理分组'
                    """.format(imei))
    if len(_ret)==0:
        owner = None
    else:
        dev   = _ret[0]
        _ret = db.query("SELECT * FROM Customer WHERE openid='{0}'".format(dev.Customer_openid))
        if len(_ret)==0:
            owner = None
        else:
            owner   = _ret[0]
    return owner

#根据类型获取用户    
def getVisiblerByImei(imei,type="all"):
    visiblers=[]
    if type=="all":
        _devs = db.query("""SELECT *,DeviceGroup.id AS grpId
                         FROM GroupHasDevice,DeviceGroup
                         WHERE GroupHasDevice.imei='{0}' AND
                               GroupHasDevice.devicegroup_id = DeviceGroup.id 
                    """.format(imei))
    else:
        _devs = db.query("""SELECT *,DeviceGroup.id AS grpId
                         FROM GroupHasDevice,DeviceGroup
                         WHERE GroupHasDevice.imei='{0}' AND
                               GroupHasDevice.devicegroup_id = DeviceGroup.id AND
                               DeviceGroup.type = '{1}' AND  privilege!="invisible"
                    """.format(imei,type))
    visiblers=[]
    for dev in _devs:
        _ret = db.query("SELECT * FROM Customer WHERE openid='{0}'".format(dev.Customer_openid))
        if len(_ret)==1:
            visiblers.append(_ret[0])
    return visiblers
    
def userHasInteligentDevice(openid):
    _ret = db.query("""SELECT *,DeviceGroup.id AS grpId
                         FROM GroupHasDevice,DeviceGroup,Device
                         WHERE DeviceGroup.type = '管理分组'  AND
                               DeviceGroup.Customer_openid='{0}' AND
                               GroupHasDevice.devicegroup_id = DeviceGroup.id AND
                               Device.imei = GroupHasDevice.imei AND 
                               devType IN ("watch")
                    """.format(openid))
    return len(_ret)>0
    

#该分组对关联的用户，不包括所属用户自身
def getUserByGrpId(grpId):
    retUsers = []
    _users = db.query("SELECT * FROM CustomerHasDeviceGroup WHERE DeviceGroup_id={0}".format(grpId))
    for user in _users:
        _wxUser  = db.query("SELECT * FROM Customer WHERE openid='{0}'".format(user.Customer_openid))
        wxUser = _wxUser[0]
        retUsers.append({
            "openid"  :user.Customer_openid,
            "status"  :user.privilege,
            "nickname":wxUser.nickname,
            "phone"   :wxUser.phone,
            "qq"      :wxUser.qq,
            "weixin"  :wxUser.weixin,
            "grpId"   :grpId,
        })
    return retUsers   

def updateShareView(openid,imeis,grpName,type):
    #查询已有分组情况
    _ret = db.query("""SELECT * FROM DeviceGroup 
                         WHERE Customer_openid='{0}' AND 
                               name='{1}' AND 
                               type='{2}'""".format(openid,grpName,type))
    #print "updateShareView({0},{1},{2},{3})".format(openid,imeis,grpName,type)
    #print len(_ret)
    #获取分组id
    if (len(_ret)>0): #已经存在
        grpId = _ret[0].id
    else: #全新生成
        grpId = db.insert("DeviceGroup", 
                            Customer_openid=openid, 
                            name           =grpName,
                            type           =type)
    
    #将IMEI插入对应的分组
    for imei in imeis:
        _ret = db.query("""SELECT * FROM GroupHasDevice 
                                    WHERE devicegroup_id={0} AND
                                          imei='{1}'""".format(grpId,imei))
        #还不存在，新插入
        if len(_ret)==0:
            _ret = db.insert("GroupHasDevice", 
                                devicegroup_id=grpId,
                                imei          =imei)
    return grpId        

#优先选择自己管理的设备
#其次，从朋友分享过来的设备中随机选一个
#都没有，返回""
def getOneDevByOpenid(openid):
    dev = ""
    #优先查询管理分组设备,需要确保当前是有数据的
    _ret = db.query("""SELECT *,DeviceGroup.id AS grpId,Device.name AS devName
                                FROM DeviceGroup,GroupHasDevice,Device,CurrentLocation
                                WHERE DeviceGroup.Customer_openid = '{0}' AND
                                      DeviceGroup.id      = GroupHasDevice.devicegroup_id AND 
                                      GroupHasDevice.imei = Device.imei AND 
                                      Device.imei = CurrentLocation.imei AND                                          
                                      DeviceGroup.type = '管理分组' AND
                                      DeviceGroup.id  > 0""".format(openid))
    sum = len(_ret)
    if sum>0:#该用户管理分组拥有设备，随机取一个
        no = random.randint(0,sum-1)
        dev = _ret[no]
    else:#查询分享设备
        _ret = db.query("""SELECT *,DeviceGroup.id AS grpId,Device.name AS devName 
                        FROM DeviceGroup,GroupHasDevice,Device
                        WHERE Device.imei  = GroupHasDevice.imei AND
                              GroupHasDevice.privilege ="visible" AND
                              GroupHasDevice.devicegroup_id = DeviceGroup.id AND 
                              DeviceGroup.Customer_openid = '{0}' AND
                              DeviceGroup.type    ='视图分组' AND
                              DeviceGroup.id      >0  """.format(openid))            
        sum = len(_ret)
        if sum>0:#该用户拥有的视图分组设备，随机取一个
            no = random.randint(0,sum-1)
            dev = _ret[no]
    if dev != "" :
        ret = dev_ret_format(dev)
    else:
        ret = ""
    return ret        

#获取该用户有权限看的设备
#优先选择具有管理员权限的设备，其次选择朋友分享的设备
def validAuthDev(openid,imei):
    if not inRepository(imei): #非法的设备imei
        return ""
        
    dev = ""
    
    #确认管理权限
    _ret = db.query("""SELECT *,DeviceGroup.id AS grpId,Device.name AS devName 
                        FROM DeviceGroup,GroupHasDevice,Device
                        WHERE Device.imei  = '{0}' AND
                              Device.imei  = GroupHasDevice.imei AND
                              GroupHasDevice.devicegroup_id = DeviceGroup.id AND 
                              DeviceGroup.Customer_openid = '{1}' AND
                              DeviceGroup.type    ='管理分组' AND 
                              DeviceGroup.id      >0 """.format(imei,openid))
    if (len(_ret)>0):
        dev = _ret[0]
    else:
        #确认分享权限
        _ret = db.query("""SELECT *,DeviceGroup.id AS grpId,Device.name AS devName 
                        FROM DeviceGroup,GroupHasDevice,Device
                        WHERE Device.imei  = '{0}' AND
                              Device.imei  = GroupHasDevice.imei AND
                              GroupHasDevice.privilege ="visible" AND
                              GroupHasDevice.devicegroup_id = DeviceGroup.id AND 
                              DeviceGroup.Customer_openid = '{1}' AND
                              DeviceGroup.type    ='视图分组' AND
                              DeviceGroup.id      >0  """.format(imei,openid))
        if(len(_ret)>0):
            dev = _ret[0]
        else:
            #确认管理员权限,管理员可以查看其他人员的设备信息
            _ret = db.query("SELECT * FROM Manager WHERE openid='{0}'".format(openid))                
            if len(_ret)==1:
                _ret = db.query("""SELECT *,DeviceGroup.id AS grpId,Device.name AS devName 
                        FROM DeviceGroup,GroupHasDevice,Device
                        WHERE Device.imei  = '{0}' AND
                              Device.imei  = GroupHasDevice.imei AND
                              GroupHasDevice.devicegroup_id = DeviceGroup.id AND 
                              DeviceGroup.type    ='管理分组' """.format(imei,openid))
                              
                dev = _ret[0]

    if dev != "" :
        ret = dev_ret_format(dev)
    else:
        ret = ""
    return ret
    
def getDevice(imei):
    _ret = db.query("""SELECT *,DeviceGroup.id AS grpId,Device.name AS devName 
                        FROM DeviceGroup,GroupHasDevice,Device
                        WHERE Device.imei  = '{0}' AND
                              Device.imei  = GroupHasDevice.imei AND
                              GroupHasDevice.devicegroup_id = DeviceGroup.id """.format(imei))
    dev = _ret[0]
    ret = dev_ret_format(dev)
    return ret

def getDeviceByImei(imei,format="orign"):
    _ret = db.query("""SELECT * FROM Device WHERE imei='{0}'""".format(imei))
    if len(_ret)==0:
        return None
    dev = uTools.dbItem2Dict(_ret[0],format)
    return dev

def customerHasGroup(openid,grpId):
    ret = False
    #确认关联分组
    _ret = db.query("""SELECT * FROM CustomerHasDeviceGroup
                            WHERE  DeviceGroup_id      = {0} AND 
                                   Customer_openid ='{1}'""".format(grpId,openid))
    
    if (len(_ret)>0):
        ret = True
    else:
        #确认归属权组
        _ret = db.query("""SELECT * FROM DeviceGroup
                                WHERE id={0} AND
                                      Customer_openid ='{0}' """.format(grpId,openid))
        if(len(_ret)>0):
            ret = True
    return ret
    
def getDemoDev(self):
    _ret = db.query("""SELECT *,DeviceGroup.id AS grpId ,Device.name AS devName
                                FROM Device,DeviceGroup,GroupHasDevice,CurrentLocation
                                WHERE GroupHasDevice.devicegroup_id = DeviceGroup.id  AND
                                      GroupHasDevice.imei = Device.imei AND 
                                      Device.imei = CurrentLocation.imei AND    
                                      Device.name LIKE '天网%'""")
    dev = _ret[0]
    ret = dev_ret_format(dev)
    return ret

def dev_ret_format(dev):
    _ret = db.query("SELECT * FROM CurrentLocation WHERE imei='{0}'".format(dev.imei))
    if len(_ret)==1:
        pos = _ret[0]
        alm_low_voltage = pos.alm_low_voltage
        alm_power_off   = pos.alm_power_off
    else:
        alm_low_voltage=0
        alm_power_off  =0
        
    ret = {
        "name"    :dev.devName,
        "type"    :dev.devType,
        'groupid' :dev.grpId,
        'imei'    :dev.imei,
        'phone'   :dev.phone,
        'arm_type':dev.arm_type,
        'heardbeat_at':dev.heardbeat_at.strftime("%Y-%m-%d %H:%M:%S"),
        'monitorState'   :dev.monitorState,
        'alm_low_voltage':alm_low_voltage,
        'alm_power_off'  :alm_power_off,
    }
    return ret

def calcGMileage(imei,before_minites=20):
    deal_time = datetime.datetime.now() - datetime.timedelta(minutes=before_minites)
    deal_time_format = deal_time.strftime("%Y-%m-%d %H:%M:%S")
    #获取待处理队列
    processing_pts=db.query("""SELECT * FROM HistoryTrack WHERE report_at<'{0}' AND gmileage=0 AND imei='{1}' ORDER BY gpsTime""".format(deal_time_format,imei))
    for pt in processing_pts:
        calcGmileage1Point(pt)
        after_pts_before_report = db.query("""SELECT * FROM HistoryTrack WHERE gmileage>0 AND imei='{0}' AND gpsTime>'{1}'  ORDER BY gpsTime """.format(pt.imei,pt.gpsTime.strftime("%Y-%m-%d %H:%M:%S")))
        for after_pt in after_pts_before_report:
            calcGmileage1Point(after_pt)
        #刷新里程数据
    return ""

def calcGmileage1Point(pt):
    last_gmileage = 0.000001
    gdist         = 0
    pt_gpsTime = pt.gpsTime.strftime("%Y-%m-%d %H:%M:%S")
    #获取已经计算好里程的，最近一个历史节点
    _ret = db.query("""SELECT * FROM HistoryTrack WHERE gmileage>0 AND imei='{0}' AND gpsTime<'{1}' ORDER BY gpsTime DESC LIMIT 0,2""".format(pt.imei,pt_gpsTime))
    #查询到指定时间前，未处理的节点信息
    if len(_ret)>0:#不是注册节点
        last_pt = _ret[0]
        gdist=uTools.getDistance(last_pt.gpsLat,last_pt.gpsLng,pt.gpsLat,pt.gpsLng)
        last_gmileage =last_pt.gmileage
        pt_id = pt.id
        db.update("HistoryTrack",where="id=$pt_id",gmileage=last_gmileage+gdist,vars=locals())
    return  
    
def routematrix(pts1):
    dist = [0] #距离列表
    
    #初始化第一个位置
    x = pts1.pop(0)
    dst = [x] #源地址
    src = [] 
    baiduMap = BaiduMap()
    while len(pts1)>0:
        src = [dst[-1]]  #初始化源地址
        dst = []
        #建立源、目的数组
        for i in range(5):
            if len(pts1)>0:
                x = pts1.pop(0)
                if len(src) < 5:
                    src.append(x)
                dst.append(x)
            else:
                break
                
        ret = baiduMap.routematrix(src,dst)
        for i in range(len(dst)):
            if ret[i*(1+len(dst))]["distance"]["value"] is None:
                meter = 0
            else:
                meter = int(ret[i*len(src)]["distance"]["value"])
            #km = float("%0.2f"%(meter/1000.0))
            dist.append(dist[-1]+meter)
    return dist
    
def getRole(openid):
    _mgr = db.query("SELECT * FROM Manager WHERE openid='{0}'".format(openid))
    
    if len(_mgr)>0:
        mgr = _mgr[0]
        cfgPara={"role":"manager","range":mgr.range}
    else:
        cfgPara={"role":"customer","range":""}
    return cfgPara

def getDistributor(openid):
    idCard=""
    _ret = db.query("SELECT * FROM Distributor WHERE Customer_openid='{0}'".format(openid))
    if len(_ret)>0:
        idCard = _ret[0].idCard
    return idCard
    

#全新设备录入，仅限管理员
def addNewDevice(imei,manufacturer,devType,phone="",warehouse_id=1,arm_type='motor'):
    _ret = db.query("SELECT * FROM GroupHasDevice WHERE imei ='{0}'".format(imei))
    ret = -1
    if len(_ret) ==0:#不存在相关组，直接插入
        ret = db.insert("GroupHasDevice",imei         =imei,
                                        devicegroup_id=0,
                                        created_at    =datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        db.insert("Device",imei        = imei,
                           manufacturer=manufacturer,
                           devType     =devType,
                           phone       =phone,
                           heardbeat_at=datetime.datetime.now(),
                           regedit_at  =datetime.datetime.now(),
                           expired_at     =datetime.date.today()+ datetime.timedelta(days=365*10),
                           service_start  =datetime.date.today(),
                           warehouse_id =warehouse_id,
                           arm_type     = arm_type)
    return ret         

def getDeviceStat(openid):        
    #获取该用户下的所有可见的分组信息
    _devs = db.query("""SELECT * FROM Device,DeviceGroup,GroupHasDevice
                                      WHERE DeviceGroup.Customer_openid ='{0}' AND
                                            DeviceGroup.id = GroupHasDevice.devicegroup_id AND
                                            DeviceGroup.type ="管理分组" AND
                                            GroupHasDevice.imei = Device.imei 
                                            
                                      """.format(openid))
    #print "getDeviceStat:{0}".format(len(_devs))
    onStat = {'on':0,'off':0,"paying":0,"expired":0,"payed":0,"sum":0}
    onStat["sum"]=len(_devs)
    for dev in _devs:
        timeDiff = (datetime.datetime.now()-dev.heardbeat_at).seconds
        key = ("off" if (timeDiff>600) else "on")
        onStat[key]+=1
        
        #服务状态
        if dev.expired_at is None:  
            key = "payed"
        else:
            expiredNum = (dev.expired_at-datetime.date.today()).days/30
            if expiredNum>1:
                key = "payed"
            elif expiredNum<0:
                key = "expired"
            else:
                key = "paying"
        onStat[key]+=1
    return onStat
    
def regeditDistributor(**param):
    id = db.insert("Distributor",name   =param["name"],
                            idCard      =param["idCard"], 
                            weixin      =param["weixin"], 
                            qq          =param["qq"], 
                            alipay      =param["alipay"], 
                            phone       =param["phone"], 
                            workAddr    =param["addr"],
                            province    =param["province"],
                            city        =param["city"],
                            district    = param["district"],
                            created_at  =web.SQLLiteral('NOW()'),
                            valid       =param["valid"],
    )
    qrcode_id = getQrcodeLimitUrl("Distributor",id)
    db.update("Distributor",where="id=$id", WeixinQRcodeScene_id=qrcode_id,vars=locals())
    return id

def getQrcodeLimitUrl(tableName,id):
    #生成文件名
    title = "{0}01{1}".format(datetime.datetime.now().strftime("%Y%m%d%H%M%S"),id)
    _qrcode_url="{0}{1}.jpg".format(env["qrcode_url"],title)
    
    #判定scene_id是否合法
    _ret = db.query("SELECT * FROM QrsceneAllocation WHERE tableName = '{0}'".format(tableName))
    scene = _ret[0]
    
    WeixinQRcodeScene_id =-1 #标记失败的id值
    if (id <= scene.end_scene - scene.start_scene):#满足要求，启动二维码制作过程
        #1.将二维码记录WeixinQRcodeScene数据库
        WeixinQRcodeScene_id = db.insert("WeixinQRcodeScene",tableName=tableName,table_id=id,qrcode_url=_qrcode_url)
        
        #2.将二维码生成任务加入并发队列
        qrUrl = '/cron/day00?act=GEN_LIMIT_QRCODE&file_name={0}&scene_id={1}'.format(title,scene.start_scene+id)
        requests.get(qrUrl)
        #add_task('QRCodeSeq', qrUrl, '')
    else:
        raise("{0}：scene_id{1} 大于 最大值：{2} ".format(tableName,scene.start_scene+id,scene.end_scene))
    return WeixinQRcodeScene_id
    
#检测分销商参数的合法性，每次只能检测一项
def validDistributor(**param):
    valid = "valid"
    #1.身份证检测
    if param["checkType"]=="idCard":
        _ret = db.query("SELECT * FROM Distributor WHERE idCard='{0}'".format(param["idCard"]))
        if len(_ret)>0:
            valid="invalid"
            
    #2.QQ号检测
    if param["checkType"]=="qq":        
        _ret = db.query("SELECT * FROM Distributor WHERE qq='{0}' AND idCard!='{1}'".format(param["qq"],param["idCard"]))
        if len(_ret)>0:
            valid="invalid"
    
    #3.微信号检测
    if param["checkType"]=="weixin":        
        _ret = db.query("SELECT * FROM Distributor WHERE weixin='{0}'  AND idCard!='{1}'".format(param["weixin"],param["idCard"]))
        if len(_ret)>0:
            valid="invalid"

    #4.手机号检测
    if param["checkType"]=="phone":        
        _ret = db.query("SELECT * FROM Distributor WHERE phone='{0}'  AND idCard!='{1}'".format(param["phone"],param["idCard"]))
        if len(_ret)>0:
            valid="invalid"      

    #4.支付宝帐号检测
    if param["checkType"]=="alipay":        
        _ret = db.query("SELECT * FROM Distributor WHERE alipay='{0}' AND idCard!='{1}'".format(param["alipay"],param["idCard"]))
        if len(_ret)>0:
            valid="invalid" 
    
    return valid

def saleStatusByMonth(last_months=3,**data):
    if data.has_key("range"):
        _saleDevs =getSaleDistributorDevs(last_months,range=data["range"])
        _wareDevs =getWarehouseDevs(range=data["range"])
    else:
        _saleDevs =getSaleDistributorDevs(last_months,idCard=data["idCard"])
        _wareDevs =getWarehouseDevs(idCard=data["idCard"])
          
    stat    = {}
    devType = []
    
    #统计库存情况
    stat["库存"]={}  
    #print("_wareDevs:{0}".format(len(_wareDevs)))
    for dev in _wareDevs:
        if stat["库存"].has_key(dev.devType) == False:
            stat["库存"][dev.devType] = 0
            if (dev.devType not in devType):
                devType.append(dev.devType)
        stat["库存"][dev.devType] += 1
        
    #统计销售情况             
    sum     =  len(_saleDevs)
    for dev in _saleDevs:
        month = dev.saled_at.strftime("%Y-%m")
        if stat.has_key(month) == False:
            stat[month]={}
        if stat[month].has_key(dev.devType) == False:
            stat[month][dev.devType] = 0
            if (dev.devType not in devType):
                devType.append(dev.devType)
        stat[month][dev.devType] += 1
    if len(stat.keys())>last_months:
        stat.pop(stat.keys()[0])
        

        
    #为了方便在html表格呈现，对不存在的元素处理为0
    for type in devType:
        for month in stat.keys():
            if stat[month].has_key(type)==False:
                stat[month][type] = 0
    return [stat,devType,sum] 

def getSaleDistributorDevs(last_months=3,**data):
    #统计最近6个月的销量
    from_time = (datetime.datetime.today() - datetime.timedelta(days=last_months*31)).strftime("%Y-%m-%d %H:%M:%S")
    if data.has_key("range"):
        if data["range"]==u"所有":
            _devs = db.query("""SELECT * FROM Device,Distributor
                                    WHERE Distributor.id    = Device.Distributor_id AND
                                          Device.saled_at > '{0}'
                                    ORDER BY Device.saled_at 
                    """.format(from_time))
        else:
            _devs = db.query("""SELECT * FROM Device,Distributor
                                    WHERE Distributor.id    = Device.Distributor_id AND
                                          Device.saled_at > '{0}' AND 
                                          Distributor.province like '{1}%'
                                    ORDER BY Device.saled_at 
                    """.format(from_time,data["range"]))
    elif data.has_key("idCard"):
        _devs = db.query("""SELECT * FROM Device,Distributor
                                    WHERE Distributor.idCard='{0}' AND
                                          Distributor.id    = Device.Distributor_id AND
                                          Device.saled_at > '{1}' 
                                    ORDER BY Device.saled_at 
                    """.format(data["idCard"],from_time))
    return _devs

def getWarehouseDevs(**data):
    if data.has_key("idCard"):
        _devs = db.query("""SELECT * FROM Device,Distributor
                                 WHERE Distributor.idCard = '{0}' AND
                                       Device.warehouse_id = Distributor.id AND
                                       Device.Distributor_id = 0                                    
                    """.format(data["idCard"]))
    else:
        if data["range"]=="所有":
            _devs = db.query("""SELECT * FROM Device
                                 WHERE Distributor_id = 0 """)
        else:
            _devs = db.query("""SELECT * FROM Device,Distributor
                                 WHERE Device.Distributor_id = 0 AND
                                       Distributor.id = Device.warehouse_id  AND
                                       Distributor.province like '{0}%'
                                 """.format(data["range"]))
    return _devs
    

def statDistributor(**data):
    if data["range"]=="所有":
        _distributors = db.query("SELECT * FROM Distributor ORDER BY id")
    else:
        _distributors = db.query("SELECT * FROM Distributor WHERE province like '{0}%' ORDER BY id".format(data["range"]))
    stat = []
    for dis in _distributors:
        distributor = {}
        for key in dis.keys():
            if type(dis[key]) is datetime.datetime:
                distributor[key] = dis[key].strftime("%Y-%m-%d %H:%M:%S")
            else:
                distributor[key] = dis[key]
        _sales = db.query("SELECT COUNT(*) AS sum FROM Device WHERE Distributor_id={0}".format(dis.id))
        distributor["sum"] = _sales[0].sum
        #按销量，从小到大进行排序
        #i = 0 
        #for i in  range(len(stat)):
        #    if stat[i]["sum"]>distributor["sum"]:
        #        break
        stat.append(distributor)
    return stat
 
def addDevice2DeviceGroup(imei,devicegroup_id):
    valid = True
    if devicegroup_id==0:#新入库的设备
        _ret = db.query("SELECT COUNT(*) AS sum FROM GroupHasDevice WHERE imei ='{0}'".format(imei))
        if _ret[0].sum>0: #已经有记录，不能再加入到0组
            valid=False
    else:
        #将设备加入缺省分组中
        _ret = db.query("SELECT * FROM GroupHasDevice WHERE imei ='{0}' AND devicegroup_id={1}".format(imei,devicegroup_id))
        if len(_ret)>0:
            valid=False
    if valid == True:
        db.insert("GroupHasDevice",devicegroup_id=devicegroup_id,imei=imei,created_at=datetime.datetime.now())
    return 

def getAccountSummary(openid):
    summary={"sum":0,"change":0}
    _ret = db.query("SELECT * FROM Account WHERE Customer_openid='{0}'".format(openid))
    if len(_ret)==1:
        summary["sum"] = _ret[0].iwaiter_money
    
    _ret = db.query("""SELECT * FROM AccountLog 
                                WHERE Customer_openid='{0}' 
                                ORDER BY created_at DESC
                                LIMIT 0,3""".format(openid))
    if len(_ret)==1:
        summary["change"] = _ret[0].amount
        
    return summary
    
def getAccountLog(openid):
    summary={"sum":0,"logs":[]}
    _ret = db.query("SELECT * FROM Account WHERE Customer_openid='{0}'".format(openid))
    if len(_ret)==1:
        summary["sum"] = _ret[0].iwaiter_money
    
    _logs = db.query("""SELECT * FROM AccountLog 
                                WHERE Customer_openid='{0}' 
                                ORDER BY created_at DESC
                                """.format(openid))
    for log in _logs:
        summary["logs"].append(dict(
            date=log.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            event=log.event,
            amount=log.amount
        ))
    return summary

def getDeviceByGroupid(openid,groupid):
    grps = db.query("""SELECT *,DeviceGroup.name AS grpName,DeviceGroup.type AS grpType,DeviceGroup.id AS grpId
                            FROM DeviceGroup,GroupHasDevice 
                            WHERE DeviceGroup.id={0}  AND
                                  DeviceGroup.id =  GroupHasDevice.devicegroup_id """.format(groupid))
    #需要格式化
    ret = genFormDeviceGroup(grps,openid)
    return ret
    
    
def getBusesByCompany(openid,company_id):
    grps =[]
    _buslines = db.query("SELECT * FROM BusLine WHERE company_id={0}".format(company_id))
    for busline in _buslines:
        _grps= db.query("""SELECT *,DeviceGroup.name AS grpName,DeviceGroup.type AS grpType,DeviceGroup.id AS grpId
                            FROM DeviceGroup,GroupHasDevice 
                            WHERE DeviceGroup.id={0}  AND
                                  DeviceGroup.id =  GroupHasDevice.devicegroup_id """.format(busline.busgroupid))
        for grp in _grps:
            grps.append(grp)
    #需要格式化
    ret = genFormDeviceGroup(grps,openid)
    
    return ret
    

    
#该设备是否在库中有保存    
def inRepository(imei):
    ret = db.query("SELECT * FROM Device WHERE imei ='{0}'".format(imei))
    return len(ret)==1
    
def getDemoDeviceImei():
    _ret = db.query("SELECT imei FROM Device WHERE demo=1")
    if len(_ret)>0:
        imei = _ret[0].imei
    return imei
    
def getDeviceByGroupid4pc(groupid):
    grps = db.query("""SELECT * FROM GroupHasDevice,Device 
                            WHERE GroupHasDevice.devicegroup_id={0}  AND
                                  Device.imei =  GroupHasDevice.imei """.format(groupid))
    ret = {"total":len(grps),"rows":[]}
    #需要格式化
    for grp in grps:
        ret["rows"].append(uTools.dbItem2Dict(grp,format="string"))
    return ret
    
def getBusSeatType():
    _seattypes = db.query('SELECT * FROM SeatType')
    ret =[]
    for seattype in _seattypes:
        ret.append(uTools.dbItem2Dict(seattype))
    return ret
        
def seat_template(imei):
    #获取设备信息
    _ret = db.query("""SELECT * FROM Device WHERE imei='{0}'""".format(imei))
    dev = _ret[0]
    #{"midbus":33,"bed":54,"seat53":60,"seat39":41}
    inTemp = {}
    seats = dev.seat_template.split(";")
    
    for seat in seats:
        inSeat = seat.split(",")
        if len(inSeat) ==2:
            sensor,_name = [item.strip() for item in inSeat]
            if sensor=="":
                continue
        else:
            continue
        try:
            name = int(_name)
        except:
            name = _name
        try:
            sensor = long(sensor)
        except:
            continue
        inTemp[sensor]=name
    return inTemp 
    
def seat2sensor(imei):
    sensor2seat =seat_template(imei)
    _seat2sensor={}
    for key in sensor2seat.keys():
        _seat2sensor[sensor2seat[key]]=key
    return _seat2sensor
    
            
#######################################################################################
#获取该用户名下所有设备分组
def getDeviceGroupByOpenid2(openid,grpType="all"):
    rows=[]
    if grpType in ["管理分组","视图分组"]:
        _ret = db.query("""SELECT * FROM DeviceGroup 
                                WHERE Customer_openid='{0}' AND type='{1}'""".format(openid,grpType))
    else:
        _ret = db.query("""SELECT * FROM DeviceGroup 
                                WHERE Customer_openid='{0}'""".format(openid))
    for dg in _ret:
        ret = db.query("""SELECT count(*) AS sum FROM GroupHasDevice WHERE devicegroup_id={0}""".format(dg.id))
        rows.append({"id":dg.id,"name":dg.name,"num":ret[0].sum})
    groups ={"total":len(rows),"rows":rows}
    return groups
    
def getDeviceByOpenid4pc(openid):
    rows = []
    locations = []
    #名下分组设备查询
    _imeis = db.query("""SELECT DISTINCT imei FROM DeviceGroup,GroupHasDevice
                             WHERE Customer_openid='{0}' AND privilege='visible' """.format(openid))
    imeis = [item.imei for item in _imeis]
    #按分组分享设备查询
    _imeis = db.query("""SELECT DISTINCT imei FROM GroupHasDevice,CustomerHasDeviceGroup
                             WHERE CustomerHasDeviceGroup.Customer_openid='{0}' AND 
                                   CustomerHasDeviceGroup.privilege<>'invisible' AND 
                                   CustomerHasDeviceGroup.DeviceGroup_id=GroupHasDevice.devicegroup_id
                      """.format(openid))
    for item in _imeis:
        if item.imei not in imeis:
            imeis.append(item.imei) 
    if len(imeis) ==0:#是一般用户，获取演示分组
        _imeis = db.query("""SELECT DISTINCT imei
                                FROM DeviceGroup, GroupHasDevice
                                WHERE DeviceGroup.description = 'twsh_demo'
                                      AND GroupHasDevice.devicegroup_id = DeviceGroup.id""") 
        imeis = [item.imei for item in _imeis]

    group = getDeviceByImei4pc(imeis)
    rows      += group["rows"]
    locations += group["locations"]
        
    devices = {"total":len(rows),"rows":rows,"locations":locations}
    return devices 
    
#考虑到手机显示效果，将数据进行精简
def getDeviceByOpenid4m(openid):
    cars = getDeviceByOpenid4pc(openid)
    rows = getDevice4m(cars)
    return rows
    
def getDevice4m(devices):
    rows =[]
    keys =["imei","addr","name","gpsTime","speed","heardbeat_at","qqLat","qqLng","baiduLat","baiduLng","arm_type"]
    for car in devices["locations"]:
        row={}
        for key in keys:
            row[key]=car[key]
        rows.append(row)
    return rows

def getDeviceByGroupid4pc(groupid):
    imei_cond = "SELECT imei FROM GroupHasDevice WHERE devicegroup_id={0}".format(groupid)
    devices = getDeviceByCond(imei_cond)
    
    return devices
    
#考虑到手机显示效果，将数据进行精简
def getDeviceByGroupid4m(groupid):
    cars = getDeviceByGroupid4pc(groupid)
    rows = getDevice4m(cars)
    return rows
    
#考虑到手机显示效果，将数据进行精简
def getCarGroupByOpenid(openid):
    groups = []
    _grps1 = db.query("""SELECT *  FROM DeviceGroup WHERE Customer_openid='{0}'""".format(openid))
    for grp in _grps1:
        groups.append(uTools.dbItem2Dict(grp,format="string"))
        _ret = db.query("SELECT COUNT(*) AS sum FROM GroupHasDevice WHERE devicegroup_id={0} AND privilege<>'invisible'".format(grp.id))
        groups[-1]["sum"] = _ret[0].sum
        
    _grps2 =db.query("""SELECT * FROM DeviceGroup WHERE id IN( 
                              SELECT DeviceGroup_id FROM CustomerHasDeviceGroup 
                              WHERE Customer_openid='{0}' AND privilege <> 'invisible' )""".format(openid))
    for grp in _grps2:
        groups.append(uTools.dbItem2Dict(grp,format="string"))
        _ret = db.query("SELECT COUNT(*) AS sum FROM GroupHasDevice WHERE devicegroup_id={0} ".format(grp.id))
        groups[-1]["sum"] = _ret[0].sum
        groups[-1]["type"] = "运营分组"
    if len(groups)==0:#还没有任何设备，引入演示分组
        _grps3 = db.query("""SELECT *  FROM DeviceGroup  WHERE description = 'twsh_demo'""")
        for grp in _grps3:
            groups.append(uTools.dbItem2Dict(grp,format="string"))
            _ret = db.query("SELECT COUNT(*) AS sum FROM GroupHasDevice WHERE devicegroup_id={0} ".format(grp.id))
            groups[-1]["sum"] = _ret[0].sum
            groups[-1]["type"] = "运营分组"
    return groups
    
def getCarGroupByOpenid4pc(openid):
    rows = getCarGroupByOpenid(openid)
    groups={"rows":rows,"total":len(rows)}
    return groups
    
def getDeviceByImei4pc(imeis):
    imei_cond = json.dumps(imeis)[1:-1]
    #print("imei_cond:{0}".format(imei_cond))
    devices = getDeviceByCond(imei_cond)
    return devices

def getDeviceByCond(imei_cond):
    rows = []
    _grps= db.query("""SELECT * FROM Device
                        WHERE imei IN ({0})
                        """.format(imei_cond))
    today = datetime.date.today()
    now   = datetime.datetime.now() 
    imei_index={}
    for grp in _grps:
        expired_days = ((grp.expired_at - today).days if grp.expired_at!=None else -1)
        rows.append(uTools.dbItem2Dict(grp,format="string"))
        if grp.ip in ["",None]:
            rows[-1]["monitor"]="none"
        else:
            rows[-1]["monitor"]={"camera":"http://"+grp.ip+"/video?act=monitor-camera",
                                 "video":"http://"+grp.ip+"/video?act=monitor-videotape"}     
        rows[-1]["offline_days"] = int((now - grp.heardbeat_at).total_seconds()/(24*3600))
        rows[-1]["speed"]        ="未知"
        rows[-1]["expired_days"] =expired_days
        imei_index[grp.imei]=len(rows)-1
    locations=[]
    _locations= db.query("""SELECT * FROM CurrentLocation
                            WHERE imei IN ({0})
                        """.format(imei_cond))
    for location in _locations:
        locations.append(uTools.dbItem2Dict(location,format="string"))
        dev = rows[imei_index[location.imei]]
        locations[-1]["arm_type"] = dev["arm_type"]
        locations[-1]["name"] = dev["name"]
        locations[-1]["heardbeat_at"] = dev["heardbeat_at"]
        locations[-1]["ip"] = dev["ip"]
        locations[-1]["port"] = dev["port"]
        locations[-1]["monitor"] = dev["monitor"]
        dev["addr"] = location["addr"]
        if dev["offline_days"]==0:
            dev["speed"]= location.speed
    devices = {"total":len(rows),"rows":rows,"locations":locations}
    return devices   
    
#全新设备录入，仅限管理员
def addDevGroup(openid,name,grpType):
    grpid=-1
    #相同用户下不能用同名的分组名称
    ret = db.query("SELECT * FROM DeviceGroup WHERE Customer_openid='{0}' AND name='{1}'".format(openid,name))
    if len(ret)==0:
        grpid = db.insert("DeviceGroup", Customer_openid = openid,
                                 name = name,type=grpType)
    return  grpid 

def deleteDevGroup(grpid):
    ret = False
    #如果有设备，分组不能删除
    _ret = db.query("SELECT COUNT(*) AS sum  FROM GroupHasDevice WHERE devicegroup_id={0}".format(grpid))
    if _ret[0].sum==0:
        ret = db.query("DELETE FROM DeviceGroup WHERE id={0}".format(grpid))
        ret = True
    return  ret 

#将一个分组的设备移入到指定组中    
def moveDevByGroup(src_groupid,tar_groupid):
    _ret =db.query("SELECT * FROM GroupHasDevice WHERE devicegroup_id={0}".format(src_groupid))
    for dev in _ret:
        id = dev.id
        db.update("GroupHasDevice",where="id=$id",vars=locals(),devicegroup_id=tar_groupid)
    return
    
#将设备移入到新的分组中    
def moveDev2Group(imei,tar_groupid):
    db.update("GroupHasDevice",where="imei=$imei",vars=locals(),devicegroup_id=tar_groupid)
    return
    
#就近获取经销商名称    
def getAvailableDistributors(openid):
    #获取用户信息
    _ret = db.query("""SELECT * FROM Customer WHERE openid ='{0}'""".format(openid))
    user = _ret[0]
    distributors =[]
    dist_ids = []
    for addr in ["district","city","province"]:
        #获取县、市、省经销商信息
        if user[addr]=="" or user[addr]==None:
            continue
        _ret = db.query("""SELECT * FROM Distributor WHERE {0} like '%{1}%' ORDER BY id DESC
                """.format(addr,user[addr][:2]))
        for dist in _ret:
            if dist.id not in dist_ids:
                distributors.append({"id":dist.id,
                                     "name":dist.name,
                                     "company":dist.company,
                                     "district":dist.district[:4],
                                     "city":dist.city[:2],
                                     "province":dist.province[:2]})
                dist_ids.append(dist.id)

    if 1 not in dist_ids:
        distributors.append({"id":1,"name":"天网守护","company":"天网守护","district":"龙岗","city":"深圳","province":"广东"})
        dist_ids.append(1)
    for dist in distributors:#没有公司名以用户名称为准
        if dist["company"]=="" or dist["company"]==None:
            dist["company"]=dist["name"]
        dist["out_name"] = "{0}({1} {2} {3})".format(dist["company"],dist["province"],dist["city"],dist["district"])
    return distributors
    
def getGroupUsers(openid,groupid):
    ret ={"total":0,"rows":[]}
    if hasRight4group(openid,groupid):
        _users = db.query("""SELECT * FROM CustomerHasDeviceGroup,Customer 
                                WHERE Customer.openid=CustomerHasDeviceGroup.Customer_openid AND 
                                      DeviceGroup_id={0}""".format(groupid))
        rows =[]
        for user in _users:
            rows.append(uTools.dbItem2Dict(user))
        ret["total"]=len(rows)
        ret["rows"] = rows
    return ret
    
def hasRight4group(openid,groupid):
    has_right = False
    #是owner
    _ret = db.query("SELECT * FROM DeviceGroup WHERE id={0} AND Customer_openid='{1}'".format(groupid,openid))
    if len(_ret)>0:
        has_right = True
    
    #是有管理权限
    _ret = db.query("""SELECT * FROM CustomerHasDeviceGroup 
                                WHERE DeviceGroup_id={0} AND Customer_openid='{1}' AND 
                                      privilege='manager'""".format(groupid,openid))
    if len(_ret)>0:
        has_right = True
    return has_right
    
#判定该用户是否有管理权限    
def isGroupManager(openid,groupid):
    ismgr = False
    _ret = db.query("""SELECT * FROM DeviceGroup 
                                WHERE type='管理分组' AND 
                                      Customer_openid='{0}' AND
                                      id={1}""".format(openid,groupid))
    if len(_ret)==1:#是分组的owner
        ismgr = True 
    else:
        _ret = db.query("""SELECT * FROM CustomerHasDeviceGroup 
                                WHERE Customer_openid='{0}' AND
                                      DeviceGroup_id={1} AND
                                      privilege ='manager'""".format(openid,groupid))
        if len(_ret)==1:
            ismgr = True
    return ismgr
    
def getCustomerDeviceGroupById(chdgid):
    _ret = db.query("SELECT * FROM CustomerHasDeviceGroup WHERE id={0}".format(chdgid))
    if len(_ret)==0:
        customerDeviceGroup= None
    else:
        customerDeviceGroup=_ret[0]
    return customerDeviceGroup
    
def getDeviceGroupById(groupid):
    _ret = db.query("SELECT * FROM DeviceGroup WHERE id={0}".format(groupid))
    grp =uTools.dbItem2Dict(_ret[0],format="string")
    return grp
    
    
def addGroupObserver(groupid,observer_openid):
    _ret = db.query("SELECT * FROM DeviceGroup WHERE id={0}".format(groupid))
    grp = _ret[0]
    #判定是否已经录入
    _ret = db.query("""SELECT * FROM CompanyHasEmployee 
                                WHERE observer_openid='{0}' AND openid='{1}'
                    """.format(observer_openid,grp.Customer_openid))
    if len(_ret)==0:
        _ret = db.query("SELECT * FROM Customer WHERE openid='{0}'".format(observer_openid))
        user = _ret[0]
        db.insert("CompanyHasEmployee",observer_openid=observer_openid,
                                       openid    =grp.Customer_openid,
                                       created_at=datetime.datetime.now(),
                                       remark    =user.nickname)
    return 
    
def getGroupObserver(groupid):
    items =[]
    #查询group owner
    _ret = db.query("SELECT * FROM DeviceGroup WHERE id={0}".format(groupid))
    group =_ret[0]
    #查询权限
    chdgs =db.query("SELECT * FROM CustomerHasDeviceGroup WHERE DeviceGroup_id={0}".format(groupid))
    changeType = {"visible":"可见","invisible":"不可见","manager":"管理者"}
    #查询该owner下的用户备注名称
    for chdg in chdgs:
        items.append(uTools.dbItem2Dict(chdg,format="string"))
        _ret = db.query("""SELECT * FROM CompanyHasEmployee 
                             WHERE openid='{0}' AND observer_openid='{1}'
                 """.format(group.Customer_openid,chdg.Customer_openid))
        items[-1]["remark"] =_ret[0].remark
        _ret = db.query("""SELECT * FROM Customer WHERE openid='{0}'
                 """.format(chdg.Customer_openid))
        items[-1]["wxname"] =_ret[0].nickname
        items[-1]["privilegeName"]=changeType[items[-1]["privilege"]]
    return items
    
    
def getCompanyBusSate():
    rows =[]
    now = datetime.datetime.now()
    _company = db.query("""SELECT * FROM Company ORDER BY id DESC""")
    for comp in _company:
        _busline = db.query("""SELECT * FROM BusLine 
                               WHERE company_id={0}""".format(comp.id))
        
        for busline in _busline:
            busline_name = "{0}-{1}".format(busline.from_name,busline.to_name)
            _buses = db.query("""SELECT * FROM Device WHERE imei IN (
                                 SELECT imei FROM GroupHasDevice 
                       WHERE DeviceGroup_id={0})
                       ORDER BY heardbeat_at DESC""".format(busline.busgroupid))
             
            for bus in _buses:
                offline_hours = (now-bus.heardbeat_at).total_seconds()/3600
                _ret =db.query("SELECT * FROM CurrentLocation WHERE imei='{0}'".format(bus.imei))
                if len(_ret)==0:
                    city="未知"
                    pos =None
                else:
                    pos = _ret[0]
                    city = pos.city
                
                if offline_hours>=0.25:
                    offline_hours = float("%0.2f"%offline_hours)
                else:
                    offline_hours = 0
                rows.append({
                    "company":comp.company[:4],
                    "busline_name":busline_name,
                    "bus_no":bus.name,
                    "heardbeat_at":bus.heardbeat_at.strftime("%m/%d %H:%M"),
                    "offline_hours":offline_hours,
                    "imei":bus.imei,
                    "city":city,
                })
    return rows
    
#下发指令给缓存        
def exeBoxCmd(imei,cmd,args=None):
    _ret = db.query("SELECT id,box_cmd FROM Device WHERE imei='{0}'".format(imei))
    if len(_ret)==0:
        return
    dev = _ret[0]
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    box_cmd=({} if dev.box_cmd in ["",None] else json.loads(dev.box_cmd))
    box_cmd[cmd]={"state":"wait","send_at":now,
                  "camera":{"video0":
                                {"name":"",
                                  "image": {"path": "","exist": "no"},
                                  "video": {"path": "","exist": "no"}
                                }
                            }
                 }
    box_cmd = json.dumps(box_cmd)
    
    db.update("Device",where="id=$dev.id",vars=locals(),box_cmd=box_cmd)      
    return  

def getBoxCmdResult(imei,cmd):  
    _ret = db.query("SELECT id,box_cmd FROM Device WHERE imei='{0}'".format(imei))
    if len(_ret)==0:
        return
    dev     = _ret[0]
    box_cmd=({} if dev.box_cmd in ["",None] else json.loads(dev.box_cmd))
    if box_cmd.has_key(cmd):
        if cmd =="monitor":
            box_cmd[cmd]["camera"]["video0"] = monitorResult(box_cmd[cmd]["camera"]["video0"])
            ret = box_cmd[cmd]
        else:
            ret = box_cmd[cmd]
    else:
        ret = {}
    return ret
    
################################################################################################
#{"monitor": 
#   {"state": "finish", 
#    "camera": {
#          "video0":{
#            "name":"名称",
#            "video":{"path":"http://171.111.153.186:8090/monitor/swrp1605050002/2016-06-07/39-20160607200846.ogg","exist":"no"},
#            "image": {"path":"http://171.111.153.186:8090/monitor/swrp1605050002/2016-06-07/39-20160607200846.ogg","exist":"no"}
#          }
#        }
#    }
#    "send_at": "2016-06-07 20:07:06",
#    "finish_at": "2016-06-07 20:10:57", 
#}   
def monitorResult(monitor_cmd_ret):
    fileType =["video","image"]
    p =re.compile(r'http://[^\/]+\/(.+)$')
    for fType in fileType:
        if monitor_cmd_ret[fType]["exist"]=="no":
            m = p.match(monitor_cmd_ret[fType]["path"])
            if m == None:
                continue
            path = m.group(1)
            args = {"file_path":path,"act":"CHECK-FILE-EXISTS"}
            resp = requests.get(icfg.file_server_api,params=args)
            data = resp.json()
            monitor_cmd_ret[fType]["exist"] = data["ret"]
    return monitor_cmd_ret
    
def isSuperManager(openid):
    _ret = db.query("SELECT * FROM Manager WHERE openid='{0}' AND privilege='manager'".format(openid))
    return len(_ret)>0
    
    
    
def getBoxMonitor(imei):
    ret = db.query("""SELECT ip FROM Device WHERE imei='{0}'""".format(imei))
    if len(ret)==0:
        return {"jpg":"","mp4":""}
    boxIp = ret[0].ip
    args=dict(act='GET-NOW-VIDEO',video='video0')
    video_url = "http://"+boxIp+"/video"
    ret = requests.get(video_url, params = args).json()
    return ret
        


    
