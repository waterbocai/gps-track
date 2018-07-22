# -*- coding: utf-8 -*-
import os,sys,json,threading,csv,datetime,logging
reload(sys)
sys.setdefaultencoding( "utf-8" )
curdir = os.path.abspath(__file__)
print("curdir:{0}".format(curdir))
root   = "/".join(curdir.split("/")[0:-3])
print("root:{0}".format(root))
sys.path.append(os.path.join(root, 'site-packages'))
sys.path.append(root)

import product.iconfig      as icfg
import product.mobile.security  as scrt
files_path = root+"/public/files/"

ftp_addr = {"ip":"192.168.56.14","user":"admin","pwd":"gxsaiwei123"}

def initLog(logFile):
    logging.basicConfig(level=logging.DEBUG,
                format='[%(asctime)s][%(filename)s:%(lineno)d][%(levelname)s] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S',
                filename=logFile,
                filemode='a+')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)
    logging.info('logFile:{0}'.format(logFile))
    logging.debug('This is debug message')
    logging.info('This is info message')
    logging.warning('This is warning message')
    
def makedir(dir):
    print("makedir:{0}".format(dir))
    dir_list = dir.split("/")
    for i in range(1,len(dir_list)+1):
        dst_dir = "/".join(dir_list[:i]).strip()
        #print("dst_dir:{0}".format(dst_dir))
        if dst_dir!="" and os.path.exists(dst_dir)==False:
            print("mkdir {0}".format(dst_dir))
            ret = os.popen("mkdir {0}".format(dst_dir))
    return
    
def getFileName(imei,create_at):
    print("getFileName...start")
    busline = linedb.getBuslineByImei(imei)
    company = linedb.getCompanyByBusline(busline["id"])
    bus     = devdb.getDeviceByImei(imei)
    _date   = datetime.datetime.now().strftime("%Y-%m-%d")
    filename= (bus["name"] if bus["name"]!="" else imei)
    dir = files_path+company["company"]+"/"+busline["from_name"]+"-"+busline["to_name"]+"/"+_date
    makedir(dir)
    _filename = dir+"/"+busline["from_name"]+"-"+busline["to_name"]+"_"+filename
    print("getFileName...done:{0}".format(_filename))
    return _filename
    

objScrt = scrt.Security()
objScrt.autoMonitor(type="manual")
    



