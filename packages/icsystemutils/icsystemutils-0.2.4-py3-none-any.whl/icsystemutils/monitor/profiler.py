"""
A wrapper class for a profiler, eg cprofile
"""

from pathlib import Path
import cProfile
from cProfile import Profile
import pstats
import io
from pstats import SortKey


class Profiler:

    def __init__(self, output_path: Path = Path("profile.prof")):
        self.handle: Profile | None = None
        self.output_path: Path = output_path
        self.stat_depth = 40

    def start(self):
        self.handle = cProfile.Profile()
        self.handle.enable()

    def stop(self) -> str:

        if not self.handle:
            return ""

        self.handle.disable()
        self.handle.dump_stats(str(self.output_path))

        s = io.StringIO()
        ps = pstats.Stats(self.handle, stream=s)
        ps.sort_stats(SortKey.CUMULATIVE)
        ps.print_stats(self.stat_depth)

        return s.getvalue()
