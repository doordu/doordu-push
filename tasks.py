import logging
import configparser
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError

from celery import Celery, Task
from raven import Client

from channels.apns import Apns
from channels.huawei import HuaWei
from channels.xiaomi import XiaoMi
from channels.meizu import MeiZu
from channels.mqtt import MQTT

config = configparser.ConfigParser()


config.read(os.path.join(os.path.dirname(__file__), "config.ini"))

client = Client('https://fa6faa5cea834cbd9cfc404fb72de7aa:6b9ac91556d8405da3bf1f75e20e4239@sentry.io/104967')

BROKER_URL = 'redis://:{}@{}:{}/0'.format(config['redis']['auth'], config['redis']['host'], config['redis']['port'])

app = Celery('tasks', broker=BROKER_URL, backend=BROKER_URL)


app.conf.update(
    CELERY_TASK_SERIALIZER='json',
    CELERY_ACCEPT_CONTENT=['json'],  # Ignore other content
    CELERY_RESULT_SERIALIZER='json',
    CELERY_TIMEZONE='Asia/Shanghai',
    CELERY_ENABLE_UTC=True,
)


class Push(Task):

    def __init__(self):
        self.logger = logging.getLogger('doordu-push')
        fh = logging.FileHandler(os.path.join(os.path.dirname(__file__),'doordu-push.log'))
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s - %(lineno)d - %(message)s')
        fh.setLevel(logging.INFO)
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
        self.logger.setLevel(logging.INFO)
        self.config = config

        self.apns = Apns(self.logger, self.config.getboolean('apns', 'use_sandbox'),
                         self.config['apns']['cert_filename'], self.config['apns']['passphrase'], client)

        self.huawei = HuaWei(self.logger, self.config['huawei']['client_id'],
                             self.config['huawei']['client_secret'])
        self.xiaomi = XiaoMi(self.logger, self.config['xiaomi']['secret_key'],
                             self.config['xiaomi']['package_name'])
        self.meizu = MeiZu(self.logger, self.config['meizu']['app_id'],
                           self.config['meizu']['secret_key'])

        self.mqtt = MQTT(self.logger, self.config['mqtt']['host'],
                         self.config.getint('mqtt', 'port'))

    def run(self, params):
        response = {}
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = []
            try:
                if len(params['ios']) > 0:
                    futures.append(executor.submit(self.apns.push, params['ios'], params['content'],
                                   params['ios_sound'] if 'ios_sound' in params else 'default',
                                   params['clear_invalid_token_url'] if 'clear_invalid_token_url' in params else None,
                                   params['message']))
            except Exception as e:
                client.captureException()
                self.logger.error("抛出异常: %s", e)

            try:
                if len(params['huawei']) > 0:
                    futures.append(executor.submit(self.huawei.push, params['huawei'],
                                                   params['title'], params['content']))
            except Exception as e:
                client.captureException()
                self.logger.error("抛出异常: %s", e)

            try:
                if len(params['xiaomi']) > 0:
                    is_make_call = False
                    try:
                        is_make_call = params['message']['cmd'] == 'makeCall'
                    except KeyError:
                        pass
                    futures.append(executor.submit(self.xiaomi.push, params['xiaomi'],
                                                   params['title'], params['content'], is_make_call))
            except Exception as e:
                client.captureException()
                self.logger.error("抛出异常: %s", e)

            try:
                if len(params['meizu']) > 0:
                    futures.append(executor.submit(self.meizu.push, params['meizu'],
                                                   params['title'], params['content']))
            except Exception as e:
                client.captureException()
                self.logger.error("抛出异常: %s", e)

            futures.append(executor.submit(self.mqtt.push, params['topic'], params['qos'],
                                           json.dumps(params['message'])))
            try:
                for future in as_completed(futures, timeout=10):
                    response.update(future.result())
            except TimeoutError as e:
                client.captureException()
                self.logger.error("超时异常：%s", e)

        return response

