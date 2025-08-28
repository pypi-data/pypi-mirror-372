# coding=utf-8
from setuptools import setup, find_packages
from fastboost import __version__

extra_brokers = [
    'sqlalchemy==1.4.13',
    'sqlalchemy_utils==0.36.1',
    'eventlet==0.33.3',
    'gevent==22.10.2',
    'psutil',
    'nats-python',
    # 'aioredis3',
]

extra_flask = []
# extra_flask = ['flask', 'flask_bootstrap', 'flask_wtf', 'wtforms', 'flask_login']
setup(
    name='fastboost',  #
    version=__version__,
    description=(
        'pip install fastboost，python全功能分布式函数调度框架,fastboost的功能是全面性重量级，用户能想得到的功能99%全都有;fastboost的使用方式是轻量级，只有@boost一行代码需要写。支持python所有类型的并发模式和一切知名消息队列中间件，支持如 celery dramatiq等框架整体作为fastboost中间件，python函数加速器，框架包罗万象，用户能想到的控制功能全都有。一统编程思维，兼容50% python业务场景，适用范围广。只需要一行代码即可分布式执行python一切函数，99%用过fastboost的pythoner 感受是　简易 方便 强劲 强大，相见恨晚 '
    ),
    # long_description=open('README.md', 'r',encoding='utf8').read(),
    keywords=["fastboost", "distributed-framework", "function-scheduling", "rabbitmq", "rocketmq", "kafka", "nsq", "redis", "disk",
              "sqlachemy", "consume-confirm", "timing", "task-scheduling", "apscheduler", "pulsar", "mqtt", "kombu", "的", "celery", "框架", '分布式调度'],
    long_description_content_type="text/markdown",
    long_description=open('README.md', 'r', encoding='utf8').read(),
    author='',
    author_email='',
    maintainer='',
    maintainer_email='',
    license='BSD License',
    # packages=['douban'], #
    packages=find_packages() + ['fastboost.beggar_version_implementation', 'fastboost.assist'],  # 也可以写在 MANiFEST.in
    # packages=['function_scheduling_distributed_framework'], # 这样内层级文件夹的没有打包进去。
    include_package_data=True,
    platforms=["all"],
    url='',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        # 'Programming Language :: Python :: 3.13',
        # 'Programming Language :: Python :: 3.14',
        # 'Programming Language :: Python :: 3.15',
        # 'Programming Language :: Python :: 3.16',
        # 'Programming Language :: Python :: 3.17',
        # 'Programming Language :: Python :: 3.18',
        # 'Programming Language :: Python :: 3.19',
        # 'Programming Language :: Python :: 3.20',
        # 'Programming Language :: Python :: 3.21',
        'Topic :: Software Development :: Libraries'
    ],
    install_requires=[
        'nb_log>=12.6',
        'nb_libs>=1.8',
        'nb_time>=1.8',
        'pymongo==3.5.1',  # 3.5.1  -> 4.0.2
        'AMQPStorm==2.10.6',
        'decorator==4.1.1',
        'tomorrow3==1.1.0',
        'apscheduler==3.10.1',
        'twisted==21.7.0',
        'pikav0',
        'pikav1',
        'redis2',
        'redis3',
        'redis55==1.0.3',
        'redis==3.5.1',
        # 'aioredis3==2.0.1',
        'setuptools_rust',
        'fabric2==2.6.0',  # 有的机器包rust错误， 这样做 curl https://sh.rustup.rs -sSf | sh
        'nb_filelock',
        'pysnooper',
        'deprecated',
        'cryptography',
        'auto_run_on_remote',
        'frozenlist',
        'fire',
        'pydantic',
        'orjson'
    ],
    extras_require={'all': extra_brokers + extra_flask,
                    'extra_brokers': extra_brokers,
                    'flask': extra_flask,
                    },

    entry_points={
        'console_scripts': [
            'fastboost = fastboost.__main__:main',
            'fastboost_cli_super = fastboost.__main__:main',
        ]}
)

"""
官方 https://pypi.org/simple
清华 https://pypi.tuna.tsinghua.edu.cn/simple
豆瓣 https://pypi.douban.com/simple/ 
阿里云 https://mirrors.aliyun.com/pypi/simple/
腾讯云  http://mirrors.tencentyun.com/pypi/simple/

打包上传
python setup.py sdist upload -r pypi

# python setup.py bdist_wheel
python setup.py bdist_wheel ; python -m twine upload dist/fastboost-23.5-py3-none-any.whl
python setup.py bdist_wheel && python -m twine upload dist/fastboost-24.8-py3-none-any.whl
python setup.py sdist & twine upload dist/fastboost-10.9.tar.gz

最快的下载方式，上传立即可安装。阿里云源同步官网pypi间隔要等很久。
./pip install fastboost==3.5 -i https://pypi.org/simple   
最新版下载
./pip install fastboost --upgrade -i https://pypi.org/simple     

pip install fastboost[all]     # 安装其他所有冷门的中间件操作包。


从git安装
pip install git+https://github.com/ydf0509/fastboost.git 
pip install git+https://gitee.com/bfzshen/fastboost.git

"""
