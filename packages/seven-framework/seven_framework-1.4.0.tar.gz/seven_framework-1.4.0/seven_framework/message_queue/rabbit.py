# -*- coding: utf-8 -*-
"""
:Author: Kangwenbin
:Date: 2022-04-27 16:38:27
:LastEditTime: 2022-05-18 16:04:26
:LastEditors: ChenXiaolei
:Description: RabbitMQHelper
"""
import pika

class RabbitMQHelper:
    def __init__(self, rabbitmq_config, exchange_name = ""):
        """
        :description: 
        :demo 配置  rabbit_config = {
                        "account":"account",
                        "password":"xxxxxxxx",
                        "host":"192.168.xxx.xxx",
                        "port":"1000",
                        "virtual_host":"xxx",
                        "keepalive": True
                    }
        :demo 实例 rabbit_conn = RabbitMQHelper(rabbit_config,"exchange_name")
        :last_editors: Kangwenbin
        """        
        # 配置验证
        key_list = ["account","password","host","port","virtual_host","keepalive"]
        assert all(map(lambda x: x in rabbitmq_config,key_list)), "RabbitMQ配置异常"

        # 创建凭证，使用rabbitmq用户密码登录 
        self.__credentials = pika.PlainCredentials(rabbitmq_config["account"], rabbitmq_config["password"])

        # 设置心跳时长
        heartbeat = 500
        if not rabbitmq_config["keepalive"]:
            heartbeat = 60

        # 创建rabbitmq连接
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(rabbitmq_config["host"],rabbitmq_config["port"],virtual_host=rabbitmq_config["virtual_host"],credentials=self.__credentials,heartbeat=heartbeat))
        # 创建信道
        self.channel = self.connection.channel()
        self.exchange_name = exchange_name
        

    def create_exchange(self,exchange_name,exchange_mode,durable = True):
        """
        :description: 创建交换机
        :param exchange_name 交换机名称
        :param exchange_mode 交换机路由模式
        :--exchange 3种模式
        :--direct: 只发送routingkey完全匹配队列
        :--topic: 发送模糊routingkey
        :--fanout: 发送所有绑定该交换机的队列
        :param durable 是否持久化
        :last_editors: Kangwenbin
        """    
        # 创建交换机，默认开启持久化
        result = self.channel.exchange_declare(exchange = exchange_name, exchange_type = exchange_mode, durable = durable)
        if result.method.NAME == "Exchange.DeclareOk":
            self.exchange_name = exchange_name
            return True
        return False

            
    def create_queue(self,queue_name,bind_exchange,routing_key,durable = True):
        """
        :description: 创建队列并绑定到exchange
        :param queue_name 队列名称
        :param bind_exchange 绑定交换机名称
        :param routing_key 路由密钥
        :param durable 队列是否需要持久化
        :last_editors: Kangwenbin
        """        
        result = False
        # 声明一个队列，用于接收消息(默认持久化)
        create_result =  self.channel.queue_declare(queue = queue_name,durable = durable)
        if create_result.method.NAME == "Queue.DeclareOk":
            result = True
        # 创建交换机绑定
        if bind_exchange and routing_key and result:
            bind_result = self.channel.queue_bind(queue_name, bind_exchange, routing_key)
            result = True if bind_result.method.NAME == "Queue.BindOk" else False
        return result
        
        
    def push_message(self,routing_key,message):
        """
        :description: 推送消息
        :param exchange 交换机名称
        :param routing_key 路由名称
        :param message 消息内容
        :last_editors: Kangwenbin
        """        

        assert self.exchange_name,"exchange不能为空"
        # 发送消息(默认消息持久化)
        self.channel.basic_publish(exchange = self.exchange_name, routing_key = routing_key, body = message, properties = pika.BasicProperties(delivery_mode = 2))


    def consumer(self,queue_name,deal_func):
        """
        :description: 创建消费者
        :param queue_name 队列名称
        :return deal_func 处理方法 消费成功返回True,失败返回False,如果不传会重复消费
        :last_editors: Kangwenbin
        """        
        # 消息回调方法
        def callback(ch,method,properties,body):
            # 方法处理
            ret = deal_func(body.decode("utf8"))
            # 消息接收确认
            if ret:
                ch.basic_ack(delivery_tag=method.delivery_tag)

        self.channel.basic_consume(queue_name,callback, False)
        # 开始消费，接收消息
        self.channel.start_consuming()


    
    

