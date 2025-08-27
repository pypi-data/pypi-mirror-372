# -*- coding: utf-8 -*-
"""
:Author: Kangwenbin
:Date: 2022-05-10 16:22:31
:LastEditTime: 2022-05-18 16:04:35
:LastEditors: ChenXiaolei
:Description: RocketMQHelper
"""
from rocketmq.client import Message, TransactionMQProducer, TransactionStatus, Producer, PushConsumer, ConsumeStatus
from enum import IntEnum
import time


class RocketMQClientType(IntEnum):
    """
    :description: rocketmq 连接类型枚举
    :NORMAL_PRODUCER 标准生产者(可发送同步、单向消息)
    :ORDERLY_PRODUCER 顺序生产者(可发送顺序消息)
    :NORMAL_CONSUMER 标准消费者(可消费除顺序消息外的所有消息)
    :ORDERLY_CONSUMER 顺序消费者(用来消费顺序消息)
    :last_editors: Kangwenbin
    """
    NORMAL_PRODUCER = 0
    ORDERLY_PRODUCER = 1
    NORMAL_CONSUMER = 3
    ORDERLY_CONSUMER = 4


class RocketMQHelper:
    def __init__(self, rocketmq_config, topic, group_id, cliend_type):
        """
        :description: RocketMQ初始化
        :param rocketmq_config 基础配置
        :demo 配置  {
                        "access_key": "sadsdasdasd",
                        "access_secret": "sadsdasdasd",
                        "channel": "" # 身份渠道
                        "name_server": "192.168.xx.xx:1234;192.168.xxx.xxx:1111" # name_server 地址
                    }
        :demo 实例 rocket_conn = RocketMQHelper(rocketmq_config,"topic1","group1",0)
        :param topic 主题
        :param group_id 组id
        :param cliend_type 客户端类型，参考RocketMQClientType
        :last_editors: Kangwenbin
        """
        # 配置验证
        key_list = ["access_key", "access_secret", "channel", "name_server"]
        assert all(map(lambda x: x in rocketmq_config, key_list)
                   ), "RocketMQ配置异常"
        self.group_id = group_id
        self.topic = topic
        self.client = None
        self.cliend_type = cliend_type
        if self.cliend_type == RocketMQClientType.NORMAL_PRODUCER:
            # 标准生产者(可发送sync、oneway消息)
            self.client = Producer(group_id)
        elif self.cliend_type == RocketMQClientType.ORDERLY_PRODUCER:
            # 顺序生产者(可发送orderly消息)
            self.client = Producer(group_id, orderly=True)
        # elif self.cliend_type == RocketMQClientType.TRANSACTION_PRODUCER:
        #     # 事务生产者(可发送事务消息)
        #     self.client = TransactionMQProducer(group_id, self.check_callback)
        elif self.cliend_type == RocketMQClientType.NORMAL_CONSUMER:
            # 标准消费者
            self.client = PushConsumer(group_id)
        elif self.cliend_type == RocketMQClientType.ORDERLY_CONSUMER:
            # 顺序消息消费者
            self.client = PushConsumer(group_id, orderly=True)
        else:
            raise ValueError("客户端类型错误")

        self.client.set_name_server_address(rocketmq_config["name_server"])
        if rocketmq_config["access_key"] and rocketmq_config["access_secret"]:
            self.client.set_session_credentials(
                rocketmq_config["access_key"], rocketmq_config["access_secret"], rocketmq_config["channel"])  # 身份验证

        if self.cliend_type in [RocketMQClientType.NORMAL_PRODUCER, RocketMQClientType.ORDERLY_PRODUCER]:
            self.client.start()

    def create_message(self, msg_key, msg_tag, msg_body):
        """
        :description: 创建消息
        :param msg_key 消息key(业务层面唯一标识，可根据该key查找消息)
        :param msg_tag 消息tag(用于消息过滤)
        :param msg_body 消息内容
        :last_editors: Kangwenbin
        """
        msg = Message(self.topic)
        msg.set_keys(msg_key)
        msg.set_tags(msg_tag)
        msg.set_body(msg_body)
        return msg

    def send_message_sync(self, msg_key, msg_tag, msg_body):
        """
        :description: 发送同步消息
        :param msg_key 消息key(业务层面唯一标识，可根据该key查找消息)
        :param msg_tag 消息tag(用于消息过滤)
        :param msg_body 消息内容
        :last_editors: Kangwenbin
        """
        assert self.cliend_type == RocketMQClientType.NORMAL_PRODUCER, "当前生产者无法发送同步消息"
        msg = self.create_message(msg_key, msg_tag, msg_body)
        ret = self.client.send_sync(msg)
        return ret

    def send_orderly_message(self, msg_key, msg_tag, msg_body, sharding_key):
        """
        :description: 发送顺序消息
        :param msg_key 消息key(业务层面唯一标识，可根据该key查找消息)
        :param msg_tag 消息tag(用于消息过滤)
        :param msg_body 消息内容
        :param sharding_key 顺序队列标识(同一个标识的消息是顺序的)
        :last_editors: Kangwenbin
        """
        assert self.cliend_type == RocketMQClientType.ORDERLY_PRODUCER, "当前生产者无法发送顺序消息"
        msg = self.create_message(msg_key, msg_tag, msg_body)
        msg.set_keys(msg_key)
        msg.set_tags(msg_tag)
        msg.set_body(msg_body)
        ret = self.client.send_orderly_with_sharding_key(msg, sharding_key)
        return ret

    def send_oneway_message(self, msg_key, msg_tag, msg_body):
        """
        :description: 发送单向消息，该消息类别无结果返回
        :param msg_key 消息key(业务层面唯一标识，可根据该key查找消息)
        :param msg_tag 消息tag(用于消息过滤)
        :param msg_body 消息内容
        :last_editors: Kangwenbin
        """
        assert self.cliend_type == RocketMQClientType.NORMAL_PRODUCER, "当前生产者无法发送单向消息"
        msg = self.create_message(msg_key, msg_tag, msg_body)
        ret = self.client.send_oneway(msg)
        return ret

    def start_consumer(self, deal_func, mes_tag):
        """
        :description: 启动消费者
        :param deal_func 消息处理方法，接收唯一参数msg，消费成功返回True，失败返回False
        :param mes_tag 消息过滤标签，不过滤："*"
        :last_editors: Kangwenbin
        """
        def callback(msg):
            ret = deal_func(msg)
            if ret:
                return ConsumeStatus.CONSUME_SUCCESS
            else:
                return ConsumeStatus.RECONSUME_LATER

        self.client.subscribe(self.topic, callback, mes_tag)
        self.client.start()

        while True:
            time.sleep(1)
