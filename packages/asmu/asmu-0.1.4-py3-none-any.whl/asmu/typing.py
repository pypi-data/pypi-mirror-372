"""This file stores abreviation of complex custom types."""
from typing import Any, Callable, Optional, Protocol, Tuple, TypeAlias, Union

import numpy as np
import numpy.typing as npt
import sounddevice as sd

from .acore import AAnalyzer, AEffect, AGenerator, AInterface

InA: TypeAlias = Union[AGenerator, AEffect, AInterface]
"""Type for ACore devices that can connect to inputs"""

InAs = Tuple[Tuple[Optional[InA], int], ...]
"""Tyoe for multiple InA devices and their corresponding channel number."""

ABlock = npt.NDArray[np.float32]
"""Type for single channel audio data block transferred by ACore devices.
ABlock.shape = (samples)"""

FFTWindow = npt.NDArray[Any]
"""Type for windowing time domain data prior to FFT.
Can be any float type, because it's converted to np.float32 anyways.
FFTWindow.shape = (windowsize)"""

FFTInput = npt.NDArray[np.float32]
"""Type for multi channel FFT data block.
Size depends on the input data window size.
FFTInput.shape = (windowsize, channels)"""

FFTOutput = npt.NDArray[np.complex128]
"""Type for multi channel FFT data block.
Size depends on the input data window size.
FFTOutput.shape = (windowsize/2+1, channels)"""


FFTFreqs = npt.NDArray[np.float32]
"""Type for FFT frequency vector.
Size depends on the input data window size.
FFTFreqs.shape = (windowsize/2+1)"""

FFTAbs = npt.NDArray[np.float32]
"""Type for multi channel abs(FFT) data block.
Size depends on the input data window size.
AvgTemp.shape = (windowsize/2+1, channels)"""

Avg = npt.NDArray[np.float32]
"""Type for multi channel average data.
RMSAvg.shape = (channels)"""

ABuffer = npt.NDArray[np.float32]
"""Type for multi channel audio data block stored in buffers of ACore devices.
ABuffer.shape = (samples, channels)"""

ACore = Union[AGenerator, AAnalyzer, AEffect, AInterface]
"""Type collecting all ACore devices."""

Device = Union[Tuple[Union[str, int, None], Union[str, int, None]],
               Union[str, int, None]]
"""Type for specifying audio device(s) to the Interface class on initialization."""

ADevice = Tuple[Union[str, int, None], Union[str, int, None]]
"""Type for specifying audio devices internally used by the Interface class."""


class CData(Protocol):
    """Type used to reflect sounddevice's CData object used in the callback function."""
    inputBufferAdcTime: float
    outputBufferDacTime: float
    currentTime: float


Callback = Callable[["npt.NDArray[np.float32]",
                     "npt.NDArray[np.float32]",
                     int,
                     CData,
                     sd.CallbackFlags],
                    None]
"""Type used to reflect sounddevice's calback function."""
