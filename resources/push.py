"""
message = {
    'huawei': ['08699060201997982000002590000001', '08643940102483282000002590000001'],
    'xiaomi': ['token1', 'token2'],
    'meizu': ['0XC71516a74786a03775006645f0d445862785763747e'],
    'ios': ['d322940a6b4ecc8739b0c8413dcddfddad0b040c106a1b99ade359fb3f7728fb'],
    'ios_sound': 'default',
    'topic': 'test',
    'qos': 0,
    'message': {'expired_at': 1472023902, 'data': 'This is data!'},
    'title': 'hello',
    'content': 'This is content!',
}
curl -d '{"qos": 0, "message": {"expired_at": 1472023902, "data": "This is data!"}, "huawei": ["08699060201997982000002590000001", "08643940102483282000002590000001"], "content": "\\u5403\\u8461\\u8404\\u4e0d\\u5410\\u8461\\u8404\\u76ae\\uff01\\uff01", "xiaomi": ["JAx8/kR4q9ABEb+S8opy8oaX29TrqD86MmUakubxPtQ="], "title": "\\u6389\\u6e23\\u5929\\u7684\\u63a8\\u9001\\uff01\\uff01", "topic": "test", "ios": ["d322940a6b4ecc8739b0c8413dcddfddad0b040c106a1b99ade359fb3f7728fb"]}' http://10.0.0.243:8082/push
"""
import json
import logging
import os.path
from concurrent.futures import ThreadPoolExecutor, as_completed

import falcon

from .base import Base
from channels.apns import Apns
from channels.huawei import HuaWei
from channels.xiaomi import XiaoMi
from channels.meizu import MeiZu
from channels.mqtt import MQTT


class PushResource(Base):

    def setup(self):
        """
        加载各推送通道
        :return: None
        """
        self.apns = Apns(self.logger, self.config['apns']['use_sandbox'],
                         self.config['apns']['cert_filename'], self.config['apns']['passphrase'])
        self.huawei = HuaWei(self.logger, self.config['huawei']['client_id'],
                             self.config['huawei']['client_secret'])
        self.xiaomi = XiaoMi(self.logger, self.config['xiaomi']['secret_key'],
                             self.config['xiaomi']['package_name'])
        self.meizu = MeiZu(self.logger, self.config['meizu']['app_id'],
                             self.config['meizu']['secret_key'])

        self.mqtt = MQTT(self.logger, self.config['mqtt']['host'],
                            self.config.getint('mqtt', 'port'))

    def on_post(self, req, resp):
        content = req.stream.read()
        params = content.decode("utf-8")
        params = json.loads(params)
        self.logger.info(params)
        response = {'status_code': 200}

        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = []
            try:
                if len(params['ios']) > 0:
                    futures.append(executor.submit(self.apns.push, params['ios'], params['title'],
                                   params['ios_sound'] if 'ios_sound' in params else 'default'))
            except Exception as e:
                self.logger.error("抛出异常: %s", e)

            try:
                if len(params['huawei']) > 0:
                    futures.append(executor.submit(self.huawei.push, params['huawei'],
                                                   params['title'], params['content']))
            except Exception as e:
                self.logger.error("抛出异常: %s", e)

            try:
                if len(params['xiaomi']) > 0:
                    futures.append(executor.submit(self.xiaomi.push, params['xiaomi'],
                                                   params['title'], params['content']))
            except Exception as e:
                self.logger.error("抛出异常: %s", e)

            try:
                if len(params['meizu']) > 0:
                    futures.append(executor.submit(self.meizu.push, params['meizu'],
                                                   params['title'], params['content']))
            except Exception as e:
                self.logger.error("抛出异常: %s", e)

            futures.append(executor.submit(self.mqtt.push, params['topic'], params['qos'],
                           json.dumps(params['message'])))

            for future in as_completed(futures):
                response.update(future.result())

        self.logger.info("推送结果: %s", response)

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(response)


