import urllib.parse
import hashlib
from operator import itemgetter

import requests

URL = "http://api-push.meizu.com/garcia/api/server/push/varnished/pushByPushId"


class MeiZu:
    def __init__(self, logger, app_id, secret_key):
        self.logger = logger
        self.app_id = app_id
        self.secret_key = secret_key
        self.logger.info("开始处理魅族推送")

    def push(self, tokens, title, content):
        self.logger.info("Tokens: {}".format(tokens))
        self.logger.info("Title: {}".format(title))

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        params = [
            ('pushIds', ','.join(tokens)),
            ('appId', self.app_id),
            ('messageJson', '{"advanceInfo":{"clearNoticeBar":true,"fixSpeed":false,"fixSpeedRate":0,"notificationType":{"lights":true,"sound":true,"vibrate":true},"suspend":true},"clickTypeInfo":{"activity":"","clickType":0,"url":""},"noticeBarInfo":{"content":"%(content)s","noticeBarType":0,"title":"%(title)s"},"noticeExpandInfo":{"noticeExpandContent":"%(content)s","noticeExpandType":1},"pushTimeInfo":{"offLine":true,"pushTimeType":0,"startTime":"","validTime":1}}' % {'title': title, 'content': content}),
        ]

        params.sort(key=itemgetter(0))

        signs = ["{}={}".format(key, value) for key, value in params]
        sign = "{}{}".format("".join(signs), self.secret_key)
        sign = hashlib.md5(sign.encode("utf-8")).hexdigest()
        params.append(('sign', sign))

        data = urllib.parse.urlencode(params)

        r = requests.post(URL, headers=headers, data=data)

        self.logger.info("魅族推送结束")
        response = r.json()

        return {'meizu': response}
