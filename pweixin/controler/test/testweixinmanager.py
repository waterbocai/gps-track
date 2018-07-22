from weixin.controler.weixin_manager import JSJDKSign,WXManager
from weixin.userdata.bbwwsh.common import userMsg
#from weixin.sdk import WechatBasic,WechatExt
from weixin.sdk.basic import WechatBasic
from weixin.sdk.ext import WechatExt
import web
class WeixinTest:
    def __init__(self):
        self.wxMgr = WXManager(userMsg)
        self.wechat = WechatBasic(token=userMsg['mytoken'],appid=userMsg['appid'],appsecret=userMsg['secret'])
                #token=None, appid=None, appsecret=None, partnerid=None,
                #partnerkey=None, paysignkey=None, access_token=None, access_token_expires_at=None,
                #jsapi_ticket=None, jsapi_ticket_expires_at=None
    def GET(self):
        data = web.input()
        act = data.act.upper()
        openid = data.openid.encode('ascii')
        if act == "SEND_MSG":
            ret = self.wxMgr.sendText2Customer(openid,"helloworld")
            #ret  = self.wechat.send_text_message(openid,'helloworld')
        return ret
            
            