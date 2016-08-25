import configparser

import falcon

from resources.push import PushResource

app = falcon.API()

config = configparser.ConfigParser()
config.read("config.ini")

push = PushResource(config)

app.add_route('/push', push)
