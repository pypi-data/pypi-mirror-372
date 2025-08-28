import typing
from distutils.command.config import config

# from fastboost.publishers.empty_publisher import EmptyPublisher
# from fastboost.publishers.http_publisher import HTTPPublisher
# from fastboost.publishers.nats_publisher import NatsPublisher
# from fastboost.publishers.peewee_publisher import PeeweePublisher
from fastboost.publishers.redis_publisher_lpush import RedisPublisherLpush
from fastboost.publishers.redis_publisher_priority import RedisPriorityPublisher
from fastboost.publishers.redis_pubsub_publisher import RedisPubSubPublisher
# from fastboost.publishers.tcp_publisher import TCPPublisher
# from fastboost.publishers.txt_file_publisher import TxtFilePublisher
# from fastboost.publishers.udp_publisher import UDPPublisher
# from fastboost.publishers.zeromq_publisher import ZeroMqPublisher
# from fastboost.publishers.kafka_publisher import KafkaPublisher
# from fastboost.publishers.local_python_queue_publisher import LocalPythonQueuePublisher
from fastboost.publishers.mongomq_publisher import MongoMqPublisher

# from fastboost.publishers.persist_queue_publisher import PersistQueuePublisher

from fastboost.publishers.rabbitmq_pika_publisher import RabbitmqPublisher

from fastboost.publishers.redis_publisher import RedisPublisher
from fastboost.publishers.rocketmq_publisher import RocketmqPublisher
from fastboost.publishers.aliyun_rocketmq_publisher import AliyunRocketmqPublisher
# from fastboost.publishers.redis_stream_publisher import RedisStreamPublisher
# from fastboost.publishers.mqtt_publisher import MqttPublisher
# from fastboost.publishers.httpsqs_publisher import HttpsqsPublisher

# from fastboost.consumers.empty_consumer import EmptyConsumer
from fastboost.consumers.redis_consumer_priority import RedisPriorityConsumer
from fastboost.consumers.redis_pubsub_consumer import RedisPbSubConsumer
# from fastboost.consumers.http_consumer import HTTPConsumer
# from fastboost.consumers.kafka_consumer import KafkaConsumer
# from fastboost.consumers.local_python_queue_consumer import LocalPythonQueueConsumer
from fastboost.consumers.mongomq_consumer import MongoMqConsumer
# from fastboost.consumers.nats_consumer import NatsConsumer

# from fastboost.consumers.peewee_conusmer import PeeweeConsumer
# from fastboost.consumers.persist_queue_consumer import PersistQueueConsumer
from fastboost.consumers.rabbitmq_pika_consumer import RabbitmqConsumer

from fastboost.consumers.redis_brpoplpush_consumer import RedisBrpopLpushConsumer
from fastboost.consumers.redis_consumer import RedisConsumer
from fastboost.consumers.redis_consumer_ack_able import RedisConsumerAckAble
from fastboost.consumers.rocketmq_consumer import RocketmqConsumer
from fastboost.consumers.ailiyun_rocketmq_consumer import AliyunRocketmqConsumer
# from fastboost.consumers.redis_stream_consumer import RedisStreamConsumer
# from fastboost.consumers.tcp_consumer import TCPConsumer
# from fastboost.consumers.txt_file_consumer import TxtFileConsumer
# from fastboost.consumers.udp_consumer import UDPConsumer
# from fastboost.consumers.zeromq_consumer import ZeroMqConsumer
# from fastboost.consumers.mqtt_consumer import MqttConsumer
# from fastboost.consumers.httpsqs_consumer import HttpsqsConsumer
from fastboost.consumers.redis_consumer_ack_using_timeout import RedisConsumerAckUsingTimeout

from fastboost.publishers.base_publisher import AbstractPublisher
from fastboost.consumers.base_consumer import AbstractConsumer
from fastboost.constant import BrokerEnum

broker_kind__publsiher_consumer_type_map = {


    BrokerEnum.REDIS: (RedisPublisher, RedisConsumer),
    # BrokerEnum.MEMORY_QUEUE: (LocalPythonQueuePublisher, LocalPythonQueueConsumer),
    BrokerEnum.RABBITMQ_PIKA: (RabbitmqPublisher, RabbitmqConsumer),
    BrokerEnum.MONGOMQ: (MongoMqPublisher, MongoMqConsumer),
    # BrokerEnum.PERSISTQUEUE: (PersistQueuePublisher, PersistQueueConsumer),
    # BrokerEnum.KAFKA: (KafkaPublisher, KafkaConsumer),
    BrokerEnum.REDIS_ACK_ABLE: (RedisPublisher, RedisConsumerAckAble),
    BrokerEnum.REDIS_PRIORITY: (RedisPriorityPublisher, RedisPriorityConsumer),
    BrokerEnum.ROCKETMQ: (RocketmqPublisher, RocketmqConsumer),
    BrokerEnum.ALIYUNROCKETMQ: (AliyunRocketmqPublisher, AliyunRocketmqConsumer),
    # BrokerEnum.REDIS_STREAM: (RedisStreamPublisher, RedisStreamConsumer),
    # BrokerEnum.ZEROMQ: (ZeroMqPublisher, ZeroMqConsumer),
    BrokerEnum.RedisBrpopLpush: (RedisPublisherLpush, RedisBrpopLpushConsumer),
    # BrokerEnum.MQTT: (MqttPublisher, MqttConsumer),
    # BrokerEnum.HTTPSQS: (HttpsqsPublisher, HttpsqsConsumer),
    # BrokerEnum.UDP: (UDPPublisher, UDPConsumer),
    # BrokerEnum.TCP: (TCPPublisher, TCPConsumer),
    # BrokerEnum.HTTP: (HTTPPublisher, HTTPConsumer),
    # BrokerEnum.NATS: (NatsPublisher, NatsConsumer),
    # BrokerEnum.TXT_FILE: (TxtFilePublisher, TxtFileConsumer),
    # BrokerEnum.PEEWEE: (PeeweePublisher, PeeweeConsumer),
    BrokerEnum.REDIS_PUBSUB: (RedisPubSubPublisher, RedisPbSubConsumer),
    BrokerEnum.REIDS_ACK_USING_TIMEOUT: (RedisPublisher, RedisConsumerAckUsingTimeout),
    # BrokerEnum.EMPTY:(EmptyPublisher,EmptyConsumer),

}

for broker_kindx, cls_tuple in broker_kind__publsiher_consumer_type_map.items():
    cls_tuple[1].BROKER_KIND = broker_kindx


def register_custom_broker(broker_kind, publisher_class: typing.Type[AbstractPublisher], consumer_class: typing.Type[AbstractConsumer]):
    """
    动态注册中间件到框架中， 方便的增加中间件类型或者修改是自定义消费者逻辑。
    :param broker_kind:
    :param publisher_class:
    :param consumer_class:
    :return:
    """
    if not issubclass(publisher_class, AbstractPublisher):
        raise TypeError(f'publisher_class 必须是 AbstractPublisher 的子或孙类')
    if not issubclass(consumer_class, AbstractConsumer):
        raise TypeError(f'consumer_class 必须是 AbstractConsumer 的子或孙类')
    broker_kind__publsiher_consumer_type_map[broker_kind] = (publisher_class, consumer_class)
    consumer_class.BROKER_KIND = broker_kind


def regist_to_funboost(broker_kind: str):
    """
    延迟导入是因为funboost没有pip自动安装这些三方包，防止一启动就报错。
    这样当用户需要使用某些三方包中间件作为消息队列时候，按照import报错信息，用户自己去pip安装好。或者 pip install funboost[all] 一次性安装所有中间件。
    建议按照 https://github.com/ydf0509/funboost/blob/master/setup.py 中的 extra_brokers 和 install_requires 里面的版本号来安装三方包版本.
    """
    if broker_kind == BrokerEnum.RABBITMQ_AMQPSTORM:
        from fastboost.publishers.rabbitmq_amqpstorm_publisher import RabbitmqPublisherUsingAmqpStorm
        from fastboost.consumers.rabbitmq_amqpstorm_consumer import RabbitmqConsumerAmqpStorm
        register_custom_broker(BrokerEnum.RABBITMQ_AMQPSTORM, RabbitmqPublisherUsingAmqpStorm, RabbitmqConsumerAmqpStorm)

    # if broker_kind == BrokerEnum.RABBITMQ_RABBITPY:
    #     from fastboost.publishers.rabbitmq_rabbitpy_publisher import RabbitmqPublisherUsingRabbitpy
    #     from fastboost.consumers.rabbitmq_rabbitpy_consumer import RabbitmqConsumerRabbitpy
    #     register_custom_broker(BrokerEnum.RABBITMQ_RABBITPY, RabbitmqPublisherUsingRabbitpy, RabbitmqConsumerRabbitpy)
    #
    # if broker_kind == BrokerEnum.PULSAR:
    #     from fastboost.consumers.pulsar_consumer import PulsarConsumer
    #     from fastboost.publishers.pulsar_publisher import PulsarPublisher
    #     register_custom_broker(BrokerEnum.PULSAR, PulsarPublisher, PulsarConsumer)
    #
    # if broker_kind == BrokerEnum.CELERY:
    #     from fastboost.consumers.celery_consumer import CeleryConsumer
    #     from fastboost.publishers.celery_publisher import CeleryPublisher
    #     register_custom_broker(BrokerEnum.CELERY, CeleryPublisher, CeleryConsumer)
    #
    # if broker_kind == BrokerEnum.NAMEKO:
    #     from fastboost.consumers.nameko_consumer import NamekoConsumer
    #     from fastboost.publishers.nameko_publisher import NamekoPublisher
    #     register_custom_broker(BrokerEnum.NAMEKO, NamekoPublisher, NamekoConsumer)
    #
    # if broker_kind == BrokerEnum.SQLACHEMY:
    #     from fastboost.consumers.sqlachemy_consumer import SqlachemyConsumer
    #     from fastboost.publishers.sqla_queue_publisher import SqlachemyQueuePublisher
    #     register_custom_broker(BrokerEnum.SQLACHEMY, SqlachemyQueuePublisher, SqlachemyConsumer)

    # if broker_kind == BrokerEnum.DRAMATIQ:
    #     from fastboost.consumers.dramatiq_consumer import DramatiqConsumer
    #     from fastboost.publishers.dramatiq_publisher import DramatiqPublisher
    #     register_custom_broker(BrokerEnum.DRAMATIQ, DramatiqPublisher, DramatiqConsumer)
    #
    # if broker_kind == BrokerEnum.HUEY:
    #     from fastboost.consumers.huey_consumer import HueyConsumer
    #     from fastboost.publishers.huey_publisher import HueyPublisher
    #     register_custom_broker(BrokerEnum.HUEY, HueyPublisher, HueyConsumer)
    #
    # if broker_kind == BrokerEnum.KAFKA_CONFLUENT:
    #     from fastboost.consumers.kafka_consumer_manually_commit import KafkaConsumerManuallyCommit
    #     from fastboost.publishers.confluent_kafka_publisher import ConfluentKafkaPublisher
    #     register_custom_broker(BrokerEnum.KAFKA_CONFLUENT, ConfluentKafkaPublisher, KafkaConsumerManuallyCommit)
    #
    # if broker_kind == BrokerEnum.KAFKA_CONFLUENT_SASlPlAIN:
    #     from fastboost.consumers.kafka_consumer_manually_commit import SaslPlainKafkaConsumer
    #     from fastboost.publishers.confluent_kafka_publisher import SaslPlainKafkaPublisher
    #     register_custom_broker(broker_kind, SaslPlainKafkaPublisher, SaslPlainKafkaConsumer)
    #
    # if broker_kind == BrokerEnum.RQ:
    #     from fastboost.consumers.rq_consumer import RqConsumer
    #     from fastboost.publishers.rq_publisher import RqPublisher
    #     register_custom_broker(broker_kind, RqPublisher, RqConsumer)
    #
    # if broker_kind == BrokerEnum.KOMBU:
    #     from fastboost.consumers.kombu_consumer import KombuConsumer
    #     from fastboost.publishers.kombu_publisher import KombuPublisher
    #     register_custom_broker(broker_kind, KombuPublisher, KombuConsumer)
    #
    # if broker_kind == BrokerEnum.NSQ:
    #     from fastboost.publishers.nsq_publisher import NsqPublisher
    #     from fastboost.consumers.nsq_consumer import NsqConsumer
    #     register_custom_broker(broker_kind, NsqPublisher, NsqConsumer)


if __name__ == '__main__':
    import sys

    print(sys.modules)
