"""
This module allows calculation and storage of cpu info
"""

import sys

from iccore.system.cpu import CpuInfo

from icsystemutils.cpu import proc_info, sys_ctl


def read() -> CpuInfo:

    if sys.platform == "darwin":
        procs = sys_ctl.read()
    else:
        procs = proc_info.read()

    # This is assuming all processors have same number of cores
    # and all cores have same number of threads
    first_proc = procs[0]
    cores_per_node = len(first_proc.cores)
    threads_per_core = first_proc.cores[0].num_threads

    return CpuInfo(
        physical_procs=procs,
        cores_per_node=cores_per_node,
        threads_per_core=threads_per_core,
    )
