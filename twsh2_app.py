# -*- coding: utf-8 -*-
import multiprocessing

bind = "127.0.0.1:7001"
workers = 4
worker_class ="gevent"
threads =2
worker_connections = 4000
#max_requests       =0
#max_requests_jitter=0
timeout            =60
graceful_timeout   =60
keepalive          =2