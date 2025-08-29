from iccore.system.gpu import GpuInfo

from icsystemutils.gpu import nvidia_smi


def read() -> GpuInfo:

    if not nvidia_smi.has_nvidia_smi():
        return GpuInfo(physical_procs=[])

    procs = nvidia_smi.read()

    return GpuInfo(physical_procs=procs)
