import os
from pathlib import Path
import csv
from pydantic import BaseModel

from iccore.serialization import csv_utils

from .sampler import Sampler


class OutputHandler:
    """
    Parent class to support all OutputHandlers
    when running ResourceMonitor
    """

    def __init__(self) -> None:
        pass

    def on_before_sample(self, samplers: list[Sampler]) -> None:
        pass

    def on_sample(self, samples: dict) -> None:
        pass

    def on_after_sample(self, samplers: list[Sampler]) -> None:
        pass


class TerminalOutputHandler(OutputHandler):
    """
    OutputHandler used when monitor is run to
    continuously print results to the CLI.
    """

    def on_sample(self, samples: dict) -> None:
        for vals in samples.values():
            if isinstance(vals, list):
                print(csv_utils.get_header_str(vals[0]) + "\n")
                for val in vals:
                    print(csv_utils.get_line(val) + "\n")
            else:
                print(csv_utils.get_header_str(vals) + "\n")
                print(csv_utils.get_line(vals) + "\n")


class CSVOutputHandler(OutputHandler):
    """
    Output Handler which supports the creation of a CSV
    file containing ResourceMonitor results.
    """

    def __init__(self, output_path: Path | None = None) -> None:
        if output_path:
            self.output_directory = Path(output_path)
        else:
            self.output_directory = Path(os.getcwd()) / "icsystemutils_monitor"
        self.csv_sampler_handler: dict = {}

    def on_before_sample(self, samplers: list[Sampler]) -> None:
        for sampler in samplers:
            name = Path(
                self.output_directory / (sampler.base_sample.__name__ + ".csv")
            ).resolve()
            f = open(name, "w", encoding="utf-8")
            writer = csv.DictWriter(
                f, fieldnames=csv_utils.get_fieldnames(sampler.base_sample)
            )
            writer.writeheader()
            each = {"output_handle": f, "writer": writer}
            self.csv_sampler_handler[sampler.base_sample.__name__] = each

    def write_to_csv(self, sample: BaseModel) -> None:
        self.csv_sampler_handler[sample.__class__.__name__]["writer"].writerow(
            sample.model_dump()
        )

    def on_sample(self, samples: dict) -> None:

        for vals in samples.values():
            if isinstance(vals, list):
                for val in vals:
                    self.write_to_csv(val)
            else:
                self.write_to_csv(vals)

    def on_after_sample(self, samplers: list[Sampler]) -> None:
        for names in self.csv_sampler_handler:
            self.csv_sampler_handler[names]["output_handle"].close()
