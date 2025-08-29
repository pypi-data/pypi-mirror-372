import time
import subprocess
import csv
import psutil

from .sample import Sample, CPUSample, GPUSample
from ..gpu.nvidia_smi import has_nvidia_smi


class Sampler:
    """
    Basic parent Sampler class for use with
    ResourceMonitor.
    """

    def __init__(self) -> None:
        self.base_sample: type[Sample]

    def before_sampling(self):
        pass

    def sample(self):
        pass


class CPUSampler(Sampler):
    """
    CPUSampler which records and returns CPUSamples
    for the ResourceMonitor.
    """

    def __init__(self) -> None:
        self.base_sample = CPUSample

    def before_sampling(self):
        psutil.cpu_percent(interval=None)

    def sample(self) -> CPUSample:
        memory = psutil.virtual_memory()
        return CPUSample(
            cpu_percent=psutil.cpu_percent(interval=None),
            memory_percent=memory.percent,
            total_memory=memory.total / 1.0e6,
            sample_time=time.time(),
        )


class GPUSampler(Sampler):
    """
    GPUSampler which records and returns a
    list of GPUSamples for each GPU in the system.
    Used by ResourceMonitor.
    """

    def __init__(self) -> None:
        self.base_sample = GPUSample

    def before_sampling(self):
        if not has_nvidia_smi():
            raise Exception("No NVIDIA GPU detected")

    def assign(self, p: dict) -> GPUSample:
        return GPUSample(
            name=str(p["name"]),
            index=int(p["index"]),
            temperature=int(p["temperature.gpu"]),
            power_draw=float(p["power.draw[W]"]),
            utilisation=int(p["utilization.gpu[%]"]),
            memory_used=int(p["memory.used[MiB]"]),
            memory_free=int(p["memory.free[MiB]"]),
            performance_state=str(p["pstate"]),
        )

    def sample(self) -> list[GPUSample]:
        ret = (
            subprocess.check_output(
                [
                    "nvidia-smi",
                    "--query-gpu=name,"
                    "index,"
                    "temperature.gpu,"
                    "power.draw,"
                    "utilization.gpu,"
                    "memory.used,"
                    "memory.free,"
                    "pstate",
                    "--format=csv,nounits",
                ]
            )
            .decode("utf-8")
            .strip()
        )
        ret_csv = csv.DictReader(ret.replace(" ", "").splitlines(), delimiter=",")
        return [self.assign(p) for p in list(ret_csv)]
