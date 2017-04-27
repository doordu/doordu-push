import logging
import os



class Base:
    def __init__(self, config, client):
        self.config = config
        self.client = client

        setup = getattr(self, 'setup')
        if setup:
            setup()

