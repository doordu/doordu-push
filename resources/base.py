import logging
import os


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

        setup = getattr(self, 'setup')
        if setup:
            setup()

