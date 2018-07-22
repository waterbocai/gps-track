# _*_ coding:utf-8 _*_
import datetime,sys,importlib,sys,os

from product.model.config import db
import product.iweixin.config as weixin
from weixinsdk.basic  import WechatBasic

weixin_orign = {
    "gh_56607309bcf5":"tianwangshouhu",
    "gh_dd34db268edc":"gxsaiwei",
    "gh_ceb2966f2c40":"dengchewang"
}


class UserDB:
    #为了确保id暴露，对id采用md5进行编号
    def get_weixin_obj(self,**data):
        if data.has_key("weixin_name"):
            weixin_name =data["weixin_name"]
        if data.has_key("orign_id"):
            weixin_name = weixin_orign[data["orign_id"]]
        #获取微信文本配置信息
        ObjWeixin = WechatBasic(token     =weixin.token,
                                appid     =weixin.appid,
                                appsecret =weixin.secret,
                                open_appid =weixin.open_appid,
                                open_secrept=weixin.open_secrept,
                                open_redirect_uri=weixin.open_redirect_uri,
                                weixinname=weixin.weixinName,
                                partnerid =weixin.weixinpay_partnerid,
                                firsteye  =weixin.firsteye,
                                menuMap   =weixin.menuMap,
                                owner_db  = db
                                )
        ObjWeixin.iconfig = weixin
        return ObjWeixin
     
    
    def getWechatObjExt(domain,weixinName):
        url = "{0}/manage?act=weixin-id".format(domain)
        weixin = requests.get(url, params = {"enname":weixinName}).json()
        ObjWeixin = WechatBasic(token=weixin["token"],appid=weixin["appid"],appsecret=weixin["secret"],weixinname=weixin["enname"],partnerid=weixin["partnerid"])
        return ObjWeixin
    
    
    def getUserByOpenid(self,weixin_name,openid):
        _ret = db.query("""SELECT * FROM Customer 
                             WHERE openid='{0}' AND
                                   weixinname='{1}'
                             """.format(openid,weixin_name))
        _user = _ret[0]
        user = {}
        for k in _user:
            if  isinstance(_user[k],datetime.datetime): 
                user[k] = _user[k].strftime("%Y-%m-%d %H:%M:%S")
            else:
                user[k] = _user[k]
        return user
        
userdb = UserDB()