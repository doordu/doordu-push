import json
import time
import traceback

import falcon
from redis import Redis

from .base import Base
from tasks import Push
from exceptions import ExpiredException, FrequentException


class PushResource(Base):

    def setup(self):
        """
        加载各推送通道
        :return: None
        """
        self.push = Push()
        self.r = Redis(host=self.config['redis']['host'],
                       port=self.config.getint('redis', 'port'),
                       db=0,
                       password=self.config['redis']['auth'])

    def on_post(self, req, resp):
        content = req.stream.read()
        params = content.decode("utf-8")
        try:
            params = json.loads(params)
            self.logger.info(params)
            try:
                expired_at = params['message']['expiredAt']
                current_timestamp = int(time.time())
                if current_timestamp > expired_at:
                    self.logger.info("已经过期!")
                    raise ExpiredException()
            except KeyError:
                pass

            try:
                topic = params['topic']
                cmd = params['message']['cmd']
                transaction_id = params['message']['transactionID']
                redis_key = 'push_{}_{}_{}'.format(topic, cmd, transaction_id)
                if self.r.get(redis_key) is not None:
                    self.logger.info("%s topic 请求频繁", redis_key)
                    raise FrequentException()
                self.r.setex(redis_key, topic, 1)
            except KeyError:
                pass

            self.push.apply_async((params, ), expires=25)
            response = {'status_code': 200}
            self.logger.info("推送结果: %s", response)
            resp.status = falcon.HTTP_200
        except ValueError:
            self.logger.info(params)
            self.logger.info(traceback.format_exc())
            response = {'status_code': 403, 'msg': "数据格式不正确"}
            resp.status = falcon.HTTP_403
        except ExpiredException:
            self.client.captureException()
            response = {'status_code': 408, "msg": "该推送消息已经过期"}
            resp.status = falcon.HTTP_403
        except FrequentException:
            self.client.captureException()
            response = {'status_code': 410, "msg": "请求过于频繁"}
            resp.status = falcon.HTTP_403
        except Exception:
            self.client.captureException()
            response = {'status_code': 404, "msg": "未知错误"}
            resp.status = falcon.HTTP_404

        resp.body = json.dumps(response)
