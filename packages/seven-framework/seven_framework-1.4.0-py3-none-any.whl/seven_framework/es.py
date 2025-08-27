# -*- coding: utf-8 -*-
"""
:Author: ChenXiaolei
:Date: 2020-04-16 14:38:22
:LastEditTime: 2024-03-07 16:00:34
:LastEditors: ChenXiaolei
:Description: 
"""
from elasticsearch import Elasticsearch


class ESHelper:
    """
    Elasticsearch二次封装操作类 
    """

    def __init__(self,
                 host=None,
                 port=None,
                 index=None,
                 auth_username=None,
                 auth_password=None,
                 config_dict=None):

        if config_dict:
            if 'host' in config_dict:
                host = config_dict.get('host')

            if 'port' in config_dict:
                port = config_dict.get('port')

            if 'index' in config_dict:
                index = config_dict.get('index')

            if 'auth_username' in config_dict:
                auth_username = config_dict.get('auth_username')

            if 'auth_password' in config_dict:
                auth_password = config_dict.get('auth_password')

        if not auth_username:
            auth_username = ''

        if not auth_password:
            auth_password = ''

        self._es_client = Elasticsearch(host,
                                        http_auth=(auth_username,
                                                   auth_password),
                                        port=port)
        """
        :Description: Elasticsearch 初始化
        :param host:集群host
        :param port:端口
        :param index:ES索引
        :param auth_username:授权用户名
        :param auth_password:授权密码
        :return: ESHelper类
        :last_editors: ChenXiaolei
        """
        if index:
            self.index = index

    def _get_index(self, index):
        """
        :Description: 判断传参index是否为空，如果为空则从初始化属性获取
        :param index: es_index
        :return: es_index
        :last_editors: ChenXiaolei
        """
        if not index:
            if not self.index:
                raise Exception("index is not configured")
            return self.index
        return index

    def get_es_client(self):
        """
        :Description: 获得es原始客户端对象
        :param 无
        :return: es客户端对象
        :last_editors: ChenXiaolei
        """
        return self._es_client

    def insert(self, body, index=None, id=None):
        """
        :Description: 写入数据
        :param body: doc 字典数据类型
        :return: 执行返回结果
        :last_editors: ChenXiaolei
        """
        return self._es_client.index(index=self._get_index(index),
                                     body=body,
                                     id=id)

    def bulk(self, body, index=None):
        """
        :Description: 批量操作
            demo:
            body = [{"index":{"_index":"test_index"}}]
            doc = {}
            doc["field"]="value"
            body.append(doc)
            es_client.bulk(body=body)

        :param body: 执行body
        :return: 执行返回结果
        :last_editors: ChenXiaolei
        """
        return self._es_client.bulk(index=self._get_index(index), body=body)

    def delete_by_id(self, id, index=None):
        """
        :Description: 根据es_id删除数据
        :param id: es_id
        :param index: es_index 
        :return: 执行返回结果
        :last_editors: ChenXiaolei
        """
        return self._es_client.delete(index=self._get_index(index), id=id)

    def delete_by_query(self, body, index=None):
        """
        :Description: 根据dsl条件删除数据
        :param body: 执行dsl
        :return: 执行返回结果
        :last_editors: ChenXiaolei
        """
        return self._es_client.delete_by_query(index=self._get_index(index),
                                               body=body)

    def update(self, id, body, index=None):
        """
        :Description: 根据_id更新数据
        :param id: es_id
        :param body: 执行dsl
        :param index: es_index 
        :return: 执行返回结果
        :last_editors: ChenXiaolei
        """
        return self._es_client.update(index=self._get_index(index),
                                      id=id,
                                      body=body)

    def update_by_query(self, body, index=None):
        """
        :Description: 根据dsl条件更新数据
        :param body: 执行dsl
        :param index: es_index 
        :return: 执行返回结果
        :last_editors: ChenXiaolei
        """
        return self._es_client.update_by_query(index=self._get_index(index),
                                               body=body)

    def search(self, body, index=None):
        """
        :Description: 根据dsl查询数据
        :param body: 执行dsl
        :param index: es_index 
        :return: 查询返回结果
        :last_editors: ChenXiaolei
        """
        return self._es_client.search(index=self._get_index(index), body=body)

    def exists_source(self, id, index=None):
        """
        :Description: 根据_id获取数据是否已存在
        :param id: es_id
        :param index: es_index 
        :return: 返回 True or False
        :last_editors: ChenXiaolei
        """
        return self._es_client.exists_source(index=self._get_index(index),
                                             id=id)

    def count(self, body, index=None):
        """
        :description: 返回与查询匹配的文档数量
        :param body: 执行dsl
        :param index: es_index 
        :return 查询返回结果
        :last_editors: ChenXiaolei
        """
        return self._es_client.count(index=self._get_index(index), body=body)

    def get(self, id, index=None):
        """
        :description: 通过_id获取文档
        :param id: _id
        :param index: es_index 
        :return 查询文档内容
        :last_editors: ChenXiaolei
        """
        return self._es_client.get(index=self._get_index(index), id=id)