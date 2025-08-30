"""In this submodule you can find all effects, so "audio processors" with one or multiple inputs and outputs."""
import queue
from typing import TYPE_CHECKING, Literal

import numpy as np

from .acore import AEffect
from .io import Input, Output
from .processor import Effect

if TYPE_CHECKING:
    from .interface import Interface
    from .typing import ABlock


class Gain(Effect):
    def __init__(self,
                 interface: "Interface",
                 gain: float,
                 in_buffer: bool = True,
                 out_buffer: bool = False) -> None:
        """The Gain class effect is used to multiply a signal with the given gain.
        It is a multi input multi output effect, that applies the same gain to all connections.
        Input-update and output-update are supported.

        Args:
            interface: Reference to an Interface instance.
            gain: The gain.
            in_buffer: Flag that decides if inputs are buffered.
            out_buffer: Flag that decides if outputs are buffered.
        """
        self._gain = gain
        self._again = self._AGain(gain, in_buffer, out_buffer, interface.blocksize, interface.start_frame)
        super().__init__(aeffect=self._again,
                         interface=interface,
                         inputs=(Input(self), ),
                         outputs=(Output(self), ),
                         in_update=True,
                         out_update=True)

    class _AGain(AEffect):
        def __init__(self,
                     gain: float,
                     in_buffer: bool,
                     out_buffer: bool,
                     blocksize: int,
                     start_frame: int) -> None:
            self._gain = gain
            super().__init__(in_buffer=in_buffer,
                             out_buffer=out_buffer,
                             blocksize=blocksize,
                             start_frame=start_frame)

        def _mod_in_buf(self, outdata: "ABlock", ch: int) -> None:
            outdata[:] = self._in_buf[:, ch] * self._gain

        def _mod_upstream(self, outdata: "ABlock", ch: int) -> None:
            in_a = self._in_as[ch][0]
            if in_a is not None:
                in_a.upstream(outdata, self._in_as[ch][1], self._frame)  # get outdata from upstream
                outdata *= self._gain  # modify outdata

        def _inc(self) -> None:
            pass


class GainRamp(Effect):
    def __init__(self,
                 interface: "Interface",
                 gain: float,
                 step: float,
                 scale: Literal["lin", "log"] = "lin",
                 in_buffer: bool = True,
                 out_buffer: bool = False) -> None:
        """The GainRamp class effect is used to smoothly change between gains.
        The gain initially specified and the newly set values are linear setpoints.
        If scale is set to "log", this will be scaled accordingly.
        It is a multi input multi output effect, that applies the same gain to all connections.
        Input-update and output-update are supported.


        Args:
            interface: Reference to an Interface instance.
            gain: The initial gain.
            step: The desired linear gain change per frame.
            scale: Scaling of the given gain.
            in_buffer: Flag that decides if inputs are buffered.
            out_buffer: Flag that decides if outputs are buffered.
        """
        self._gain = gain
        self._againramp = self._AGainRamp(gain, step, scale, in_buffer, out_buffer,
                                          interface.blocksize, interface.start_frame)
        super().__init__(aeffect=self._againramp,
                         interface=interface,
                         inputs=(Input(self), ),
                         outputs=(Output(self), ),
                         in_update=True,
                         out_update=True)

    def set_gain(self, gain: float) -> None:
        """This is updated at the next upcoming frame.
        This is updated at the next upcoming frame.
        The function call blocks when called faster than the frames.

        Args:
            gain: The linear gain setpoint. If scale is set to "log", this will be scaled accordingly.
        """
        self._gain = gain
        self._againramp.gain_queue.put(self._gain)

    class _AGainRamp(AEffect):
        def __init__(self,
                     gain: float,
                     step: float,
                     scale: Literal["lin", "log"],
                     in_buffer: bool,
                     out_buffer: bool,
                     blocksize: int,
                     start_frame: int) -> None:
            self.gain_queue: queue.Queue[float] = queue.Queue(maxsize=1)

            self._is_gain = gain
            self._set_gain = gain
            self._ramp = np.linspace(0, step, blocksize, endpoint=True, dtype=np.float32)
            self._scale = scale

            self._gainramp = np.ones_like(self._ramp, dtype=np.float32) * gain
            super().__init__(in_buffer=in_buffer,
                             out_buffer=out_buffer,
                             blocksize=blocksize,
                             start_frame=start_frame)

        def _mod_in_buf(self, outdata: "ABlock", ch: int) -> None:
            outdata[:] = self._in_buf[:, ch] * self._gainramp

        def _mod_upstream(self, outdata: "ABlock", ch: int) -> None:
            in_a = self._in_as[ch][0]
            if in_a is not None:
                in_a.upstream(outdata, self._in_as[ch][1], self._frame)  # get outdata from upstream
                outdata *= self._gainramp  # modify outdata

        def _inc(self) -> None:
            # get new gain if available
            if not self.gain_queue.empty():
                self._set_gain = self.gain_queue.get()
            # check if we are still in ramp mode (with tolerance)
            if abs(self._set_gain - self._is_gain) > 0.001:
                if self._set_gain > self._is_gain:
                    # ramping downwards
                    self._gainramp = self._is_gain + self._ramp
                    self._gainramp[self._gainramp > self._set_gain] = self._set_gain
                else:
                    # ramping upwards
                    self._gainramp = self._is_gain - self._ramp
                    self._gainramp[self._gainramp < self._set_gain] = self._set_gain
                # set new gain
                self._is_gain = self._gainramp[-1]

                # scale the ramp
                if self._scale == "log":
                    self._log(self._gainramp)
            else:
                self._gainramp[:] = self._set_gain

        def _log(self, x: "ABlock") -> None:
            x += np.log10(1 / 9)
            np.power(10, x, out=x)
            x -= 1 / 9


class Sum(Effect):
    def __init__(self,
                 interface: "Interface",
                 out_buffer: bool = False) -> None:
        """The Sum class effect is used to sum multiple inputs to a single output.
        Arithmetic averaging is used for summing.
        It is a multi input single output effect, therefore output-update is not supported.
        Input-update is supported.

        Args:
            interface: Reference to an Interface instance.
            out_buffer: Flag that decides if outputs are buffered.
        """
        self._asum = self._ASum(out_buffer, interface.blocksize, interface.start_frame)
        super().__init__(aeffect=self._asum,
                         interface=interface,
                         inputs=(Input(self), ),
                         outputs=(Output(self), ),
                         in_update=True,
                         out_update=False)

    class _ASum(AEffect):
        def __init__(self,
                     out_buffer: bool,
                     blocksize: int,
                     start_frame: int) -> None:
            super().__init__(in_buffer=True,
                             out_buffer=out_buffer,
                             blocksize=blocksize,
                             start_frame=start_frame)

        def _mod_in_buf(self, outdata: "ABlock", ch: int) -> None:
            np.mean(self._in_buf, axis=1, out=outdata, dtype=np.float32)

        def _inc(self) -> None:
            pass
