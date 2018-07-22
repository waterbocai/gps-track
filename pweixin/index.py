# -*- coding: utf-8 -*-
import os
import sys
import web
root = os.path.dirname(__file__)
sys.path.insert(0, root)
#weixin config start
from pweixin.controler.weixin import Weixin
from pweixin.utility.tool import Tool
urls = (
   '/service',"Weixin",
   '/tool'   ,"Tool",
   '/index'  ,"index",
   
)

class index:
    def GET(self, path):
        return "hellohello1231 " + path

#weixin config end

app_weixin = web.application(urls, locals())
#application = sae.create_wsgi_app(app)