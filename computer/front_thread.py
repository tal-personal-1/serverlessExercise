import threading
from multiprocessing import Queue, Event
from threading import Thread

from computer.function_process import FunctionProcess
from computer.shared_info import SharedInfo
from loaded_function import LoadedFunction


# The FrontThread is a thread that is responsible to start, stop, and communicate with a process.
# It also updates the monitors shared info, so it knows the activity status of the process
class FrontThread(Thread):

    # When a front is created it uses the supplied shared info,
    # creates queues to communicate with other threads, creates a new FunctionProcess and ProcessTimer to stop it
    # and sets a thread safe Event to synchronize when it is done.
    def __init__(self, shared_info: SharedInfo):
        Thread.__init__(self)
        self.shared_info = shared_info
        self._tuned_process = FunctionProcess()
        self._input_queue = Queue()
        self._output_queue = Queue()
        self.finished = Event()
        self.timer = ProcessTimer([self._tuned_process, self.finished, shared_info])

    # called from a different thread, sends the computation to the front thread and get an answer from it
    def compute(self, loaded_function: LoadedFunction):
        self._input_queue.put(loaded_function)
        return self._output_queue.get()

    # run executes after the thread starts (using FrontThread.Start())
    # It starts a process and wait for computation requests,
    # then it waits for the process to complete and returns an answer (can be an End)
    def run(self):
        self._start_process()
        while not self.finished.is_set():
            request = self._input_queue.get()
            self._got_request()
            self._got_answer(self._tuned_process.compute(request))

    # When a process starts it is considered alive, so we update the shared info
    def _start_process(self):
        self._tuned_process.start()
        self.shared_info.add_alive(self._tuned_process.pid, self)

    # When the front thread gets a request it restarts the process timer - unless the process is dead.
    def _got_request(self):
        if self.finished.is_set():
            return
        self.timer.cancel()
        self.timer = ProcessTimer([self._tuned_process, self.finished, self.shared_info])
        self.timer.start()

    # When answer is returned the process is free, so the front is added to the shared info ready list
    def _got_answer(self, value):
        self._output_queue.put(value)
        self.shared_info.add_ready(self._tuned_process.pid)

    # the front has a property to reflect its process's pid
    @property
    def pid(self):
        return self._tuned_process.pid


# the process timer class is an extension of a regular timer - it just sets a default interval and function to run
# when the timer is done
class ProcessTimer(threading.Timer):
    def __init__(self, args):
        threading.Timer.__init__(self, 6.0, process_timer, args)


# will run on a different thread when ProcessTimer finishes (defaults to 6).
# it kills the FunctionProcess, so it returns an End from the process queue, sets the front finished to True,
# and removes the front from the live processes list.
def process_timer(tuned_process: FunctionProcess, finished: Event, shared_info: SharedInfo):
    if shared_info.remove_alive(tuned_process.pid):
        return
    finished.set()
    tuned_process.sabotage()
    tuned_process.kill()
