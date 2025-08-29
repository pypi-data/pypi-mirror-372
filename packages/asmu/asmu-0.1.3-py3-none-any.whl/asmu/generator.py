"""In this submodule you can find all generators, so "audio processors" with one or multiple outputs."""
import queue
import threading
from typing import TYPE_CHECKING, Literal

import numpy as np

from .acore import AGenerator
from .io import Output
from .processor import Generator

if TYPE_CHECKING:
    from soundfile import SoundFile

    from .afile import AFile
    from .interface import Interface
    from .typing import ABlock, ABuffer


class Player(Generator):
    def __init__(self,
                 interface: "Interface",
                 afile: "AFile|SoundFile",
                 loop: bool = False) -> None:
        """The Player class generator is used to play audio of a given file.
        It is a multi output generator, with the output count extracted from the given AFile.
        Output-update is not supported.

        Args:
            interface: Reference to an Interface instance.
            afile: Reference to an AFile instance.
            loop: Flag to enable looping.

        Raises:
            ValueError: The given AFile was not opened.
        """
        # check afile is open and reset
        self._afile = afile
        if afile.closed:
            raise ValueError("AFile was not opened - can not be used in Recorder.")
        afile.flush()
        afile.seek(0)

        self._loop = loop

        self._aplayer = self._APlayer(afile, loop, interface.blocksize, interface.start_frame)
        super().__init__(agenerator=self._aplayer,
                         interface=interface,
                         outputs=tuple(Output(self) for i in range(afile.channels)),
                         out_update=False)

    def finished(self, block: bool = True, timeout: float = 1) -> bool:
        """This function can be used to wait for the Player to finish playback.

        Args:
            block: Decides if the call of finished() should block.
            timeout: The timeout after which False is returned.

        Returns:
            `True`, when the Player finished. `False` on timeout.
        """
        if block:
            return self._aplayer.finished_event.wait(timeout=timeout)
        else:
            return self._aplayer.finished_event.is_set()

    def restart(self) -> bool:
        """Restart the Player, unset the finished() flag.

        Returns:
            `True`, when successful. `False`, when the Player isn't finished yet.
        """
        if not self.finished(block=False):
            return False
        self._afile.seek(0)
        self._aplayer.finished_event.clear()
        return True

    def looped(self, block: bool = True, timeout: float = 1) -> bool:
        """This function can be used to wait for the Player to loop.

        Args:
            block: Decides if the call of looped() should block.
            timeout: The timeout after which False is returned.

        Returns:
            `True`, when a loop occured. `False` on timeout.
        """
        looped = False
        if block:
            looped = self._aplayer.looped_event.wait(timeout=timeout)
        else:
            looped = self._aplayer.looped_event.is_set()
        if looped:
            self._aplayer.looped_event.clear()
        return looped

    def set_seek(self, position: int = 0) -> None:
        """Reset the Player to the given file position.
        This is updated at the next upcoming frame.
        The function call blocks when called faster than the frames.

        Args:
            position: Position to seek."""
        self._aplayer.seek_queue.put(position)

    class _APlayer(AGenerator):
        def __init__(self,
                     afile: "AFile",
                     loop: bool,
                     blocksize: int,
                     start_frame: int) -> None:
            self.finished_event = threading.Event()
            self.looped_event = threading.Event()
            self.seek_queue: queue.Queue[int] = queue.Queue()

            self._afile = afile
            self._loop = loop
            self._samples = afile.frames

            self._firstread = False
            super().__init__(out_buffer=True,  # The _out_buf is used to write the file into on _inc()
                             blocksize=blocksize,
                             start_frame=start_frame)

        def _mod(self, outdata: "ABlock", ch: int) -> None:
            if not self._firstread:
                self._inc()
                self._firstread = True

        def _inc(self) -> None:
            if self.finished_event.is_set():
                return
            if not self.seek_queue.empty():
                self._afile.seek(self.seek_queue.get())
            # calculate the rest to play
            rest = self._samples - self._afile.tell()
            if self._loop and rest < self._blocksize:
                # read rest (not full vlock)
                self._afile.read(rest, dtype="float32", always_2d=True, out=self._out_buf[:rest, :])
                self.looped_event.set()
                self._afile.seek(0)
                self._afile.read(self._blocksize - rest, dtype="float32", always_2d=True, out=self._out_buf[rest:, :])
                return
            # if there are no samples left to play
            if rest == 0:
                self.finished_event.set()
                return
            # load a block of samples in the buffer
            self._afile.read(self._blocksize, dtype="float32", always_2d=True, fill_value=0, out=self._out_buf)


class Sine(Generator):
    def __init__(self,
                 interface: "Interface",
                 frequency: float,
                 phase: float = 0,
                 out_buffer: bool = False) -> None:
        """The Sine class generator is used to craete a sine wave with given frequency and phase.
        It is a single output generator, therefore output-update is not supported.

        Args:
            interface: Reference to an Interface instance.
            frequency: Sine frequency in Hertz.
            phase: Sine phase in radiant.
            out_buffer: Flag that decides if outputs are buffered.
        """
        self._frequency = frequency

        self._asine = self._ASine(frequency, phase, interface.samplerate, out_buffer,
                                  interface.blocksize, interface.start_frame)
        super().__init__(agenerator=self._asine,
                         interface=interface,
                         outputs=(Output(self), ),
                         out_update=False)

    def set_frequency(self, frequency: float) -> None:
        """Change the frequency to the given value.
        This is updated at the next upcoming frame.
        The function call blocks when called faster than the frames.

        Args:
            frequency: The new set frequency in Hertz."""
        self._frequency = frequency
        self._asine.frequency_queue.put(frequency)

    class _ASine(AGenerator):
        def __init__(self,
                     frequency: float,
                     phase: float,
                     samplerate: int,
                     out_buffer: bool,
                     blocksize: int,
                     start_frame: int) -> None:
            self.frequency_queue: queue.Queue[float] = queue.Queue(maxsize=1)

            self._frequency = frequency
            self._samplerate = samplerate
            self._phase = phase
            self._omega_per_block = 2 * np.pi * frequency * blocksize / samplerate

            self._omegas = np.linspace(start_frame * self._omega_per_block,
                                       (start_frame + 1) * self._omega_per_block,
                                       blocksize, endpoint=False, dtype=np.float32)
            super().__init__(out_buffer=out_buffer,
                             blocksize=blocksize,
                             start_frame=start_frame)

        def _mod(self, outdata: "ABlock", ch: int) -> None:
            np.sin(self._omegas + self._phase, out=outdata)

        def _inc(self) -> None:
            self._phase += self._omega_per_block
            self._phase %= 2 * np.pi

            if not self.frequency_queue.empty():
                self._frequency = self.frequency_queue.get()
                self._omega_per_block = 2 * np.pi * self._frequency * self._blocksize / self._samplerate
                self._omegas = np.linspace(0, self._omega_per_block, self._blocksize,
                                           endpoint=False, dtype=np.float32)


class SineBurst(Generator):
    def __init__(self,
                 interface: "Interface",
                 frequency: float,
                 periods: int,
                 phase: float = 0,
                 out_buffer: bool = False) -> None:
        """The SineBurst class generator is used to craete a sine burst wave
        with given frequency and phase for given periods.
        It is a single output generator, therefore output-update is not supported.

        Args:
            interface: Reference to an Interface instance.
            frequency: Sine frequency in Hertz.
            periods: The number of periods.
            phase: Sine phase in radiant.
            out_buffer: Flag that decides if outputs are buffered.
        """
        self._asine = self._ASineBurst(frequency, periods, phase, interface.samplerate,
                                       out_buffer, interface.blocksize, interface.start_frame)
        super().__init__(agenerator=self._asine,
                         interface=interface,
                         outputs=(Output(self), ),
                         out_update=False)

    class _ASineBurst(AGenerator):
        def __init__(self,
                     frequency: float,
                     periods: int,
                     phase: float,
                     samplerate: int,
                     out_buffer: bool,
                     blocksize: int,
                     start_frame: int) -> None:
            self.frequency_queue: queue.Queue[float] = queue.Queue(maxsize=1)

            self._frequency = frequency
            self._samplerate = samplerate
            self._phase = phase
            self._maxang = phase + 2 * np.pi * periods
            self._omega_per_block = 2 * np.pi * frequency * blocksize / samplerate

            self._omegas = np.linspace(start_frame * self._omega_per_block,
                                       (start_frame + 1) * self._omega_per_block,
                                       blocksize, endpoint=False, dtype=np.float32)
            super().__init__(out_buffer=out_buffer,
                             blocksize=blocksize,
                             start_frame=start_frame)

        def _mod(self, outdata: "ABlock", ch: int) -> None:
            if self._phase < self._maxang:
                np.sin(self._omegas + self._phase, out=outdata)
                outdata[self._omegas >= self._maxang] = 0

        def _inc(self) -> None:
            if self._phase < self._maxang:
                self._phase += self._omega_per_block


class Vector(Generator):
    def __init__(self, interface: "Interface", vector: "ABuffer") -> None:
        """The Vector class generator is used to craete a custom wave given by a numpy array.
        It is a multi output generator, with the output count extracted from axis 1 of the given array.
        Output-update is not supported.

        Args:
            interface: Reference to an Interface instance.
            vector: Wave(s) to generate as numpy vector.
        """
        self._vector = vector.astype(np.float32, copy=True)

        self._avector = self._AVector(self._vector, interface.blocksize, interface.start_frame)
        super().__init__(agenerator=self._avector,
                         interface=interface,
                         outputs=tuple(Output(self) for i in self._vector[0, :]),
                         out_update=False)

    def finished(self, block: bool = True, timeout: float = 1) -> bool:
        """This function can be used to wait for the Player to finish playback.

        Args:
            block: Decides if the call of finished() should block.
            timeout: The timeout after which False is returned.

        Returns:
            `True`, when the Player finished. `False` on timeout.
        """
        if block:
            return self._avector.finished_event.wait(timeout=timeout)
        else:
            return self._avector.finished_event.is_set()

    def restart(self) -> bool:
        """Restart the Player, unset the finished() flag.

        Returns:
            `True`, when successful. `False`, when the Player isn't finished yet.
        """
        if not self.finished(block=False):
            return False
        self._avector.pos = 0
        self._avector.finished_event.clear()
        return True

    class _AVector(AGenerator):
        def __init__(self,
                     vector: "ABuffer",
                     blocksize: int,
                     start_frame: int) -> None:
            self.finished_event = threading.Event()
            self._vector = vector
            self._samples = np.size(vector[:, 0])
            self.pos = 0

            super().__init__(out_buffer=False,
                             blocksize=blocksize,
                             start_frame=start_frame)

        def _mod(self, outdata: "ABlock", ch: int) -> None:
            if self.finished_event.is_set():
                return
            rest = self._samples - self.pos
            if rest < self._blocksize:
                # read rest (not full vlock)
                outdata[:rest] = self._vector[:, ch]
                return
            outdata[:] = self._vector[:, ch]

        def _inc(self) -> None:
            if self.finished_event.is_set():
                return
            self.pos += self._blocksize
            # if there are no samples left to play
            if self._samples - self.pos <= 0:
                self.finished_event.set()
                return


class Noise(Generator):
    def __init__(self,
                 interface: "Interface",
                 weight: Literal["white", "pink"] = "white",
                 out_buffer: bool = False) -> None:
        """The WhiteNoise class generator is used to craete a random unweighted noise signal.
        It is a single output generator, therefore output-update is not supported.

        Args:
            interface: Reference to an Interface instance.
            weight: The frequency spectrum of the noise.
            out_buffer: Flag that decides if outputs are buffered.
        """

        self._asine = self._ANoise(weight, out_buffer, interface.blocksize, interface.start_frame)
        super().__init__(agenerator=self._asine,
                         interface=interface,
                         outputs=(Output(self), ),
                         out_update=False)

    class _ANoise(AGenerator):
        def __init__(self,
                     weight: Literal["white", "pink"],
                     out_buffer: bool,
                     blocksize: int,
                     start_frame: int) -> None:
            self._tmp = np.empty(blocksize, dtype=np.float64)
            self._rng = np.random.default_rng()
            # weighting
            self.w = np.ones(int(blocksize / 2 + 1), dtype=np.complex128)
            match(weight):
                case "pink":
                    f = np.fft.rfftfreq(blocksize).astype(np.float32)
                    # the reshape(-1) should do nothing but is needed for
                    # type-checking
                    self.w = (1 / np.where(f == 0, float('inf'), np.sqrt(f))).reshape(-1).astype(np.complex128)
                    self.w = self.w / np.sqrt(np.mean(self.w**2))
            # numpy fft only supports complex128
            self.rnd_spec = np.fft.rfft(np.random.randn(blocksize)).astype(np.complex128)
            super().__init__(out_buffer=out_buffer,
                             blocksize=blocksize,
                             start_frame=start_frame)

        def _mod(self, outdata: "ABlock", ch: int) -> None:
            np.fft.irfft(self.rnd_spec, out=self._tmp)
            self._tmp /= 4
            np.clip(self._tmp, -1, 1, dtype=np.float32, out=outdata)

        def _inc(self) -> None:
            self._rng.standard_normal(self._blocksize, out=self._tmp)
            np.fft.rfft(self._tmp, out=self.rnd_spec)
            self.rnd_spec *= self.w


class Constant(Generator):
    def __init__(self, interface: "Interface", value: float) -> None:
        """The Constant class generator is used to generate a constant output value, typically used for testing.
        It is a single output generator, therefore output-update is not supported.

        Args:
            interface: Reference to an Interface instance.
            value: The constant output value
        """
        self._aconstant = self._AConstant(value, interface.blocksize, interface.start_frame)
        super().__init__(agenerator=self._aconstant,
                         interface=interface,
                         outputs=(Output(self), ),
                         out_update=False)

    class _AConstant(AGenerator):
        def __init__(self,
                     value: float,
                     blocksize: int,
                     start_frame: int) -> None:
            self._value = value
            super().__init__(out_buffer=False,
                             blocksize=blocksize,
                             start_frame=start_frame)

        def _mod(self, outdata: "ABlock", ch: int) -> None:
            outdata[:] = self._value

        def _inc(self) -> None:
            pass
