import re
from wsgiref.simple_server import make_server

class Request:
    def __init__(self, environ):
        self.method = environ['REQUEST_METHOD']
        self.path = environ['PATH_INFO']
        self.query = environ['QUERY_STRING']
        self.environ = environ

class Response:
    def __init__(self, body, status=200, headers=None):
        self.body = body.encode() if isinstance(body, str) else body
        self.status = status
        self.headers = headers or [('Content-type', 'text/html; charset=utf-8')]

class Webloop:
    def __init__(self):
        self.routes = {}

    def route(self, path, methods=['GET']):
        def decorator(func):
            for m in methods:
                self.routes[(path, m)] = func
            return func
        return decorator

    def __call__(self, environ, start_response):
        request = Request(environ)
        handler = self.routes.get((request.path, request.method))
        if handler:
            response = handler(request)
            if isinstance(response, Response):
                start_response(f"{response.status} OK", response.headers)
                return [response.body]
            else:
                start_response("200 OK", [('Content-type', 'text/html')])
                return [str(response).encode()]
        start_response("404 Not Found", [('Content-type', 'text/plain')])
        return [b"Not Found"]

    def run(self, host="127.0.0.1", port=5000):
        print(f"Webloop running on http://{host}:{port}")
        with make_server(host, port, self) as httpd:
            httpd.serve_forever()
