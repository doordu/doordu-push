import configparser
import os

import falcon

from resources.push import PushResource
from resources.online import OnlineResource

app = falcon.API()

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__),"config.ini"))

push = PushResource(config)
online = OnlineResource(config)

app.add_route('/push', push)
app.add_route('/online', online)
