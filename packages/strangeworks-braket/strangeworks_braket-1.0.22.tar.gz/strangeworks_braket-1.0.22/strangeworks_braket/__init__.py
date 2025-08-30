"""Strangeworks Braket SDK"""
import importlib.metadata

from .device import StrangeworksDevice  # noqa: F401
from .job import StrangeworksQuantumJob  # noqa: F401
from .task import StrangeworksQuantumTask  # noqa: F401


__version__ = importlib.metadata.version("strangeworks-braket")
