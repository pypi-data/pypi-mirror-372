# -*- coding: utf-8 -*-
"""
:Author: ChenXiaolei
:Date: 2023-03-07 14:56:15
:LastEditTime: 2023-03-07 15:44:36
:LastEditors: ChenXiaolei
:Description: 
"""
import memcache


class MemcachedHelper():
    def __init__(self, host, debug=True):
        """
        :description: 初始化Memcached连接
        :params host: memcached实例数组 如:["10.19.18.130:11211","10.19.154.69:11211"]
        :params debug: debug=True表示运行出现错误时，可以显示错误信息，正式环境为False
        :demo memcached_client = MemcachedHelper(config.get_value("memcached")).memcached_client 
        :demo 配置: "memcached":["10.19.18.130:11211","10.19.154.69:11211"]
        :demo 使用: memcached_client.set("test","1")    memcached_client.get("test") 
        :return 无
        :last_editors: ChenXiaolei
        """
        self.memcached_client = memcache.Client(host, debug)
