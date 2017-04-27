import os.path
import json
import time
import traceback
import logging

from apns2.client import APNsClient, Notification
from apns2.payload import Payload


class Apns:
    def __init__(self, use_sandbox, cert_filename, passphrase, bundle_id, raven):
        cert_file = os.path.join(os.path.dirname(__file__), os.path.pardir,
                    'certs', '{}_{}.pem'.format(cert_filename, 'dev' if use_sandbox else 'pro'))

        logging.info("注册APNS通道")
        logging.info("cert_file: %s", cert_file)

        self.use_sandbox = use_sandbox
        self.cert_filename = cert_filename
        self.cert_file = cert_file
        self.bundle_id = bundle_id
        self.passphrase = passphrase
        self.raven = raven

    def push(self, tokens, alert, sound='default', ios_remove_token_url=None, content={}):
        logging.info("开始APNS推送")
        expiry = content['expiredAt'] if 'expiredAt' in content else None
        logging.info("Tokens: %s, Sound: %s, Expiry: %s", tokens, sound, expiry)
        logging.info("Alert: %s, Extra: %s", alert, content)

        invalid_tokens = []

        payload = Payload(alert=alert, sound=sound, badge=1, custom=content)
        notifications = (Notification(token=token, payload=payload) for token in tokens)

        try:
            print(self.passphrase)
            client = APNsClient(self.cert_file, use_sandbox=self.use_sandbox, password=self.passphrase)
            client.send_notification_batch(notifications, self.bundle_id)
        except Exception as e:
            logging.info("APNS 抛出异常: %s", traceback.format_exc())
            self.raven.captureException()

        logging.info("APNS 推送结束！")

        return {'invalid_ios_tokens': invalid_tokens}
