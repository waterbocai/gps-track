# -*- coding: utf-8 -*-
import os
import sys
import web
root = os.path.dirname(__file__)
sys.path.append(os.path.join(root, 'site-packages'))
sys.path.append(root)

from product.index  import app_mobile
from ptools.index   import app_ptool
from pweixin.index   import app_weixin
from product.pc.index  import app_pc
from logstat        import LogStat

urls = (
   '/weixin'  ,app_weixin,
   '/m'       ,app_mobile,
   '/ptool'   ,app_ptool,
   '/logstat' ,'LogStat',    
   '/pc'      ,app_pc,
   '/'        ,"index",
)

class index:
    def GET(self):
        return web.seeother("/pc/user?act=login")

#weixin config end

application = web.application(urls, locals()).wsgifunc()
#application = sae.create_wsgi_app(app)