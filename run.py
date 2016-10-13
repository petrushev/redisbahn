from twisted.application.service import Application
from redisbahn.server import RedisSubscriberConnFactory, Redis2WebsocketService

from redisbahn import broadcast

BIND = 'ws://localhost:9090'
CHANNEL = 'mychannel'
REDIS_CONN = '127.0.0.1', 6379


wsFactory = broadcast.Factory(url=BIND)
redisConnFactory = RedisSubscriberConnFactory(host=REDIS_CONN[0], port=REDIS_CONN[1])
service = Redis2WebsocketService(wsFactory, redisConnFactory, channel=CHANNEL)

application = Application('ws server')
service.setServiceParent(application)
