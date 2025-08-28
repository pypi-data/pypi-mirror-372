# coding=utf8
"""
IP感知路由器 - 支持多Redis DB的消费者路由系统
基于Redis实现消费者注册、心跳监控和任务路由功能
"""

import json
import socket
import time
import typing
from threading import Thread, Event
from dataclasses import dataclass, asdict

from fastboost.core.loggers import flogger
from fastboost.core.redis_db_manager import RedisDBManagerMixin


@dataclass
class ConsumerInfo:
    """消费者信息数据类"""
    consumer_id: str
    ip_address: str
    queue_name: str
    hostname: str
    process_id: int
    thread_id: int
    start_time: float
    last_heartbeat: float
    status: str = 'active'  # active, inactive, offline

    def to_dict(self) -> dict:
        """转换为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'ConsumerInfo':
        """从字典创建实例"""
        return cls(**data)


class IPRouter(RedisDBManagerMixin):
    """
    IP感知路由器

    功能：
    1. 消费者注册和心跳管理
    2. 基于IP的任务路由
    3. 多Redis DB支持
    4. 消费者状态监控
    5. 路由策略实现
    """

    def __init__(self, boost_params=None):
        super().__init__()
        self.boost_params = boost_params
        self.queue_name = boost_params.queue_name if boost_params else 'default'

        # IP路由配置
        self.enable_ip_routing = getattr(boost_params, 'enable_ip_routing', False) if boost_params else False
        self.heartbeat_interval = getattr(boost_params, 'ip_routing_heartbeat_interval', 30) if boost_params else 30
        self.consumer_timeout = getattr(boost_params, 'ip_routing_consumer_timeout', 90) if boost_params else 90
        self.redis_key_prefix = getattr(boost_params, 'ip_routing_redis_key_prefix', 'fastboost:ip_routing') if boost_params else 'fastboost:ip_routing'

        # 获取本机IP
        self.local_ip = self._get_local_ip()

        # 心跳线程控制
        self._heartbeat_thread = None
        self._heartbeat_stop_event = Event()
        self._is_registered = False

        # Redis键名
        self._consumer_registry_key = f"{self.redis_key_prefix}:consumers:{self.queue_name}"
        self._consumer_heartbeat_key = f"{self.redis_key_prefix}:heartbeat:{self.queue_name}"
        self._routing_queue_key = f"{self.redis_key_prefix}:routing:{self.queue_name}"

    def _get_local_ip(self) -> str:
        """获取本机IP地址"""
        try:
            # 创建一个UDP socket来获取本机IP
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(('8.8.8.8', 80))
                return s.getsockname()[0]
        except Exception:
            return '127.0.0.1'

    def register_consumer(self, consumer_id: str) -> bool:
        """
        注册消费者

        Args:
            consumer_id: 消费者唯一标识

        Returns:
            注册是否成功
        """
        if not self.enable_ip_routing:
            return True

        try:
            redis_client = self.get_ip_routing_redis_client(self.boost_params)

            # 创建消费者信息
            consumer_info = ConsumerInfo(
                consumer_id=consumer_id,
                ip_address=self.local_ip,
                queue_name=self.queue_name,
                hostname=socket.gethostname(),
                process_id=os.getpid(),
                thread_id=threading.current_thread().ident,
                start_time=time.time(),
                last_heartbeat=time.time(),
                status='active'
            )

            # 注册到Redis
            redis_client.hset(
                self._consumer_registry_key,
                consumer_id,
                json.dumps(consumer_info.to_dict())
            )

            # 设置心跳
            redis_client.hset(
                self._consumer_heartbeat_key,
                consumer_id,
                time.time()
            )

            self._is_registered = True
            flogger.info(f"消费者注册成功: {consumer_id} @ {self.local_ip}")
            return True

        except Exception as e:
            flogger.error(f"消费者注册失败: {e}")
            return False

    def unregister_consumer(self, consumer_id: str) -> bool:
        """
        注销消费者

        Args:
            consumer_id: 消费者唯一标识

        Returns:
            注销是否成功
        """
        if not self.enable_ip_routing:
            return True

        try:
            redis_client = self.get_ip_routing_redis_client(self.boost_params)

            # 从注册表删除
            redis_client.hdel(self._consumer_registry_key, consumer_id)
            redis_client.hdel(self._consumer_heartbeat_key, consumer_id)

            self._is_registered = False
            flogger.info(f"消费者注销成功: {consumer_id}")
            return True

        except Exception as e:
            flogger.error(f"消费者注销失败: {e}")
            return False

    def start_heartbeat(self, consumer_id: str):
        """
        启动心跳线程

        Args:
            consumer_id: 消费者唯一标识
        """
        if not self.enable_ip_routing or self._heartbeat_thread:
            return

        self._heartbeat_stop_event.clear()
        self._heartbeat_thread = Thread(
            target=self._heartbeat_worker,
            args=(consumer_id,),
            daemon=True,
            name=f"IPRouter-Heartbeat-{consumer_id}"
        )
        self._heartbeat_thread.start()
        flogger.debug(f"心跳线程已启动: {consumer_id}")

    def stop_heartbeat(self):
        """停止心跳线程"""
        if self._heartbeat_thread:
            self._heartbeat_stop_event.set()
            self._heartbeat_thread.join(timeout=5)
            self._heartbeat_thread = None
            flogger.debug("心跳线程已停止")

    def _heartbeat_worker(self, consumer_id: str):
        """心跳工作线程"""
        while not self._heartbeat_stop_event.wait(self.heartbeat_interval):
            try:
                self._send_heartbeat(consumer_id)
            except Exception as e:
                flogger.error(f"发送心跳失败: {e}")

    def _send_heartbeat(self, consumer_id: str):
        """发送心跳"""
        try:
            redis_client = self.get_ip_routing_redis_client(self.boost_params)
            current_time = time.time()

            # 更新心跳时间
            redis_client.hset(self._consumer_heartbeat_key, consumer_id, current_time)

            # 更新消费者信息中的最后心跳时间
            consumer_data = redis_client.hget(self._consumer_registry_key, consumer_id)
            if consumer_data:
                consumer_info = json.loads(consumer_data)
                consumer_info['last_heartbeat'] = current_time
                redis_client.hset(
                    self._consumer_registry_key,
                    consumer_id,
                    json.dumps(consumer_info)
                )

        except Exception as e:
            flogger.error(f"发送心跳失败: {e}")

    def get_active_consumers(self) -> typing.List[ConsumerInfo]:
        """
        获取活跃的消费者列表

        Returns:
            活跃消费者信息列表
        """
        if not self.enable_ip_routing:
            return []

        try:
            redis_client = self.get_ip_routing_redis_client(self.boost_params)
            current_time = time.time()
            active_consumers = []

            # 获取所有消费者信息
            consumer_data = redis_client.hgetall(self._consumer_registry_key)
            heartbeat_data = redis_client.hgetall(self._consumer_heartbeat_key)

            for consumer_id, info_json in consumer_data.items():
                try:
                    consumer_info = ConsumerInfo.from_dict(json.loads(info_json))

                    # 检查心跳时间
                    last_heartbeat = float(heartbeat_data.get(consumer_id, 0))
                    if current_time - last_heartbeat <= self.consumer_timeout:
                        consumer_info.status = 'active'
                        consumer_info.last_heartbeat = last_heartbeat
                        active_consumers.append(consumer_info)
                    else:
                        # 清理过期消费者
                        self._cleanup_expired_consumer(consumer_id)

                except Exception as e:
                    flogger.warning(f"解析消费者信息失败: {consumer_id}, {e}")

            return active_consumers

        except Exception as e:
            flogger.error(f"获取活跃消费者失败: {e}")
            return []

    def _cleanup_expired_consumer(self, consumer_id: str):
        """清理过期消费者"""
        try:
            redis_client = self.get_ip_routing_redis_client(self.boost_params)
            redis_client.hdel(self._consumer_registry_key, consumer_id)
            redis_client.hdel(self._consumer_heartbeat_key, consumer_id)
            flogger.info(f"清理过期消费者: {consumer_id}")
        except Exception as e:
            flogger.error(f"清理过期消费者失败: {e}")

    def get_consumers_by_ip(self, target_ip: str) -> typing.List[ConsumerInfo]:
        """
        根据IP获取消费者列表

        Args:
            target_ip: 目标IP地址

        Returns:
            指定IP的消费者列表
        """
        active_consumers = self.get_active_consumers()
        return [c for c in active_consumers if c.ip_address == target_ip]

    def route_task_to_ip(self, target_ip: str, task_data: dict, strategy: str = 'strict') -> bool:
        """
        将任务路由到指定IP的消费者

        Args:
            target_ip: 目标IP地址
            task_data: 任务数据
            strategy: 路由策略 ('strict', 'fallback', 'load_balance')

        Returns:
            路由是否成功
        """
        if not self.enable_ip_routing:
            return False

        try:
            target_consumers = self.get_consumers_by_ip(target_ip)

            if strategy == 'strict':
                return self._route_strict(target_consumers, task_data, target_ip)
            elif strategy == 'fallback':
                return self._route_fallback(target_consumers, task_data, target_ip)
            elif strategy == 'load_balance':
                return self._route_load_balance(target_consumers, task_data, target_ip)
            else:
                flogger.error(f"不支持的路由策略: {strategy}")
                return False

        except Exception as e:
            flogger.error(f"任务路由失败: {e}")
            return False

    def _route_strict(self, target_consumers: typing.List[ConsumerInfo], task_data: dict, target_ip: str) -> bool:
        """严格路由策略：必须路由到指定IP"""
        if not target_consumers:
            flogger.warning(f"严格路由失败: 没有找到IP {target_ip} 的活跃消费者")
            return False

        # 选择第一个可用的消费者
        consumer = target_consumers[0]
        return self._send_task_to_consumer(consumer, task_data)

    def _route_fallback(self, target_consumers: typing.List[ConsumerInfo], task_data: dict, target_ip: str) -> bool:
        """回退路由策略：优先指定IP，失败则回退到任意消费者"""
        if target_consumers:
            consumer = target_consumers[0]
            if self._send_task_to_consumer(consumer, task_data):
                return True

        # 回退到任意活跃消费者
        all_consumers = self.get_active_consumers()
        if all_consumers:
            consumer = all_consumers[0]
            flogger.info(f"回退路由: 任务从IP {target_ip} 回退到 {consumer.ip_address}")
            return self._send_task_to_consumer(consumer, task_data)

        flogger.warning("回退路由失败: 没有任何活跃消费者")
        return False

    def _route_load_balance(self, target_consumers: typing.List[ConsumerInfo], task_data: dict, target_ip: str) -> bool:
        """负载均衡路由策略：在指定IP的消费者间负载均衡"""
        if not target_consumers:
            flogger.warning(f"负载均衡路由失败: 没有找到IP {target_ip} 的活跃消费者")
            return False

        # 简单的轮询负载均衡（可以扩展为更复杂的算法）
        consumer_index = hash(str(task_data)) % len(target_consumers)
        consumer = target_consumers[consumer_index]
        return self._send_task_to_consumer(consumer, task_data)

    def _send_task_to_consumer(self, consumer: ConsumerInfo, task_data: dict) -> bool:
        """
        发送任务到指定消费者

        Args:
            consumer: 目标消费者信息
            task_data: 任务数据

        Returns:
            发送是否成功
        """
        try:
            redis_client = self.get_redis_client_for_db(self.boost_params.redis_db if self.boost_params else None, self.boost_params)

            # 创建专用的路由队列
            routing_queue_name = f"{self.queue_name}:ip:{consumer.ip_address}:{consumer.consumer_id}"

            # 发送任务到路由队列
            redis_client.lpush(routing_queue_name, json.dumps(task_data))

            flogger.debug(f"任务已路由到消费者: {consumer.consumer_id} @ {consumer.ip_address}")
            return True

        except Exception as e:
            flogger.error(f"发送任务到消费者失败: {e}")
            return False

    def get_routing_queue_name(self, consumer_id: str) -> str:
        """
        获取消费者的路由队列名称

        Args:
            consumer_id: 消费者ID

        Returns:
            路由队列名称
        """
        return f"{self.queue_name}:ip:{self.local_ip}:{consumer_id}"

    def get_consumer_stats(self) -> dict:
        """
        获取消费者统计信息

        Returns:
            统计信息字典
        """
        if not self.enable_ip_routing:
            return {'ip_routing_enabled': False}

        try:
            active_consumers = self.get_active_consumers()

            # 按IP分组统计
            ip_stats = {}
            for consumer in active_consumers:
                ip = consumer.ip_address
                if ip not in ip_stats:
                    ip_stats[ip] = {
                        'consumer_count': 0,
                        'consumers': []
                    }
                ip_stats[ip]['consumer_count'] += 1
                ip_stats[ip]['consumers'].append({
                    'consumer_id': consumer.consumer_id,
                    'hostname': consumer.hostname,
                    'start_time': consumer.start_time,
                    'last_heartbeat': consumer.last_heartbeat
                })

            return {
                'ip_routing_enabled': True,
                'queue_name': self.queue_name,
                'total_consumers': len(active_consumers),
                'total_ips': len(ip_stats),
                'local_ip': self.local_ip,
                'heartbeat_interval': self.heartbeat_interval,
                'consumer_timeout': self.consumer_timeout,
                'ip_stats': ip_stats
            }

        except Exception as e:
            flogger.error(f"获取消费者统计信息失败: {e}")
            return {'error': str(e)}


class IPRouterMixin(RedisDBManagerMixin):
    """
    IP路由器Mixin类
    为Consumer和Publisher类提供IP路由能力
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._ip_router = None

    def _get_ip_router(self) -> IPRouter:
        """获取IP路由器实例"""
        if self._ip_router is None:
            boost_params = getattr(self, 'boost_params', None)
            self._ip_router = IPRouter(boost_params)
        return self._ip_router

    def register_ip_consumer(self, consumer_id: str) -> bool:
        """注册IP消费者"""
        return self._get_ip_router().register_consumer(consumer_id)

    def unregister_ip_consumer(self, consumer_id: str) -> bool:
        """注销IP消费者"""
        return self._get_ip_router().unregister_consumer(consumer_id)

    def start_ip_heartbeat(self, consumer_id: str):
        """启动IP心跳"""
        self._get_ip_router().start_heartbeat(consumer_id)

    def stop_ip_heartbeat(self):
        """停止IP心跳"""
        if self._ip_router:
            self._ip_router.stop_heartbeat()

    def route_task_to_ip(self, target_ip: str, task_data: dict, strategy: str = 'strict') -> bool:
        """路由任务到指定IP"""
        return self._get_ip_router().route_task_to_ip(target_ip, task_data, strategy)

    def get_ip_routing_queue_name(self, consumer_id: str) -> str:
        """获取IP路由队列名称"""
        return self._get_ip_router().get_routing_queue_name(consumer_id)

    def get_ip_consumer_stats(self) -> dict:
        """获取IP消费者统计信息"""
        return self._get_ip_router().get_consumer_stats()


# 添加缺失的导入
import os
import threading

if __name__ == '__main__':
    # 测试代码
    from fastboost.core.func_params_model import BoosterParams

    # 创建测试参数
    params = BoosterParams(
        queue_name='test_queue',
        enable_ip_routing=True,
        ip_routing_heartbeat_interval=10,
        redis_db=0
    )

    # 创建IP路由器
    router = IPRouter(params)

    # 测试消费者注册
    consumer_id = f"test_consumer_{int(time.time())}"
    print(f"注册消费者: {router.register_consumer(consumer_id)}")

    # 获取消费者统计
    stats = router.get_consumer_stats()
    print(f"消费者统计: {json.dumps(stats, indent=2, ensure_ascii=False)}")

    # 测试心跳
    router.start_heartbeat(consumer_id)
    time.sleep(2)

    # 获取活跃消费者
    active_consumers = router.get_active_consumers()
    print(f"活跃消费者数量: {len(active_consumers)}")

    # 清理
    router.stop_heartbeat()
    router.unregister_consumer(consumer_id)
