import logging


class Base:
    def __init__(self, config):
        self.logger = logging.getLogger('doordu-push')
        fh = logging.FileHandler('doordu-push.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setLevel(logging.INFO)
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
        self.logger.setLevel(logging.INFO)
        self.config = config

        setup = getattr(self, 'setup')
        if setup:
            setup()

