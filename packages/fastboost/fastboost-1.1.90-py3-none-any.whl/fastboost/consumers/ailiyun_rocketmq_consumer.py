# -*- coding: utf-8 -*-
import time
from fastboost.constant import BrokerEnum
from fastboost.consumers.base_consumer import AbstractConsumer
from fastboost.funboost_config_deafult import BrokerConnConfig
from fastboost.core.func_params_model import PublisherParams
from fastboost.publishers.aliyun_rocketmq_publisher import AliyunRocketmqPublisher

logger = __import__('logging').getLogger(__name__)


class AliyunRocketmqConsumer(AbstractConsumer):
    """
    支持阿里云 RocketMQ 的消费者类（使用 SimpleConsumer 实现）。
    """

    GROUP_ID_PREFIX = 'GID-'  # 阿里云要求 Group ID 以 GID- 开头

    def _shedual_task(self):
        try:
            from rocketmq import SimpleConsumer, ClientConfiguration, Credentials, Producer, Message
        except ImportError as e:
            logger.error(f"无法导入 RocketMQ 模块: {e}")
            raise ImportError("请先安装阿里云 RocketMQ SDK: alibabacloud-rocketmq") from e

        group_id = f'{self.GROUP_ID_PREFIX}{self._queue_name}'
        topic = self._queue_name

        # 构造认证信息
        credentials = Credentials(
            access_key_id=self.ALIYUN_ROCKETMQ_ACCESS_KEY,
            access_key_secret=self.ALIYUN_ROCKETMQ_SECRET_KEY
        )

        endpoints = self.ALIYUN_ROCKETMQ_NAMESRV_ADDR


        # 构建客户端配置
        config = ClientConfiguration(
            endpoints=endpoints,
            credential=credentials,
            instance_id=self.ALIYUN_ROCKETMQ_INSTANCE_ID
        )

        # 创建 SimpleConsumer
        simple_consumer = SimpleConsumer(config, group_id)

        # 初始化消息重发 publisher
        self._publisher = AliyunRocketmqPublisher(publisher_params=PublisherParams(queue_name=self._queue_name))

        try:
            simple_consumer.startup()
            simple_consumer.subscribe(topic)
            self.logger.info(f"阿里云 RocketMQ 消费者已启动，监听主题 [{topic}]")
            while True:
                try:
                    messages = simple_consumer.receive(max_message_num=32, wait_seconds=15)
                    if messages:
                        self.logger.debug(f"收到 {len(messages)} 条消息")
                        for msg in messages:
                            try:
                                body = msg.body.decode('utf-8')
                                self.logger.debug(f'从阿里云 RocketMQ 的 [{topic}] 主题中取出消息: {body}')
                                kw = {'body': body, 'rocketmq_msg': msg}
                                self._submit_task(kw)
                                simple_consumer.ack(msg)
                                self.logger.info(f"消息 [{msg.message_id}] 已确认消费成功")
                            except Exception as e:
                                self.logger.error(f"处理消息失败: {e}", exc_info=True)
                                self._requeue(kw)
                except Exception as e:
                    self.logger.error(f"接收或确认消息异常: {e}", exc_info=True)
        except Exception as e:
            self.logger.error(f"订阅主题 [{topic}] 异常: {e}", exc_info=True)
        finally:
            simple_consumer.shutdown()

    def _confirm_consume(self, kw):
        pass  # 已在 _shedual_task 中处理

    def _requeue(self, kw):
        self._publisher.publish(kw['body'])