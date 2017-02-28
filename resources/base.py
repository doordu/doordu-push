import logging
import os



class Base:
    def __init__(self, config, logger, client):
        self.config = config
        self.logger = logger
        self.client = client

        setup = getattr(self, 'setup')
        if setup:
            setup()

