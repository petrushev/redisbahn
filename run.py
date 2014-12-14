BIND = 'ws://localhost:9090'
CHANNEL = 'mychannel'
REDIS_CONN = '127.0.0.1', 6379

from twisted.application.service import Application
from redisbahn.server import RedisSubConnFactory, Redis2WebsocketService
from redisbahn import broadcast

wsFactory = broadcast.Factory(url=BIND)
redisConnFactory = RedisSubConnFactory(host=REDIS_CONN[0], port=REDIS_CONN[1])
service = Redis2WebsocketService(wsFactory, redisConnFactory, channel=CHANNEL)

application = Application('ws server')
service.setServiceParent(application)
