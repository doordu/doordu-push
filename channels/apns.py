import os.path
import json
import time

from apns2.client import APNsClient, Notification
from apns2.payload import Payload


class Apns:
    def __init__(self, logger, use_sandbox, cert_filename, passphrase, bundle_id, raven):
        cert_file = os.path.join(os.path.dirname(__file__), os.path.pardir,
                    'certs', '{}_{}.pem'.format(cert_filename, 'dev' if use_sandbox else 'pro'))

        self.logger = logger
        self.logger.info("注册APNS通道")
        self.logger.info("cert_file: %s", cert_file)

        self.use_sandbox = use_sandbox
        self.cert_filename = cert_filename
        self.cert_file = cert_file
        self.bundle_id = bundle_id
        self.passphrase = passphrase
        self.raven = raven

        self.client = APNsClient(self.cert_file, use_sandbox=self.use_sandbox, password=self.passphrase)

    def push(self, tokens, alert, sound='default', ios_remove_token_url=None, content={}):
        self.logger.info("开始APNS推送")
        expiry = content['expiredAt'] if 'expiredAt' in content else None
        self.logger.info("Tokens: %s, Sound: %s, Expiry: %s", tokens, sound, expiry)
        self.logger.info("Alert: %s, Extra: %s", alert, content)

        invalid_tokens = []

        payload = Payload(alert=alert, sound=sound, badge=1)
        notifications = (Notification(token=token, payload=payload) for token in tokens)

        try:
            self.client.send_notification_batch(notifications, self.bundle_id)
        except Exception as e:
            self.logger.info("APNS 抛出异常: %s", e)
            self.raven.captureException()
            self.client = APNsClient(self.cert_file, use_sandbox=self.use_sandbox, password=self.passphrase)

        self.logger.info("APNS 推送结束！")

        return {'invalid_ios_tokens': invalid_tokens}
