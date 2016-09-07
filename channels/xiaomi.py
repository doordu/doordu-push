import requests

URL = 'https://api.xmpush.xiaomi.com/v3/message/regid'


class XiaoMi:
    def __init__(self, logger, secret_key, package_name):
        self.logger = logger
        self.secret_key = secret_key
        self.package_name = package_name
        self.logger.info("开始处理小米推送")

    def push(self, tokens, title, content):
        self.logger.info("Tokens: {}".format(tokens))
        self.logger.info("Title: {}".format(title))

        payload = {
            'payload': "",
            'title': title,
            'description': content,
            'pass_through': 0,
            'notify_type': -1,
            'restricted_package_name': self.package_name,
            'notify_id': 2,
            'extra.notify_foreground': 1,
            'registration_id': ','.join(tokens)
        }

        r = requests.post(URL, headers={'Authorization': 'key={}'.format(self.secret_key)},
                          data=payload)

        self.logger.info("小米推送结束")
        response = r.json()

        return {'xiaomi': response}
