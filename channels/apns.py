from apns2.client import APNsClient, Notification
from apns2.payload import Payload

import os.path
import json
import time

from apnsclient import *
import requests

class Apns:
    def __init__(self, logger, use_sandbox, cert_filename, passphrase, raven):
        cert_file = os.path.join(os.path.dirname(__file__), os.path.pardir,
                    'certs', '{}_{}.pem'.format(cert_filename, 'dev' if use_sandbox else 'pro'))

        self.logger = logger
        self.logger.info("注册APNS通道")
        self.logger.info("cert_file: %s", cert_file)

        session = Session()
        self.use_sandbox = use_sandbox
        self.cert_filename = cert_filename
        self.cert_file = cert_file
        self.passphrase = passphrase
        self.raven = raven
        self.conn = session.get_connection("push_sandbox" if use_sandbox else "push_production",
                                            cert_file=cert_file, passphrase=passphrase)
        # Send the message.
        self.srv = APNs(self.conn)

        self.client = APNsClient(cert_file, use_sandbox=use_sandbox)

    def push(self, tokens, alert, sound='default', ios_remove_token_url=None, content={}):
        self.logger.info("开始APNS推送")
        expiry = content['expiredAt'] if 'expiredAt' in content else None
        self.logger.info("Tokens: %s, Sound: %s, Expiry: %s", tokens, sound, expiry)
        self.logger.info("Alert: %s, Extra: %s", alert, content)

        invalid_tokens = []

        payload = Payload(alert=alert, sound=sound, badge=1)
        notifications = (Notification(token=token, payload=payload) for token in tokens)

        try:
            self.client.send_notification_batch(notifications, 'com.doordu.mobile')
        except Exception as e:
            self.raven.captureException()

        return {'invalid_ios_tokens': invalid_tokens}
