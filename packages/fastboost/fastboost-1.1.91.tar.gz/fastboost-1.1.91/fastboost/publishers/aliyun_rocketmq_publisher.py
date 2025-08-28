# -*- coding: utf-8 -*-
import threading
import time
import atexit
from typing import Dict, Optional, Set

from fastboost.funboost_config_deafult import BrokerConnConfig
from fastboost.publishers.base_publisher import AbstractPublisher
from logging import getLogger

logger = getLogger(__name__)


class AliyunRocketmqPublisher(AbstractPublisher):
    """
    阿里云RocketMQ发布者实现，支持连接池和自动关闭
    """
    # 全局连接池，用于在多个发布者实例间共享连接
    _producer_pool: Dict[str, 'Producer'] = {}
    _lock = threading.Lock()
    _is_shutdown_hook_registered = False
    _instances: Set['AliyunRocketmqPublisher'] = set()  # 跟踪所有实例，便于全局管理

    def custom_init(self):
        """初始化阿里云RocketMQ发布者"""
        try:
            from rocketmq import ClientConfiguration, Credentials, Message, Producer
        except ImportError as e:
            raise ImportError("请先安装阿里云 RocketMQ SDK: pip install alibabacloud-rocketmq") from e

        # 获取配置参数
        access_key = BrokerConnConfig.ALIYUN_ROCKETMQ_ACCESS_KEY
        secret_key = BrokerConnConfig.ALIYUN_ROCKETMQ_SECRET_KEY
        endpoint = BrokerConnConfig.ALIYUN_ROCKETMQ_NAMESRV_ADDR
        instance_id = getattr(BrokerConnConfig, 'ALIYUN_ROCKETMQ_INSTANCE_ID', None)

        # 构造连接池键（用于区分不同配置的生产者）
        pool_key = f"{instance_id or 'default'}/{self._queue_name}"
        self._pool_key = pool_key

        with self._lock:
            # 注册全局退出钩子（只需注册一次）
            if not self.__class__._is_shutdown_hook_registered:
                atexit.register(self.__class__._shutdown_all)
                self.__class__._is_shutdown_hook_registered = True
                self.logger.debug("已注册全局退出钩子，程序结束时将自动关闭所有RocketMQ连接")
            
            # 添加实例到全局跟踪集合
            self.__class__._instances.add(self)

            # 从连接池获取或创建生产者
            if pool_key not in self._producer_pool:
                # 构造认证信息
                credentials = Credentials(ak=access_key, sk=secret_key)

                # 构建客户端配置
                config = ClientConfiguration(
                    endpoints=endpoint,
                    credentials=credentials,
                    namespace=instance_id or ""
                )

                # 创建生产者
                producer = Producer(config, topics=(self._queue_name,))

                try:
                    producer.startup()
                    self._producer_pool[pool_key] = producer
                    self.logger.info(f"创建并启动RocketMQ生产者成功：{pool_key}")
                except Exception as e:
                    self.logger.error(f"启动RocketMQ生产者失败: {e}", exc_info=True)
                    raise
            else:
                self.logger.debug(f"复用已有的RocketMQ生产者：{pool_key}")

            # 设置实例属性
            self._producer = self._producer_pool[pool_key]

    def concrete_realization_of_publish(self, msg: str):
        """发送消息到阿里云RocketMQ"""
        try:
            from rocketmq.client import Message
        except ImportError as e:
            self.logger.error(f"加载RocketMQ模块失败: {e}")
            raise ImportError(f'阿里云RocketMQ包未正确安装: {str(e)}') from e

        # 创建消息对象 - 修复：传入topic参数
        rocket_msg = Message(self._queue_name)
        rocket_msg.body = msg.encode('utf-8')

        # 设置TAG
        if getattr(self, '_tag', None):
            rocket_msg.tag = self._tag
        else:
            rocket_msg.tag = "DEFAULT_TAG"

        # 设置KEY
        rocket_msg.keys = "FASTBOOST_MSG"

        # 设置必要的属性，解决AttributeError
        rocket_msg.message_group = None
        rocket_msg.delivery_timestamp = None
        rocket_msg.topic = self._queue_name
        rocket_msg.properties = {}

        # 发送消息
        try:
            result = self._producer.send(rocket_msg)
            # SendReceipt对象没有status属性，只要没有异常就表示发送成功
            self.logger.debug(f"消息发送成功: {getattr(result, 'msg_id', str(result))}")
        except Exception as e:
            self.logger.error(f"发送消息异常: {e}", exc_info=True)
            raise

    def clear(self):
        """清除队列（阿里云RocketMQ不支持此操作）"""
        self.logger.warning('清除队列暂不支持，阿里云SDK无相关API')

    def get_message_count(self):
        """获取队列中的消息数量（阿里云RocketMQ不支持此操作）"""
        self.logger.warning('获取消息数量暂不支持，阿里云SDK无相关API')
        return -1

    def close(self):
        """关闭当前生产者实例（仅释放引用，不实际关闭连接）"""
        if hasattr(self, '_producer'):
            self._producer = None
            self.logger.debug(f"已释放生产者引用")
            # 从全局跟踪集合中移除自身
            with self._lock:
                if self in self.__class__._instances:
                    self.__class__._instances.remove(self)

    @classmethod
    def _shutdown_all(cls):
        """关闭所有生产者（程序退出时调用）"""
        logger.info("开始关闭所有RocketMQ生产者...")
        with cls._lock:
            # 关闭所有连接池中的生产者
            for key, producer in list(cls._producer_pool.items()):
                try:
                    producer.shutdown()
                    logger.info(f"已关闭RocketMQ生产者: {key}")
                except Exception as e:
                    logger.warning(f"关闭RocketMQ生产者异常: {e}")
            cls._producer_pool.clear()
            
            # 清空实例集合
            cls._instances.clear()
        logger.info("所有RocketMQ生产者已关闭")

    def _at_exit(self):
        """框架退出时调用，与AbstractPublisher._at_exit集成"""
        self.logger.info(f"RocketMQ发布者{self._queue_name}正在退出，释放资源...")
        self.close()

    def __del__(self):
        """析构函数，释放资源"""
        self.close()  # 只释放引用，不关闭连接（由_shutdown_all统一处理）