"""In this submodule you can find all analyzers, so "audio processors" with one or multiple inputs."""
from datetime import datetime
from typing import TYPE_CHECKING, Literal, Optional, Tuple

import numpy as np

from .acore import AAnalyzer, AAnalyzerBuf
from .io import IInput, Input
from .processor import Analyzer

if TYPE_CHECKING:
    from soundfile import SoundFile

    from .afile import AFile
    from .interface import Interface
    from .io import IOutput
    from .typing import (
        Avg,
        FFTAbs,
        FFTFreqs,
        FFTInput,
        FFTOutput,
        FFTWindow,
    )


class Recorder(Analyzer):
    def __init__(self,
                 interface: "Interface",
                 afile: "AFile|SoundFile") -> None:
        """The Recorder class analyzer is used to record audio to a given file.
        It is a multi input analyzer, with the input count extracted from the given AFile.
        Input-update is not supported.

        Args:
            interface: Reference to an Interface instance.
            afile: Reference to an AFile instance.

        Raises:
            ValueError: The given AFile was not opened.
        """
        # check afile is open and reset
        self._afile = afile
        if afile.closed:
            raise ValueError("The given AFile was not opened.")
        afile.flush()
        afile.seek(0)

        self._arecorder = self._ARecorder(afile, interface.blocksize, interface.start_frame)
        super().__init__(aanalyzer=self._arecorder,
                         interface=interface,
                         inputs=tuple(Input(self) for i in range(afile.channels)),
                         in_update=False)

    class _ARecorder(AAnalyzer):
        def __init__(self,
                     afile: "AFile|SoundFile",
                     blocksize: int,
                     start_frame: int) -> None:
            self._afile = afile
            super().__init__(in_buffer=True,
                             blocksize=blocksize,
                             start_frame=start_frame)

        def _process_in_buf(self) -> None:
            self._afile.write(self._in_buf)


class Vector(Analyzer):
    def __init__(self, interface: "Interface", samples: int) -> None:

        self._avector = AAnalyzerBuf(samples, interface.blocksize, interface.start_frame)
        super().__init__(aanalyzer=self._avector,
                         interface=interface,
                         inputs=(Input(self), ),
                         in_update=True)

    def get_buffer(self, block: bool = True, timeout: float = 1) -> "FFTInput | Literal[False]":
        """Get one full buffer from the queue filled by the audio backend.

        Args:
            block: Determines if the call should block, wait for new value.
            timeout: The timeout after which False is returned.

        Returns:
            Buffer array or False, if block is set False and result is not ready yet.
        """
        # we do it this way and not with get(block), because this would raise an exception.
        if block or not self._avector.buf_queue.empty():
            return self._avector.buf_queue.get(timeout=timeout)
        return False


class FFT(Analyzer):
    def __init__(self,
                 interface: "Interface",
                 win: Optional["FFTWindow"] = None) -> None:
        """Compute FFT of input signals.
        Computations are phase-accurate, and can be done for windowsizes multiple of blocksize.
        It is a multi input analyzer and input-update is supported.

        Args:
            interface: Reference to an Interface instance.
            win: Windowing function vector, also determines FFT size.
                Defaults to std_fft_window().

        Raises:
            ValueError: When windowsize is not a multiple of blocksize.
        """
        if win is None:
            win = self.std_fft_window(interface)
        if win.size < interface.blocksize:
            raise ValueError("Window size must be larger than blocksize.")
        self._win: "FFTWindow" = win.astype(np.float32)
        self._tiledwin: "FFTInput"
        self._winsize = int(win.size)
        self._rms_win = np.sqrt(np.mean(self._win**2))
        self._peak_win = np.mean(self._win)

        self._fft: "FFTOutput"
        self._fs = np.fft.rfftfreq(self._winsize, 1/interface.samplerate).astype(np.float32)

        self._tmp: "FFTAbs"
        self._avg: "Avg"

        self._afft = AAnalyzerBuf(win.size, interface.blocksize, interface.start_frame)
        super().__init__(aanalyzer=self._afft,
                         interface=interface,
                         inputs=(Input(self), ),
                         in_update=True)

    @property
    def frequencies(self) -> "FFTFreqs":
        return self._fs

    def update_acore(self) -> None:
        self._fft = np.empty((int(self._winsize / 2 + 1), len(self._inputs)), dtype=np.complex128)
        self._tiledwin = np.tile(self._win[:, None], (1, len(self._inputs)))
        self._tmp = np.empty((int(self._winsize / 2 + 1), len(self._inputs)), dtype=np.float32)
        self._avg = np.empty(len(self._inputs), dtype=np.float32)
        return super().update_acore()

    def fft(self, indata: "FFTInput") -> None:
        """Appyl given window to indata, compute physical correcly scaled fft, and store it in outdata.

        Args:
            indata: Time domain input array.
        """
        indata *= self._tiledwin
        # memory allocation can not be avoided with numpy fft
        np.fft.rfft(indata, norm="forward", out=self._fft, axis=0)

    def std_fft_window(self, interface: "Interface") -> "FFTWindow":
        return np.hanning(interface.samplerate)

    def get_fft(self, block: bool = True, timeout: float = 1) -> "FFTOutput | Literal[False]":
        """Get the computation result FFT array from the queue filled by the audio backend.

        Args:
            block: Determines if the call should block, wait for new value.
            timeout: The timeout after which False is returned.

        Returns:
            FFT array or False, if block is set False and result is not ready yet.
        """
        # we do it this way and not with get(block), because this would raise an exception.
        if block or not self._afft.buf_queue.empty():
            indata = self._afft.buf_queue.get(timeout=timeout)
            self.fft(indata)
            return self._fft
        return False

    def get_rms(self, block: bool = True, timeout: float = 1) -> "Avg | Literal[False]":
        """Get the RMS average value obtained by fft-peak from the queue filled by the audio backend.

        Args:
            block: Decides if the call oshould block, wait for new value.
            timeout: The timeout after which False is returned.

        Returns:
            The RMS average of each channel or False, if block is set False and result is not ready yet.
        """
        data = self.get_fft(block=block, timeout=timeout)
        if data is False:
            return False
        return self.fft2rms(data)

    def fft2rms(self, fft: "FFTOutput") -> "Avg":
        np.abs(fft, out=self._tmp)
        self._tmp = self._tmp**2
        self._tmp[1:-1] *= 2
        np.sum(self._tmp, axis=0, out=self._avg)
        np.sqrt(self._avg, out=self._avg)
        self._avg /= self._rms_win
        return self._avg

    def fft2peak(self, fft: "FFTOutput") -> Tuple["Avg", "Avg"]:
        np.abs(fft, out=self._tmp)
        self._tmp[1:-1] *= 2
        ipeak = np.argmax(self._tmp, axis=0)
        self._avg = self._tmp[ipeak, np.arange(fft.shape[1])]
        self._avg /= self._peak_win
        return self._fs[ipeak], self._avg


class RMS(Analyzer):
    def __init__(self,
                 interface: "Interface",
                 samples: int) -> None:
        """Compute the RMS average of incomming audio data.
        It is a multi input analyzer and input-update is supported.

        Args:
            interface: Reference to an Interface instance.
            samples: Number of samples used in the RMS average.
        """

        self._armsavg = AAnalyzerBuf(samples, interface.blocksize, interface.start_frame)
        super().__init__(self._armsavg,
                         interface,
                         inputs=(Input(self), ),
                         in_update=True)

    def get_rms(self, block: bool = True, timeout: float = 1) -> "Avg | Literal[False]":
        """Get the RMS average value from the queue filled by the audio backend.

        Args:
            block: Decides if the call oshould block, wait for new value.
            timeout: The timeout after which False is returned.

        Returns:
            Array of RMS average value per channel or False, if block is set False and result is not ready yet.
        """
        # we do it this way and not with get(block), because this would raise an exception.
        if block or not self._armsavg.buf_queue.empty():
            return np.sqrt(np.mean(self._armsavg.buf_queue.get(timeout=timeout)**2,
                                   axis=0,
                                   dtype=np.float32), dtype=np.float32)
        return False


class CalIInput(FFT):
    def __init__(self,
                 interface: "Interface",
                 actual: float,
                 unit: Literal["VRms", "Vp", "PaRms", "Pap", "SPL"],
                 win: Optional["FFTWindow"] = None,
                 averages: int = 10,
                 mode: Literal["peak", "rms"] = "peak",
                 iinput: Optional["IInput"] = None,
                 gain: float = 0) -> None:
        """The CalcIInput class analyzer is used to calibrate the connected interface IInput.
        It is a single input analyzer, therefore input-update is not supported.

        Args:
            interface: Reference to an Interface instance.
            actual: The actual value of the signal used for calibration.
            unit: The unit of the value given

                - `"VRms"`   : RMS value of the sinusoidal signal in Volt.
                - `"Vp"`   : Amplitude value of the sinusoidal signal in Volt.
                - `"PaRms"`  : RMS value of the sinusoidal signal in Pascal.
                - `"Pap"`  : Amplitude value of the sinusoidal signal in Pascal.
                - `"SPL"` : Sound Pressure Level (RMS pressure in Dezibel).

            win: The windowing function used for the FFT.
                Defaults to std_fft_window().
            averages: Number of samples averages.
            mode: Depending on the mode the rms average of the fft or just the fft peak is used.
            iinput: The IInput to save the calibration to.
                If None, the connected IInput is used.
            gain: Gain setting of the interface. This is not used for the calculation, but stored in the IInput.
        """
        self._actual = actual
        self._unit = unit

        self._averages = averages
        self._n: int = 0  # counter used for averages
        self._c: float = 0
        self._f: float = 0

        self._mode = mode
        self._gain = gain
        self._iinput = iinput

        super().__init__(interface=interface,
                         win=win)
        # FFT usually supports in_update, but in our case we only want a single input!
        self.in_update = False

    def evaluate(self,
                 block: bool = True,
                 timeout: float = 2,
                 save: bool = True) -> Tuple[float, float] | Literal[False]:
        """If the measurement is finished, this evaluates the result and returns True.
        If the measurement is still running and block is False, False is returned.

        Args:
            block: Decides if the call should block.
            timeout: The timeout after which False is returned.
            save: Decides if the results should be saved to the connected or given IInput.

        Returns:
            (Frequency, Calibration Factor), when everything was successful.
            `False`, when the measurement is not done yet.

        Raises:
            ValueError: Given unit is unknown.
            ValueError: Given mode is unknown.
        """
        # get iinput if not given
        if self._iinput is None:
            assert isinstance(self.inputs[0].connected_output, IInput)
            self._iinput = self.inputs[0].connected_output

        # get fft spectrum
        fft = self.get_fft(block, timeout)
        if fft is False:
            return fft

        # ectract value
        match self._mode:
            case "peak":
                freqs, measured_peaks = self.fft2peak(fft)
            case "rms":
                freqs, _ = self.fft2peak(fft)
                measured_peaks = self.fft2rms(fft) * np.sqrt(2)
            case _:
                raise ValueError("Given mode is unknown.")

        freq = float(freqs[0])
        measured_peak = float(np.abs(measured_peaks[0]))

        # calculate the rms of the cal signal
        match self._unit:
            case "VRMS" | "PaRMS":
                peak = self._actual * np.sqrt(2)
            case "Vp" | "Pap":
                peak = self._actual
            case "SPL":
                peak = 2e-5 * 10 ** (self._actual / 20) * np.sqrt(2)
            case _:
                raise ValueError("Given unit is unknown.")

        # calculate calibration factor and frquency
        self._c += peak / measured_peak
        self._f += freq
        self._n += 1

        # check averages
        if self._n < self._averages:
            return False

        # average and reset
        c = self._c / self._n
        f = self._f / self._n
        self._n = 0
        self._c = 0
        self._f = 0

        # write to IInput
        now = datetime.now()
        if save and self._iinput is not None:
            self._iinput.gain = self._gain
            if "V" in self._unit:
                self._iinput.cV = c
                self._iinput.fV = f
                self._iinput.dateV = now.strftime("%Y-%m-%dT%H:%M:%S%z")  # ISO 8601
            elif self._unit == "SPL" or "Pa" in self._unit:
                self._iinput.cPa = c
                self._iinput.fPa = f
                self._iinput.datePa = now.strftime("%Y-%m-%dT%H:%M:%S%z")  # ISO 8601
        return (f, c)


class CalIOutput(FFT):
    def __init__(self,
                 interface: "Interface",
                 value: float,
                 quantity: Literal["V", "Pa"],
                 ioutput: "IOutput",
                 win: Optional["FFTWindow"] = None,
                 averages: int = 10,
                 mode: Literal["peak", "rms"] = "peak",
                 iinput: Optional["IInput"] = None,
                 gain: float = 0) -> None:
        """The CalcIOutput class analyzer is used to calibrate the given IOutput.
        For this calibration procedure a Sine generator with an amplitude of "actual"
        has to be connected to the given IOutput.
        This IOutput must be physically connected to the IInput, which needs to be pre-calibrated,
        and this IInput must be connected to this analyzer.
        It is a single input analyzer, therefore input-update is not supported.

        Args:
            interface: Reference to an Interface instance.
            value: The peak amplitude value of the signal used for calibration in arbitrary units.
            quantity: The physical quantity to calibrate for.

                - `"V"`   : Calibrate the ioutput in Volt.
                - `"Pa"`  : Calibrate the ioutput in Pascal.

            ioutput: The IOutput to calibrate, used to generate the signal and connected to the IInput.
            win: The windowing function used for the FFT.
                Defaults to std_fft_window().
            averages: Number of samples averages.
            mode: Depending on the mode the rms average of the fft or just the fft peak is used.
            iinput: The IInput to save the calibration to.
                If None, the connected IInput is used.
            gain: Gain setting of the interface. This is not used for the calculation, but stored in the IInput.
        """
        self._value = value
        self._quantity = quantity
        self._ioutput = ioutput

        self._averages = averages
        self._n: int = 0  # counter used for averages
        self._c: float = 0
        self._f: float = 0

        self._mode = mode
        self._gain = gain
        self._iinput = iinput

        super().__init__(interface=interface,
                         win=win)
        # FFT usually supports in_update, but in our case we only want a single input!
        self.in_update = False

    def evaluate(self,
                 block: bool = True,
                 timeout: float = 2,
                 save: bool = True) -> Tuple[float, float] | Literal[False]:
        """If the measurement is finished, this evaluates the result and returns True.
        If the measurement is still running and block is False, False is returned.

        Args:
            block: Decides if the call should block.
            timeout: The timeout after which False is returned.
            save: Decides if the results should be saved to the connected or given IInput.

        Returns:
            (Frequency, Calibration Factor), when everything was successful.
            `False`, when the measurement is not done yet.

        Raises:
            ValueError: Given unit is unknown.
            ValueError: Given mode is unknown.
        """
        # get iinput if not given
        if self._iinput is None:
            assert isinstance(self.inputs[0].connected_output, IInput)
            self._iinput = self.inputs[0].connected_output

        # get fft spectrum
        fft = self.get_fft(block, timeout)
        if fft is False:
            return fft

        # ectract value
        match self._mode:
            case "peak":
                freqs, measured_peaks = self.fft2peak(fft)
            case "rms":
                freqs, _ = self.fft2peak(fft)
                measured_peaks = self.fft2rms(fft) * np.sqrt(2)
            case _:
                raise ValueError("Given mode is unknown.")

        freq = float(freqs[0])
        measured_peak = float(np.abs(measured_peaks[0]))

        # calculate the rms of the cal signal
        match self._quantity:
            case "V":
                assert self._iinput.cV is not None, "Given IInput must be calibrated for voltage first."
                actual = measured_peak * self._iinput.cV
            case "Pa":
                assert self._iinput.cPa is not None, "Given IInput must be calibrated for pressure first."
                actual = measured_peak * self._iinput.cPa
            case _:
                raise ValueError("Given unit is unknown.")

        # calculate calibration factor and frquency
        self._c += actual / self._value
        self._f += freq
        self._n += 1

        # check averages
        if self._n < self._averages:
            return False

        # average and reset
        c = self._c / self._n
        f = self._f / self._n
        self._n = 0
        self._c = 0
        self._f = 0

        # write to IOutput
        now = datetime.now()
        if save:
            self._ioutput.gain = self._gain
            if self._quantity == "V":
                self._ioutput.cV = c
                self._ioutput.fV = f
                self._ioutput.dateV = now.strftime("%Y-%m-%dT%H:%M:%S%z")  # ISO 8601
            else:
                self._ioutput.cPa = c
                self._ioutput.fPa = f
                self._ioutput.datePa = now.strftime("%Y-%m-%dT%H:%M:%S%z")  # ISO 8601
        return (f, c)
