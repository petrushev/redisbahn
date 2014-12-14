"""A protocol which pushes messages to all connections whenever a message
is broadcasted from the parrent factory
"""

import json
from uuid import uuid4

from twisted.internet import reactor
from autobahn.twisted.websocket import WebSocketServerProtocol, WebSocketServerFactory


class Protocol(WebSocketServerProtocol):

    factoryRef = None

    def onOpen(self):
        # use this factory ref for future funneling of channels to separate clients
        self.factoryRef = uuid4().bytes
        self.factory.register(self)

    def connectionLost(self, reason):
        WebSocketServerProtocol.connectionLost(self, reason)
        self.factory.unregister(self)

    def onMessage(self, msg):
        self.sendMessage(json.dumps(msg))


class Factory(WebSocketServerFactory):

    protocol = Protocol
    clients = dict()

    def __init__(self, *args, **kwargs):
        WebSocketServerFactory.__init__(self, *args, **kwargs)

    def register(self, client):
        self.clients[client.factoryRef] = client

    def unregister(self, client):
        del self.clients[client.factoryRef]

    def broadcast(self, msg):
        # when message is received, pass to all clients
        for cli in self.clients.itervalues():
            reactor.callLater(0, cli.onMessage, msg)
