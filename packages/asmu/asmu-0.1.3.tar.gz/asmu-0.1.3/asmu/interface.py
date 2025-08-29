import logging
from typing import TYPE_CHECKING, Any, List, Optional, Tuple

import sounddevice as sd

from .acore import AInterface
from .exceptions import DeviceError
from .io import IInput, IOutput
from .processor import Processor

if TYPE_CHECKING:
    from pathlib import Path

    from .asetup import ASetup
    from .processor import Analyzer
    from .typing import ADevice, Callback, CData, Device, InAs

logger = logging.getLogger(__name__)


class Interface(Processor):
    def __init__(self,
                 asetup: Optional["ASetup"] = None,
                 device: "Device" = None,
                 samplerate: int = 44100,
                 blocksize: int = 1024,
                 analog_input_channels: Optional[List[int]] = None,
                 analog_output_channels: Optional[List[int]] = None):
        """The Interface class represents the audio interface or soundcard.
        It is holding the audio generator and manages settings.
        The settings can either be specified on intialization, by an ASetup class, or used as default.

        Args:
            asetup: Reference to an ASetup instance.
                If set, loads the settings from the given ASetup and the other arguments are ignored.
                If you dont want that, specify it after initialization, by setting `Interface.asetup = ASetup`.
            device: Tuple of device names for different input and output device.
                If None, the default devices are used.
            samplerate: The samplerate in samples per second.
            blocksize: The blocksize defines the samples per frame.
            analog_input_channels: List if analog input channels, only works for ASIO, CoreAudio devices.
            analog_output_channels: List if analog output channels, only works for ASIO, CoreAudio devices.

        Notes:
            The device names can be obtained by running
            ```python linenums="1" title="List audio devices"
            import asmu
            asmu.query_devices()
            ```
        """
        # this is used for the analyzers to add themselfes later
        self._analyzers: Tuple["Analyzer", ...] = ()

        self.asetup = asetup
        if asetup is not None:
            asetup.load()
        else:
            # init from given values
            self._samplerate = samplerate
            self._blocksize = blocksize
            self.latency = 0

            # init device if not test
            self._device: ADevice = (None, None)
            if not self._is_test():
                if device is None or device == (None, None):
                    # if None use default
                    self._device = sd.default.device
                elif isinstance(device, str) or isinstance(device, int):
                    # if single device use for input and output
                    self._device = (device, device)
                elif isinstance(device, tuple):
                    self._device = device
                else:
                    DeviceError("Device specification is not correct, refer to the API.")

            # if not asio or coraaudio or test overwrite the channel lists with all available in-/outputs
            if not self._is_test() and not self._is_asio() and not self._is_ca():
                logger.warning("No ASIO or CoreAudio device specified, channel numbers are ignored.")
                analog_input_channels = list(range(sd.query_devices(device=self._device[0],
                                                   kind="input")["max_input_channels"]))
                analog_input_channels = [ch + 1 for ch in analog_input_channels]
                analog_output_channels = list(range(sd.query_devices(device=self._device[1],
                                                    kind="output")["max_output_channels"]))
                analog_output_channels = [ch + 1 for ch in analog_output_channels]

            # set in-/outputs accordingly
            self._iinputs: Tuple["IInput", ...] = ()
            if (self._device[0] is not None or self._is_test()) and analog_input_channels is not None:
                self._iinputs = tuple(IInput(self, iin_ch) for iin_ch in analog_input_channels)
            self._ioutputs: Tuple["IOutput", ...] = ()
            if (self._device[1] is not None or self._is_test()) and analog_output_channels is not None:
                self._ioutputs = tuple(IOutput(self, iout_ch) for iout_ch in analog_output_channels)

            self._ainterface = AInterface(blocksize=self._blocksize, start_frame=self.start_frame)
        super().__init__(self)

    def __del__(self) -> None:
        # deregister from asetup
        if self._asetup is not None:
            self._asetup.interface = None

    @property
    def samplerate(self) -> int:
        return self._samplerate

    @property
    def blocksize(self) -> int:
        return self._blocksize

    @property
    def device(self) -> Optional["Device"]:
        return self._device

    @property
    def start_frame(self) -> int:
        # callback starts at frame 0 so this drops the first three frames
        return -3

    @property
    def asetup(self) -> Optional["ASetup"]:
        return self._asetup

    @asetup.setter
    def asetup(self, value: Optional["ASetup"]) -> None:
        self._asetup = value
        # register in asetup
        if value is not None and self._asetup is not None:
            self._asetup.interface = self

    @property
    def analyzers(self) -> Tuple["Analyzer", ...]:
        return self._analyzers

    @analyzers.setter
    def analyzers(self, value: Tuple["Analyzer", ...]) -> None:
        self._analyzers = value
        self.update_acore()

    @property
    def acore(self) -> "AInterface":
        return self._ainterface

    @property
    def outputs(self) -> Tuple["IInput", ...]:
        return self._iinputs

    @property
    def iinputs(self) -> Tuple["IInput", ...]:
        return self._iinputs

    @property
    def ioutputs(self) -> Tuple["IOutput", ...]:
        return self._ioutputs

    def iinput(self,
               idx: int = 0,
               ch: Optional[int] = None,
               name: Optional[str] = None,
               ref: Optional[bool] = None) -> "IInput":
        """Get the interface analog IInput, which is an asmu Output, by the given argument.

        Args:
            idx: Index in zero indexed list of IInputs.
            ch: Interface analog input channel, stored in the IInput.
            name: Given name of the channel, stored in the IInput.
            ref: The reference IInput.

        Raises:
            ValueError: No IInput for the given argument registered

        Returns:
            Reference to IInput object.
        """
        if ch is not None:
            try:
                return next((outpu for outpu in self._iinputs if outpu.channel == ch))
            except StopIteration as exc:
                raise ValueError(f"No IInput on channel {ch} registered.") from exc
        if name is not None:
            try:
                return next((outpu for outpu in self._iinputs if outpu.name == name))
            except StopIteration as exc:
                raise ValueError(f"No IInput with name {name} registered.") from exc
        if ref is not None:
            try:
                return next((outpu for outpu in self._iinputs if outpu.reference))
            except StopIteration as exc:
                raise ValueError("No reference IInput registered.") from exc
        return self._iinputs[idx]

    def ioutput(self,
                idx: int = 0,
                ch: Optional[int] = None,
                name: Optional[str] = None,
                ref: Optional[bool] = None) -> "IOutput":
        """Get the interface analog IOutput, which is an asmu Input, by the given argument.

        Args:
            idx: Index in zero indexed list of IOutputs.
            ch: Interface analog output channel, stored in the IOutput.
            name: Given name of the channel, stored in the IOutput.
            ref: The reference IInput.

        Raises:
            ValueError: No IOutput for the given argument registered

        Returns:
            Reference to IOutput object.
        """
        if ch is not None:
            try:
                return next((inpu for inpu in self._ioutputs if inpu.channel == ch))
            except StopIteration as exc:
                raise ValueError(f"No IOutput on channel {ch} registered.") from exc
        if name is not None:
            try:
                return next((inpu for inpu in self._ioutputs if inpu.name == name))
            except StopIteration as exc:
                raise ValueError(f"No IOutput with name {name} registered.") from exc
        if ref is not None:
            try:
                return next((inpu for inpu in self._ioutputs if inpu.reference))
            except StopIteration as exc:
                raise ValueError("No reference IOutput registered.") from exc
        return self._ioutputs[idx]

    def _cal_latency(self, time: "CData") -> None:
        """Calculate and store loopback latency without physical connection.

        !!! warning
            Dont rely on this method, as it only calculates the ADC/DAC's internal latency.
            Use [latency_from_rec.py](../examples.md/#latency_from_rec.py)
            to compare this result with the real loopback calibration.

        Args:
            time (CData): The time object given in the callback function.
        """
        self.latency = round((time.outputBufferDacTime - time.inputBufferAdcTime)
                             * self.samplerate + 1.0)  # the +1 was measured experimentally (could be the cable?)

    def _is_asio(self) -> bool:
        """Determine if ALL of the set io devices are ASIO compatible.

        Returns:
            `True`, when all given devices are ASIO compatible. `False` otherwise.
        """
        asio = True
        if self._device[0] is not None:
            asio = ("asio" in str(sd.query_devices(device=self._device[0], kind="input")["name"]).lower())
        if self._device[1] is not None:
            asio = ("asio" in str(sd.query_devices(device=self._device[1], kind="output")["name"]).lower())
        return asio
        return False

    def _is_ca(self) -> bool:
        """Determine if ALL of the set io devices are CoraAudio compatible.

        Returns:
            `True`, when all given devices are CoraAudio compatible. `False` otherwise.
        """
        ca = True
        if self._device[0] is not None:
            ca = ("coreaudio" in str(sd.query_devices(device=self._device[0], kind="input")["name"]).lower())
        if self._device[1] is not None:
            ca = ("coreaudio" in str(sd.query_devices(device=self._device[1], kind="output")["name"]).lower())
        return ca
        return False

    def _is_test(self) -> bool:
        """Used to skip the sounddevice initialization, if the TestInterface class is derived."""
        return False

    # SOUNDDEVICE
    def _init_sounddevice(self) -> None:
        """Initiializes sounddevice with the classes attributes for the given lists of inputs and outputs.
        """
        stream = sd.default
        stream.dtype = ("float32", "float32")
        if self.samplerate is not None:
            stream.samplerate = self.samplerate
        if self.blocksize is not None:
            stream.blocksize = self.blocksize
        stream.device = self.device
        if self._is_asio():
            if self._iinputs:
                # convert to channel names starting with 0
                in_channels = [inpu.channel - 1 for inpu in self._iinputs]
                asio_in = sd.AsioSettings(channel_selectors=in_channels)

                if not self._ioutputs:
                    stream.extra_settings = asio_in
                    stream.channels = len(in_channels)
                    return

            if self._ioutputs:
                out_channels = [output.channel - 1 for output in self._ioutputs]
                asio_out = sd.AsioSettings(channel_selectors=out_channels)

                if not self._iinputs:
                    stream.extra_settings = asio_out
                    stream.channels = len(out_channels)
                    return

            if self._iinputs and self._ioutputs:
                stream.extra_settings = (asio_in, asio_out)
                stream.channels = (len(in_channels), len(out_channels))
                return

        elif self._is_ca():
            raise NotImplementedError("CoreAudio channel selection is not tested!")
            if self._iinputs:
                # convert to channel names starting with 0
                in_channels = [inpu.channel - 1 for inpu in self._iinputs]
                ca_in = sd.CoreAudioSettings(channel_map=in_channels)

                if not self._ioutputs:
                    stream.extra_settings = ca_in
                    stream.channels = len(in_channels)
                    return

            if self._ioutputs:
                out_channels = [-1] * sd.query_devices(device=self.device, kind="output")["max_output_channels"]
                for idx, c in enumerate(self._ioutputs):
                    out_channels[c.channel - 1] = idx
                ca_out = sd.CoreAudioSettings(channel_map=out_channels)

                if not self._iinputs:
                    stream.extra_settings = ca_out
                    stream.channels = len(out_channels)
                    return

            if self._iinputs and self._ioutputs:
                stream.extra_settings = (ca_in, ca_out)
                stream.channels = (len(in_channels), len(out_channels))
                return

    def start(self, end_frame: Optional[int] = None) -> sd.Stream:
        """Start the audio stream.

        Args:
            end_frame: If set, the stream is stopped at the given end_frame.

        Returns:
            Reference to the started sounddevice stream.
            The full documentation is linked
            [here](https://python-sounddevice.readthedocs.io/en/latest/api/streams.html#sounddevice.Stream).
                But the basic functions can be summerized as:

                - `Stream.active`  : `True`, when the stream is active. `False` otherwise.
                    This is useful when end_frame is used, to check if the stream is finished.
                - `Stream.stop()`  : Terminate audio processing.
                    This waits until all pending audio buffers have been played before it returns.
                - `Stream.close()` : Close the stream. This should be used after the stream has been stopped,
                    because the end_frame has been reached or Stream.stop has been called.

                If it is used for an active stream, the audio buffers are discarded.
        """
        self._init_sounddevice()
        self._ainterface.end_frame = end_frame
        stream = sd.Stream(callback=self._ainterface.callback)
        stream.start()
        return stream

    def update_acore(self) -> None:
        # create in_as tuple
        in_as: InAs = ()
        for inp in self._ioutputs:
            # add proper connection constraint
            if inp.connected_output is None:
                in_as = in_as + ((None, 0), )
            else:
                # find channel idx it is connected to
                in_as = in_as + ((inp.connected_output.acore, inp.connected_output.idx), )
        self._ainterface.in_as = in_as
        # count outputs that have a connection
        self._ainterface.out_chs = len(self._iinputs)
        # update alz
        self._ainterface.alzs = tuple(alz.acore for alz in self.analyzers)

    def serialize(self, setup_path: "Path") -> dict[str, Any]:
        data: dict[str, Any] = {}
        data["samplerate"] = int(self._samplerate)
        data["blocksize"] = int(self._blocksize)
        data["latency"] = int(self.latency)

        if self._device is not None:
            data["device"] = tuple(self._device)

        iinputs = []
        for iinput in self._iinputs:
            iinputs.append(iinput.serialize(setup_path))
        data["iinputs"] = iinputs

        ioutputs = []
        for ioutput in self._ioutputs:
            ioutputs.append(ioutput.serialize(setup_path))
        data["ioutputs"] = ioutputs
        return data

    def deserialize(self, data: dict[str, Any]) -> None:
        self._samplerate = int(data["samplerate"])
        self._blocksize = int(data["blocksize"])
        self.latency = int(data["latency"])

        self._device = (None, None)
        try:
            self._device = tuple(data["device"])
        except KeyError:
            pass

        self._iinputs = ()
        for iinput_data in data["iinputs"]:
            iinput = IInput(self, iinput_data["channel"])
            iinput.deserialize(iinput_data)
            self._iinputs += (iinput, )

        self._ioutputs = ()
        for ioutput_data in data["ioutputs"]:
            ioutput = IOutput(self, ioutput_data["channel"])
            ioutput.deserialize(ioutput_data)
            self._ioutputs += (ioutput, )

        self._ainterface = AInterface(blocksize=self._blocksize, start_frame=self.start_frame)


class TestInterface(Interface):
    __test__ = False  # set this so pytest does not collect this class

    def __init__(self,
                 asetup: Optional["ASetup"] = None,
                 samplerate: int = 44100,
                 blocksize: int = 1024,
                 analog_input_channels: Optional[List[int]] = None,
                 analog_output_channels: Optional[List[int]] = None) -> None:
        super().__init__(asetup=asetup,
                         samplerate=samplerate,
                         blocksize=blocksize,
                         analog_input_channels=analog_input_channels,
                         analog_output_channels=analog_output_channels)

    @property
    def callback(self) -> "Callback":
        return self._ainterface.callback

    @property
    def start_frame(self) -> int:
        # for testing we want to start directly
        return 0

    def _is_test(self) -> bool:
        return True
