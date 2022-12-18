from multiprocessing import Lock

from computer.front_thread import FrontThread
from computer.function_process import End
from computer.shared_info import SharedInfo
from loaded_function import LoadedFunction


# The ProcessMonitor class is a thread safe singleton that holds process management related data
# it can handle computation requests, count the number of requests handled and return a list of all active processes
class ProcessMonitor:
    _instance = None
    _lock = Lock()

    # the __new__ function is called every time a new ProcessMonitor is requested.
    # if there isn't an instance already it creates one with the shared memory needed to manage the processes,
    # and the request counter.
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(ProcessMonitor, cls).__new__(cls)
                    cls._instance._shared_info = SharedInfo()
                    cls._instance._request_counter = RequestCounter()
        return cls._instance

    # gets a function with arguments to compute and returns an answer
    # either an End or the computation result
    def compute(self, loaded_function: LoadedFunction):
        front = self._get_front()
        answer = front.compute(loaded_function)
        if not isinstance(answer, End):
            self._request_counter.request_handled()
        return answer

    # A front is a type of thread that manages a process - in order to use a process you need its front.
    # _get_front either makes a new front and starts it or returns an existing ready to use front.
    def _get_front(self):
        front = self._shared_info.get_ready_front()
        if front is None:
            front = FrontThread(self._shared_info)
            front.start()
        return front

    # returns a list of alive pids
    @property
    def active_processes(self):
        return self._shared_info.alive_pids

    # returns a list of requests handled
    @property
    def handled_requests(self):
        return self._request_counter.handled_requests


# A class to safely hold the number of requests handled using a simple lock
class RequestCounter:
    def __init__(self):
        self._counter = 0
        self._lock = Lock()

    # locks - adds one to counter - release
    def request_handled(self):
        with self._lock:
            self._counter += 1

    # locks - return counter - release
    @property
    def handled_requests(self):
        with self._lock:
            return self._counter
