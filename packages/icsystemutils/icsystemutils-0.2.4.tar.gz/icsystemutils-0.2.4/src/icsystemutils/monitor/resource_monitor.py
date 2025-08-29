import logging
import time
from pathlib import Path

from pydantic import BaseModel

from .handler import OutputHandler
from .sampler import Sampler

logger = logging.getLogger(__name__)


class Config(BaseModel, frozen=True):
    """
    Config to modify the parameters when running
    ResourceMonitor.
    """

    target_proc: int = -1
    self_proc: int = -1
    sample_interval: int = 2000  # ms
    sample_duration: float = 0.0  # s
    stopfile: Path | None = None


class ResourceMonitor:
    """
    Resource monitor which runs for some config specified time
    and can use OutputHandlers to print/save the results.
    """

    def __init__(
        self,
        config: Config = Config(),
        samplers: list[Sampler] | None = None,
        output_handlers: list[OutputHandler] | None = None,
    ) -> None:
        self.config: Config = config
        self.samplers = samplers if samplers else []
        self.output_handlers = output_handlers if output_handlers else []

    def _sample(self) -> dict:
        return {s.base_sample.__name__: s.sample() for s in self.samplers}

    def on_before_sample(self) -> None:
        for sampler in self.samplers:
            sampler.before_sampling()
        for output_handler in self.output_handlers:
            output_handler.on_before_sample(self.samplers)

    def on_sample(self, samples: dict) -> None:
        for output_handler in self.output_handlers:
            output_handler.on_sample(samples)

    def on_after_sample(self) -> None:
        for output_handler in self.output_handlers:
            output_handler.on_after_sample(self.samplers)

    def run(self) -> None:
        count = 0
        self.on_before_sample()

        while True:
            samples = self._sample()
            self.on_sample(samples)

            time.sleep(self.config.sample_interval / 1000)
            count += 1
            if (
                self.config.sample_duration > 0
                and (self.config.sample_interval * count) / 1000
                >= self.config.sample_duration
            ):
                break

            if self.config.stopfile and self.config.stopfile.exists():
                break
        logger.info("Closing run")

        self.on_after_sample()
