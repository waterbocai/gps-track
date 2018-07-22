# -*- coding: utf-8 -*-
import os
import sys
import web

from user import User
from monitor import Monitor
from manager import Manager
from user import User
from seat import Seat
from device import Device
urls = (
   '/monitor','Monitor',
   '/manager','Manager',
   '/user','User',
   '/seat','Seat',
   '/device','Device',
)
#weixin config end

app_pc = web.application(urls, locals())
#application = sae.create_wsgi_app(app)