# -*- coding: utf-8 -*-
"""
@Author: ChenXiaolei
@Date: 2020-08-05 16:32:25
:LastEditTime: 2024-07-31 15:26:09
:LastEditors: ChenXiaolei
@Description: 监控处理
"""

from seven_framework.redis import *
from seven_framework.web_tornado.base_handler.base_api_handler import *


class MonitorHandler(BaseApiHandler):
    def prepare(self, *args, **argkw):
        # 过滤日志
        pass
    def get_async(self):
        """
        @description: 通用监控处理
        @last_editors: ChenXiaolei
        """
        config_monitor = config.app_config
        self.set_status(500)
        # 遍历配置,监控状态
        for key, value in config_monitor.items():
            if type(value) != dict:
                continue

            # Check MYSQL
            if key.find("db") > -1:
                try:
                    MySQLHelper(value).connection()
                except:
                    self.write(f"Mysql监控异常:{traceback.format_exc()}")
                    return
            # Check Redis
            elif key.find("redis") > -1:
                now_time = str(int(time.time()))

                try:
                    monitor_key = f"framework_monitor_{config_monitor['run_port']}"
                    
                    if JsonHelper.json_dumps(value).find("cluster_nodes")>-1:
                        redis_client = RedisHelper.redis_cluster_init(config_dict=value)
                    else:
                        redis_client = RedisHelper.redis_init(config_dict=value,decode_responses=True)

                    redis_client.set(monitor_key, now_time)
                    
                    monitor_time = redis_client.get(monitor_key)
                    if  not monitor_time:
                        self.write(f"Reids监控异常,数据存在存取延迟[{monitor_time}][{now_time}]")
                        return
                except:
                    self.write(f"Redis监控异常:{traceback.format_exc()}")
                    return
        self.set_status(200)
        self.write("ok")
