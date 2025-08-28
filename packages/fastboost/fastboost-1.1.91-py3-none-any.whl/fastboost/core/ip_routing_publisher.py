# coding=utf8
"""
IP路由发布者扩展模块
为Publisher类提供IP感知任务发布能力，支持多Redis DB
"""

import json
import typing
from functools import wraps

from fastboost.core.loggers import flogger
from fastboost.core.redis_db_manager import RedisDBManagerMixin
from fastboost.core.ip_router import IPRouter


class IPRoutingPublisherMixin(RedisDBManagerMixin):
    """
    IP路由发布者Mixin类
    为Publisher类提供IP感知任务发布能力
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._ip_router = None

    def _get_ip_router(self) -> IPRouter:
        """获取IP路由器实例"""
        if self._ip_router is None:
            boost_params = getattr(self, 'publisher_params', None) or getattr(self, 'boost_params', None)
            self._ip_router = IPRouter(boost_params)
        return self._ip_router

    def publish_to_ip(self, target_ip: str, *args, strategy: str = 'strict', **kwargs) -> bool:
        """
        发布任务到指定IP的消费者

        Args:
            target_ip: 目标IP地址
            *args: 任务参数
            strategy: 路由策略 ('strict', 'fallback', 'load_balance')
            **kwargs: 任务关键字参数

        Returns:
            发布是否成功
        """
        try:
            # 构建任务数据
            task_data = {
                'args': args,
                'kwargs': kwargs,
                'target_ip': target_ip,
                'strategy': strategy
            }

            # 使用IP路由器路由任务
            router = self._get_ip_router()
            return router.route_task_to_ip(target_ip, task_data, strategy)

        except Exception as e:
            flogger.error(f"发布任务到IP {target_ip} 失败: {e}")
            return False

    def get_ip_consumer_stats(self) -> dict:
        """获取IP消费者统计信息"""
        try:
            router = self._get_ip_router()
            return router.get_consumer_stats()
        except Exception as e:
            flogger.error(f"获取IP消费者统计信息失败: {e}")
            return {'error': str(e)}


class IPRoutingHelper:
    """
    IP路由辅助工具类
    提供便捷的IP路由功能
    """

    @staticmethod
    def create_ip_routing_decorator(target_ip: str, strategy: str = 'strict'):
        """
        创建IP路由装饰器

        Args:
            target_ip: 目标IP地址
            strategy: 路由策略

        Returns:
            装饰器函数
        """

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # 这里需要获取当前的发布者实例来发布任务
                # 实际使用时需要结合具体的发布者实现
                flogger.info(f"任务 {func.__name__} 将被路由到IP: {target_ip}, 策略: {strategy}")
                return func(*args, **kwargs)

            # 添加路由信息到函数属性
            wrapper._ip_routing_target = target_ip
            wrapper._ip_routing_strategy = strategy
            return wrapper

        return decorator

    @staticmethod
    def get_available_ips(boost_params) -> typing.List[str]:
        """
        获取可用的消费者IP列表

        Args:
            boost_params: BoosterParams参数对象

        Returns:
            可用IP列表
        """
        try:
            router = IPRouter(boost_params)
            active_consumers = router.get_active_consumers()
            return list(set(consumer.ip_address for consumer in active_consumers))
        except Exception as e:
            flogger.error(f"获取可用IP列表失败: {e}")
            return []

    @staticmethod
    def validate_ip_availability(target_ip: str, boost_params) -> bool:
        """
        验证目标IP是否有可用的消费者

        Args:
            target_ip: 目标IP地址
            boost_params: BoosterParams参数对象

        Returns:
            IP是否可用
        """
        try:
            router = IPRouter(boost_params)
            target_consumers = router.get_consumers_by_ip(target_ip)
            return len(target_consumers) > 0
        except Exception as e:
            flogger.error(f"验证IP可用性失败: {e}")
            return False


# 便捷的装饰器函数
def route_to_ip(target_ip: str, strategy: str = 'strict'):
    """
    IP路由装饰器

    Args:
        target_ip: 目标IP地址
        strategy: 路由策略 ('strict', 'fallback', 'load_balance')

    Returns:
        装饰器函数

    Usage:
        @route_to_ip('192.168.1.100', strategy='fallback')
        @boost('my_queue', enable_ip_routing=True)
        def my_task(a, b):
            return a + b
    """
    return IPRoutingHelper.create_ip_routing_decorator(target_ip, strategy)


def route_to_gpu_server(strategy: str = 'strict'):
    """
    路由到GPU服务器的装饰器

    Args:
        strategy: 路由策略

    Returns:
        装饰器函数
    """
    # 这里可以配置GPU服务器的IP地址
    # 实际使用时可以从配置文件或环境变量中读取
    gpu_server_ip = '192.168.1.200'  # 示例GPU服务器IP
    return route_to_ip(gpu_server_ip, strategy)


def route_to_cpu_server(strategy: str = 'fallback'):
    """
    路由到CPU服务器的装饰器

    Args:
        strategy: 路由策略

    Returns:
        装饰器函数
    """
    # 这里可以配置CPU服务器的IP地址
    cpu_server_ip = '192.168.1.100'  # 示例CPU服务器IP
    return route_to_ip(cpu_server_ip, strategy)


class IPRoutingQueue:
    """
    IP路由队列管理器
    管理不同IP的专用队列
    """

    def __init__(self, boost_params):
        self.boost_params = boost_params
        self.router = IPRouter(boost_params)

    def create_ip_queue(self, target_ip: str, consumer_id: str) -> str:
        """
        为指定IP和消费者创建专用队列

        Args:
            target_ip: 目标IP地址
            consumer_id: 消费者ID

        Returns:
            队列名称
        """
        queue_name = f"{self.boost_params.queue_name}:ip:{target_ip}:{consumer_id}"
        return queue_name

    def get_ip_queues(self, target_ip: str) -> typing.List[str]:
        """
        获取指定IP的所有队列

        Args:
            target_ip: 目标IP地址

        Returns:
            队列名称列表
        """
        try:
            consumers = self.router.get_consumers_by_ip(target_ip)
            return [self.create_ip_queue(target_ip, consumer.consumer_id) for consumer in consumers]
        except Exception as e:
            flogger.error(f"获取IP队列失败: {e}")
            return []

    def cleanup_expired_queues(self):
        """清理过期的IP队列"""
        try:
            # 获取所有活跃消费者
            active_consumers = self.router.get_active_consumers()
            active_queue_names = set()

            for consumer in active_consumers:
                queue_name = self.create_ip_queue(consumer.ip_address, consumer.consumer_id)
                active_queue_names.add(queue_name)

            # 这里可以添加清理逻辑，删除不再活跃的队列
            # 具体实现取决于使用的消息队列中间件
            flogger.info(f"活跃IP队列数量: {len(active_queue_names)}")

        except Exception as e:
            flogger.error(f"清理过期队列失败: {e}")


if __name__ == '__main__':
    # 测试代码
    from fastboost.core.func_params_model import BoosterParams

    # 创建测试参数
    params = BoosterParams(
        queue_name='test_ip_routing_queue',
        enable_ip_routing=True,
        ip_routing_heartbeat_interval=10,
        redis_db=0
    )

    # 测试IP路由辅助工具
    helper = IPRoutingHelper()

    # 获取可用IP列表
    available_ips = helper.get_available_ips(params)
    print(f"可用IP列表: {available_ips}")

    # 测试IP可用性验证
    if available_ips:
        test_ip = available_ips[0]
        is_available = helper.validate_ip_availability(test_ip, params)
        print(f"IP {test_ip} 可用性: {is_available}")

    # 测试IP路由队列管理器
    queue_manager = IPRoutingQueue(params)

    if available_ips:
        test_ip = available_ips[0]
        ip_queues = queue_manager.get_ip_queues(test_ip)
        print(f"IP {test_ip} 的队列: {ip_queues}")

    # 清理过期队列
    queue_manager.cleanup_expired_queues()

    print("IP路由发布者扩展测试完成")
