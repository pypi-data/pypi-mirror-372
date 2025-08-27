import random

from schemas.process import Process
from schemas.process_type import ProcessType


class ProcessMother:
    def __init__(self):
        self.processes = [
            Process(pid=1, command="init", type=ProcessType.TASK, priority=None),
            Process(pid=2, command="bash", type=ProcessType.THREAD, priority=None),
            Process(pid=3, command="kworker", type=ProcessType.KTHREAD, priority=None),
            Process(pid=4, command="python", type=ProcessType.TASK, priority=None),
            Process(pid=5, command="top", type=ProcessType.THREAD, priority=None),
            Process(pid=6, command="htop", type=ProcessType.TASK, priority=None),
            Process(pid=7, command="systemd", type=ProcessType.KTHREAD, priority=None),
            Process(pid=8, command="tmux", type=ProcessType.THREAD, priority=None),
            Process(pid=9, command="node", type=ProcessType.TASK, priority=None),
            Process(pid=10, command="java", type=ProcessType.KTHREAD, priority=None),
            Process(pid=11, command="emacs", type=ProcessType.THREAD, priority=None),
            Process(pid=12, command="vim", type=ProcessType.TASK, priority=None),
            Process(pid=13, command="zsh", type=ProcessType.THREAD, priority=None),
            Process(pid=14, command="docker", type=ProcessType.KTHREAD, priority=None),
        ]

    def get_random_processes(self, count: int = 5) -> list[Process]:
        return random.sample(self.processes, min(count, len(self.processes)))
