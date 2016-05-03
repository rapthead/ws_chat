# -*- coding: utf-8 -*-
"""
    Simple sockjs-tornado chat application. By default will listen on port 8080.
"""
import tornado.ioloop
import tornado.web

import tornadoredis.pubsub
import sockjs.tornado


class IndexHandler(tornado.web.RequestHandler):
    """Regular HTTP handler to serve the chatroom page"""
    def get(self):
        self.render('index.html')


subscriber = tornadoredis.pubsub.SockJSSubscriber(tornadoredis.Client())


class SubscriptionHandler(sockjs.tornado.SockJSConnection):
    """
    SockJS connection handler.

    Note that there are no "on message" handlers - SockJSSubscriber class
    calls SockJSConnection.broadcast method to transfer messages
    to subscribed clients.
    """
    def __init__(self, *args, **kwargs):
        super(SubscriptionHandler, self).__init__(*args, **kwargs)
        subscriber.subscribe('messages-updated', self)

    def on_close(self):
        subscriber.unsubscribe('messages-updated', self)


if __name__ == "__main__":
    import logging
    logging.getLogger().setLevel(logging.DEBUG)

    # 1. Create chat router
    RedisRouter = sockjs.tornado.SockJSRouter(SubscriptionHandler, '/chat-ws')

    # 2. Create Tornado application
    app = tornado.web.Application(
            [(r"/", IndexHandler)] + RedisRouter.urls
    )

    # 3. Make Tornado app listen on port 8080
    app.listen(8080)

    # 4. Start IOLoop
    tornado.ioloop.IOLoop.instance().start()
