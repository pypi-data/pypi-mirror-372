import random

from schemas.process import Process
from schemas.process_type import ProcessType


class PriorityMother:
    def __init__(self):
        self.processes = [
            Process(pid=15, command="sshd", type=ProcessType.TASK, priority=10),
            Process(pid=16, command="nginx", type=ProcessType.THREAD, priority=5),
            Process(pid=17, command="postgres", type=ProcessType.KTHREAD, priority=1),
            Process(pid=18, command="redis", type=ProcessType.TASK, priority=7),
            Process(pid=19, command="chrome", type=ProcessType.THREAD, priority=8),
            Process(pid=20, command="firefox", type=ProcessType.TASK, priority=6),
            Process(pid=21, command="docker", type=ProcessType.KTHREAD, priority=3),
            Process(pid=22, command="mysql", type=ProcessType.TASK, priority=9),
            Process(pid=23, command="emacs", type=ProcessType.THREAD, priority=4),
            Process(pid=24, command="vim", type=ProcessType.TASK, priority=2),
            Process(pid=25, command="zsh", type=ProcessType.THREAD, priority=5),
            Process(pid=26, command="python", type=ProcessType.TASK, priority=7),
            Process(pid=27, command="java", type=ProcessType.KTHREAD, priority=6),
        ]

    def get_random_processes(self, count: int = 5) -> list[Process]:
        return random.sample(self.processes, min(count, len(self.processes)))
