# -*- coding: utf-8 -*-
import web
import datetime    
from datetime import timedelta
import requests
import json
import re
import utility as uTools
import logstat
from weixinpay import *
from product.mobile.company import Company
import product.iconfig as icfg
import product.model.linedb as linedb
import product.model.devdb as devdb
classModule = {
    "Company":Company,
}

class TradeOrder:
    """订票处理接口""" 
    
    def __init__(self):
        templates_path =__file__.split(".py")[0]
        self.render = web.template.render(templates_path)
        self.devdb  = devdb 
        
        
    def GET(self):
        data = web.input()
        openid       =icfg.objWeixin.getOpenid(data)
        self.env = icfg.getEnvObj()
        act = uTools.get_act(data)
        logstat.logAccessUrl(openid,act) #记录用户访问  
        #print data
        if act =="QUERY"   :
            ret = self.getOrderByid(openid,data)
        elif act == "QRCODE":
            ret = self.getOrderByQrcode(openid,data)
        elif act == "ACCOUNT-LOG":
            ret = self.getAccountLog(openid,data)
        return ret

    def POST(self):
        data = web.input()
        #print data.keys
        openid       =icfg.objWeixin.getOpenid(data)
        self.env = icfg.getEnvObj()
        act=( data.act.upper() if data.has_key('act')  else "")
        if act =="GEN_SEATS_SHARE":
            ret = self.genOrder(openid,"share_seats_view",data)
        elif act =="GEN_SHARE_ORDER2":
            ret = self.genOrder(openid,"share_view",data)
        elif act =="GEN_SHARE_VIEW":
            ret = self.genShareView(openid,data)
        elif act =="GEN_TRANFER_ORDER":
            ret = self.genOrder(openid,"transfer",data)
        elif act =="ACCEPT_SHARE":
            ret = self.acceptShare(openid,data)
        elif act =="UPDATE_MANAGER":
            ret =self.updateManger(openid,data)
        return uTools.formatPostMsg(ret)       
    
        
    '''网页数据传输数据接口形式
     content = {
        "ids":[1,2,3,4],
        "price":{"GT300":250,"T5":280},
        "total_fee":8000,
     }
    '''         
    def getOrderByid(self,openid,data):
        para = data["act"].split("-")
        
        if len(para)>=3:
            out_trade_no = para[2].encode('utf-8')
        else:
            out_trade_no = data.out_trade_no.encode('utf-8')
        #获取订单信息
        _order = icfg.db.query("SELECT * FROM TradeOrder WHERE out_trade_no='{0}'".format(out_trade_no))
        order = _order[0]
       
        #查询该用户下的分享组
        cfgPara =devdb.getDeviceGroup(openid)
        cfgPara["openid"] = openid
        trade = json.loads(order.trade)
        cfgPara["trade"]=trade
        diffImeis = list(set(trade['imeis'])-set(cfgPara['imeis']))
        cfgPara1  = devdb.getDeviceGroupByImei(diffImeis)
        
        #合并元素内容
        cfgPara['imeis'] =cfgPara['imeis']+cfgPara1['imeis']
        cfgPara['items'] =cfgPara['items']+cfgPara1['items']
        
        #生成jdk签名
        jdkSign = icfg.objWeixin.get_jdk_sign(self.env["url"])   
        
        #生成分享链接填充内容
        _user = icfg.db.query("SELECT * FROM Customer WHERE openid ='{0}'".format(openid))
        fixPara={
            "user"        :_user[0].nickname,
            "num"         :len(trade['imeis']),
            "openid"      :openid,
            "out_trade_no":out_trade_no,
            "share_url"   :order.share_url,
         }
        if  web.ctx.env['REQUEST_METHOD']=='GET':
            if order.type== "share_view":#视图共享
                ret = self.render.share_view(json.dumps(cfgPara,ensure_ascii=False),jdkSign,fixPara)
            elif order.type== "sell":#转让
                ret = self.render.share_order(json.dumps(cfgPara,ensure_ascii=False))
        else:
            ret = cfgPara
        return ret


        
    def genShareView(self,openid,data):
        imeis = data.imeis.split(",")
        grpName      = data.grpName
        _ret = icfg.db.query("SELECT * FROM Customer WHERE openid='{0}'".format(openid))
        customer_id = _ret[0].id 
        
        #生成分组视图
        grpId=devdb.updateShareView(openid,imeis,grpName,"视图分组")
        trade = {
            "imeis"    :imeis,
            "grpName"  :grpName,
            "grpId"    :grpId, 
        }        
        out_trade_no = "{0}01{1}".format(datetime.datetime.now().strftime("%Y%m%d%H%M%S"),customer_id)

        _qrcode_url="{0}{1}.jpg".format(self.env["qrcode_url"],out_trade_no)
        #分享给用户的URL
        _share_url = "{0}/m/order?act=QRCODE&out_trade_no={1}".format(web.ctx.homedomain,out_trade_no)
        
        #用户访问的url
        url = "{0}/m/order?act=QUERY-out_trade_no-{1}".format(web.ctx.homedomain,out_trade_no)
        cfgPara={
            "out_trade_no":out_trade_no,
            "url"         :icfg.objWeixin.getAuth2Url(url),
            "url1"        :"/m/order?act=QUERY&strict=y&out_trade_no={0}&openid={1}".format(out_trade_no,openid),
         }
         
        #信息入库
        ret = icfg.db.insert("TradeOrder",out_trade_no=out_trade_no,
                          created_at  =datetime.datetime.now(),
                          type        ='share_view',
                          trade       =json.dumps(trade),
                          qrcode_url  =_qrcode_url,
                          openid      =openid,
                          share_url   =_share_url,
                          weixin_url  =url
        )

        return cfgPara
    
     
    def genShareOrder(self,openid,data):
        out_trade_no = data.out_trade_no
        _order = icfg.db.query("SELECT * FROM TradeOrder WHERE out_trade_no='{0}'".format(out_trade_no))
        order = _order[0]
        share_url = order.share_url
        #往队列中增加一个二维码的生成任务
        file_name =icfg.qrcode_root_dir+"/"+out_trade_no+".jpg"
        icfg.objWeixin.create_temp_qrcode2(order.id,file_name)
        #qrUrl = '{2}/utility/cronday00?act=GEN_TRADE_QRCODE&out_trade_no={0}&order_id={1}&weixinname={3}&qrcode_root_dir={4}'.format(out_trade_no,order.id,icfg.iwaiter_service_url,objWeixin.weixinName,icfg.qrcode_root_dir)
        #requests.get(qrUrl)
        #add_task('QRCodeSeq', qrUrl, 'share_order')
        cfgPara={"result":"success","share_url":share_url}
        return cfgPara
        
    def genOrder(self,openid,type,data):
        out_trade_no =data.out_trade_no
        #二维码地址
        _qrcode_url="{0}{1}.jpg".format(self.env["qrcode_url"],out_trade_no)
        #用户访问的url
        url = "{0}/m/order?act=QUERY-out_trade_no-{1}".format(web.ctx.homedomain,out_trade_no)
        trade = {"imeis":[data.imei]}
        order_id = icfg.db.insert("TradeOrder",out_trade_no=out_trade_no,
                          created_at  =datetime.datetime.now(),
                          type        =type,
                          trade       =json.dumps(trade),
                          qrcode_url  =_qrcode_url,
                          openid      =openid,
                          share_url   =data.share_url,
                          weixin_url  =icfg.objWeixin.getAuth2Url(url),
                          owner       =icfg.objWeixin.weixinName
        )
        #往队列中增加一个二维码的生成任务
        #qrUrl = '{2}/utility/cronday00?act=GEN_TRADE_QRCODE&out_trade_no={0}&order_id={1}&weixinname={3}&qrcode_root_dir={4}'.format(out_trade_no,order_id,icfg.iwaiter_service_url,objWeixin.weixinName,iconfig.qrcode_root_dir)
        #requests.get(qrUrl)
        file_name =icfg.qrcode_root_dir+"/"+out_trade_no+".jpg"
        icfg.objWeixin.create_temp_qrcode2(order_id,file_name)       
        #add_task('QRCodeSeq', qrUrl, 'share_order')
        cfgPara={"result":"success","share_url":data.share_url}
        return cfgPara
                
    def getOrderByQrcode(self,openid,data):
        out_trade_no=data.out_trade_no
        trusting =(data.trusting if data.has_key("trusting")  else "no" )
        #获取订单信息
        _order = icfg.db.query("SELECT * FROM TradeOrder WHERE out_trade_no='{0}' AND owner='{1}'".format(out_trade_no,icfg.objWeixin.weixinName))
        order = _order[0]  
        if openid == order.openid: #共享视图接收者
            ret = self.getOrderByid(data)
        else:
            trade = json.loads(order.trade)
            cfgPara ={}
            cfgPara["items"]       =devdb.getDeviceGroupByImei(trade['imeis'])
            cfgPara["out_trade_no"]=out_trade_no
            cfgPara["openid"]      =openid
            cfgPara["type"]        =order.type   
            _cfgPara = json.dumps(cfgPara,ensure_ascii=False)
            
            fixPara = {"openid":openid,"qrcode_url":order.qrcode_url,"qrcode_trusting":"/static/img/qrcode_trusting.gif","trusting":trusting}
            fixPara["state"] = "finished"
            #if order.type =="share_view":
            #    #确认是否已经完成”确认“
            #    #visible = devdb.customerHasGroup(openid,trade["grpId"])
            #    #fixPara["state"] = ("finished" if visible==True else "finishing")   
            #else:
            #    #确认是否已经完成”确认“
            #    fixPara["state"] = "finished"  
            jdkSign = icfg.objWeixin.get_jdk_sign(self.env["url"]) 
            ret = self.render.share_view4user(_cfgPara,fixPara,jdkSign)                
        return ret

    #tianwangshouhu 统一微信接口
    def procWeixinScene(self,msg):
        openid = msg.fromUser
        pattern = re.compile(r"[^0-9P]*(P?)(\d+)")
        m= pattern.match(msg.eventKey)
        scene_id = int(m.group(2))
        flag = m.group(1)
        if flag=="P":#处理永久scene
            ret = self.procPermScene(openid,scene_id,msg)
        else:
            ret = self.procTempScene(openid,scene_id,msg)
        return ret
    
    def procTempScene(self,openid,scene_id,msg):
        weixinName = icfg.objWeixin.weixinName
        trade_order_id = scene_id
        _ret = icfg.db.query("SELECT type,state,openid FROM  TradeOrder WHERE id={0} AND owner='{1}'".format(trade_order_id,weixinName))
        order = _ret[0]
        if  openid ==order.openid:
            retMsg = msg.reply_text("交易只能在不同用户间进行!")
        elif order.state=="close":#交易已经完成，直接退出
            retMsg = msg.reply_text("交易已经关闭！！")
        else:
            if order.type =="transfer":#在同一个用户间转让，不需要做任何处理
                retMsg = self.procTransferEvent(trade_order_id,openid,msg);
            elif order.type in ["share_seats_view","share_view"]:
                retMsg = self.procShareViewEvent(trade_order_id,openid,msg);
            icfg.db.update("TradeOrder",where="id=$trade_order_id AND owner=$weixinName",vars=locals(),state="close")
        return retMsg  

    def procPermScene(self,openid,scene_id,msg):
        _ret = icfg.db.query("SELECT * FROM  WeixinQRcodeScene WHERE id={0}".format(scene_id))
        if len(_ret)==0:#非法的scene
            retMsg = msg.reply_text("该场景已经不存在")
        else:
            scene = _ret[0]
            retMsg= classModule[scene.tableName]().procWeixinEvent(scene,msg)
        return retMsg        
    
    def getWeixinNews(self,trade_order_id,openid,msg):
        weixinName = icfg.objWeixin.weixinName
        _ret = icfg.db.query("SELECT type,state,openid FROM  TradeOrder WHERE id={0} AND owner='{1}'".format(trade_order_id,icfg.objWeixin.weixinName))
        order = _ret[0]
        if  openid ==order.openid:
            retMsg = msg.reply_text("交易只能在不同用户间进行!")
        elif order.state=="close":#交易已经完成，直接退出
            retMsg = msg.reply_text("交易已经关闭！！")
        else:
            if order.type =="transfer":#在同一个用户间转让，不需要做任何处理
                retMsg = self.procTransferEvent(trade_order_id,openid,msg);
            elif order.type in ["share_seats_view","share_view"]:
                retMsg = self.procShareViewEvent(trade_order_id,openid,msg);
            icfg.db.update("TradeOrder",where="id=$trade_order_id AND owner=$weixinName",vars=locals(),state="close")
        return retMsg 

    def procShareViewEvent2(self,trade_order_id,openid,msg):
        #获取交易信息
        _ret = icfg.db.query("SELECT * FROM  TradeOrder WHERE id={0}".format(trade_order_id))
        order = _ret[0]
        
        devLinks =[] #记录被分享的名字，含链接 
         
        #修改每一个imei的管理分组
        i = 0;
        trade = json.loads(order.trade) 
        for imei in trade["imeis"]:
            #获取该imei所属的公司
            company =linedb.getCompanyByImei(imei)
            company_id = company["id"] 
            #确认该用户是否已经在公司名下
            employee =linedb.getCompanyEmployeeByOpenid
            devLinks.append("{0}/m/bustrack?act=MINE_TRACK&imei={1}&company_id={2}".format(web.ctx.homedomain,imei,company_id)) 
            if employee!=None:#已经分享到了该用户
                icfg.db.update("CompanyHasEmployee",where="company_id=$company_id",vars=locals(),privilege="visible")
                continue
            else:
                #成为员工，权限为visible
                icfg.db.insert("CompanyHasEmployee",company_id=company_id,openid=openid,privilege="visible")      
        
        systemMsg = icfg.objWeixin.iconfig.systemMsg
        systemMsg["data"]["keyword2"]["value"] =datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        systemMsg["data"]["remark"]["value"]="点击查看设备信息"
        systemMsg["touser"] = openid
        
        if i==0:
            systemMsg["url"]=devLinks[0]+"&openid="+openid
            systemMsg["data"]["first"]["value"]   ="设备分享成功提醒"
            systemMsg["data"]["keyword1"]["value"]="重复处理"
            icfg.objWeixin.send_template_msg(systemMsg)
        else:
            #通知接受方用户
            user  = icfg.objWeixin.get_user_info(order.openid)
            systemMsg["url"]=devLinks[0]+"&openid="+openid
            systemMsg["data"]["first"]["value"]="设备分享成功提醒"
            systemMsg["data"]["keyword1"]["value"]="设备分享成功"
            systemMsg["data"]["remark"]["value"]="""分享朋友: {0}
点击查看详情""".format(user['nickname'])
            icfg.objWeixin.send_template_msg(systemMsg)
            
            #通知分享主人
            systemMsg["url"]=devLinks[0]+"&openid="+order.openid
            receiver  = icfg.objWeixin.get_user_info(msg.fromUser)
            systemMsg["data"]["remark"]["value"]="""接收朋友: {0}
点击查看详细""".format(receiver['nickname'])
            systemMsg["touser"] = order.openid
            icfg.objWeixin.send_template_msg(systemMsg)
        return msg.reply_text("留意系统消息")
        
    def procShareViewEvent(self,trade_order_id,openid,msg):
        #获取交易信息
        _ret = icfg.db.query("SELECT * FROM  TradeOrder WHERE id={0}".format(trade_order_id))
        order = _ret[0]
        
        devLinks =[] #记录被分享的名字，含链接 
         
        #修改每一个imei的管理分组
        i = 0;
        trade = json.loads(order.trade) 
        for imei in trade["imeis"]:
            #确认该设备是否已经被分享给了该用户
            _dev = icfg.db.query("""SELECT *,GroupHasDevice.id AS ghdId FROM GroupHasDevice,DeviceGroup
                                        WHERE GroupHasDevice.imei = '{0}' AND 
                                              GroupHasDevice.devicegroup_id =DeviceGroup.id AND 
                                              DeviceGroup.type ='视图分组' AND
                                              DeviceGroup.Customer_openid ='{1}'
                                              """.format(imei,openid))
            company =linedb.getCompanyByImei(imei)
            company_id = company["id"] 
            devLinks.append("{0}/m/bustrack?act=MINE_TRACK&imei={1}&company_id={2}".format(web.ctx.homedomain,imei,company_id))      
            if len(_dev)>0:#已经分享到了该用户，不要再处理
                dev =_dev[0]
                #ghdId =dev.ghdId
                #把可视权限开启
                icfg.db.update("GroupHasDevice",where="id=$dev.ghdId",vars=locals(),privilege="visible")
                continue
            else:
                #选定目标用户视图分组，缺省id最小的组
                _ret = icfg.db.query("""SELECT * FROM DeviceGroup 
                                WHERE Customer_openid='{0}' AND type='视图分组' 
                                ORDER BY id""".format(openid))
                if len(_ret)==0:#从来没有分组，自动创建一个分组
                    grpId = icfg.db.insert("DeviceGroup", type="视图分组",name="分享来的",
                                        Customer_openid=openid,
                                        created_at=datetime.datetime.now())
                else:
                    grpId = _ret[0].id
                icfg.db.insert("GroupHasDevice",imei=imei,devicegroup_id=grpId,
                                           privilege="visible",created_at=datetime.datetime.now())
                _ret = icfg.db.query("SELECT * FROM Device WHERE imei='{0}'".format(imei))
                dev = _ret[0]
                i+=1
                
        
        systemMsg = icfg.objWeixin.iconfig.systemMsg
        systemMsg["data"]["keyword2"]["value"] =datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        systemMsg["data"]["remark"]["value"]="点击查看设备信息"
        systemMsg["touser"] = openid
        
        if i==0:
            systemMsg["url"]=devLinks[0]+"&openid="+openid
            systemMsg["data"]["first"]["value"]   ="设备分享成功提醒"
            systemMsg["data"]["keyword1"]["value"]="重复处理"
            icfg.objWeixin.send_template_msg(systemMsg)
        else:
            #通知接受方用户
            user  = icfg.objWeixin.get_user_info(order.openid)
            systemMsg["url"]=devLinks[0]+"&openid="+openid
            systemMsg["data"]["first"]["value"]="设备分享成功提醒"
            systemMsg["data"]["keyword1"]["value"]="设备分享成功"
            systemMsg["data"]["remark"]["value"]="""分享朋友: {0}
点击查看详情""".format(user['nickname'])
            icfg.objWeixin.send_template_msg(systemMsg)
            
            #通知分享主人
            systemMsg["url"]=devLinks[0]+"&openid="+order.openid
            receiver  = icfg.objWeixin.get_user_info(msg.fromUser)
            systemMsg["data"]["remark"]["value"]="""接收朋友: {0}
点击查看详细""".format(receiver['nickname'])
            systemMsg["touser"] = order.openid
            icfg.objWeixin.send_template_msg(systemMsg)
        return msg.reply_text("留意系统消息")
        
    def procTransferEvent(self,trade_order_id,openid,msg): 
        #选定目标用户管理分组，缺省id最小的组
        _ret = icfg.db.query("""SELECT * FROM DeviceGroup 
                           WHERE Customer_openid='{0}' AND type='管理分组' 
                           ORDER BY id""")
        if len(_ret)==0:#从来没有分组，自动创建一个分组
            grpId = icfg.db.insert("DeviceGroup", type="管理分组",name="未分组",
                                Customer_openid=openid)
        else:
            grpId = _ret[0].id
        #获取交易信息
        _ret = icfg.db.query("SELECT * FROM  TradeOrder WHERE id={0}".format(trade_order_id))
        order = _ret[0]
        
        devLinks =[] #记录被分享的名字，含链接 
        devNames =[] #记录被分享的名字，不含链接
        #修改每一个imei的管理分组
        i = 0;
        trade = json.loads(order.trade) 
        for imei in trade["imeis"]:
            #确认该设备是否已经在该用户名下
            _dev = icfg.db.query("""SELECT *,Device.name  AS devName  
                                        FROM GroupHasDevice,DeviceGroup,Device
                                        WHERE GroupHasDevice.imei = '{0}' AND
                                              Device.imei = GroupHasDevice.imei AND
                                              GroupHasDevice.devicegroup_id =DeviceGroup.id AND 
                                              DeviceGroup.Customer_openid ='{1}' AND
                                              DeviceGroup.type ='管理分组' 
                                              """.format(imei,openid))
            if len(_dev)>0:
                dev =_dev[0]
                devNames.append(dev.devName)
                devLinks.append("{0}/{3}/m/bustrack?act=MINE_TRACK&openid={1}&imei={2}".format(web.ctx.homedomain,openid,imei,dev.name,icfg.objWeixin.weixinName))  
                continue
            
            #完成正常转让过程    
            _dev = icfg.db.query("""SELECT *,GroupHasDevice.id AS ghdid,
                                        DeviceGroup.name AS grpName,
                                        Device.name  AS devName
                                        FROM GroupHasDevice,DeviceGroup,Device
                                        WHERE Device.imei = '{0}' AND 
                                              Device.imei = GroupHasDevice.imei AND
                                              GroupHasDevice.devicegroup_id =DeviceGroup.id AND 
                                              DeviceGroup.type ='管理分组'
                                              """.format(imei))
            dev = _dev[0]
            srcId = dev.ghdid
            icfg.db.update("GroupHasDevice",where="id=$dev.ghdid",vars=locals(),devicegroup_id=grpId)
            devLinks.append("{0}/{3}/m/device?act=about&openid={1}&imei={2}".format(web.ctx.homedomain,openid,imei,dev.devName,icfg.objWeixin.weixinName))
            devNames.append(dev.devName)
            i+=1
        systemMsg = icfg.objWeixin.iconfig.systemMsg
        systemMsg["url"]=devLinks[0]
        systemMsg["data"]["keyword2"]["value"] =datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        systemMsg["touser"] = openid        
        systemMsg["data"]["keyword1"]["value"]="设备转让成功"
        if i==0:
            systemMsg["data"]["first"]["value"]="设备重复转让提醒"
            systemMsg["data"]["remark"]["value"]="\r\n".join(devNames) + "\r\n   已经在您名下。"
            icfg.objWeixin.send_template_msg(systemMsg)
        else:
            systemMsg["data"]["first"]["value"]="设备转让提醒"
            #通知接受方用户
            user  = icfg.objWeixin.get_user_info(order.openid)
            systemMsg["data"]["remark"]["value"]="""收到新设备: {0} 
转出朋友: {1}""".format("\r\n".join(devNames),user['nickname'])
            icfg.objWeixin.send_template_msg(systemMsg)
           
            #通知转出方用户
            systemMsg["url"]=""
            receiver  = icfg.objWeixin.get_user_info(msg.fromUser)
            systemMsg["data"]["remark"]["value"]="""接收朋友: {0}
转出设备: {1}""".format(receiver['nickname']," ".join(devNames))
            systemMsg["touser"] = order.openid
            icfg.objWeixin.send_template_msg(systemMsg)
        return msg.reply_text("留意系统消息")
        
                               
    def acceptShare(self,openid,data):
        out_trade_no  = data.out_trade_no
        #查询订单信息
        _ret = icfg.db.query("SELECT * FROM TradeOrder WHERE out_trade_no={0}".format(out_trade_no))
        order = _ret[0]
        #获取订单内容
        trade = json.loads(order.trade)
        #确认是否已经插入
        _ret = icfg.db.query("""SELECT * FROM CustomerHasDeviceGroup 
                                       WHERE DeviceGroup_id={0} AND
                                       Customer_openid='{1}'""".format(trade["grpId"],openid))
        if len(_ret)==0:
            icfg.db.insert("CustomerHasDeviceGroup",DeviceGroup_id =trade["grpId"],
                                            Customer_openid=openid,
                                            privilege ="visible",
                                            created_at=datetime.datetime.now())
        cfgPara={"result":"success"}
        return cfgPara 
    
    def updateManger(self,openid,data):
        openids = data.openids.split(",")
        paras   = data.paras.split(",")
        grpId   = data.grpId
        for i in range(len(openids)):
            wh ="Customer_openid='{0}' AND DeviceGroup_id={1}".format(openids[i],grpId)
            visible = ("visible" if paras[i]=="on" else "invisible")
            sql = icfg.db.update("CustomerHasDeviceGroup",where=wh,privilege=visible, _test=True)
        cfgPara={"result":"success"}
        return cfgPara   
    
    def genPreSharePara(self,type,openid,imei):
        self.env = icfg.getEnvObj()
            
        #权限确认
        isOwner =linedb.isManager2(openid,imei)
        
        if isOwner:
            #生成分享链接填充内容
            _user = icfg.db.query("SELECT * FROM Customer WHERE openid ='{0}'".format(openid))
            
            #订单号
            timeStamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            out_trade_no = "{0}_{1}_{2}".format(type,imei,timeStamp)
    
            #分享给用户的URL
            _share_url = "{0}/m/order?act=QRCODE&out_trade_no={1}".format(web.ctx.homedomain,out_trade_no)
            
            sharePara={
                "user"        :_user[0].nickname,
                "openid"      :openid,
                "imei"        :imei,
                "out_trade_no":out_trade_no,
                "show_url"    :icfg.urlHome,
                "share_url"   :_share_url,
                "logo_url"    :icfg.logo_url,
            }
        else:
            sharePara={
                "title"       :icfg.advertising_word,
                "share_url"   :icfg.urlHome,
                "show_url"    :icfg.urlHome,
                "logo_url"    :icfg.logo_url,
                "user"        :"",
                "openid"      :openid,
                "imei"        :imei,
                "out_trade_no":"",
            }
        sharePara["isOwner"]   = isOwner
        sharePara["catchword"] = icfg.catchword
        sharePara["advertising_word"] = icfg.advertising_word
        sharePara["homedomain"] = self.env["homedomain"]
        sharePara["logo"]       = icfg.logo_url
        return sharePara

    #查询账户流水日志
    def getAccountLog(self,openid,data):
        logs = devdb.getAccountLog(openid)
        jdkSign = icfg.objWeixin.get_jdk_sign(self.env["url"])
        cfgPara=dict(
            openid=openid,
            logs  =logs, 
        )
        ret = self.render.account_log(cfgPara,jdkSign)
        return ret
        

tradeObj =   TradeOrder()         