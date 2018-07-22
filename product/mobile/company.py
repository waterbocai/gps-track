# -*- coding: utf-8 -*-
import web
import time
import datetime
import calendar
import product.model.devdb as devdb
import utility as uTools
import logstat
import json
import re
import product.iconfig as icfg
import product.model.linedb as linedb


class  Company:
    def __init__(self):
        templates_path =__file__.split(".py")[0]
        self.render = web.template.render(templates_path)
        
    def GET(self):
        data = web.input()
        self.env = icfg.getEnvObj()
        act = uTools.get_act(data)
        openid = icfg.objWeixin.getOpenid(data)
        logstat.logAccessUrl(openid,act) #记录用户访问
        ret = ""
        if act == "HOME" :
            ret = self.home_metro(openid,data)
        elif act == "MANAGER-HOME" :
            ret = self.manager_home_metro(openid,data)
        elif act == "COMPANY-HOME" :
            ret = self.company_home_metro(openid,data)
            #ret = self.home(data)
        elif act =="REGEDIT-COMPANY":
            ret =self.regeditCompany(openid,data)
        elif act =="CERT-COMPANY":
            ret = self.certCompany(openid,data)
        elif act =="UPDATE-COMPANY":
            ret = self.updateCompanyGet(openid,data)
        elif act =="SALE-STATUS-COMPANY":
            ret = self.saleStatusCompany(openid,data)
        elif act =="MANAGE-COMPANY":
            ret = self.manageCompany(openid,data)
        return ret
    
    def POST(self):
        data = web.input()
        self.env = icfg.getEnvObj()
        act = data.act.upper()
        openid = icfg.objWeixin.getOpenid(data)
        if act =="REGEDIT-COMPANY":
            ret =self.regeditCompany(openid,data)
        elif act =="VALID-COMPANY":
            ret =self.validCompany(openid,data)
        elif act =="COMPANY-CONFIRM":
            ret =self.companyConfirm(openid,data.company_id)
        elif act =="UPDATE-COMPANY":
            ret =self.updateCompany(openid,data)
        elif act =="SIGN-COMPANY":
            ret =self.signCompany(openid,data)
        return ret
        
    def procWeixinEvent(self,scene,msg):
        self.env = icfg.getEnvObj()
        company_id = scene.table_id
        #该comany_id是否有效
        _ret = icfg.db.query("SELECT * FROM Company WHERE id={0}".format(company_id))
        if len(_ret)==0:
            retMsg = msg.reply_text('非法的二维码！')
        else:
            company = _ret[0]
            #判定是否已经完成确认
            if company.owner_openid==None and company.regedit_openid!=msg.fromUser:#完成确认
                retMsg = self.companyConfirmFromScan(company,msg)
            else:
                retMsg = self.addEmployee2Company(company,msg)
        return retMsg
    
    def addEmployee2Company(self,company,msg):
        _ret = icfg.db.query("""SELECT * FROM CompanyHasEmployee 
                                  WHERE openid='{0}' AND 
                                        company_id={1}""".format(msg.fromUser,company.id))
        if len(_ret)==0:#是新员工
            icfg.db.insert("CompanyHasEmployee",company_id=company.id,
                                             openid    =msg.fromUser,
                                             create_at =datetime.datetime.now(),
                                             privilege ="manager")
            retMsg = msg.reply_text('你已经成为:{0} 运营管理员'.format(company.company))
        else:#已经加入了该公司
            retMsg = msg.reply_text('欢迎光临:{0} '.format(company.company))
        return retMsg
    
    def companyConfirm(self,openid,company_id):
        icfg.db.update("Company",where="id=$company_id",
                               confirmed_at =web.SQLLiteral('NOW()'),
                               owner_openid = openid,
                               vars         =locals(),
                               valid        ="有效")
        cfgPara ={'openid' :openid}
        cfgPara["result"]="success"
        ret =uTools.formatPostMsg(cfgPara)
        return ret

    def companyConfirmFromScan(self,company,msg):
        openid = msg.fromUser
        #首先完成确认
        company_id = company.id
        icfg.db.update("Company",where="id=$company_id",
                               confirmed_at =web.SQLLiteral('NOW()'),
                               owner_openid = openid,
                               vars         =locals(),
                               valid        ="有效")
        icfg.db.insert("CompanyHasEmployee",company_id=company_id,
                                                     openid    =msg.fromUser,
                                                     create_at =datetime.datetime.now(),
                                                     privilege ="manager")
        #发送消息给录单员
        #通知接受方用户
        employee  = icfg.objWeixin.get_user_info(company.regedit_openid)
        user      = icfg.objWeixin.get_user_info(openid)
        systemMsg = icfg.objWeixin.iconfig.systemMsg
        systemMsg["url"]="{0}/m/company?act=cert-company&company_id={1}".format(self.env["homedomain"],company_id)
        systemMsg["data"]["first"]["value"]   ="运输公司确认完成通知"
        systemMsg["data"]["keyword1"]["value"]="确认完成"
        systemMsg["data"]["remark"]["value"]  ="""确认用户: {0}
录单员工:{1}
点击查看详情""".format(user['nickname'],employee['nickname'])
        systemMsg["data"]["keyword2"]["value"] =datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        systemMsg["touser"] = company.regedit_openid
        
        icfg.objWeixin.send_template_msg(systemMsg)
        #记录已发送的用户
        sended_openids=[company.regedit_openid]
        mgrs = icfg.objWeixin.getManager()
        for mgr in mgrs:
            if mgr.privilege!="invisible" and (mgr.openid not in sended_openids):
                systemMsg["touser"] = mgr.openid
                icfg.objWeixin.send_template_msg(systemMsg)
        #返回信息给扫码的用户
        serviceCenter = "https://open.weixin.qq.com/connect/oauth2/authorize?appid={0}&redirect_uri={1}/m/manager?act=home&response_type=code&scope=snsapi_base&state=123#wechat_redirect".format(icfg.objWeixin.appid,self.env["homedomain"])
        retMsg = msg.reply_text("恭喜你成为赛微公司VIP用户，进入<a href='{0}'>服务中心</a>".format(serviceCenter))
        return retMsg
        
    def home(self,openid,data):
        
        #简要统计分组信息
        grpMgrStat  = devdb.getGroupStat(openid,"管理分组")
        grpViewStat = devdb.getGroupStat(openid,"视图分组")
        grpShareStat = devdb.getGroupStat(openid,"朋友分享")
        grpStat={"mgr":grpMgrStat["sum"],"view":grpViewStat["sum"],"share":grpShareStat["sum"]}
        #print grpStat
        #devStat=devdb.getDeviceStat(openid)
        
        user = icfg.objWeixin.get_user_info(openid)
        jdkSign = icfg.objWeixin.get_jdk_sign(self.env["url"])
        mgr = devdb.getRole(openid)
            
        idCard=config.db.getCompany(openid)
         
        
        #customerType =("older" if grpStat["mgr"]>0 else "newer")
        cfgPara ={
            'openid'      :openid,
            'user'        :user,
            'grpStat'     :grpStat,
            #'role'        :mgr["role"],
            #'range'       :mgr["range"],
            #'customerType':customerType, 
            'idCard'      :idCard,
            'grid'        :"abc" 
        }
        ret = self.render.home(cfgPara,jdkSign)
        return ret

    def manager_home_metro(self,openid,data):
        user = icfg.objWeixin.get_user_info(openid)
        jdkSign = icfg.objWeixin.get_jdk_sign(self.env["url"])
        
        mgr = devdb.getRole(openid)
        fixPara = icfg.getFixPara(openid)       
        cfgPara ={
            'openid'      :openid,
            'user'        :user,
            'role'        :mgr["role"],
            'appid'       :icfg.objWeixin.appid,
            'homedomain'  :self.env["homedomain"],
            'range'       :mgr["range"],
            'grid'        :"abc" 
        }
        ret = self.render.manager_home(cfgPara,jdkSign,fixPara)
        return ret
        
    def company_home_metro(self,openid,data):
        user = icfg.objWeixin.get_user_info2(openid,format="string")
        jdkSign = icfg.objWeixin.get_jdk_sign(self.env["url"])
        idCard=devdb.getCompany(openid)
        cfgPara ={
            'openid'      :openid,
            'user'        :user,
            'idCard'      :idCard,
            'grid'        :"abc" 
        }
        fixPara = icfg.getFixPara(openid)
        ret = self.render.company_home(cfgPara,jdkSign,fixPara)
        return ret
    
    def home_metro(self,openid,data):
        grpMgrStat  = devdb.getDeviceTypeStat(openid,"管理分组")
        grpStat={"mgr":grpMgrStat["sum"]}
        
        user = icfg.objWeixin.get_user_info(openid)
        jdkSign = icfg.objWeixin.get_jdk_sign(self.env["url"])
        
        mgr = devdb.getRole(openid)
        idCard=devdb.getcompany(openid)
        customerType =("older" if grpStat["mgr"]>0 else "newer")
        cfgPara ={
            'openid'      :openid,
            'user'        :user,
            'grpStat'     :grpStat,
            'role'        :mgr["role"],
            'range'       :mgr["range"],
            'customerType':customerType, 
            'idCard'      :idCard,
            'grid'        :"abc" 
        }
        fixPara = icfg.getFixPara(openid)
        ret = self.render.home(cfgPara,jdkSign,fixPara)
        return ret
        
    def validCompany(self,openid,data):
        type   = data.type
        value  = data.value
        idCard = data.idCard
        #身份证检测
        if type == "idCard":
            valid = devdb.validcompany(idCard=value,checkType=type)
        #手机号检测
        if type =="phone":
            valid = devdb.validcompany(idCard=idCard,phone=value,checkType=type)
        #QQ检测
        if type =="qq":
             valid = devdb.validcompany(idCard=idCard,qq=value,checkType=type)
        #weixin检测
        if type =="weixin":
            valid = devdb.validcompany(idCard=idCard,weixin=value,checkType=type)
        #支付宝检测
        if type =="alipay":
           valid = devdb.validcompany(idCard=idCard,alipay=value,checkType=type)
        
        cfgPara = {"result":valid}
        ret = uTools.formatPostMsg(cfgPara)
        return ret
    
    def regeditCompany(self,openid,data):
        cfgPara ={'openid'      :openid}
        if  web.ctx.method=='GET':
            cfgPara["actionEN"]="regedit"
            cfgPara["actionCH"]="注册"
            cfgPara["homedomain"]=self.env["homedomain"]
            cfgPara["appid"]     = icfg.objWeixin.appid
            jdkSign = icfg.objWeixin.get_jdk_sign(self.env["url"])
            fixPara = icfg.getFixPara(openid)
            ret = self.render.regedit_company(cfgPara,jdkSign,fixPara)
        else:
            id = linedb.regeditCompany(name=data.name,
                qq      =data.qq,     
                weixin  =data.weixin,
                #alipay  =data.alipay,
                #idCard  =data.idCard,
                phone   =data.phone,
                district=data.district,
                province=data.province,
                city    =data.city,
                addr    =data.address,
                company =data.company,
                regedit_openid = data.regedit_openid,
                valid   ="待确认",
            )
            cfgPara["result"]=("success" if id>=0 else "fail")
            cfgPara["company_id"] = id
            ret =uTools.formatPostMsg(cfgPara)
        return ret

    def certCompany(self,openid,data):
        if data.has_key("act2"):#来自auth的请求
            company_id = data.act2.split("_")[2]
        else:
            company_id = data.company_id
        _distRret = icfg.db.query("""SELECT *,Company.id AS company_id FROM Company, WeixinQRcodeScene
                                         WHERE Company.id='{0}' AND
                                               Company.WeixinQRcodeScene_id = WeixinQRcodeScene.id
                                         """.format(company_id))
        if (len(_distRret)>0):
            company = _distRret[0]
        else:
            return web.seeother(icfg.urlHome)
        cfgPara ={'openid'      :openid,
                  'company'     :company,
                  'homedomain'  :self.env["homedomain"],
                  "appid"       :icfg.objWeixin.appid
                 }
        jdkSign = icfg.objWeixin.get_jdk_sign(self.env["url"])
        fixPara = icfg.getFixPara(openid)
        ret = self.render.cert_company(cfgPara,jdkSign,fixPara)
        return ret
      

        
    def updateCompany(self,openid,data):
        result = icfg.db.update("Company",where="id=$company_id",vars={"company_id":data.company_id},
                                            name    =data.name,
                                            company =data.company,
                                            qq      =data.qq,     
                                            weixin  =data.weixin,
                                            #alipay  =data.alipay,
                                            #idCard  =data.idCard,
                                            phone   =data.phone,
                                            district=data.district,
                                            province=data.province,
                                            city    =data.city,
                                            workAddr=data.address,
                                            #company =data.company,
                                        )
        cfgPara={"openid":openid,"result":"success"}
        ret =uTools.formatPostMsg(cfgPara)
        return ret
        
    def updateCompanyGet(self,openid,data):
        if data.has_key("act2"):#来自auth的请求
            idCard = data.act2.split("_")[2]
        else:
            idCard = data.idCard
        cfgPara ={'openid' :openid}
        jdkSign = icfg.objWeixin.get_jdk_sign(self.env["url"])
        cfgPara["actionEN"]="update"
        cfgPara["actionCH"]="更新"
        #获取该用户的信息
        _ret = icfg.db.query("SELECT * FROM Company WHERE idCard='{0}'".format(idCard))
        company = _ret[0]
        _company ={}
        for key in company:
            if type(company[key]) is datetime.datetime:
                value = company[key].strftime("%Y-%m-%d %H:%M:%S")
            else:
                value = company[key]
            _company[key]=value
        _company =  json.dumps(_company,ensure_ascii=False)
        #fixPara = icfg.getFixPara(openid)
        ret = self.render.regedit_company(cfgPara,jdkSign,_company)
        return ret    
    
    def signCompany(self,openid,data):
        imei       = data.imei
        weixin_url = data.weixin_url
        
        cfgPara ={}
        #获取分销商信息
        _ret = icfg.db.query("""SELECT * FROM WeixinQRcodeScene,company 
                                    WHERE url='{0}' AND 
                                          WeixinQRcodeScene.tableName='company' AND 
                                          company.id = WeixinQRcodeScene.table_id
                                          """.format(weixin_url))
        company= _ret[0]
        if company.valid =="invalid":
            cfgPara["result"]="company_invalid" 
        else:
            #确认该设备没有被分销商绑定过
            _dev = db.query("SELECT * FROM Device WHERE imei ='{0}'".format(imei))
            if len(_dev)==0:
                cfgPara["result"]="imei_invalid"
            else:
                dev = _dev[0]
                
                if (dev.saled_at is None):
                    t = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    #db.update("Device",where="imei=$ime",company_id=company_id,
                    #                                    saled_at=t)
                    cfgPara["result"]="success"
                    cfgPara["saled_at"] = t
                    cfgPara["company_name"] = company.name
                    cfgPara["company_id"] = company.id
                else:
                    cfgPara["result"]="already_binded"
                    cfgPara["saled_at"] = dev.saled_at.strftime("%Y-%m-%d %H:%M:%S")
                    cfgPara["company_name"] = company.name
        ret =uTools.formatPostMsg(cfgPara)
        return ret
            
    def saleStatusCompany(self,openid,data):
        #jdkSign = icfg.objWeixin.get_jdk_sign(self.env["url"])
        #获取用户角色，判定是否为管理层
        #mgr = devdb.getRole(openid)
        
        #确认查询
        
        cfgPara ={'openid' :openid}
        if data.has_key("range"):#管理者查询
            ret = devdb.saleStatusByMonth(3,range=data.range)
            idCard = "manager"
        else:
            if data.has_key("idCard") == False: 
                _ret = db.query("SELECT * FROM company WHERE Customer_openid='{0}'".format(openid))
                company = _ret[0]
                idCard = company.idCard
            else:
                idCard = data.idCard
            ret = devdb.saleStatusByMonth(3,idCard=idCard)
        cfgPara["idCard"]  = idCard   
        cfgPara["stat"]    = ret[0]
        cfgPara["devType"] = ret[1]
        cfgPara["sum"]     = ret[2]
        ret = self.render.sale_status_company(cfgPara)
        return ret

    def manageCompany(self,openid,data):
        #jdkSign = icfg.objWeixin.get_jdk_sign(self.env["url"])
        cfgPara ={'openid' :openid,"appid":icfg.objWeixin.appid,"homedomain":self.env["homedomain"]}
        
        stat = linedb.statCompany(self.env,openid)
        cfgPara['stat']=stat
        ret = self.render.manage_company(cfgPara)
        return ret    
