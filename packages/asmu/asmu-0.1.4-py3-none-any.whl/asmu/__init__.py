"""Welcome to the API of the asmu module!

To get started, navigate through the submodules on the right.

!!! info
    The [asmu.io][] is rarely used directly, but can be usefull to access the paramteres of audio interface IO.
    [asmu.processor][] and [asmu.acore][] are used for custum devices,
    that should probabpy be implemented in the package source code directly.
"""
import logging
import os
from typing import TYPE_CHECKING, Any, Literal, Optional

# enable sounddevice ASIO (before importing the other modules that require sounddevice)
os.environ["SD_ENABLE_ASIO"] = "1"

from . import analyzer, effect, exceptions, generator, io, typing  # noqa: E402
from .afile import AFile  # noqa: E402
from .asetup import ASetup  # noqa: E402
from .interface import Interface, TestInterface  # noqa: E402

if TYPE_CHECKING:
    import sounddevice as sd


__all__ = ["Interface", "TestInterface", "ASetup", "AFile",
           "io", "generator", "effect", "analyzer", "typing", "exceptions"]

# enable logging
logging.getLogger("asmu").addHandler(logging.NullHandler())


def query_devices(device: Optional[str | int] = None,
                  kind: Optional[Literal["input", "output"]] = None) -> "sd.DeviceList | dict[str, Any]":
    import sounddevice as sd
    return sd.query_devices(device, kind)
