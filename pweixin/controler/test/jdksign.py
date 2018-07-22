import random
import string
import hashlib
def jdkSign(jsapi_ticket, url,nonceStr="",timestamp=""):
    temp = url.split("#")[0]
    ret = {
        'nonceStr': nonceStr,
        'jsapi_ticket': jsapi_ticket,
        'timestamp': timestamp,
        'url': temp
    }
    string = '&'.join(['%s=%s' % (key.lower(), ret[key]) for key in sorted(ret)])
    ret['signature'] = hashlib.sha1(string).hexdigest().upper()
    ret['appid'] = "self.appid"
    ret['url'] = url
    ret['string'] = string
    return ret

jsapi_ticket = "bxLdikRXVbTPdHSM05e5uw40wrVAmNsg_3nNE15KJHBmsNVJFT7l-6s21nIu6jpmZanXsL5NLpn5hSQ_5dRcmw"
nonceStr ="ro3bkaLajpBaxVW"
timestamp =1424526906
url = "https://open.weixin.qq.com/connect/oauth2/authorize?appid=wxd1ac6e0c829fd839&redirect_uri=http://gxsaiwei.sinaapp.com/m/active?act=zhuanpan&response_type=code&scope=snsapi_base&state=123#wechat_redirect"
print jdkSign(jsapi_ticket, url,nonceStr,timestamp)