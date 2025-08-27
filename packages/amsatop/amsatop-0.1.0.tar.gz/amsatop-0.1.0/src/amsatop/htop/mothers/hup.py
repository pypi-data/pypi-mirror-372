import random

from schemas.process import Process
from schemas.process_type import ProcessType


class HupMother:
    def __init__(self):
        self.processes = [
            Process(pid=28, command="sshd", type=ProcessType.TASK, priority=10),
            Process(pid=29, command="nginx", type=ProcessType.THREAD, priority=5),
            Process(pid=30, command="postgres", type=ProcessType.KTHREAD, priority=1),
            Process(pid=31, command="redis", type=ProcessType.TASK, priority=7),
            Process(pid=32, command="chrome", type=ProcessType.THREAD, priority=8),
            Process(pid=33, command="firefox", type=ProcessType.TASK, priority=6),
            Process(pid=34, command="docker", type=ProcessType.KTHREAD, priority=3),
            Process(pid=35, command="mysql", type=ProcessType.TASK, priority=9),
            Process(pid=36, command="emacs", type=ProcessType.THREAD, priority=4),
            Process(pid=37, command="vim", type=ProcessType.TASK, priority=2),
            Process(pid=38, command="zsh", type=ProcessType.THREAD, priority=5),
            Process(pid=39, command="python", type=ProcessType.TASK, priority=7),
            Process(pid=40, command="java", type=ProcessType.KTHREAD, priority=6),
        ]

    def get_random_processes(self, count: int = 5) -> list[Process]:
        return random.sample(self.processes, min(count, len(self.processes)))
