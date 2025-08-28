# coding=utf8
"""
Redis多DB连接管理器
支持多Redis实例、多DB索引的统一连接管理，为IP感知路由提供基础设施
"""

import copy
import threading
import typing
from urllib.parse import urlparse

import redis55

from fastboost.funboost_config_deafult import BrokerConnConfig
from fastboost.utils import decorators
from fastboost.core.loggers import flogger


class RedisDBManager:
    """
    Redis多DB连接管理器

    特性：
    1. 支持多Redis实例连接管理
    2. 支持多DB索引连接池复用
    3. 线程安全的连接获取
    4. 自动连接池管理和优化
    5. 支持URL和参数两种连接方式
    """

    # 全局连接池缓存 {(host, port, db, username, password): redis_client}
    _connection_pool_cache = {}
    _cache_lock = threading.RLock()

    def __init__(self,
                 redis_url: typing.Optional[str] = None,
                 host: str = None,
                 port: int = None,
                 db: int = None,
                 username: str = None,
                 password: str = None,
                 **connection_kwargs):
        """
        初始化Redis DB管理器

        Args:
            redis_url: Redis连接URL，格式：redis://[username:password@]host:port[/db]
            host: Redis主机地址
            port: Redis端口
            db: Redis数据库索引
            username: Redis用户名
            password: Redis密码
            **connection_kwargs: 其他连接参数
        """
        self.connection_kwargs = connection_kwargs.copy()

        # 解析连接参数
        if redis_url:
            self._parse_redis_url(redis_url)
        else:
            self._parse_connection_params(host, port, db, username, password)

        # 设置默认连接池参数
        self.connection_kwargs.setdefault('max_connections', 1000)
        self.connection_kwargs.setdefault('decode_responses', True)
        self.connection_kwargs.setdefault('socket_connect_timeout', 5)
        self.connection_kwargs.setdefault('socket_timeout', 5)
        self.connection_kwargs.setdefault('retry_on_timeout', True)

    def _parse_redis_url(self, redis_url: str):
        """解析Redis URL"""
        try:
            parsed = urlparse(redis_url)
            self.connection_kwargs.update({
                'host': parsed.hostname or '127.0.0.1',
                'port': parsed.port or 6379,
                'db': int(parsed.path.lstrip('/')) if parsed.path and parsed.path != '/' else 0,
                'username': parsed.username or '',
                'password': parsed.password or ''
            })
        except Exception as e:
            flogger.warning(f"解析Redis URL失败，使用默认配置: {e}")
            self._use_default_config()

    def _parse_connection_params(self, host, port, db, username, password):
        """解析连接参数"""
        self.connection_kwargs.update({
            'host': host or BrokerConnConfig.REDIS_HOST,
            'port': port or BrokerConnConfig.REDIS_PORT,
            'db': db if db is not None else BrokerConnConfig.REDIS_DB,
            'username': username or BrokerConnConfig.REDIS_USERNAME,
            'password': password or BrokerConnConfig.REDIS_PASSWORD
        })

    def _use_default_config(self):
        """使用默认配置"""
        self.connection_kwargs.update({
            'host': BrokerConnConfig.REDIS_HOST,
            'port': BrokerConnConfig.REDIS_PORT,
            'db': BrokerConnConfig.REDIS_DB,
            'username': BrokerConnConfig.REDIS_USERNAME,
            'password': BrokerConnConfig.REDIS_PASSWORD
        })

    def get_redis_client(self, db: typing.Optional[int] = None) -> redis55.Redis:
        """
        获取指定DB的Redis客户端

        Args:
            db: 数据库索引，为None时使用初始化时的db

        Returns:
            Redis客户端实例
        """
        # 使用指定的db或默认db
        target_db = db if db is not None else self.connection_kwargs['db']

        # 创建连接键
        connection_key = (
            self.connection_kwargs['host'],
            self.connection_kwargs['port'],
            target_db,
            self.connection_kwargs['username'],
            self.connection_kwargs['password']
        )

        # 线程安全地获取或创建连接
        with self._cache_lock:
            if connection_key not in self._connection_pool_cache:
                # 创建新的连接参数
                conn_kwargs = self.connection_kwargs.copy()
                conn_kwargs['db'] = target_db

                # 创建Redis客户端
                try:
                    redis_client = redis55.Redis(**conn_kwargs)
                    # 测试连接
                    redis_client.ping()
                    self._connection_pool_cache[connection_key] = redis_client
                    flogger.debug(f"创建新的Redis连接: {self.connection_kwargs['host']}:{self.connection_kwargs['port']}/db{target_db}")
                except Exception as e:
                    flogger.error(f"创建Redis连接失败: {e}")
                    raise

            return self._connection_pool_cache[connection_key]

    def get_ip_routing_redis_client(self, ip_routing_redis_db: typing.Optional[int] = None) -> redis55.Redis:
        """
        获取IP路由专用的Redis客户端

        Args:
            ip_routing_redis_db: IP路由专用DB索引

        Returns:
            IP路由专用Redis客户端
        """
        if ip_routing_redis_db is not None:
            return self.get_redis_client(db=ip_routing_redis_db)
        else:
            # 使用默认DB
            return self.get_redis_client()

    def test_connection(self, db: typing.Optional[int] = None) -> bool:
        """
        测试Redis连接

        Args:
            db: 要测试的数据库索引

        Returns:
            连接是否成功
        """
        try:
            redis_client = self.get_redis_client(db)
            redis_client.ping()
            return True
        except Exception as e:
            flogger.error(f"Redis连接测试失败: {e}")
            return False

    def get_connection_info(self) -> dict:
        """
        获取连接信息

        Returns:
            连接信息字典
        """
        return {
            'host': self.connection_kwargs['host'],
            'port': self.connection_kwargs['port'],
            'db': self.connection_kwargs['db'],
            'username': self.connection_kwargs['username'],
            'max_connections': self.connection_kwargs['max_connections'],
            'active_connections': len(self._connection_pool_cache)
        }

    @classmethod
    def clear_connection_cache(cls):
        """清空连接缓存"""
        with cls._cache_lock:
            for redis_client in cls._connection_pool_cache.values():
                try:
                    redis_client.connection_pool.disconnect()
                except:
                    pass
            cls._connection_pool_cache.clear()
            flogger.info("已清空Redis连接缓存")

    @classmethod
    def get_cache_stats(cls) -> dict:
        """获取缓存统计信息"""
        with cls._cache_lock:
            return {
                'total_connections': len(cls._connection_pool_cache),
                'connection_keys': list(cls._connection_pool_cache.keys())
            }


class RedisDBManagerMixin:
    """
    Redis DB管理器Mixin类
    为其他类提供多DB Redis连接能力
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._redis_db_manager = None

    def _get_redis_db_manager(self, boost_params=None) -> RedisDBManager:
        """
        获取Redis DB管理器实例

        Args:
            boost_params: BoosterParams参数对象

        Returns:
            RedisDBManager实例
        """
        if self._redis_db_manager is None:
            if boost_params:
                # 从boost_params获取Redis配置
                self._redis_db_manager = RedisDBManager(
                    redis_url=boost_params.redis_url,
                    host=None,  # 优先使用redis_url
                    port=None,
                    db=boost_params.redis_db,
                    username=None,
                    password=boost_params.redis_password,
                    **boost_params.redis_connection_pool_kwargs
                )
            else:
                # 使用默认配置
                self._redis_db_manager = RedisDBManager()

        return self._redis_db_manager

    def get_redis_client_for_db(self, db: typing.Optional[int] = None, boost_params=None) -> redis55.Redis:
        """
        获取指定DB的Redis客户端

        Args:
            db: 数据库索引
            boost_params: BoosterParams参数对象

        Returns:
            Redis客户端实例
        """
        manager = self._get_redis_db_manager(boost_params)
        return manager.get_redis_client(db)

    def get_ip_routing_redis_client(self, boost_params=None) -> redis55.Redis:
        """
        获取IP路由专用Redis客户端

        Args:
            boost_params: BoosterParams参数对象

        Returns:
            IP路由专用Redis客户端
        """
        manager = self._get_redis_db_manager(boost_params)
        ip_routing_db = getattr(boost_params, 'ip_routing_redis_db', None) if boost_params else None
        return manager.get_ip_routing_redis_client(ip_routing_db)


# 全局Redis DB管理器实例
_global_redis_db_manager = None
_global_manager_lock = threading.RLock()


def get_global_redis_db_manager(
    redis_url: typing.Optional[str] = None,
    host: str = None,
    port: int = None,
    db: int = None,
    username: str = None,
    password: str = None,
    **connection_kwargs
) -> RedisDBManager:
    """
    获取全局Redis DB管理器实例（单例模式）

    Args:
        redis_url: Redis连接URL
        host: Redis主机
        port: Redis端口
        db: Redis数据库索引
        username: Redis用户名
        password: Redis密码
        **connection_kwargs: 其他连接参数

    Returns:
        全局RedisDBManager实例
    """
    global _global_redis_db_manager

    with _global_manager_lock:
        if _global_redis_db_manager is None:
            _global_redis_db_manager = RedisDBManager(
                redis_url=redis_url,
                host=host,
                port=port,
                db=db,
                username=username,
                password=password,
                **connection_kwargs
            )

    return _global_redis_db_manager


def create_redis_db_manager_from_boost_params(boost_params) -> RedisDBManager:
    """
    从BoosterParams创建Redis DB管理器

    Args:
        boost_params: BoosterParams参数对象

    Returns:
        RedisDBManager实例
    """
    return RedisDBManager(
        redis_url=boost_params.redis_url,
        host=None,  # 优先使用redis_url
        port=None,
        db=boost_params.redis_db,
        username=None,
        password=boost_params.redis_password,
        **boost_params.redis_connection_pool_kwargs
    )


if __name__ == '__main__':
    # 测试代码
    import time

    # 测试基本功能
    manager = RedisDBManager()
    print("连接信息:", manager.get_connection_info())

    # 测试多DB连接
    redis_db0 = manager.get_redis_client(0)
    redis_db1 = manager.get_redis_client(1)

    print("DB0连接测试:", manager.test_connection(0))
    print("DB1连接测试:", manager.test_connection(1))

    # 测试缓存统计
    print("缓存统计:", RedisDBManager.get_cache_stats())

    # 测试URL连接
    url_manager = RedisDBManager(redis_url="redis://127.0.0.1:6379/2")
    print("URL管理器连接信息:", url_manager.get_connection_info())
