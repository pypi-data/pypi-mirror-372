"""
eFleetScheduler - Electric Fleet Scheduling Tool
"""

# src/efleetscheduler/__init__.py

from importlib.metadata import version as _pkg_version
import importlib as _importlib

__author__ = "Carolina Gil Ribeiro"
try:
    __version__ = _pkg_version("efleetscheduler")
except Exception:  # during editable installs/builds
    __version__ = "V1.0.1"

# We export two *modules* and two *symbols*
__all__ = [
    "schedule_configure",     # module
    "generate_graphs",        # module
    "ScheduleGenerator",      # class (from schedule_generator_1)
    "generate_schedules",     # function (from schedule_generator_2)
]

def __getattr__(name):
    if name == "ScheduleGenerator":
        from .schedule_generator_1 import ScheduleGenerator
        return ScheduleGenerator
    if name == "generate_schedules":
        from .schedule_generator_2 import generate_schedules
        return generate_schedules
    if name in ("schedule_configure", "generate_graphs"):
        # return the submodule itself
        return _importlib.import_module(f".{name}", __name__)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

def __dir__():
    return sorted(list(globals().keys()) + __all__)
