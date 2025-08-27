import asyncio
import tornado
import tornado.web


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        # breakpoint()
        self.write("Hello, world")


def make_app():
    return tornado.web.Application(
        [
            # TODO
            (r"/_app/", MainHandler),
        ]
    )
