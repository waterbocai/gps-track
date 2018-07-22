# _*_ coding:utf-8 _*_
import web,copy
#from datapool.model.config import *
myDomain = "http://sw.gxsaiwei.com"
#myDomain = web.ctx.homedomain
def getEnvObj():
    myDomain = web.ctx.homedomain.encode("utf-8")
    if web.ctx.env.has_key("RAW_URI"):#gunicorn 
        url = copy.deepcopy(web.ctx.env["RAW_URI"])
    else:#uWsgi
        url = copy.deepcopy(web.ctx.env["REQUEST_URI"])
    obj =dict(qrcode_url =myDomain+"/qrcode/",
              url =(myDomain + url).encode("utf-8"),
              homedomain=myDomain
    )
    return obj
