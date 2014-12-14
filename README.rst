Redisbahn
=========


A simple proof of concept for passing messages from redis to websocket using Python, Twisted and Autobahn.


Python requirements
-------------------

  - twisted
  - txredisapi
  - autobahn


Start
-----

  - in console, type ``twisted -ny run``
  - in browser, open ``index.html``
  - in console, open ``redis-cli``, then type: ``publish mychannel "hello world!"``
