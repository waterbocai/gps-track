# -*- coding: utf-8 -*-

import urllib  
import urllib2  
from urllib import urlencode  
import json  
import sys  
reload(sys)  
sys.setdefaultencoding('UTF-8')
import requests

class WXManager:
    comUrl   = "https://api.weixin.qq.com/cgi-bin/"
    comToken = "?access_token="
    def __init__(self,appid=None,secret=None):
        self.appid = appid
        self.secret = secret
        self.accessToken = self.getAccessToken()

    
    def cmdUrl(self,cmd):
        comUrl = "https://api.weixin.qq.com/cgi-bin/"+cmd+ "?access_token=" + self.accessToken
        return comUrl
         
    def getAccessToken(self):
        accessUrl = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=" + self.appid + "&secret="+self.secret
        f = urllib2.urlopen(accessUrl)
        stringjson = f.read()   
        access_token = json.loads(stringjson)['access_token']
        return access_token

    def delMenu(self):
        req  = urllib2.Request(self.cmdUrl("menu/delete"))
        html = urllib2.urlopen(req)
        result = json.loads(html.read().decode("utf-8"))
        return result["errcode"]
        
    def createMenu(self,menu):
        print self.cmdUrl("menu/create")
        f  = urllib2.urlopen(url = self.cmdUrl("menu/create"), data = menu.encode('utf-8'))
        return f.read()
        
        #return 0
    def getMenu(self):
        html  = urllib2.urlopen(self.cmdUrl("menu/get"))
        return html.read().decode("utf-8")
    
    def getGroups(self):
        html  = urllib2.urlopen(self.cmdUrl("groups/get"))
        return html.read().decode("utf-8")
    
    def createGroup(self,name,id):
        group = '''
          {
            "group": {
                "id": ''' + id +''',
                "name" :"'''+name+ '''
            }
        }'''
         
        html  = urllib2.urlopen(self.cmdUrl("groups/create"),group.encode('utf-8'))
        return html.read().decode("utf-8")
    
    def moveMember2Group(self,openid,to_groupid):
        sto_groupid = '%d' %to_groupid
        group = '''{"openid":"''' + openid +'''","to_groupid":'''+sto_groupid +"}"
        html  = urllib2.urlopen(self.cmdUrl("groups/members/update"),group.encode('utf-8'))
        return html.read().decode("utf-8")
     
    def createQcode(self,scene_id,expire_seconds=0):
        if isinstance(scene_id,int):
            sscene_id= '%d' %scene_id 
            if expire_seconds == 0:
                args = '''{"action_name": "QR_LIMIT_SCENE", "action_info": {"scene": {"scene_id":'''+ sscene_id +'}}}'
            else :
                args = '''{"expire_seconds":'''+ expire_seconds+''', "action_name": "QR_SCENE", "action_info": {"scene": {"scene_id":'''+ sscene_id+'''}}}'''
        else:
            args = '''{"action_name": "QR_LIMIT_STR_SCENE", "action_info": {"scene": {"scene_str": "'''+scene_id+'''"}}}'''
        html  = urllib2.urlopen(self.cmdUrl("qrcode/create"),args.encode('utf-8'))
        result =  json.loads(html.read().decode("utf-8"))
        return result

    def getUser(self,openid,lang="zh_CN"):
        html  = urllib2.urlopen(self.cmdUrl("user/info")+"&openid="+openid+"&lang="+lang)
        result =  json.loads(html.read().decode("utf-8"))
        return result
    
    def create_temp_qrcode(self, scene_id,expire_seconds=604800):
        """
        创建二维码
        详情请参考 http://mp.weixin.qq.com/wiki/18/28fc21e7ed87bec960651f0ce873ef8a.html
        :param data: 你要发送的参数 dict
        :return: 返回的 JSON 数据包
        :raise HTTPError: 微信api http 请求失败
        """
        #self._check_appid_appsecret()
        data = {
            "access_token"  :self.getAccessToken(),
            "expire_seconds":expire_seconds,
            "action_name"   : "QR_SCENE",
            "action_info"   : {"scene": {"scene_id": scene_id}}
        }
        return self._post(
            url='https://api.weixin.qq.com/cgi-bin/qrcode/create',
            data=data
        )
    def create_perm_qrcode(self, scene_str):
        """
        创建二维码
        详情请参考 http://mp.weixin.qq.com/wiki/18/28fc21e7ed87bec960651f0ce873ef8a.html
        :param data: 你要发送的参数 dict
        :return: 返回的 JSON 数据包
        :raise HTTPError: 微信api http 请求失败
        """
        #self._check_appid_appsecret()
        
        data = {"access_token"  :self.getAccessToken()}
        if (type(scene_str) is str):#字符串类型scene_id
            data["action_name"]="QR_LIMIT_STR_SCENE"
            data["action_info"]= {"scene": {"scene_str": scene_str}}
        else:#整数类型scene_id
            data["action_name"]="QR_LIMIT_SCENE"
            data["action_info"]= {"scene": {"scene_id": scene_str}}
        return self._post(
            url='https://api.weixin.qq.com/cgi-bin/qrcode/create',
            data=data
        )
        
    def _request(self, method, url, **kwargs):
        """
        向微信服务器发送请求
        :param method: 请求方法
        :param url: 请求地址
        :param kwargs: 附加数据
        :return: 微信服务器响应的 json 数据
        :raise HTTPError: 微信api http 请求失败
        """
        if "params" not in kwargs:
            kwargs["params"] = {
                "access_token": self.getAccessToken(),
            }
        if isinstance(kwargs.get("data", ""), dict):
            body = json.dumps(kwargs["data"], ensure_ascii=False)
            body = body.encode('utf8')
            kwargs["data"] = body

        r = requests.request(
            method=method,
            url=url,
            **kwargs
        )
        r.raise_for_status()
        response_json = r.json()
        #self._check_official_error(response_json)
        return response_json

    def _get(self, url, **kwargs):
        """
        使用 GET 方法向微信服务器发出请求
        :param url: 请求地址
        :param kwargs: 附加数据
        :return: 微信服务器响应的 json 数据
        :raise HTTPError: 微信api http 请求失败
        """
        return self._request(
            method="get",
            url=url,
            **kwargs
        )

    def _post(self, url, **kwargs):
        """
        使用 POST 方法向微信服务器发出请求
        :param url: 请求地址
        :param kwargs: 附加数据
        :return: 微信服务器响应的 json 数据
        :raise HTTPError: 微信api http 请求失败
        """
        return self._request(
            method="post",
            url=url,
            **kwargs
        )
