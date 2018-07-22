# _*_ coding:utf-8 _*_
import sys
weixinName         ="gxsaiwei"
token              ="gxsaiwei"
appid              ="wxd1ac6e0c829fd839"
secret             ="cc2dfe46a653ab7169d678b2685e1e19"
open_appid         ="wxa9088619dd87dfc2"
open_secrept        ="2f6201eaf2862e5c00e3a43838a1f578"
open_redirect_uri  ="http://sw.gxsaiwei.com/pc/monitor?act=CAR-ONLINE"

orign_id           ="gh_dd34db268edc"
weixinpay_partnerid=-1
weixinpay_account  =""
myDomain           ="http://sw.gxsaiwei.com"
urlLogin           ="http://sw.gxsaiwei.com/pc/user?act=login"

firsteye  =[{
        "title"       :"赛微——智慧客运探路人",
        "description" :'赛微——赛出新颖 微动未来',
        "picurl"      : "http://sw.gxsaiwei.com/static/img/gxsaiwei/logo.jpg",
        "url"         : "http://eqxiu.com/s/02L4LMtk"
    }]


menu= '''
{"button":[
    {"name":"服务中心","type":"view","url":"https://open.weixin.qq.com/connect/oauth2/authorize?appid=wxd1ac6e0c829fd839&redirect_uri=__MYDOMAIN__/m/manager?act=home&response_type=code&scope=snsapi_base&state=123#wechat_redirect"},
    {"name":"演示大厅","type":"view","url":"https://open.weixin.qq.com/connect/oauth2/authorize?appid=wxd1ac6e0c829fd839&redirect_uri=__MYDOMAIN__/m/device?act=seat-status-auto&response_type=code&scope=snsapi_base&state=123#wechat_redirect"},
]}
'''
#
#为了方便迁移，对字符__APPID__ __MYDOMAIN__进行替换
menu = menu.replace("__APPID__",appid)
menu = menu.replace("__MYDOMAIN__",myDomain)
menuMap = {
    "TRAFFIC_QUERY" : {
        "title"       :"点击进入了解--业务咨询",
        "description" :"致力于为企业创造正确价值，降低融资成本。客服热线：\r\n0755-82556519\r\n13825224235\r\n18665908997",
        "picurl"      :"http://e.picphotos.baidu.com/album/s%3D1100%3Bq%3D90/sign=a515df566d061d95794633394bc431a0/ca1349540923dd545a5a0106d209b3de9c8248b6.jpg",
        "url"         :"http://mp.weixin.qq.com/s?__biz=MzA5NDAzNTM2Mw==&mid=201143768&idx=1&sn=a2881b5db1990a2cfa01383068089385#rd"
    },
    "ABOUT" :{
        "title"   : "正在建设中"
    },
}


exceptMsg = {
    "touser":"",
    "template_id":"9wfpD5Gc-G938HrKKVdB6izt6mygcSf38KAjGCy8jlk",
    "url":"http://www.iwaiter.cn",
    "topcolor":"#FF0000",
    "data":{
        "first": {
            "value":"",
            "color":"#173177"
        },
        "keyword1":{
            "value":"",
            "color":"#173177"
        },
        "keyword2":{
            "value":"",
            "color":"#173177"
        },
        "keyword3":{
            "value":"",
            "color":"#173177"
        },
        "keyword4":{
            "value":"",
            "color":"#173177"
        },
        "remark":{
            "value":"",
            "color":"#008B8B"
        },
    }
}

systemMsg = {
    "touser":"",
    "template_id":"_vl8wxPi60G8J7VL_4pHmHz3h7p_fLNVGXtukxhjMOg",
    "url":"http://www.iwaiter.cn",
    "topcolor":"#FF0000",
    "data":{
        "first": {
            "value":"",
            "color":"#173177"
        },
        "keyword1":{
            "value":"",
            "color":"#173177"
        },
        "keyword2":{
            "value":"",
            "color":"#173177"
        },
        "remark":{
            "value":"",
            "color":"#173177"
        },
    }
}