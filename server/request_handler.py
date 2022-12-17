from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse
from server.handler_functions import on_sleep_and_sum, on_active_processes, on_request_counter

'''The Request Handler runs the requests, maps them to the correct method and supply many tools for request handling.
Only GET is implemented.
'''

class RequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        endpoint = urlparse(self.path).path
        match endpoint:
            case '/sleep_and_sum':
                on_sleep_and_sum(self.wfile, self.path, self.send_error)
            case '/active_processes':
                on_active_processes(self.wfile)
            case '/request_counter':
                on_request_counter(self.wfile)
            case other:
                self.send_error(404, f'{other} Not Found')
