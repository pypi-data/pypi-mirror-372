import os
import time
from fastboost.publishers.aliyun_rocketmq_publisher import AliyunRocketmqPublisher
from fastboost.consumers.ailiyun_rocketmq_consumer import AliyunRocketmqConsumer
from fastboost.core.func_params_model import PublisherParams

# 设置必要的环境变量
os.environ['ALIYUN_ROCKETMQ_ACCESS_KEY'] = 'gjk89HdJZ5aJRAUs'
os.environ['ALIYUN_ROCKETMQ_SECRET_KEY'] = 's6S6w27SVa8lf0nq'
os.environ['ALIYUN_ROCKETMQ_NAMESRV_ADDR'] = 'rmq-cn-jte462x811d.cn-shanghai.rmq.aliyuncs.com:8080'
os.environ['ALIYUN_ROCKETMQ_INSTANCE_ID'] = 'rmq-cn-jte462x811d'

def test_rocketmq():
    queue_name = "DEFAULT_TOPIC"
    
    # 创建发布者
    publisher_params = PublisherParams(queue_name=queue_name)
    publisher = AliyunRocketmqPublisher(publisher_params=publisher_params)

    # 创建消费者
    consumer = AliyunRocketmqConsumer()

    try:
        # 启动消费者
        import threading
        consumer_thread = threading.Thread(target=consumer._shedual_task)
        consumer_thread.daemon = True
        consumer_thread.start()

        # 给消费者一些时间来启动
        time.sleep(5)

        # 发布一条测试消息
        test_message = "Hello, Alibaba Cloud RocketMQ!"
        publisher.publish(test_message)
        print("Test message published.")

        # 等待一段时间让消息被消费
        time.sleep(10)

    finally:
        # 清理资源
        publisher.close()
        consumer.close()

if __name__ == "__main__":
    test_rocketmq()
