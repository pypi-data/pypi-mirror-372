from enum import Enum


class ProcessType(Enum):
    TASK = "task"
    THREAD = "thread"
    KTHREAD = "kthread"
