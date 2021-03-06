"""
{
    users: ['zhangshan', 'lisi', 'wangwu']
}
"""
import json

import falcon
import redis
import itertools

from .base import Base


class OnlineResource(Base):
    def setup(self):
        pool = redis.ConnectionPool(host=self.config['redis']['host'],
                                    port=self.config.getint('redis', 'port'),
                                    db=0,
                                    password = self.config['redis']['auth'])
        self.r = redis.Redis(connection_pool=pool)

    def on_get(self, req, resp):
        content = req.stream.read()
        users = req.get_param_as_list('users') or []
        self.logger.info("users: %s", users)

        response = {
            'users': None
        }
        try:
            if len(users):
                users_states = self.r.hmget('mqtt', users)
                self.logger.info("state: %s", users_states)
                online_users = [user.decode('utf-8') for user in users_states if user is not None]
                response['users'] = online_users
        except Exception as e:
            self.logger.error("抛出异常: %s", e)

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(response)




