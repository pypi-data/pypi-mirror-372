#!/usr/bin/env python3

import argparse
import logging
from pathlib import Path

from iccore import runtime, logging_utils

from icsystemutils.cpu import cpu_info
from icsystemutils.gpu import gpu_info
from icsystemutils.monitor import ResourceMonitor, Config, tracing
from icsystemutils.monitor.sampler import Sampler, CPUSampler, GPUSampler
from icsystemutils.monitor.handler import (
    OutputHandler,
    CSVOutputHandler,
    TerminalOutputHandler,
)

logger = logging.getLogger(__name__)


def launch_common(args):
    runtime.ctx.set_is_dry_run(args.dry_run)
    logging_utils.setup_default_logger()


def read_cpu_info(args):
    launch_common(args)

    logger.info("Reading CPU info")

    info = cpu_info.read()
    print(info.model_dump_json(indent=4))

    logger.info("Finished Reading CPU info")


def read_gpu_info(args):
    launch_common(args)

    logger.info("Reading GPU info")

    info = gpu_info.read()
    print(info.model_dump_json(indent=4))

    logger.info("Finished Reading GPU information")


def monitor(args) -> None:
    launch_common(args)

    logger.info("Starting monitor")

    output_handlers: list[OutputHandler] = [TerminalOutputHandler()]

    if args.output_path:
        output_handlers.append(CSVOutputHandler(Path(args.output_path)))
    stopfile: Path | None = None
    if args.stop_file:
        stopfile = Path(args.stop_file).resolve()

    config = Config(stopfile=stopfile)

    arg_samplers: list[Sampler] = [CPUSampler()]
    if args.include == "gpu":
        arg_samplers = [GPUSampler()]
    elif args.include == "all":
        arg_samplers = [CPUSampler(), GPUSampler()]

    resource_monitor = ResourceMonitor(
        config,
        samplers=arg_samplers,
        output_handlers=output_handlers,
    )

    resource_monitor.run()
    logger.info("Finished monitor")


def cli_tracing(args):
    launch_common(args)

    logger.info("Starting processing trace")
    events = tracing.process(args.trace_file.resolve(), args.trace_config.resolve())
    print(events)
    logger.info("Finished processing trace")


def main_cli():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dry_run",
        type=int,
        default=0,
        help="Dry run script - 0 can modify, 1 can read, 2 no modify - no read",
    )
    subparsers = parser.add_subparsers(required=True)

    read_cpu_parser = subparsers.add_parser("read_cpu")
    read_cpu_parser.set_defaults(func=read_cpu_info)

    read_gpu_parser = subparsers.add_parser("read_gpu")
    read_gpu_parser.set_defaults(func=read_gpu_info)

    monitor_parser = subparsers.add_parser("monitor")
    monitor_parser.set_defaults(func=monitor)

    monitor_parser.add_argument(
        "--output_path",
        type=str,
        default="",
        help="Path to an output folder. Will log to console if empty.",
    )
    monitor_parser.add_argument(
        "--stop_file",
        type=str,
        default="",
        help="Path to a file whose existance causes the monitor to close.",
    )

    monitor_parser.add_argument(
        "--include",
        nargs="?",
        default="cpu",
        choices=("cpu", "gpu", "all"),
        help="Specifies what monitoring will occur.",
    )

    tracing_parser = subparsers.add_parser("tracing")
    tracing_parser.add_argument(
        "--trace_file",
        type=Path,
        help="Path to the trace file to load",
    )
    tracing_parser.add_argument(
        "--trace_config",
        type=Path,
        help="Path to the trace config to load",
    )
    tracing_parser.set_defaults(func=cli_tracing)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main_cli()
