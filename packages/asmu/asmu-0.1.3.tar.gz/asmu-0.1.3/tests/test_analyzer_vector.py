"""PyTest for the Vector Analyzer (+AAnalyzerBuf)."""
from typing import TYPE_CHECKING, List

import numpy as np
import pytest

import asmu

if TYPE_CHECKING:
    from asmu.typing import ABuffer

PLOT = False


def test_analyzer_vector(out_buffer: bool, benchmark):  # type: ignore[no-untyped-def]
    ampl = 0.5  # sine amplitude
    freq = 100  # sine frequency
    phase = np.pi/2  # sine phase
    bufsize = 441  # buffersize (samplerate / freq) -> buffer fits one period

    # create objects
    interface = asmu.TestInterface(samplerate=44100,
                                   blocksize=192)
    sine = asmu.generator.Sine(interface, freq, phase=phase, out_buffer=out_buffer)
    gain05 = asmu.effect.Gain(interface, ampl, in_buffer=False, out_buffer=False)
    vector = asmu.analyzer.Vector(interface, bufsize)

    # establish connections
    sine.output().connect(gain05.input())
    gain05.output().connect(vector.input())

    buffers: List[ABuffer] = []
    while len(buffers) < 2:
        interface.callback(None, None, None, None, None)  # type: ignore[arg-type]
        res = vector.get_buffer(block=False)
        if res is not False:
            buffers.append(res)

    if PLOT:
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        ax.plot(range(bufsize), buffers[0])
        ax.plot(range(bufsize, 2*bufsize, 1), buffers[1])
        plt.show()

    for buf in buffers:
        assert buf.shape == (bufsize, 1)
        assert buf[0, 0] == pytest.approx(ampl)

    # benchmark (calls callback very often)
    if benchmark is not None:
        benchmark(interface.callback, None, None, None, None, None)


if __name__ == "__main__":
    pass
    # test_analyzer_vector(None)
