"""PyTest for the RMSAverage Analyzer."""
import numpy as np
import pytest

import asmu


def test_analyzer_rmsavg(out_buffer: bool, benchmark):  # type: ignore[no-untyped-def]
    """Test the accuracy of the rms average.
    This test only performs well, if the RMS samples are a multiple of the sine period length.
    We ensure this by setting samples=int(interface.samplerate/freq)
    """
    gain = 0.25
    freq = 100
    # create objects
    interface = asmu.TestInterface(samplerate=44100,
                                   blocksize=192)
    # reference sine
    sine = asmu.generator.Sine(interface, freq, out_buffer=out_buffer)
    gain_b = asmu.effect.Gain(interface, gain, in_buffer=False, out_buffer=False)
    rms = asmu.analyzer.RMS(interface, int(interface.samplerate/freq))

    # establish connections
    sine.output().connect(gain_b.input())
    sine.output().connect(rms.input(0))
    gain_b.output().connect(rms.input(1))

    # repeatedly call callback
    while True:
        interface.callback(None, None, None, None, None)  # type: ignore[arg-type]
        result = rms.get_rms(block=False)
        if result is not False:
            break

    assert (isinstance(result, np.ndarray))
    assert result.shape == (2, )

    # check if transfer functions are correct
    assert np.mean(result[0]) == pytest.approx(1/np.sqrt(2))
    assert np.mean(result[1]) == pytest.approx(gain/np.sqrt(2))

    # benchmark (calls callback very often)
    if benchmark is not None:
        benchmark(interface.callback, None, None, None, None, None)


if __name__ == "__main__":
    pass
    # test_analyzer_rmsavg(False, benchmark=None)
