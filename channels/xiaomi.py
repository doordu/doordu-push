import logging

import requests
from requests.exceptions import ConnectTimeout

URL = 'https://api.xmpush.xiaomi.com/v3/message/regid'


class XiaoMi:
    def __init__(self, secret_key, package_name):
        self.secret_key = secret_key
        self.package_name = package_name
        logging.info("开始处理小米推送")

    def push(self, tokens, title, content, is_ringtone=False):
        logging.info("Tokens: {}".format(tokens))
        logging.info("Title: {}".format(title))

        payload = {
            'payload': "",
            'title': title,
            'description': content,
            'pass_through': 0,
            'notify_type': 1,
            'restricted_package_name': self.package_name,
            'notify_id': 2,
            'time_to_live': 40000, # ms
            'extra.notify_foreground': 1,
            # 'extra.sound_uri': 'android.resource://com.doordu.mobile/raw/ringtone_long',
            'extra.notify_effect': 1,
            'registration_id': ','.join(tokens)
        }

        if is_ringtone:
            payload['extra.sound_uri'] = 'android.resource://com.doordu.mobile/raw/ringtone_long'

        response = ""
        try:
            r = requests.post(URL, headers={'Authorization': 'key={}'.format(self.secret_key)},
                              data=payload, timeout=10)

            logging.info("小米推送结束")
            response = r.json()
            logging.info(response)
        except ConnectTimeout:
            logging.info("小米推送异常")

        return {'xiaomi': response}
