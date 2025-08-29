"""
This module obtains NVIDIA GPU information

See https://docs.nvidia.com/deploy/nvidia-smi/index.html for nvidia-smi manual
"""

import shutil
import subprocess
from csv import DictReader
from dataclasses import dataclass

from iccore.system.gpu import GpuProcessor, Process


@dataclass(frozen=True)
class NvidiaSmiQuery:

    gpu = [
        "name",
        "serial",
        "pci.bus_id",
        "index",
        "memory.free",
        "memory.total",
    ]

    compute_apps = [
        "gpu_serial",
        "pid",
        "name",
        "used_memory",
    ]

    format = ["csv", "nounits"]


def _nvidia_smi_command(query: str) -> list[str]:
    command = ["nvidia-smi"]
    if query == "gpu":
        command.append("--query-gpu=" + ",".join(NvidiaSmiQuery.gpu))
        command.append("--format=" + ",".join(NvidiaSmiQuery.format))
        return command
    if query == "compute_apps":
        command.append("--query-compute-apps=" + ",".join(NvidiaSmiQuery.compute_apps))
        command.append("--format=" + ",".join(NvidiaSmiQuery.format))
        return command
    return command


def has_nvidia_smi() -> bool:
    if shutil.which("nvidia-smi") is None:
        return False
    return True


def _read_nvidia_smi(query_params: list[str]) -> str:
    ret = subprocess.check_output(query_params)
    return ret.decode("utf-8").strip()


def _gpu_from_smi(p: dict, pids: list[Process] = []) -> GpuProcessor:
    gpu_proc = GpuProcessor(
        id=int(p["index"]),
        model=str(p["name"]),
        serial=int(p["serial"]),
        bus_id=str(p["pci.bus_id"]),
        max_memory=int(p["memory.total[MiB]"]),
        free_memory=int(p["memory.free[MiB]"]),
        processes=pids,
    )
    return gpu_proc


def _pid_from_smi(p: dict) -> Process:
    return Process(pid=int(p["pid"]), name=str(p["process_name"]))


def _assign_pid(pids: list[dict]) -> dict:
    serials: dict = {}
    for each_pid in pids:
        if each_pid["gpu_serial"] not in serials:
            serials[each_pid["gpu_serial"]] = []
        serials[each_pid["gpu_serial"]].append(each_pid)
    return {s: [_pid_from_smi(p) for p in serials[s]] for s in serials}


def parse(content: str) -> DictReader[str]:
    formatted_content = content.replace(" ", "").splitlines()
    return DictReader(formatted_content, delimiter=",")


def read() -> list[GpuProcessor]:

    pids = list(parse(_read_nvidia_smi(_nvidia_smi_command("compute_apps"))))
    if pids:
        assigned_pids = _assign_pid(pids)
        return [
            _gpu_from_smi(p, assigned_pids[p["serial"]])
            for p in list(parse(_read_nvidia_smi(_nvidia_smi_command("gpu"))))
        ]

    return [
        _gpu_from_smi(p)
        for p in list(parse(_read_nvidia_smi(_nvidia_smi_command("gpu"))))
    ]
