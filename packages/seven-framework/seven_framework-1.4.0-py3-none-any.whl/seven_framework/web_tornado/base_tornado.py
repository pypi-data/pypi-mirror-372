# -*- coding: utf-8 -*-
"""
:Author: ChenXiaolei
:Date: 2020-05-12 17:47:10
:LastEditTime: 2024-10-31 15:07:07
:LastEditors: ChenXiaolei
:Description: 基础tornado引用
"""
# 框架引用
import os
import tornado.web
import tornado.ioloop
import tornado.httpserver
import platform
from seven_framework import *
import sys
from nacos import NacosClient
global environment
config_file = None
if "--production" in sys.argv:
    environment = "production"
    config_file = "config.json"
elif "--testing" in sys.argv:
    environment = "testing"
    config_file = "config_testing.json"
else:
    for arg in sys.argv:
        if arg.startswith("--config_"):
            environment = arg.replace("--config_","")
            config_file = f"config_{environment}.json"
    if not config_file:
        environment = "dev"
        config_file = "config_dev.json"

sys.path.append(".local")  # 不可删除,置于其他import前
# 初始化配置,执行顺序需先于调用模块导入
config.init_config(config_file)  # 全局配置,只需要配置一次

# 项目标识
project_name = config.get_value("project_name", None)

# 初始化error级别日志
logger_error = None
# 初始化info级别日志
logger_info = None

# 读取日志配置
log_config = config.get_value("logger")

# 日志存储路径
log_file_path = "logs"
if log_config and "log_file_path" in log_config:
    log_file_path = log_config["log_file_path"]

logger_error = Logger(f"{log_file_path.rstrip('/')}/log_error", "ERROR", "log_error",
                      HostHelper.get_host_ip(), project_name,
                      log_config).get_logger()

logger_info = Logger(f"{log_file_path.rstrip('/')}/log_info", "INFO", "log_info",
                     HostHelper.get_host_ip(), project_name,
                     log_config).get_logger()

logger_sql = Logger(f"{log_file_path.rstrip('/')}/log_sql", "SQL", "log_sql",
                    HostHelper.get_host_ip(), project_name,
                    log_config).get_logger()

logger_http = Logger(f"{log_file_path.rstrip('/')}/log_http", "HTTP", "log_http",
                     HostHelper.get_host_ip(), project_name,
                     log_config).get_logger()

# nacos配置获取
nacos_config = config.get_value("nacos", None)

if nacos_config:
    nacos_host = nacos_config["host"]
    nacos_namespace = nacos_config["namespace"]
    nacos_data_id = nacos_config['data_id']
    nacos_group = nacos_config.get("group","DEFAULT_GROUP")
    nacos_username = nacos_config.get("username",None)
    nacos_password = nacos_config.get("password",None)

    if not nacos_host or not nacos_namespace or not nacos_data_id or not nacos_group:
        raise Exception("nacos配置错误")
    try:
        nacos_client = NacosClient(server_addresses=nacos_host,namespace=nacos_namespace,username=nacos_username,password=nacos_password)

        nacos_client.add_naming_instance(nacos_data_id, HostHelper.get_host_ip(), int(config.get_value("run_port")),heartbeat_interval=5,group_name=nacos_group)

        # 从Nacos获取配置，并更新到Flask应用的config对象中，以便在应用中使用这些配置
        config_content = nacos_client.get_config(data_id=nacos_data_id, group=nacos_group)
        config.init_config_from_nacos(config_file, config_content)
    except Exception as ex:
        logger_error.error(f"nacos连接失败:{ex},将使用本地配置。")
        config.init_config(config_file)
    # 添加配置监听器，当Nacos中的配置发生变化时，自动更新Flask应用的config对象
    try:
        nacos_client.add_config_watcher(data_id=nacos_data_id, group=nacos_group,
                                    cb=lambda cfg: config.init_config_from_nacos(config_file, cfg["content"]))
    except:
        pass

# 验证Lisence
if environment == "production" and config.get_value("not_lisence", False) != True:
    if not project_name:
        raise Exception("config.json必须配置project_name")

    dir_hash = CryptoHelper.get_dir_hash(
        ".", only_dirs=["handlers", "libs", "utils", "static", "templates"])

    lisence_response = HTTPHelper.get(
        f"https://lisence-py.gao7.com/lisence?project_name={project_name}&dir_hash={dir_hash}")

    if lisence_response.status_code == 200:
        lisence = json.loads(lisence_response.text)

        if lisence["result"] == 0:
            raise Exception(lisence["desc"])
