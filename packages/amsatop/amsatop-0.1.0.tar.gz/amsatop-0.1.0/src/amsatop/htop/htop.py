import os
from abc import ABC, abstractmethod

from schemas.process import Process


class Htop(ABC):
    proc_folder: str

    def __init__(self):
        super().__init__()
        self.proc_folder = os.getenv("PROC_FOLDER", "/proc")

    @abstractmethod
    def get_processes(self) -> list[Process]:
        pass

    @abstractmethod
    def get_priorities(self) -> list[Process]:
        pass

    @abstractmethod
    def get_hup(self) -> list[Process]:
        pass
