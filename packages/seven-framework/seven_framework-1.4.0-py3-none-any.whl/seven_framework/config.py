# -*- coding: utf-8 -*-
"""
:Author: ChenXiaolei
:Date: 2020-03-21 18:29:31
:LastEditTime: 2024-12-13 17:32:28
:LastEditors: ChenXiaolei
:Description: 全局配置
"""

import os
import json

import threading
_lock = threading.Condition()


def init_config(path):
    """
    :Description: 初始化配置文件
    :param path: 配置文件路径，可使用物理路径或url
    :return: global app_config
    :last_editors: ChenXiaolei
    """    
    if path.lower().find("http://") > -1:
        import requests
        json_str = requests.get(path)
    else:
        with open(path, "r+", encoding="utf-8") as f:
            json_str = f.read()
    global app_config
    app_config = json.loads(json_str)

def init_config_from_nacos(config_file, config_content):
    """
    :Description: 初始化配置文件
    :param path: 配置文件路径，可使用物理路径或url
    :return: global app_config
    :last_editors: ChenXiaolei
    """    
    print(f"成功获取nacos配置，并替换本地配置文件{config_file}")

    global app_config
    
    app_config = json.loads(config_content)
    # 改写配置config.json只保留nacos键值，其他替换成app_config内容。
    with open(config_file, "r+", encoding="utf-8") as f:
        json_str = f.read()
        local_config = json.loads(json_str)
        if "nacos" in local_config:
            app_config["nacos"] = local_config["nacos"]
            with open(config_file, "w", encoding="utf-8") as f:
                f.write(json.dumps(app_config, indent=4, ensure_ascii=False))

def set_value(key, value):
    """
    :Description: 设置一个全局键值配置
    :param key:参数键名
    :param value:参数值
    :return: 无
    :last_editors: ChenXiaolei
    """    
    _lock.acquire()
    try:
        app_config[key] = value
    except:
        raise
    finally:
        _lock.release()


def get_value(key, default_value=None):
    """
    :Description: 获得一个全局变量,不存在则返回默认值
    :param key:参数键名
    :param default_value:获取不到返回的默认值
    :return: 参数值
    :last_editors: ChenXiaolei
    """
    try:
        _lock.acquire()
        config_value = app_config[key]
    except KeyError:
        # print(f"config未获取key[{key}]的配置")
        config_value = default_value
    finally:
        _lock.release()

    return config_value