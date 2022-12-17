from multiprocessing import Process, Queue

from loaded_function import LoadedFunction


# The FunctionProcess is a Process that can handle and return a computation
class FunctionProcess(Process):
    # __init__ defines queues that will send information between this process and another
    def __init__(self):
        Process.__init__(self)
        self._input_queue = Queue()
        self._output_queue = Queue()

    # run executes after a process starts (using Process.Start())
    # it waits for a computation and then returns it using the queues
    def run(self):
        while True:
            loaded_function: LoadedFunction = self._input_queue.get()
            answer = loaded_function.run()
            self._output_queue.put(answer)

    # compute is called externally using a different process, it inputs a computation and waits for an answer
    def compute(self, loaded_function: LoadedFunction):
        self._input_queue.put(loaded_function)
        return self._output_queue.get()

    # sabotage output from the process queue an answer - End.
    # It is used to end blocking communication with the process
    def sabotage(self):
        self._output_queue.put(End())


class End:
    pass
