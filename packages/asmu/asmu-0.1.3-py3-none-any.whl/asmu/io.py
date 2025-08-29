"""In this submodule you can find the Input and Output classes used in the "audio processors".
You will rarely use them directly, but the special IInput and IOutput classes used by the interface,
store a lot of important information you may want to access or modify."""
import contextlib
import logging
from typing import TYPE_CHECKING, Any, Optional, Tuple, Union

import numpy as np

if TYPE_CHECKING:
    from pathlib import Path

    import numpy.typing as npt

    from .interface import Interface
    from .processor import Analyzer, Effect, Generator
    from .typing import InA

logger = logging.getLogger(__name__)


class Input:
    def __init__(self, processor: Union["Effect", "Interface", "Analyzer"]):
        """Input base class.

        Args:
            processor: Reference to the corresponding Processor object.
        """
        self._processor = processor
        self._output: Optional["Output"] = None

    def __del__(self) -> None:
        if self._output is not None:
            self._output.disconnect(self)
        else:
            logger.info("No output to disconnect.")

    @property
    def connected_output(self) -> Optional["Output|IInput"]:
        return self._output

    @connected_output.setter
    def connected_output(self, value: Optional["Output|IInput"]) -> None:
        self._output = value
        # if an output was set or unset, update acore module of processor
        self._processor.update_acore()


class Output:
    def __init__(self, processor: Union["Generator", "Effect", "Interface"]):
        """Output base class.
        (Tuples are used to store the inputs because they are static typas and therefore more efficient than lists.)

        Args:
            processor: Reference to the corresponding Processor object.
        """
        self._processor = processor
        self._inputs: Tuple[Input, ...] = ()

    def __del__(self) -> None:
        for inpu in self.inputs:
            self.disconnect(inpu)

    @property
    def inputs(self) -> Tuple[Input, ...]:
        return self._inputs

    @property
    def idx(self) -> int:
        return self._processor.outputs.index(self)

    @property
    def acore(self) -> "InA":
        return self._processor.acore

    def connect(self, input: "Input") -> None:
        """Connect this output to the given Input.

        Args:
            input: The Input to connect this output to.

        Example: Connect devices
            ```python
            import asmu

            interface = asmu.Interface()
            sine = asmu.generator.Sine(interface, 1000)
            gain = asmu.effect.Gain(interface, 0.5)

            sine.output().connect(gain.input())
            gain.output().connect(interface.ioutput(ch = 2))
            ```
        """
        if input not in self._inputs:
            self._inputs += (input, )
            input.connected_output = self
            self._processor.update_acore()
        else:
            logger.info("Input is already connected to output.")

    def disconnect(self, input: "Input") -> None:
        """Disconnect this output from the given Input.

        Args:
            input: The Input to disconnect this output from.
        """
        if input.connected_output is self and input in self._inputs:
            self._inputs = tuple(inp for inp in self._inputs if inp != input)
            input.connected_output = None
            self._processor.update_acore()
        else:
            logger.info("Trying to disconnect an input that is not connected to this output")


class IInput(Output):
    def __init__(self,
                 interface: "Interface",
                 channel: int,
                 reference: Optional[bool] = None,
                 name: Optional[str] = None,
                 gain: Optional[float] = None,
                 latency: Optional[int] = None,
                 color: Optional[str] = None,
                 cPa: Optional[float] = None,
                 fPa: Optional[float] = None,
                 datePa: Optional[str] = None,
                 cV: Optional[float] = None,
                 fV: Optional[float] = None,
                 dateV: Optional[str] = None,
                 cFR: Optional["npt.NDArray[np.complex128]"] = None,
                 fFR: Optional["npt.NDArray[np.float32]"] = None,
                 pos: Optional["npt.NDArray[Any]"] = None):
        """A special type of Output class used for the analog interface inputs.
        It stores various settings and options.

        Args:
            interface: Reference to an Interface instance.
            channel: Channel number on the interface.
            reference: Flag if the channel is used as reference for computation/calibration.
            name: Trivial name.
            gain: The gain setting of the input.
            latency: Individual IO latency (relative to Interface's system latency).
            color: A color used for plotting.
            cPa: Pressure calibration factor in Pascal.
            fPa: Frequency used for pressure calibration.
            datePa: Date of last pressure calibration (ISO 8601).
            cV: Voltage calibration factor in Volts.
            fV: Frequency used for voltage calibration.
            dateV: Date of last voltage calibration (ISO 8601).
            cFR: Frequency response calibration vector.
            fFR: Corresponding frequency vector.
            pos: Position vector.
        """
        self._interface = interface
        self.channel = channel
        self.reference = reference
        self.name = name
        self.gain = gain
        self.latency = latency
        self.color = color
        self.cPa = cPa
        self.fPa = fPa
        self.datePa = datePa
        self.cV = cV
        self.fV = fV
        self.dateV = dateV
        self.cFR = cFR
        self.fFR = fFR
        self.pos = pos
        super().__init__(interface)

    def serialize(self, setup_path: "Path") -> dict[Any, Any]:
        data: dict[str, Any] = {}
        data["channel"] = self.channel
        if self.reference is not None:
            data["reference"] = bool(self.reference)
        if self.name is not None:
            data["name"] = self.name
        if self.gain is not None:
            data["gain"] = float(self.gain)
        if self.latency is not None:
            data["latency"] = int(self.latency)
        if self.color is not None:
            data["color"] = self.color
        if self.cPa is not None:
            data["cPa"] = float(self.cPa)
        if self.fPa is not None:
            data["fPa"] = float(self.fPa)
        if self.datePa is not None:
            data["datePa"] = str(self.datePa)
        if self.cV is not None:
            data["cV"] = float(self.cV)
        if self.fV is not None:
            data["fV"] = float(self.fV)
        if self.dateV is not None:
            data["dateV"] = str(self.dateV)
        if self.cFR is not None:
            _path = setup_path.with_suffix(f"/in_ch{self.channel:3.0f}_cFR.npy")
            np.save(_path, self.cFR)
            data["cFR"] = _path
        if self.fFR is not None:
            _path = setup_path.with_suffix(f"/in_ch{self.channel:3.0f}_fFR.npy")
            np.save(_path, self.fFR)
            data["fFR"] = _path
        if self.pos is not None:
            data["pos"] = list(self.pos)
        return data

    def deserialize(self, data: dict[str, Any]) -> None:
        self.channel = int(data["channel"])
        with contextlib.suppress(KeyError):
            self.reference = bool(data["reference"])
        with contextlib.suppress(KeyError):
            self.name = data["name"]
        with contextlib.suppress(KeyError):
            self.gain = float(data["gain"])
        with contextlib.suppress(KeyError):
            self.latency = int(data["latency"])
        with contextlib.suppress(KeyError):
            self.color = data["color"]
        with contextlib.suppress(KeyError):
            self.cPa = float(data["cPa"])
        with contextlib.suppress(KeyError):
            self.fPa = float(data["fPa"])
        with contextlib.suppress(KeyError):
            self.datePa = str(data["datePa"])
        with contextlib.suppress(KeyError):
            self.cV = float(data["cV"])
        with contextlib.suppress(KeyError):
            self.fV = float(data["fV"])
        with contextlib.suppress(KeyError):
            self.dateV = str(data["dateV"])
        with contextlib.suppress(KeyError):
            self.cFR = np.load(data["cFR"])
        with contextlib.suppress(KeyError):
            self.fFR = np.load(data["fFR"])
        with contextlib.suppress(KeyError):
            self.pos = np.array(data["pos"])


class IOutput(Input):
    def __init__(self,
                 interface: "Interface",
                 channel: int,
                 reference: Optional[bool] = None,
                 name: Optional[str] = None,
                 gain: Optional[float] = None,
                 latency: Optional[int] = None,
                 color: Optional[str] = None,
                 cPa: Optional[float] = None,
                 fPa: Optional[float] = None,
                 datePa: Optional[str] = None,
                 cV: Optional[float] = None,
                 fV: Optional[float] = None,
                 dateV: Optional[str] = None,
                 cFR: Optional["npt.NDArray[np.complex128]"] = None,
                 fFR: Optional["npt.NDArray[np.float32]"] = None,
                 pos: Optional["npt.NDArray[Any]"] = None):
        """A special type of Input class used for the analog interface outputs.
        It stores various settings and options.

        Args:
            interface: Reference to an Interface instance.
            channel: Channel number on the interface.
            reference: Flag if the channel is used as reference for computation/calibration.
            name: Trivial name.
            gain: The gain setting of the output.
            latency: Individual IO latency (relative to Interface's system latency).
            color: A color used for plotting.
            cPa: Pressure calibration factor in Pascal.
            fPa: Frequency used for pressure calibration.
            datePa: Date of last pressure calibration (ISO 8601).
            cV: Voltage calibration factor in Volts.
            fV: Frequency used for voltage calibration.
            dateV: Date of last voltage calibration (ISO 8601).
            cFR: Frequency response calibration vector.
            fFR: Corresponding frequency vector.
            pos: Position vector.
        """
        self._interface = interface
        self.channel = channel
        self.reference = reference
        self.name = name
        self.gain = gain
        self.latency = latency
        self.color = color
        self.cPa = cPa
        self.fPa = fPa
        self.datePa = datePa
        self.cV = cV
        self.fV = fV
        self.dateV = dateV
        self.cFR = cFR
        self.fFR = fFR
        self.pos = pos
        super().__init__(interface)

    def serialize(self, setup_path: "Path") -> dict[str, Any]:
        data: dict[str, Any] = {}
        data["channel"] = self.channel
        if self.reference is not None:
            data["reference"] = self.reference
        if self.name is not None:
            data["name"] = self.name
        if self.gain is not None:
            data["gain"] = float(self.gain)
        if self.latency is not None:
            data["latency"] = int(self.latency)
        if self.color is not None:
            data["color"] = self.color
        if self.cPa is not None:
            data["cPa"] = float(self.cPa)
        if self.fPa is not None:
            data["fPa"] = float(self.fPa)
        if self.datePa is not None:
            data["datePa"] = str(self.datePa)
        if self.cV is not None:
            data["cV"] = float(self.cV)
        if self.fV is not None:
            data["fV"] = float(self.fV)
        if self.dateV is not None:
            data["dateV"] = str(self.dateV)
        if self.cFR is not None:
            _path = setup_path.with_suffix(f"/out_ch{self.channel:3.0f}_cFR.npy")
            np.save(_path, self.cFR)
            data["cFR"] = _path
        if self.fFR is not None:
            _path = setup_path.with_suffix(f"/out_ch{self.channel:3.0f}_fFR.npy")
            np.save(_path, self.fFR)
            data["fFR"] = _path
        if self.pos is not None:
            data["pos"] = list(self.pos)
        return data

    def deserialize(self, data: dict[str, Any]) -> None:
        self.channel = data["channel"]
        with contextlib.suppress(KeyError):
            self.reference = data["reference"]
        with contextlib.suppress(KeyError):
            self.name = data["name"]
        with contextlib.suppress(KeyError):
            self.gain = float(data["gain"])
        with contextlib.suppress(KeyError):
            self.latency = int(data["latency"])
        with contextlib.suppress(KeyError):
            self.color = data["color"]
        with contextlib.suppress(KeyError):
            self.cPa = float(data["cPa"])
        with contextlib.suppress(KeyError):
            self.fPa = float(data["fPa"])
        with contextlib.suppress(KeyError):
            self.datePa = str(data["datePa"])
        with contextlib.suppress(KeyError):
            self.cV = float(data["cV"])
        with contextlib.suppress(KeyError):
            self.fV = float(data["fV"])
        with contextlib.suppress(KeyError):
            self.dateV = str(data["dateV"])
        with contextlib.suppress(KeyError):
            self.cFR = np.load(data["cFR"])
        with contextlib.suppress(KeyError):
            self.fFR = np.load(data["fFR"])
        with contextlib.suppress(KeyError):
            self.pos = np.array(data["pos"])
