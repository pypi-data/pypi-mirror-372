"""
This module is for getting Mac specific cpu info

See https://man.freebsd.org/cgi/man.cgi?sysctl(8) for BSD sysctl info
"""

import subprocess
from pathlib import Path

from iccore.system.cpu import PhysicalProcessor


def _read_sysctl_key(key: str, sysctl_path: Path = Path("/usr/sbin/sysctl")) -> str:
    ret = subprocess.check_output([str(sysctl_path), key])
    return ret.decode("utf-8").strip()


def _get_key_value(content: str, delimiter: str = ":") -> tuple[str, str]:
    key, value = content.split(delimiter)
    return key.strip(), value.strip()


def parse(content: str) -> list[PhysicalProcessor]:
    machdep = {}
    for line in content.splitlines():
        key, value = _get_key_value(line)
        key_no_prefix = key[len("machdep.cpu.") :]
        machdep[key_no_prefix] = value

    proc: dict = {"id": 0, "cores": []}
    if "brand_string" in machdep:
        proc["model"] = machdep["brand_string"]

    core_count = 1
    if "core_count" in machdep:
        core_count = int(machdep["core_count"])

    for idx in range(core_count):
        proc["cores"].append({"id": idx, "threads": []})

    thread_count = 1
    if "thread_count" in machdep:
        thread_count = int(machdep["thread_count"])
    threads_per_core = int(thread_count / core_count)
    for core in proc["cores"]:
        for idx in range(threads_per_core):
            core["threads"].append({"id": idx})
    return [PhysicalProcessor(**proc)]


def read() -> list[PhysicalProcessor]:
    content = _read_sysctl_key("machdep.cpu")
    return parse(content)
