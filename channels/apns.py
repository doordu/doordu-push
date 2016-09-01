import OpenSSL
OpenSSL.SSL.SSLv3_METHOD = OpenSSL.SSL.TLSv1_METHOD

import os.path
import binascii

from apnsclient import *


class Apns:

    def __init__(self, logger, use_sandbox, cert_filename):
        cert_file = os.path.join(os.path.dirname(__file__), os.path.pardir,
                    'certs', '{}_{}.pem'.format(cert_filename, 'dev' if use_sandbox else 'pro'))

        self.logger = logger
        self.logger.info("注册APNS通道")

        session = Session()
        self.conn = session.get_connection("push_sandbox" if use_sandbox else "push_production",
                                            cert_file=cert_file, passphrase='doordu123456')

    def push(self, tokens, title, content={}):
        service = APNs(self.conn)
        invalid_tokens = []
        contain_invalid_token = False
        while True:
            self.logger.info("开始APNS推送")
            self.logger.info("Tokens: %s", tokens)
            self.logger.info("Title: %s", title)
            message = Message(tokens, alert=title, badge=1, sound='default', extra=content)
            try:
                res = service.send(message)
            except binascii.Error:
                self.logger.error("Token有误忽略！")
                break

            for token, reason in res.failed.items():
                code, errmsg = reason
                self.logger.error("推送失败！Token: {0}, 错误: {1}, code: {2}".format(token,
                                                                               errmsg, code))
                if code == 8:
                    tokens.remove(token)
                    invalid_tokens.append(token)
                    contain_invalid_token = True

            if contain_invalid_token:
                continue

            for code, errmsg in res.errors:
                self.logger.error("推送出错！错误: %s", errmsg)

            if res.needs_retry():
                retry_message = res.retry()

            break
        self.logger.info("结束APNS推送")
        return {'invalid_ios_tokens': invalid_tokens}



