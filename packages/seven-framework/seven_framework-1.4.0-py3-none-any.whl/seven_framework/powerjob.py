# -*- coding: utf-8 -*-
"""
:Author: ChenXiaolei
:Date: 2025-04-17 14:35:18
:LastEditTime: 2025-04-17 18:00:57
:LastEditors: ChenXiaolei
:Description: 
"""
from .http import *
from .json import *


class PowerJobHelper:
    """
    配置文件示例：
    "powerjob":{
        "host":"http://192.168.100.147:7700",
        "app_id":1,
        "job_id":12,
        "instance_params":"docker run --rm  registry.cn-zhangjiakou.aliyuncs.com/gao7com/db_index_check:latest application.py --config_dev"
    }

    启动任务示例（传参）：
    # 通知powerjob启动任务
    powerjob_config = config.get_value("powerjob")
    powerjob_instance_id = PowerJobHelper(powerjob_config["host"]).run_job(powerjob_config["app_id"],powerjob_config["job_id"],f"{powerjob_config['instance_params']} --plan_id={idx_plan_id}")
    """
    # 枚举定义 实例状态
    INSTANCE_STATUS = {
        1: "等待派发",
        2: "等待Worker接收",
        3: "运行中",
        4: "失败",
        5: "成功",
        9: "取消",
        10: "手动停止"
    }

    def __init__(self, host):
        """
        :description: PoerJob Helper
        :param host: PowerJob地址
        :last_editors: ChenXiaolei
        """
        self.host = host

    def run_job(self, job_id, job_params, instance_params, delay=0):
        """
        :description: 运行PowerJob任务
        :param job_id: 应用ID
        :param job_params: 任务ID
        :param instance_params: 实例参数
        :return: 实例ID
        :last_editors: ChenXiaolei
        :demo PowerJobHelper("http://http://192.168.100.147:7700").run_job(1, 10, "cd /root/task_powerjob_test && python3.8 application.py --production")
        """
        response = requests.post(
            f"{self.host}/openApi/runJob?appId={job_id}&jobId={job_params}&instanceParams={instance_params}&delay={delay}",
            headers={"Content-Type": "application/json"}
        )

        result,data = self.__powerjob_response(response)

        if result:
            return data
        return None

    def fetch_instance_info(self, instance_id):
        """
        :description: 获取PowerJob实例信息
        :param instance_id: 实例ID
        :return: result,实例信息
        :last_editors: ChenXiaolei
        :demo PowerJobHelper("http://http://192.168.100.147:7700").fetch_instance_info("793137199443869800")
        """
        response = requests.get(
            f"{self.host}/openApi/fetchInstanceInfo?instanceId={instance_id}",
            headers={"Content-Type": "application/json"}
        )

        return self.__powerjob_response(response)

    def fetch_instance_status(self, instance_id):
        """
        :description: 获取PowerJob实例状态
        :param instance_id: 实例ID
        :return: result,实例状态
        :last_editors: ChenXiaolei
        :demo PowerJobHelper("http://http://192.168.100.147:7700").fetch_instance_status("793137199443869800")
        """
        response = requests.get(
            f"{self.host}/openApi/fetchInstanceStatus?instanceId={instance_id}",
            headers={"Content-Type": "application/json"}
        )

        result,data = self.__powerjob_response(response)

        if result:
            return True,self.INSTANCE_STATUS.get(data, "未知状态")
        
        return False,data

    def stop_instance(self, instance_id, app_id):
        """
        :description: 停止PowerJob实例
        :param instance_id: 实例ID
        :return: result,data
        :last_editors: ChenXiaolei
        :demo PowerJobHelper("http://http://192.168.100.147:7700").stop_instance("793137199443869800",1)
        """
        response = requests.post(
            f"{self.host}/openApi/stopInstance?instanceId={instance_id}&appId={app_id}",
            headers={"Content-Type": "application/json"}
        )

        return self.__powerjob_response(response)
    
    def cancel_instance(self, instance_id, app_id):
        """
        :description: 取消PowerJob定时任务实例
        :param instance_id: 实例ID
        :param app_id: 应用ID
        :return: result,data
        :last_editors: ChenXiaolei
        :demo PowerJobHelper("http://http://192.168.100.147:7700").cancel_instance("793137199443869800",1)
        """
        response = requests.post(
            f"{self.host}/openApi/cancelInstance?instanceId={instance_id}&appId={app_id}",
            headers={"Content-Type": "application/json"}
        )

        return self.__powerjob_response(response)


    # 统一处理返回结果

    def __powerjob_response(self, response):
        """
        :description: 统一处理返回结果
        :param response: powerjob返回结果
        :return 数据结果
        :last_editors: ChenXiaolei
        """
        if not response or response.status_code != 200:
            return None

        response_json = json.loads(response.text)

        if "success" in response_json and response_json["success"] == True:
            return True,response_json["data"]
        elif "message" in response_json and response_json["message"]:
            return False,response_json["message"]
        else:
            return False,""
