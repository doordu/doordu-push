import requests

URL = 'https://api.xmpush.xiaomi.com/v3/message/regid'


class XiaoMi:
    def __init__(self, logger, secret_key, package_name):
        self.logger = logger
        self.secret_key = secret_key
        self.package_name = package_name
        self.logger.info("开始处理小米推送")

    def push(self, tokens, title, content, is_ringtone=False):
        self.logger.info("Tokens: {}".format(tokens))
        self.logger.info("Title: {}".format(title))

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

        r = requests.post(URL, headers={'Authorization': 'key={}'.format(self.secret_key)},
                          data=payload)

        self.logger.info("小米推送结束")
        response = r.json()
        self.logger.info(response)

        return {'xiaomi': response}
