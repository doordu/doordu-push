import os
import logging

import falcon
import yaml
from raven import Client

from resources.push import PushResource
from resources.online import OnlineResource

app = falcon.API()

config_file = os.path.join(os.path.dirname(__file__), "config.yaml")
config = None

with open(config_file, "r") as handle:
    config = yaml.load(handle)

logger = logging.getLogger('doordu-push')
fh = logging.FileHandler(os.path.join(os.path.dirname(__file__), 'doordu-push.log'))
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(filename)s - %(lineno)d - %(message)s')
fh.setLevel(logging.INFO)
fh.setFormatter(formatter)
logger.addHandler(fh)
logger.setLevel(logging.INFO)
client = Client('https://fa6faa5cea834cbd9cfc404fb72de7aa:6b9ac91556d8405da3bf1f75e20e4239@sentry.io/104967')

push = PushResource(config, logger, client)
online = OnlineResource(config, logger, client)

app.add_route('/push', push)
app.add_route('/online', online)
