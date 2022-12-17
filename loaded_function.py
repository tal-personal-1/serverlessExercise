from dataclasses import dataclass
from typing import Callable


@dataclass
class LoadedFunction:
    function: Callable
    args: tuple

    def run(self):
        return self.function(*self.args)