import os
import psutil

from iccore.system.process import Process  # NOQA


def load(local_rank: int = 0) -> Process:
    pid = os.getpid()

    ps = psutil.Process(pid)
    user = ps.username()

    return Process(local_rank=local_rank, pid=pid, username=user)
