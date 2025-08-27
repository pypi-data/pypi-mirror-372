# -*- coding: utf-8 -*-
"""
:Author: ChenXiaolei
:Date: 2023-03-08 09:50:39
:LastEditTime: 2023-04-10 16:26:40
:LastEditors: ChenXiaolei
:Description: 微信帮助类
"""
from seven_framework.http import *
from seven_framework.json import *
from seven_framework.time import *
from seven_framework.uuid import *
from seven_framework.crypto import *


def get_access_token(wechat_app_id, wechat_app_secret):
    """
    :description: 获取access_token: 微信AccessToken，避免频繁获取。
    :last_editors: ChenXiaolei
    """
    if not wechat_app_id or not wechat_app_secret:
        raise Exception(
            "missing wechat_app_id or wechat_app_secret,please configure in init!")

    access_token_result = HTTPHelper.get(
        f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={wechat_app_id}&secret={wechat_app_secret}"
    )

    if access_token_result and access_token_result.text:
        access_token_json = json.loads(access_token_result.text)
        if not access_token_json or "errmsg" in access_token_json:
            raise Exception(access_token_json["errmsg"])

        return access_token_json["access_token"]

    return None


class WechatMiniProgramHelper():
    def __init__(self, wechat_app_id=None, wechat_app_secret=None):
        """
        :description: 微信小程序帮助类
        :param wechat_app_id: 微信小程序APPID
        :param wechat_app_secret: 微信小程序APPSECRET
        :last_editors: ChenXiaolei
        """
        if wechat_app_id:
            self.wechat_app_id = wechat_app_id
        if wechat_app_secret:
            self.wechat_app_secret = wechat_app_secret

    def get_user_phone_number(self, code, access_token=None):
        """
        :description: 获取微信用户的手机号码
        :param code: 小程序获取手机授权code
        :param access_token: 微信AccessToken 如业务有缓存则有限从缓存传入,避免频繁获取。
        :return 用户手机号码
        :last_editors: ChenXiaolei
        """
        if not access_token:
            access_token = get_access_token(self.wechat_app_id, self.wechat_app_secret)
            
        if not access_token:
            raise Exception("missing access_token!")

        if not code:
            raise Exception("missing code!")

        user_phone_number_result = HTTPHelper.post(f"https://api.weixin.qq.com/wxa/business/getuserphonenumber?access_token={access_token}",data={"code":code},headers={"Content-Type":"application/json"})

        if user_phone_number_result and user_phone_number_result.text:
            user_phone_number_json = json.loads(user_phone_number_result.text)
            if  not user_phone_number_json or user_phone_number_json["errcode"]!=0:
                raise Exception(user_phone_number_json["errmsg"])
            
            return user_phone_number_json["phone_info"]["purePhoneNumber"]
        
        return ""

class WechatPublicAccountHelper():
    def __init__(self, wechat_app_id=None, wechat_app_secret=None):
        """
        :description: 微信公众号帮助类
        :param wechat_app_id: 微信公众号APPID
        :param wechat_app_secret: 微信公众号APPSECRET
        :last_editors: ChenXiaolei
        """
        if wechat_app_id:
            self.wechat_app_id = wechat_app_id
        if wechat_app_secret:
            self.wechat_app_secret = wechat_app_secret

    def get_ticket(self, access_token=None):
        """
        :description: 获取微信票据
        :param access_token: 微信AccessToken 如业务有缓存则有限从缓存传入,避免频繁获取。
        :return ticket
        :last_editors: ChenXiaolei
        """
        if not access_token:
            access_token = get_access_token(
                self.wechat_app_id, self.wechat_app_secret)

        ticket_result = requests.get(
            f"https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token={access_token}&type=jsapi"
        )

        if ticket_result and ticket_result.text:
            ticket_result_json = json.loads(ticket_result.text)
            if not ticket_result_json or ticket_result_json[
                    "errcode"] != 0:
                raise Exception(ticket_result_json["errmsg"])
            return ticket_result_json["ticket"]

        return None

    def sign_jssdk(self, sign_url, ticket=None, access_token=None):
        """
        :description: jssdk验签
        :param sign_url: jssdk验签URL
        :param ticket: 微信票据 如业务有缓存则有限从缓存传入,避免频繁获取。
        :param access_token: 微信AccessToken 如业务有缓存则有限从缓存传入,避免频繁获取。
        :return 验签结果字典 包含 timestamp nonce_str signature
        :last_editors: ChenXiaolei
        """
        if not ticket:
            ticket = self.get_ticket(access_token)

        timestamp = TimeHelper.get_now_timestamp()

        nonce_str = UUIDHelper.get_uuid()

        signature = CryptoHelper.sha1_encrypt(
            f"jsapi_ticket={ticket}&noncestr={nonce_str}&timestamp={timestamp}&url={sign_url}")

        return {"timestamp": timestamp, "nonce_str": nonce_str, "signature": signature}
