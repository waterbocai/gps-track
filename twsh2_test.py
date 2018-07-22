# -*- coding: utf-8 -*-
import multiprocessing

bind = "127.0.0.1:8002"
workers = 1
worker_class ="gevent"
threads = 1
worker_connections = 4000
#max_requests       =0
#max_requests_jitter=0
timeout            =60
graceful_timeout   =60
keepalive          =2
loglevel = 'info'