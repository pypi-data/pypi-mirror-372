# noinspection PyUnresolvedReferences
import atexit

import nb_log
# noinspection PyUnresolvedReferences
from nb_log import nb_print

'''
set_frame_config 这行要放在所有导入其他代码之前最好,以便防止其他项目提前 from funboost.funboost_config_deafult import xx ,
如果是 from funboost import funboost_config_deafult,在函数内部使用他的配置就没事,但最后不要让其他模块在 set_frame_config 之前导入.
set_frame_config这个模块的 use_config_form_funboost_config_module() 是核心,把用户的funboost_config.py的配置覆盖到funboost_config_deafult模块了

这段注释说明和使用的用户无关,只和框架开发人员有关.
'''

# __version__ = "146.2"
__version__ = "1.1.89"

from fastboost.set_frame_config import show_frame_config

# noinspection PyUnresolvedReferences
from fastboost.utils.dependency_packages_in_pythonpath import add_to_pythonpath  # 这是把 dependency_packages_in_pythonpath 添加到 PYTHONPATH了。
from fastboost.utils import monkey_patches

from fastboost.core.loggers import get_logger, get_funboost_file_logger, FunboostFileLoggerMixin, FunboostMetaTypeFileLogger, flogger
from fastboost.core.func_params_model import (BoosterParams, BoosterParamsComplete, FunctionResultStatusPersistanceConfig,
                                             PriorityConsumingControlConfig, PublisherParams, BoosterParamsComplete)
from fastboost.funboost_config_deafult import FunboostCommonConfig, BrokerConnConfig

# from fastboost.core.fabric_deploy_helper import fabric_deploy, kill_all_remote_tasks # fabric2还没适配python3.12以上版本，不在这里导入，否则高版本python报错。
from fastboost.utils.paramiko_util import ParamikoFolderUploader

from fastboost.consumers.base_consumer import (wait_for_possible_has_finish_all_tasks_by_conusmer_list,
                                              FunctionResultStatus, AbstractConsumer)
from fastboost.consumers.empty_consumer import EmptyConsumer
from fastboost.core.exceptions import ExceptionForRetry, ExceptionForRequeue, ExceptionForPushToDlxqueue
from fastboost.core.active_cousumer_info_getter import ActiveCousumerProcessInfoGetter
from fastboost.core.msg_result_getter import HasNotAsyncResult, ResultFromMongo
from fastboost.publishers.base_publisher import (PriorityConsumingControlConfig,
                                                AbstractPublisher, AsyncResult, AioAsyncResult)
from fastboost.publishers.empty_publisher import EmptyPublisher
from fastboost.factories.broker_kind__publsiher_consumer_type_map import register_custom_broker
from fastboost.factories.publisher_factotry import get_publisher
from fastboost.factories.consumer_factory import get_consumer

from fastboost.timing_job import fsdf_background_scheduler, timing_publish_deco, funboost_aps_scheduler, ApsJobAdder
from fastboost.constant import BrokerEnum, ConcurrentModeEnum

from fastboost.core.booster import boost, Booster, BoostersManager
# from funboost.core.get_booster import get_booster, get_or_create_booster, get_boost_params_and_consuming_function
from fastboost.core.kill_remote_task import RemoteTaskKiller
from fastboost.funboost_config_deafult import BrokerConnConfig, FunboostCommonConfig
from fastboost.core.cli.discovery_boosters import BoosterDiscovery

# from funboost.core.exit_signal import set_interrupt_signal_handler
from fastboost.core.helper_funs import run_forever

from fastboost.utils.ctrl_c_end import ctrl_c_recv
from fastboost.utils.redis_manager import RedisMixin
from fastboost.concurrent_pool.custom_threadpool_executor import show_current_threads_num

from fastboost.core.current_task import funboost_current_task,fct,get_current_taskid



# atexit.register(ctrl_c_recv)  # 还是需要用户自己在代码末尾加才可以.
# set_interrupt_signal_handler()

# 有的包默认没加handlers，原始的日志不漂亮且不可跳转不知道哪里发生的。这里把warnning级别以上的日志默认加上handlers。
# nb_log.get_logger(name='', log_level_int=30, log_filename='pywarning.log')

