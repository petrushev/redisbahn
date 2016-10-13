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
        """Called when websocket client is connected"""
        # use this factory ref for future funneling of channels to separate clients
        self.factoryRef = uuid4().bytes
        self.factory.register(self)

    def connectionLost(self, reason):
        """Called when websocket client is disconnected"""
        self.factory.unregister(self)
        WebSocketServerProtocol.connectionLost(self, reason)

    def onMessage(self, msg):
        """Sends a json serialized message to the websocket client"""
        self.sendMessage(json.dumps(msg))


class Factory(WebSocketServerFactory):

    protocol = Protocol
    clients = dict()

    def register(self, client):
        """Keeps track of websocket clients in dictionary"""
        self.clients[client.factoryRef] = client

    def unregister(self, client):
        """Removes websocket client from registry"""
        del self.clients[client.factoryRef]

    def broadcast(self, msg):
        """When message is received, it is pass to all connected clients"""
        for cli in self.clients.itervalues():
            reactor.callLater(0, cli.onMessage, msg)
