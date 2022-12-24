import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse

from computer.function_process import End
from computer.process_monitor import ProcessMonitor
from loaded_function import LoadedFunction

'''The Request Handler runs the requests, maps them to the correct method and supply many tools for request handling.
Only GET is implemented.
'''


class RequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        endpoint = urlparse(self.path).path
        match endpoint:
            case '/sleep_and_sum':
                self.on_sleep_and_sum()
            case '/active_processes':
                self.on_active_processes()
            case '/request_counter':
                self.on_request_counter()
            case other:
                self.send_error(404, f'{other} Not Found')

    # """
    # If sleep and sum got bad arguments in the uri it returns an error, else -
    # It uses the process monitor (a thread safe singleton) to compute a heavy function.
    # it passes a LoadedFunction, a structure that hold a callable and the arguments to call it with.
    # it can get back as an answer an End if the computation failed - if so a 500 error will be called, else -
    # it write the answer to the output stream
    # """
    def on_sleep_and_sum(self):
        query = get_query_arguments(self.path)
        if not query:
            self.send_error(HTTPStatus.BAD_REQUEST)
            return

        answer = ProcessMonitor().compute(LoadedFunction(heavy_addition, tuple([3, *query])))
        self._send_answer(answer)

    def _send_answer(self, answer):
        if isinstance(answer, End):
            self.send_error(HTTPStatus.BAD_REQUEST, 'Computation was too heavy')
        else:
            self.send_response(HTTPStatus.OK)
            self.end_headers()
            self.wfile.write(str(answer).encode())

    # returns a list of the active processes from the monitor
    def on_active_processes(self):
        self.send_response(HTTPStatus.OK)
        self.end_headers()
        self.wfile.write(str(ProcessMonitor().active_processes).encode())

    # returns the number of handled requests from the monitor
    def on_request_counter(self):
        self.send_response(HTTPStatus.OK)
        self.end_headers()
        self.wfile.write((str(ProcessMonitor().handled_requests)).encode())


# The function that simulates a heavy cpu computation
def heavy_addition(seconds, a: int, b: int):
    time.sleep(seconds)
    return a + b


# parse the uri to get two query arguments.
# if there are two arguments return a tuple(a,b) and if there isn't return None
def get_query_arguments(uri: str):
    query = tuple(map(lambda var: safe_cast(var.split("=").pop(), float), urlparse(uri).query.split("&")[:2]))

    if len(query) != 2:
        return False

    a, b = query
    if a is None or b is None:
        return False
    return a, b


# safely convert a type to a different one by returning a default value on a value error
def safe_cast(val, into_type, default=None):
    try:
        return into_type(val)
    except (ValueError, TypeError):
        return default
