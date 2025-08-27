# -*-coding:utf-8-*-
"""
:Author: LinGuilin
:Date: 2020-08-21 14:07:08
:LastEditTime: 2023-04-10 17:41:56
:LastEditors: ChenXiaolei
:Description: 企业微信应用接口调用

"""

from seven_framework.sign import SignHelper
from seven_framework.crypto import CryptoHelper
from seven_framework.json import JsonHelper
from seven_framework.http import HTTPHelper
from seven_framework.time import TimeHelper
from seven_framework.uuid import UUIDHelper
import time
import requests
import traceback
import json
import filetype
import os

def get_access_token(wechat_app_id, wechat_app_secret):
    """
    :description: 获取access_token: 微信AccessToken，避免频繁获取。
    :last_editors: ChenXiaolei
    """
    if not wechat_app_id or not wechat_app_secret:
        raise Exception(
            "missing wechat_app_id or wechat_app_secret,please configure in init!")

    access_token_result = HTTPHelper.get(
        f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={wechat_app_id}&corpsecret={wechat_app_secret}"
    )

    if access_token_result and access_token_result.text:
        access_token_json = json.loads(access_token_result.text)
        if not access_token_json or ("errmsg" in access_token_json and access_token_json["errmsg"]!="ok"):
            raise Exception(access_token_json["errmsg"])

        return access_token_json["access_token"]

    return None

class WorkWechatHelper(object):
    """"
    :Description:企业微信应用接口类
    Usage::

      >>> from seven_framework import *
      >>> work_wechat = WorkWechatHelper(app_id=APP_ID,app_key=APP_KEY)
      >>> res = work_wechat.get_web_auth_link(redirect_uri='https://httpbin.org/get',state=STATE)
      >>> if res:
      >>>       print('res)
      https://open.weixin.qq.com/connect/oauth2/...
    """

    def __init__(self, app_id="", app_key="", oauth_url=None, msg_url=None):
        """
        :Description: 初始化参数
        :param app_id: 应用id
        :param app_key: 应用凭证
        :param oauth_url: 登录认证请求路径
        :param msg_url: 消息请求路径
        :last_editors: LinGuilin
        """
        self.oauth_url = oauth_url
        self.msg_url = msg_url

        if not oauth_url:
            self.oauth_url = "https://wwc.gao7.com/auth/get_link"

        if not msg_url:
            self.msg_url = "https://wwc.gao7.com/message/send"

        self.app_key = app_key
        self.app_id = app_id

    def _get_oauth_params(self, redirect_uri, link_type, state=None):
        """
        :Description: 获取登录认证请求参数字典
        :param redirect_uri:重定向链接
        :param state: 透传参数
        :param link_type: 链接类型 code/web
        :return dict  请求参数字典 
        :last_editors: LinGuilin
        """

        timestamp = int(time.time())
        params = {}
        params["timestamp"] = timestamp
        params["redirect_uri"] = redirect_uri
        params["state"] = state
        params["link_type"] = link_type
        params["app_id"] = self.app_id

        # 生成签名
        sign = SignHelper.params_sign_md5(params=params, app_key=self.app_key)
        # 构造请求参数
        params["sign"] = sign
        return params

    def _get_msg_params(self,
                        notice_content,
                        notice_object,
                        notice_object_type,
                        notice_content_type="text",
                        webhook_key=None):
        """
        :Description: 获取消息请求参数
        :param notice_content: 消息内容
        :param notice_content_type: 消息内容类型
        :param notice_object: 消息接收对象
        :param notice_object_type: 消息接收对象类型
        :param webhook_key:机器人密钥
        :return dict  消息字典
        :last_editors: LinGuilin
        """

        timestamp = int(time.time())
        params = {}
        params["app_id"] = self.app_id
        params["timestamp"] = timestamp
        params["notice_object_type"] = notice_object_type
        params["notice_content"] = notice_content
        params["notice_content_type"] = notice_content_type
        params["notice_object"] = notice_object
        params["webhook_key"] = webhook_key
        # 生成签名
        sign = SignHelper.params_sign_md5(params=params, app_key=self.app_key)

        # 构建请求字典
        params["sign"] = sign
        return params

    def get_web_auth_link(self, redirect_uri, state=None):
        """
        :Description: 获取网页认证登录链接
        :param redirect_uri: 重定向链接 
        :param state: 透传参数
        :return 链接或者None
        :last_editors: LinGuilin
        """

        params = self._get_oauth_params(redirect_uri=redirect_uri,
                                        state=state,
                                        link_type="web")
        try:
            response = requests.get(url=self.oauth_url, params=params)
            response.raise_for_status()
            res = response.json()

        except:
            print(
                f"get请求url:{self.oauth_url},params:{params} 异常:{traceback.format_exc()}")
            return None
        else:
            if int(res["result"]) == 1:
                return res["data"]["auth_url"]
            print(f"get请求url:{self.oauth_url}出现异常,异常信息:{res['desc']}")
            return None

    def get_code_auth_link(self, redirect_uri, state=None):
        """
        :Description: 获取二维码认证登录链接
        :param redirect_uri: 重定向链接 
        :param state: 透传参数
        :return 链接或者None
        :last_editors: LinGuilin
        """

        params = self._get_oauth_params(redirect_uri=redirect_uri,
                                        state=state,
                                        link_type="code")

        try:
            response = requests.get(url=self.oauth_url, params=params)
            response.raise_for_status()
            res = response.json()
        except:
            print(
                f"get请求url:{self.oauth_url},params:{params} 异常:{traceback.format_exc()}")
            return None
        else:

            if int(res["result"]) == 1:
                return res["data"]["auth_url"]
            print(f"get请求url:{self.oauth_url}出现异常,异常信息:{res['desc']}")
            return None

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
            f"https://qyapi.weixin.qq.com/cgi-bin/get_jsapi_ticket?access_token={access_token}"
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

class WorkWechatWebhookHelper(object):
    """
    :description: 企业微信群机器人帮助类
    :last_editors: ChenXiaolei
    """    
    def __init__(self, webhook_key, host="https://wwc.gao7.com/api"):
        """
        :description: 
        :param webhook_key: 群机器人webhook_key     例:假设webhook是：https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=693a91f6-7xxx-4bc4-97a0-0ec2sifa5aaa 则webhook_key即为693a91f6-7xxx-4bc4-97a0-0ec2sifa5aaa
        :param host: 企微应用中心服务地址
        :last_editors: ChenXiaolei
        """        
        self.webhook_key = webhook_key
        self.host = host

    def _webhook_request(self, params):
        """
        :description: 企微中心http请求
        :param params: 参数
        :param action: 路由
        :return 成功True 失败False
        :last_editors: ChenXiaolei
        """
        request_url = f"{self.host}/message/webhook"

        if "webhook_key" not in params:
            params["webhook_key"] = self.webhook_key

        response = requests.post(request_url, data=JsonHelper.json_dumps(params).encode("utf-8"),
                                 headers={'Content-Type': 'application/json'})

        response_json = json.loads(response.text)

        if not response_json or "result" not in response_json:
            print(f"请求企微应用中心发送webhook消息失败 post请求 url:{request_url}出现异常")
            return False

        if response_json["result"] != 1:
            # 错误
            print(
                f"请求企微应用中心发送webhook消息失败 post请求 url:{request_url}出现异常,异常信息:{response_json['desc']}")

        return True

    def _webhook_upload_file(self, file_path):
        url = f"{self.host}/message/upload_file"

        payload = {'webhook_key': self.webhook_key}

        kind = filetype.guess(file_path)
        if kind is None:
            print('Cannot guess file type!')
            return
        # 媒体类型，如：image/png
        mime_type = kind.mime
        files = [
            ('media', (os.path.split(file_path)
                       [-1], open(file_path, 'rb'), mime_type))
        ]
        headers = {}

        response = requests.request(
            "POST", url, headers=headers, data=payload, files=files)

        response_json = json.loads(response.text)

        if not response_json or "result" not in response_json:
            print(f"请求企微应用中心发送webhook消息失败 post请求 url:{request_url}出现异常")
            return False

        if response_json["result"] != 1:
            # 错误
            print(
                f"请求企微应用中心发送webhook消息失败 post请求 url:{request_url}出现异常,异常信息:{response_json['desc']}")

        return response_json["data"]["media_id"]

    def send_webhook_message_text(self, content):
        """
        :description: 发送微信机器人消息(文本)
        :param content: 消息内容
        :return 成功True 失败False
        :last_editors: ChenXiaolei
        """
        params = {"msg_type": "text", "content": content}
        return self._webhook_request(params)

    def send_webhook_message_markdown(self, content):
        """
        :description: 发送微信机器人消息(markdown)
        :param content: 消息内容
        :return 成功True 失败False
        :last_editors: ChenXiaolei
        """
        params = {"msg_type": "markdown", "content": content}
        return self._webhook_request(params)

    def send_webhook_message_file(self, file_path):
        """
        :description: 发送微信机器人消息(文件)
        :param file_path: 文件路径
        :return 成功True 失败False
        :last_editors: ChenXiaolei
        """
        media_id = self._webhook_upload_file(file_path)

        params = {"msg_type": "file", "media_id": media_id}

        return self._webhook_request(params)

    def send_webhook_message_image(self, image_path):
        """
        :description: 发送微信机器人消息(图片)
        :param image_path: 图片路径
        :return 成功True 失败False
        :last_editors: ChenXiaolei
        """
        import base64
        base64 = base64.b64encode(open(image_path, 'rb').read())

        md5 = CryptoHelper.md5_file(image_path)

        params = {"msg_type": "image", "base64": base64, "md5": md5}

        return self._webhook_request(params)

    def send_webhook_message_news(self, articles):
        """
        :description: 发送微信机器人消息(图文)
        :param articles: 图文消息列表 如 [{"title":"title","description":"desc","url":"http://www.gao7.com","picurl":"https://resources.gao7.com/www/Content/images/gao7-logo/foot-logo-new.jpg"}]
        :return 成功True 失败False
        :last_editors: ChenXiaolei
        """

        params = {"msg_type": "news", "articles": articles}

        return self._webhook_request(params)
