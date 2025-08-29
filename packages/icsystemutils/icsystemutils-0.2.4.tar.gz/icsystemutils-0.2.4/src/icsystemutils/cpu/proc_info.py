from pathlib import Path
import typing

from iccore.filesystem import read_file
from iccore.serialization.key_value import get_key_value_blocks
from iccore.dict_utils import get_key_or_default_int
from iccore.system.cpu import PhysicalProcessor


def _to_physical_proc(identifier: int, block: dict) -> dict:
    proc: dict = {"id": identifier}
    if "model name" in block:
        proc["model"] = block["model name"]
    if "cache size" in block:
        # Assuming KB
        cache_size, _ = block["cache size"].split(" ")
        proc["cache_size"] = cache_size
    if "siblings" in block:
        proc["siblings"] = int(block["siblings"])
    if "cpu cores" in block:
        proc["core_count"] = int(block["cpu cores"])
    proc["cores"] = []
    return proc


def _has_entry_for_key(content: list[dict], key: str, check: typing.Any) -> bool:
    for item in content:
        if item[key] == check:
            return True
    return False


def parse(content: str) -> list[PhysicalProcessor]:
    blocks = get_key_value_blocks(content)

    procs = {}
    for block in blocks:
        physical_id = get_key_or_default_int(block, "physical id", 0)
        if physical_id not in procs:
            procs[physical_id] = _to_physical_proc(physical_id, block)

        core_id = get_key_or_default_int(block, "core id", 0)
        cores = procs[physical_id]["cores"]
        if not _has_entry_for_key(cores, "id", core_id):
            cores.append({"id": core_id, "threads": []})

        processor_id = get_key_or_default_int(block, "processor", 0)
        threads = procs[physical_id]["cores"][core_id]["threads"]
        if not _has_entry_for_key(threads, "id", processor_id):
            threads.append({"id": processor_id})

    return [PhysicalProcessor(**p) for p in procs.values()]


def read(path: Path = Path("/proc/cpuinfo")) -> list[PhysicalProcessor]:
    return parse(read_file(path))
