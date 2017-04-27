import time
import json
import datetime
import logging

import requests
from requests.exceptions import ConnectTimeout


class HuaWei:

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.expire_at = 0
        logging.info("开始处理华为推送")

    def auth(self):
        r = requests.post("https://login.vmall.com/oauth2/token", data={
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret
        })
        response = r.json()
        self.access_token = response['access_token']
        self.expire_at = int(response['expires_in'])
        logging.info("Access Token: %s, Expire At: %s", self.access_token, self.expire_at)

    def push(self, tokens, title, content):
        current_timestamp = int(time.time())
        if self.expire_at - current_timestamp < 300:
            self.auth()

        logging.info("Tokens: %s", tokens)
        logging.info("Title: %s", title)

        message = {'notification_title': title,
                   'notification_content': content,
                   'doings': 1}

        send_time = datetime.datetime.fromtimestamp(current_timestamp, datetime.timezone.utc).astimezone().isoformat()
        expire_time = datetime.datetime.fromtimestamp(current_timestamp + 40, datetime.timezone.utc).astimezone().isoformat()

        response = ''

        try:
            r = requests.post("https://api.vmall.com/rest.php", data={
                'push_type': 1,
                'access_token': self.access_token,
                'tokens': ','.join(tokens),
                'android': json.dumps(message),
                'nsp_svc': 'openpush.openapi.notification_send',
                'nsp_ts': current_timestamp + 3 * 60 * 60 * 1000,
                'send_time': send_time,
                'expire_time': expire_time,
            }, timeout=10)

            logging.info("华为推送结束")
            response = json.loads(json.loads(r.text))
            logging.info(response)
        except ConnectTimeout:
            logging.info("华为推送超时")

        return {'huawei': response}
