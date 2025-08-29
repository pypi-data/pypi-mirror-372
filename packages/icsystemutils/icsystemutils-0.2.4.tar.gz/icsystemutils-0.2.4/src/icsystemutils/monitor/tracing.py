from pathlib import Path

from iccore.serialization import read_yaml
from iccore.filesystem import read_file_lines
from iccore.system import SystemEvent
from iccore.logging_utils import LogLine


def _on_log_line(line: str, delimiter="|") -> LogLine | None:

    if line.startswith(delimiter) or delimiter not in line:
        return None

    entries = line.split(delimiter)
    if len(entries) != 3:
        return None

    timestamp, thread_id, message = entries
    thread_id = thread_id.strip()
    if thread_id.startswith("0x"):
        thread_int = int(thread_id[2 : len(thread_id)], 16)
    else:
        thread_int = int(thread_id)
    return LogLine(float(timestamp.strip()), thread_int, message.strip())


def _read_log(path: Path) -> list[LogLine]:
    trace_lines = []
    for line in read_file_lines(path):
        maybe_trace = _on_log_line(line)
        if maybe_trace:
            trace_lines.append(maybe_trace)
    return trace_lines


def _get_last_event_of_type(event_type: str, events):
    for event in reversed(events):
        if event.event_type == event_type:
            return event
    return None


def _get_trace_info(line: LogLine, prefix) -> tuple | None:
    if not line.message.startswith(prefix):
        return None

    msg_no_prefix = line.message[len(prefix) : len(line.message)].strip()
    msg_split = msg_no_prefix.split(" ")
    if len(msg_split) != 2:
        return None
    return tuple(msg_split)


def _get_config_event(config: dict, label: str) -> dict | None:
    if "events" not in config:
        return None
    for event in config["events"]:
        if event["label"] == label:
            return event
    return None


def process(trace_file: Path, trace_config_path: Path) -> list[SystemEvent]:

    config = read_yaml(trace_config_path)
    trace_lines = _read_log(trace_file)

    if "prefix" in config:
        prefix = f'{config["prefix"]}:'
    else:
        prefix = "trace:"

    events = []
    for trace_line in trace_lines:
        trace_info = _get_trace_info(trace_line, prefix)
        if not trace_info:
            continue
        tag, label = trace_info
        event = _get_config_event(config, label)
        if not event:
            continue

        if tag == "Start":
            events.append(
                SystemEvent(
                    event_type=label,
                    start_time=trace_line.timestamp,
                    thread_id=trace_line.thread_id,
                )
            )
        elif tag == "Finish":
            last_event = _get_last_event_of_type(label, events)
            if last_event:
                last_event = last_event.model_copy(
                    update={"end_time": trace_line.timestamp}
                )

    return events
