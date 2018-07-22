#----- -*- coding: utf-8 -*-
import os,sys,web

from ptools.backgroundtask import BackgroundTask

urls = (
   '/bktask','BackgroundTask',
)

app_ptool = web.application(urls, locals())
#application = sae.create_wsgi_app(app)