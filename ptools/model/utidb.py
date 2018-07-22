# -*- coding: utf-8 -*-
import web,datetime,json
import product.iconfig as icfg
import utility as uTools

    
def getLineStatTaskByOpenid(openid,from_time):
    _tasks = icfg.db.query("""SELECT * FROM BackgroudTaskSequence
                              WHERE owner='{0}'     AND 
                                    (create_at>'{1}' OR state<>'complete') AND
                                    name ='line-stat'
                              ORDER BY create_at DESC
                   """.format(openid,from_time))
    tasks = []
    for _task in _tasks:
        param = json.loads(_task.param)
        _dev = icfg.db.query("SELECT * FROM Device WHERE imei ='{0}'".format(param["imei"]))
        dev  = _dev[0]
        task = uTools.dbItem2Dict(_task,format="short_datetime")
        task["bus_no"]=dev.name
        task["imei"]  =dev.imei
        task.pop("param")
        tasks.append(task)
    return tasks

    
    
