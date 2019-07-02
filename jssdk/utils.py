import json
import random
import time
import hashlib
import requests
import redis
# 获取 access_token   (appId,appSecret)   最好全局缓存
# 获取 jsapi_ticket   (appId,appSecret)   全局缓存
# 签名（jsapi_ticket,调用页面的完整 url）
# 微信JS-SDK说明文档：https://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1421141115
class JSSDK:
    def __init__(self,appId,appSecret):
        self.appId = appId
        self.appSecret = appSecret
        self.rds = redis.Redis(host='127.0.0.1', port=6379)

    # 获取access_token
    def get_access_token(self)->str:
        # access_token应该全局存储与更新
        access_token = self.rds.get('wx_access_token')
        if not access_token:
            url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={0}&secret={1}'.format(self.appId,self.appSecret)
            response = requests.get(url)
            response = json.loads(response.text)
            if response['access_token']:
                self.rds.set('wx_access_token',response['access_token'],ex=7200)
                access_token = response['access_token']
        else:
            access_token = self.rds.get('wx_access_token')
        return access_token

    # 获取get_jsapi_ticket
    def get_jsapi_ticket(self,access_token):
        jsapi_ticket = self.rds.get('wx_jsapi_ticket')
        if not jsapi_ticket:
            url = 'https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token={0}&type=jsapi'.format(access_token)
            response = requests.get(url)
            response = json.loads(response.text)
            if response['ticket']:
                self.rds.set('wx_jsapi_ticket', response['ticket'], ex=7200)
                jsapi_ticket = response['ticket']
        else:
            jsapi_ticket = self.rds.get('wx_jsapi_ticket')
        return jsapi_ticket

    # sign签名算法
    def get_sign_package(self,jsapi_ticket,url)->dict:
        import string
        nonce_str = ''.join(random.sample(string.ascii_letters + string.digits, 16))
        timestamp = int(time.time())
        ret = {
            'noncestr': nonce_str,
            'jsapi_ticket': str(jsapi_ticket,'utf-8'),
            'timestamp': timestamp,
            'url': url          # 当前网页的URL
        }
        # 对所有待签名参数按照字段名的ASCII 码从小到大排序（字典序）
        # URL键值对的格式（即key1=value1&key2=value2…）拼接成字符串
        # 需要注意的是所有参数名均为小写字符
        str_for_sign = '&'.join(['%s=%s' % (key, ret[key]) for key in sorted(ret)])
        print(str(jsapi_ticket,'utf-8'))
        print(nonce_str)
        print(timestamp)
        print(url)
        print(str_for_sign)
        ret['signature'] = hashlib.sha1(str_for_sign.encode('utf8')).hexdigest()
        ret.pop('jsapi_ticket')
        ret['appId'] = self.appId
        print(ret['signature'])
        return ret

