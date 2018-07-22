#----- -*- coding: utf-8 -*-
import web,os,sys,time,datetime,json
import product.iconfig as icfg
import ptools.model.utidb as utidb
import utility as uTools
import logstat
import product.model.linedb as linedb

#应用程序的根路径


class BackgroundTask:
    def __init__(self):
        templates_path =__file__.split(".py")[0]
        self.render = web.template.render(templates_path)
    
    def GET(self):
        data = web.input()
        act = uTools.get_act(data)
        self.env = icfg.getEnvObj()
        self.url =self.env['url']
        openid = icfg.objWeixin.getOpenid(data)
        logstat.logAccessUrl(openid,act) #记录用户访问
        if act == 'SHOW-LINE-STAT-TASK':
            ret = self.showLineStatTask(openid,data)
        else:
            ret = web.seeother(urlHome)
        return ret
     
    def POST(self):
        data = web.input()
        if not data.has_key('act'):
            return
        act = data.act.upper()
        openid =icfg.objWeixin.getOpenid(data)  
        if act == 'ADD-LINE-STAT-TASK':
            ret = self.addLineStatTask(openid,data)
        else:
            ret = "指令错误"
        return ret

    #添加后台任务    
    def addLineStatTask(self,openid,data):
        from_time = data.from_time
        to_time   = data.to_time
        imeis     = data.imeis.split(",")
        busline_id= data.busline_id
        param ={"from_time":from_time,"to_time":to_time,"busline_id":busline_id}
        for imei in imeis:
            param["imei"] = imei
            icfg.db.insert("BackgroudTaskSequence",
                               name      ="line-stat",
                               create_at = datetime.datetime.now(),
                               owner     = openid,
                               param     = json.dumps(param),
                               state     ="waiting",
                               )
        cfgPara={"result":"succuss"}
        ret = uTools.formatPostMsg(cfgPara)
        return ret
        
        
    def showLineStatTask(self,openid,data):
        busline_id = data.busline_id
        company_id = data.company_id
        from_time = datetime.datetime.now() - datetime.timedelta(hours=24)

        tasks   = utidb.getLineStatTaskByOpenid(openid,from_time)

        jdkSign = icfg.objWeixin.get_jdk_sign(self.url)
        fixPara = icfg.getFixPara(openid,busline_id=busline_id,
                                         company_id=company_id)
        
        cfgPara={"openid"    :openid,
                 "busline_id":busline_id,
                 "company_id":company_id,
                 "tasks"     :tasks}
        _cfgPara = json.dumps(cfgPara,ensure_ascii=False)
        ret = self.render.show_task(_cfgPara,jdkSign,fixPara)
        return ret
        
        
        
        
    
 