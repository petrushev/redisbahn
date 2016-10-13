from twisted.internet import reactor
from twisted.python import log
from twisted.application.service import Service

from txredisapi import SubscriberProtocol, RedisFactory
from autobahn.twisted.websocket import listenWS


class RedisSubscriberProtocol(SubscriberProtocol):

    def connectionMade(self):
        self.subscribe(self.factory.channel)

    def connectionLost(self, failure):
        # probably should stop the reactor as well
        log.err(failure.getErrorMessage())

    def messageReceived(self, pattern, channel, message):
        self.factory.onMessageReceived(message)

class RedisSubscriberConnFactory(RedisFactory):

    def __init__(self, host="localhost", port=6379, dbid=None,
                 reconnect=True, charset="utf-8", password=None):
        uuid = "%s:%s" % (host, port)
        RedisFactory.__init__(self, uuid, dbid, charset=charset, password=password, poolsize=1)
        self._host = host
        self._port = port

        self.protocol = RedisSubscriberProtocol
        self.continueTrying = reconnect

    def connectTCP(self, channel, reactor_):
        self.channel = channel
        reactor_.connectTCP(self._host, self._port, self)

    def onMessageReceived(self, message):
        """Implement this for a way to handle what messages
        from redis subscribe are used for"""
        raise NotImplementedError


class Redis2WebsocketService(Service):
    """Service that connects a redis channel with websocket factory"""

    def __init__(self, wsfactory, redisConnFactory, channel):
        self.wsfactory = wsfactory
        self.redisFactory = redisConnFactory
        self.channel = channel

    def startService(self):
        # here the channel requested from the websocket is passed to the redis conn
        # basically, the listeners of websockets and redis messages are coupled here

        def onMessageReceived(message):
            msg = dict(channel=self.channel, message=message)
            self.wsfactory.broadcast(msg)

        self.redisFactory.onMessageReceived = onMessageReceived

        # start listening for websocket connections
        listenWS(self.wsfactory)

        # connect to redis
        self.redisFactory.connectTCP(self.channel, reactor)
