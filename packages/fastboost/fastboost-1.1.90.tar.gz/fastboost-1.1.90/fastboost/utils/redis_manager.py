# coding=utf8

import copy
# import redis2 as redis
# import redis3
import redis55
from fastboost.funboost_config_deafult import BrokerConnConfig
from fastboost.utils import decorators

# from aioredis.client import Redis as AioRedis



def get_redis_conn_kwargs():
    return {'host': BrokerConnConfig.REDIS_HOST, 'port': BrokerConnConfig.REDIS_PORT,
            'username': BrokerConnConfig.REDIS_USERNAME,
            'password': BrokerConnConfig.REDIS_PASSWORD, 'db': BrokerConnConfig.REDIS_DB}


def _get_redis_conn_kwargs_by_db(db):
    conn_kwargs = copy.copy(get_redis_conn_kwargs())
    conn_kwargs['db'] = db
    return conn_kwargs


class RedisManager(object):
    _redis_db__conn_map = {}

    def __init__(self, host='127.0.0.1', port=6379, db=0, username='', password=''):
        self._key = (host, port, db, username, password,)
        if self._key not in self.__class__._redis_db__conn_map:
            self.__class__._redis_db__conn_map[self._key] = redis55.Redis(host=host, port=port, db=db, username=username,
                                                                         password=password, max_connections=1000, decode_responses=True)
        self.redis = self.__class__._redis_db__conn_map[self._key]

    def get_redis(self) -> redis55.Redis:
        """
        :rtype :redis5.Redis
        """
        return self.redis


# class AioRedisManager(object):
#     _redis_db__conn_map = {}
#
#     def __init__(self, host='127.0.0.1', port=6379, db=0, username='', password=''):
#         self._key = (host, port, db, username, password,)
#         if self._key not in self.__class__._redis_db__conn_map:
#             self.__class__._redis_db__conn_map[self._key] = AioRedis(host=host, port=port, db=db, username=username,
#                                                                      password=password, max_connections=1000, decode_responses=True)
#         self.redis = self.__class__._redis_db__conn_map[self._key]
#
#     def get_redis(self) -> AioRedis:
#         """
#         :rtype :redis5.Redis
#         """
#         return self.redis


# noinspection PyArgumentEqualDefault
class RedisMixin(object):
    """
    可以被作为万能mixin能被继承，也可以单独实例化使用。
    """

    def redis_db_n(self, db):
        return RedisManager(**_get_redis_conn_kwargs_by_db(db)).get_redis()

    @property
    @decorators.cached_method_result
    def redis_db_frame(self):
        return RedisManager(**get_redis_conn_kwargs()).get_redis()

    @property
    @decorators.cached_method_result
    def redis_db_filter_and_rpc_result(self):
        return RedisManager(**_get_redis_conn_kwargs_by_db(BrokerConnConfig.REDIS_DB_FILTER_AND_RPC_RESULT)).get_redis()

    def get_rpc_redis_connection(self, booster_params=None):
        """
        根据BoosterParams配置动态获取RPC存储的Redis连接
        支持多种RPC存储策略：跟随任务实例、使用默认配置、显式指定
        """
        if booster_params is None:
            # 如果没有传入参数，使用默认配置
            return self.redis_db_filter_and_rpc_result

        strategy = getattr(booster_params, 'rpc_storage_strategy', 'follow_task_instance')

        if strategy == 'use_default':
            # 使用默认配置
            return self.redis_db_filter_and_rpc_result

        elif strategy == 'explicit':
            # 显式指定RPC存储位置
            rpc_redis_url = getattr(booster_params, 'rpc_redis_url', None)
            rpc_redis_db = getattr(booster_params, 'rpc_redis_db', None)

            if rpc_redis_url and rpc_redis_db is not None:
                # 解析Redis URL
                import urllib.parse
                parsed = urllib.parse.urlparse(rpc_redis_url)
                host = parsed.hostname or '127.0.0.1'
                port = parsed.port or 6379
                username = parsed.username or ''
                password = parsed.password or ''

                return RedisManager(host=host, port=port, db=rpc_redis_db,
                                    username=username, password=password).get_redis()
            else:
                # 配置不完整，根据fallback策略处理
                if getattr(booster_params, 'rpc_fallback_to_default', True):
                    return self.redis_db_filter_and_rpc_result
                else:
                    raise ValueError("显式RPC配置不完整且不允许回退到默认配置")

        elif strategy == 'follow_task_instance':
            # 跟随任务实例策略
            task_redis_url = getattr(booster_params, 'redis_url', None)
            task_redis_db = getattr(booster_params, 'redis_db', None)
            rpc_db_offset = getattr(booster_params, 'rpc_db_offset', 1)

            if task_redis_db is not None:
                # 计算RPC DB = 任务DB + 偏移量
                rpc_db = task_redis_db + rpc_db_offset

                if task_redis_url:
                    # 使用指定的Redis URL
                    import urllib.parse
                    parsed = urllib.parse.urlparse(task_redis_url)
                    host = parsed.hostname or '127.0.0.1'
                    port = parsed.port or 6379
                    username = parsed.username or ''
                    password = parsed.password or ''

                    return RedisManager(host=host, port=port, db=rpc_db,
                                        username=username, password=password).get_redis()
                else:
                    # 使用默认Redis连接配置，但使用计算出的RPC DB
                    return RedisManager(**_get_redis_conn_kwargs_by_db(rpc_db)).get_redis()
            else:
                # 任务实例配置不完整，根据fallback策略处理
                if getattr(booster_params, 'rpc_fallback_to_default', True):
                    return self.redis_db_filter_and_rpc_result
                else:
                    raise ValueError("任务实例配置不完整且不允许回退到默认配置")

        else:
            # 未知策略，使用默认配置
            return self.redis_db_filter_and_rpc_result

    def timestamp(self):
        """ 如果是多台机器做分布式控频 乃至确认消费，每台机器取自己的时间，如果各机器的时间戳不一致会发生问题，改成统一使用从redis服务端获取时间，单位是时间戳秒。"""
        time_tuple = self.redis_db_frame.time()
        # print(time_tuple)
        return time_tuple[0] + time_tuple[1] / 1000000


class AioRedisMixin(object):
    @property
    @decorators.cached_method_result
    def aioredis_db_filter_and_rpc_result(self):
        # aioredis 包已经不再更新了,推荐使用redis包的asyncio中的类
        # return AioRedisManager(**_get_redis_conn_kwargs_by_db(BrokerConnConfig.REDIS_DB_FILTER_AND_RPC_RESULT)).get_redis()
        return redis55.asyncio.Redis(**_get_redis_conn_kwargs_by_db(BrokerConnConfig.REDIS_DB_FILTER_AND_RPC_RESULT),decode_responses=True)

    def get_async_rpc_redis_connection(self, booster_params=None):
        """
        根据BoosterParams配置动态获取异步RPC存储的Redis连接
        支持多种RPC存储策略：跟随任务实例、使用默认配置、显式指定
        """
        if booster_params is None:
            # 如果没有传入参数，使用默认配置
            return self.aioredis3_db_filter_and_rpc_result

        strategy = getattr(booster_params, 'rpc_storage_strategy', 'follow_task_instance')

        if strategy == 'use_default':
            # 使用默认配置
            return self.aioredis3_db_filter_and_rpc_result

        elif strategy == 'explicit':
            # 显式指定RPC存储位置
            rpc_redis_url = getattr(booster_params, 'rpc_redis_url', None)
            rpc_redis_db = getattr(booster_params, 'rpc_redis_db', None)

            if rpc_redis_url and rpc_redis_db is not None:
                # 解析Redis URL
                import urllib.parse
                parsed = urllib.parse.urlparse(rpc_redis_url)
                host = parsed.hostname or '127.0.0.1'
                port = parsed.port or 6379
                username = parsed.username or ''
                password = parsed.password or ''

                return redis55.asyncio.Redis(host=host, port=port, db=rpc_redis_db,
                                             username=username, password=password, decode_responses=True)
            else:
                # 配置不完整，根据fallback策略处理
                if getattr(booster_params, 'rpc_fallback_to_default', True):
                    return self.aioredis3_db_filter_and_rpc_result
                else:
                    raise ValueError("显式RPC配置不完整且不允许回退到默认配置")

        elif strategy == 'follow_task_instance':
            # 跟随任务实例策略
            task_redis_url = getattr(booster_params, 'redis_url', None)
            task_redis_db = getattr(booster_params, 'redis_db', None)
            rpc_db_offset = getattr(booster_params, 'rpc_db_offset', 1)

            if task_redis_db is not None:
                # 计算RPC DB = 任务DB + 偏移量
                rpc_db = task_redis_db + rpc_db_offset

                if task_redis_url:
                    # 使用指定的Redis URL
                    import urllib.parse
                    parsed = urllib.parse.urlparse(task_redis_url)
                    host = parsed.hostname or '127.0.0.1'
                    port = parsed.port or 6379
                    username = parsed.username or ''
                    password = parsed.password or ''

                    return redis55.asyncio.Redis(host=host, port=port, db=rpc_db,
                                                 username=username, password=password, decode_responses=True)
                else:
                    # 使用默认Redis连接配置，但使用计算出的RPC DB
                    redis_kwargs = _get_redis_conn_kwargs_by_db(rpc_db)
                    return redis55.asyncio.Redis(**redis_kwargs, decode_responses=True)
            else:
                # 任务实例配置不完整，根据fallback策略处理
                if getattr(booster_params, 'rpc_fallback_to_default', True):
                    return self.aioredis3_db_filter_and_rpc_result
                else:
                    raise ValueError("任务实例配置不完整且不允许回退到默认配置")

        else:
            # 未知策略，使用默认配置
            return self.aioredis3_db_filter_and_rpc_result
