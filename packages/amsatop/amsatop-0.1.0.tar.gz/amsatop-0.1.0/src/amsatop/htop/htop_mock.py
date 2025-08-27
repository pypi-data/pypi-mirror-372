from typing import override

from htop.htop import Htop
from mothers.hup import HupMother
from mothers.priority import PriorityMother
from mothers.process import ProcessMother
from schemas.process import Process


class HtopMock(Htop):
    @override
    def get_processes(self) -> list[Process]:
        process_mother = ProcessMother()
        return process_mother.get_random_processes()

    @override
    def get_priorities(self) -> list[Process]:
        priority_mother = PriorityMother()
        return priority_mother.get_random_processes()

    @override
    def get_hup(self) -> list[Process]:
        hup_mother = HupMother()
        return hup_mother.get_random_processes()
