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
client = Client('https://97d0be6069704601a8000b2a95a1298b:2eaf1284edc04ef3b15d859d36919845@sdlog.doordu.com:8205/14')

push = PushResource(config, logger, client)
online = OnlineResource(config, logger, client)

app.add_route('/push', push)
app.add_route('/online', online)
