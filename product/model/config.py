# -*- coding: utf-8 -*-
import web

db = web.database(
    dbn   ='mysql',
    host  ='localhost',
    port  =3306,
    user  ='root',
    passwd='qiuwen.19',
    db    ='app_gxsaiwei',
    #db    ='iwaitercn_twsh2',
    charset='utf8'
)
owner_db = db
