import logging
import os

from raven import Client


class Base:
    def __init__(self, config):
        self.logger = logging.getLogger('doordu-push')
        fh = logging.FileHandler(os.path.join(os.path.dirname(__file__), 'doordu-push.log'))
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(filename)s - %(lineno)d - %(message)s')
        fh.setLevel(logging.INFO)
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
        self.logger.setLevel(logging.INFO)
        self.config = config
        self.client = Client('https://fa6faa5cea834cbd9cfc404fb72de7aa:6b9ac91556d8405da3bf1f75e20e4239@sentry.io/104967')

        setup = getattr(self, 'setup')
        if setup:
            setup()

