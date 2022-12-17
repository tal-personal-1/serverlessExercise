from http.server import ThreadingHTTPServer

from server.request_handler import RequestHandler


# Start a server on a port and uses the RequestHandler to handle requests on
def run(port):
    with ThreadingHTTPServer(('', port), RequestHandler) as httpd:
        httpd.serve_forever()
