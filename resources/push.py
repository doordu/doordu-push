"""
message = {
    'huawei': ['08699060201997982000002590000001', 'token2'],
    'xiaomi': ['token1', 'token2'],
    'ios': ['d322940a6b4ecc8739b0c8413dcddfddad0b040c106a1b99ade359fb3f7728fb'],
    'topic': 'test',
    'qos': 0,
    'message': {'expired_at': 1472023902, 'data': 'This is data!'},
    'title': '掉渣天的推送！！',
    'content': '吃葡萄不吐葡萄皮！！',
}
curl -d '{"ios": ["0e46cbe2098927e6a9a0062e30d877674296384ddcc79eecda3973467f6244bc"], "content": "this is content", "xiaomi": ["token1", "token2"], "topic": "test", "message": {"data": "This is data!", "expired_at": 1472023902}, "qos": 0, "title": "hello", "huawei": ["08699060201997982000002590000001", "token2"]}' http://127.0.0.1:8000/push
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
from channels.mqtt import MQTT


class PushResource(Base):

    def setup(self):
        """
        加载各推送通道
        :return: None
        """
        self.apns = Apns(self.logger, self.config['apns']['use_sandbox'],
                         self.config['apns']['cert_filename'])
        self.huawei = HuaWei(self.logger, self.config['huawei']['client_id'],
                             self.config['huawei']['client_secret'])
        self.xiaomi = XiaoMi(self.logger, self.config['xiaomi']['secret_key'],
                             self.config['xiaomi']['package_name'])

        self.mqtt = MQTT(self.logger, self.config['mqtt']['host'],
                            self.config.getint('mqtt', 'port'))


    def on_post(self, req, resp):
        """
        发起推送
        :param req: 请求实体
        :param resp: 响应实体
        :return: None
        """
        content = req.stream.read()
        params = content.decode("utf-8")
        params = json.loads(params)
        self.logger.info(params)
        response = {}

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            if len(params['ios']) > 0:
                futures.append(executor.submit(self.apns.push, params['ios'], params['title'], params['message']))
            if len(params['huawei']) > 0:
                futures.append(executor.submit(self.huawei.push, params['huawei'], params['title'], params['content']))
            if len(params['xiaomi']) > 0:
                futures.append(executor.submit(self.xiaomi.push, params['xiaomi'], params['title'], params['content']))

            futures.append(executor.submit(self.mqtt.push, params['topic'], params['qos'], json.dumps(params['message'])))

            for future in as_completed(futures):
                response.update(future.result())

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(response)


