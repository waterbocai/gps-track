import os
import sys
import web

from product.mobile.manager import Manager
from product.mobile.busmap import BusTrack
from product.mobile.device import Device
from product.mobile.seat_stat import SeatStat
from product.mobile.tradeorder import TradeOrder
from product.mobile.company import Company
import LogStat
urls = (
   '/manager','Manager',
   '/bustrack','BusTrack',
   '/device','Device',
   '/seat_stat',"SeatStat",
   '/order','TradeOrder',
   '/company','Company',
   '/logstat'  ,'LogStat'
)
#weixin config end

app_gxsaiwei2 = web.application(urls, locals())
#application = sae.create_wsgi_app(app)