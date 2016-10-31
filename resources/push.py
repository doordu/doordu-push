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
    'clear_invalid_token_url': ''
}
curl -d '{"qos": 0, "message": {"expired_at": 1472023902, "data": "This is data!"}, "huawei": ["08699060201997982000002590000001", "08643940102483282000002590000001"], "content": "\\u5403\\u8461\\u8404\\u4e0d\\u5410\\u8461\\u8404\\u76ae\\uff01\\uff01", "xiaomi": ["JAx8/kR4q9ABEb+S8opy8oaX29TrqD86MmUakubxPtQ="], "title": "\\u6389\\u6e23\\u5929\\u7684\\u63a8\\u9001\\uff01\\uff01", "topic": "test", "ios": ["d322940a6b4ecc8739b0c8413dcddfddad0b040c106a1b99ade359fb3f7728fb"]}' http://10.0.0.243:8082/push
"""
import json
import time

import falcon

from .base import Base
from tasks import Push
from exceptions import ExpiredException


class PushResource(Base):

    def setup(self):
        """
        加载各推送通道
        :return: None
        """
        self.push = Push()

    def on_post(self, req, resp):
        content = req.stream.read()
        params = content.decode("utf-8")
        try:
            params = json.loads(params)
            self.logger.info(params)
            self.push.delay(params)
            try:
                expired_at = params['message']['expiredAt']
                current_timestamp = int(time.time())
                if current_timestamp > expired_at:
                    self.logger.info("已经过期!")
                    raise ExpiredException()
            except KeyError:
                pass

            response = {'status_code': 200}
            self.logger.info("推送结果: %s", response)
            resp.status = falcon.HTTP_200
        except ValueError:
            self.logger.info(params)
            response = {'status_code': 403, 'msg': "数据格式不正确"}
            resp.status = falcon.HTTP_403
        except ExpiredException:
            self.client.captureException()
            response = {'status_code': 403, "msg": "该推送消息已经过期"}
            resp.status = falcon.HTTP_403
        except Exception:
            self.client.captureException()
            response = {'status_code': 404, "msg": "未知错误"}
            resp.status = falcon.HTTP_404

        resp.body = json.dumps(response)


