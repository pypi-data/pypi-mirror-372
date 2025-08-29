import os
from pathlib import Path
import logging
import time
from contextlib import contextmanager

from iccore.system.process import run_async
from iccore.filesystem import write_file

logger = logging.getLogger()


def launch(path: Path, stop_file: Path):
    logger.info("Launching resource monitor")

    os.makedirs(path, exist_ok=True)
    cmd = f"icsystemutils monitor --output_path {path} --stop_file {stop_file}"

    return run_async(
        cmd,
        stdout_path=path / "monitor.out",
        stderr_path=path / "monitor.err",
    )


def close(proc, stop_file: Path, max_wait: int = 10, check_rate: int = 1):
    logger.info("Closing resource monitor")

    write_file(stop_file, "Monitor closed by stop_file")

    wait = max_wait
    while proc.poll() is None and wait > 0:
        logger.info("Waiting for resource monitor to close: %d.", wait)
        time.sleep(check_rate)
        wait -= check_rate

    if wait == 0:
        proc.terminate()
        logger.info(
            "Failed to close monitor after %d seconds. Terminating proc.", max_wait
        )
    if proc.poll() != 0:
        raise ChildProcessError("Process failed to close successfully")

    stop_file.unlink()
    logger.info("Monitor closed")


@contextmanager
def run(path: Path, stop_file: Path = Path("icsystemutils.close")):

    if not stop_file.absolute():
        stop_file = path / stop_file

    proc = launch(path, stop_file)
    try:
        yield proc
    finally:
        close(proc, stop_file)
