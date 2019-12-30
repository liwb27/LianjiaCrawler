from app import app


if __name__ == "__main__":
    app.run()
    # from tornado.wsgi import WSGIContainer
    # from tornado.httpserver import HTTPServer
    # from tornado.ioloop import IOLoop

    # http_server = HTTPServer(WSGIContainer(app))
    # http_server.listen(8000)
    # IOLoop.instance().start()
