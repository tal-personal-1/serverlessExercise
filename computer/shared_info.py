from multiprocessing import Lock


# A class that hold shared info about the front threads
# _ready_pids is a list of all the fronts that are open, have a running process - but are not used.
# _pids_to_fronts is a dictionary of all the fronts that are alive
class SharedInfo:
    def __init__(self):
        self._ready_pids = list()
        self._pids_to_fronts = dict()
        self._lock = Lock()

    # adds a front pid to the ready list - only if it's still alive.
    def add_ready(self, pid):
        with self._lock:
            if pid in self._pids_to_fronts:
                self._ready_pids.append(pid)

    # removes a front pid from the ready list - only if it's in the list.
    def remove_ready(self, pid):
        with self._lock:
            if pid in self._ready_pids:
                self._ready_pids.remove(pid)

    # removes a front pid from the ready list and returns the front itself
    def get_ready_front(self):
        with self._lock:
            if len(self._ready_pids) > 0:
                return self._pids_to_fronts[self._ready_pids.pop(0)]

    # add a new front to pids_to_fronts
    def add_alive(self, pid: int, front):
        with self._lock:
            self._pids_to_fronts[pid] = front

    # remove a front from the shared info
    def remove_alive(self, pid):
        with self._lock:
            self._pids_to_fronts.pop(pid)
            if pid in self._ready_pids:
                self._ready_pids.remove(pid)

    # a property that returns as a list all the alive processes pids
    @property
    def alive_pids(self):
        with self._lock:
            return tuple(self._pids_to_fronts.keys())
