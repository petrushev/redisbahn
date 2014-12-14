from twisted.internet import reactor
from twisted.python import log
from twisted.application.service import Service

from txredisapi import SubscriberProtocol, RedisFactory
from autobahn.twisted.websocket import listenWS


class RedisSubProtocol(SubscriberProtocol):

    def connectionMade(self):
        self.subscribe(self.factory.channel)

    def connectionLost(self, failure):
        # probably should stop the reactor as well
        log.err(failure.getErrorMessage())

    def messageReceived(self, pattern, channel, message):
        # push all received messages to factory
        msg = dict(channel=channel, message=message)
        self.factory.callback(msg)


def RedisSubConnFactory(host="localhost", port=6379, dbid=None,
                        reconnect=True, charset="utf-8", password=None):
    """Returns connection factory.
    The callable should be passed
    - channel: the redis channel listened to
    - callback: the function called with the payload on each message
    """

    def connFactory(channel, callback):
        uuid = "%s:%s" % (host, port)
        factory = RedisFactory(uuid, dbid, charset=charset, password=password,
                               poolsize=1)
        factory.protocol = RedisSubProtocol
        factory.continueTrying = reconnect

        # custom attributes
        factory.channel = channel
        factory.callback = callback

        reactor.connectTCP(host, port, factory)
        return factory.deferred

    return connFactory


class Redis2WebsocketService(Service):
    """Service that connects a redis channel with websocket factory
    """

    def __init__(self, wsfactory, redisConnFactory, channel):
        self.wsfactory = wsfactory
        wsfactory.service = self
        self.redisFactory = redisConnFactory
        self.channel = channel

    def startService(self):
        # here the channel requested from the websocket is passed to redis conn
        # basically, the listeners of websockets and redis messages are coupled here
        self.redisFactory(channel=self.channel,
                          callback=self.wsfactory.broadcast)

        # start listening for websocket connections
        listenWS(self.wsfactory)
