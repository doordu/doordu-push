import time
import json

import requests


class HuaWei:

    def __init__(self, logger, client_id, client_secret):
        self.logger = logger
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.expire_at = 0
        self.logger.info("开始处理华为推送")

    def auth(self):
        r = requests.post("https://login.vmall.com/oauth2/token", data={
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret
        })
        response = r.json()
        self.access_token = response['access_token']
        self.expire_at = int(response['expires_in'])
        self.logger.info("Access Token: %s, Expire At: %s", self.access_token, self.expire_at)

    def push(self, tokens, title, content):
        current_timestamp = int(time.time())
        if self.expire_at - current_timestamp < 300:
            self.auth()

        self.logger.info("Tokens: %s", tokens)
        self.logger.info("Title: %s", title)

        message = {'notification_title': title,
                   'notification_content': content,
                   'doings': 1}

        r = requests.post("https://api.vmall.com/rest.php", data={
            'push_type': 1,
            'access_token': self.access_token,
            'tokens': ','.join(tokens),
            'android': json.dumps(message),
            'nsp_svc': 'openpush.openapi.notification_send',
            'nsp_ts': current_timestamp + 3 * 60 * 60 * 1000
        })

        self.logger.info("华为推送结束")
        response = r.json()

        return {'huawei': response}
