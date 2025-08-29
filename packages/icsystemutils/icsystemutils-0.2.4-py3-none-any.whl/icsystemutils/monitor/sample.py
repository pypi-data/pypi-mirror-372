import csv
import typing
from pathlib import Path

from pydantic import BaseModel


class Sample(BaseModel, frozen=True):
    """
    Base sample model for use with ResourceMonitor.
    Uses pydantic BaseModel as a framework.
    """

    pass


class CPUSample(Sample, frozen=True):
    """
    Standard CPU Sample for use with psutil.
    Records CPU statistics.
    """

    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    total_memory: float = 0.0
    sample_time: float = 0.0


class GPUSample(Sample, frozen=True):
    """
    Standard GPU sample for use with nvidia-smi.
    Records GPU statistics.
    """

    name: str = ""
    index: int = 0
    temperature: int = 0
    power_draw: float = 0.0
    utilisation: int = 0
    memory_used: int = 0
    memory_free: int = 0
    performance_state: str = ""


def read_csv(path: Path, sample: type[Sample]) -> list[Sample]:

    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [sample(**typing.cast(dict, row)) for row in reader]
