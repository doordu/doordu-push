import OpenSSL
OpenSSL.SSL.SSLv3_METHOD = OpenSSL.SSL.TLSv1_METHOD

import os.path
import binascii
import json


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

    def push(self, tokens, alert, sound='default', ios_remove_token_url=None, content={}):
        self.logger.info("开始APNS推送")
        self.logger.info("Tokens: %s, Sound: %s", tokens, sound)
        # New message to 3 devices. You app will show badge 10 over app's icon.
        message = Message(tokens,
                          alert=alert, badge=1, sound=sound, extra=content)
        invalid_tokens = []
        contain_invalid_token = False
        while tokens:
            try:
                res = self.srv.send(message)
            except binascii.Error:
                self.logger.error("Token有误！")
                self.raven.captureMessage("Token有误! {}".format(tokens))
                break
            except OpenSSL.SSL.SysCallError:
                self.logger.error("SSL握手失败，重新尝试连接")
                session = Session()
                self.conn = session.get_connection("push_sandbox" if self.use_sandbox else "push_production",
                                                   cert_file=self.cert_file, passphrase=self.passphrase)
                # Send the message.
                self.srv = APNs(self.conn)
                self.raven.captureException()
                continue
            except Exception:
                self.logger.error("Can't connect to APNs, looks like network is down")
                self.raven.captureException()
                break
            else:
                # Check failures. Check codes in APNs reference docs.
                for token, reason in res.failed.items():
                    code, errmsg = reason
                    # according to APNs protocol the token reported here
                    # is garbage (invalid or empty), stop using and remove it.
                    self.logger.error("Device failed: {0}, reason: {1}".format(token, errmsg))
                    if code == 8:
                        tokens.remove(token)
                        invalid_tokens.append(token)
                        contain_invalid_token = True

                # Check failures not related to devices.
                for code, errmsg in res.errors:
                    self.logger.error("Error: {}".format(errmsg))

                if contain_invalid_token:
                    contain_invalid_token = False
                    continue

                # Check if there are tokens that can be retried
                if res.needs_retry():
                    # repeat with retry_message or reschedule your task
                    retry_message = res.retry()

                break

        self.logger.info("APNS推送结束")

        if invalid_tokens and ios_remove_token_url:
            self.logger.info("Invalid tokens: %s", invalid_tokens)
            payload = json.dumps({'invalid_tokens': invalid_tokens})
            try:
                requests.delete(ios_remove_token_url, data=payload, headers={'Content-Type': 'application/json'})
            except Exception:
                pass


        return {'invalid_ios_tokens': invalid_tokens}
