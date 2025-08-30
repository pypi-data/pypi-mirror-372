"""PyTest for the FFT Analyzer."""
import numpy as np
import pytest

import asmu


def test_analyzer_fft_tf(out_buffer: bool, benchmark):  # type: ignore[no-untyped-def]
    """Test the fft by computing a transfer function between two scaled noise functions."""
    gain = 0.25
    # create objects
    interface = asmu.TestInterface(samplerate=44100,
                                   blocksize=192)
    # reference noise (this is very slow and the bottleneck of this test)
    noise = asmu.generator.Noise(interface, out_buffer=out_buffer)
    gain_b = asmu.effect.Gain(interface, gain, in_buffer=False, out_buffer=False)

    # the window size can be chosen as whole numbered multiples of blocksize
    fft = asmu.analyzer.FFT(interface)

    # establish connections
    noise.output().connect(gain_b.input())

    noise.output().connect(fft.input(0))
    noise.output().connect(fft.input(1))
    gain_b.output().connect(fft.input(2))

    # repeatedly call callback
    while True:
        interface.callback(None, None, None, None, None)  # type: ignore[arg-type]
        result = fft.get_fft(block=False)
        if result is not False:
            break

    assert (isinstance(result, np.ndarray))

    # compute transfer function
    tf = result[:, 1:] / result[:, [0]]

    # check if transfer functions are correct
    assert np.mean(np.abs(tf[:, 0])) == pytest.approx(1)
    assert np.mean(np.abs(tf[:, 1])) == pytest.approx(gain)
    assert np.mean(np.angle(tf[:, 0])) == pytest.approx(0)
    assert np.mean(np.angle(tf[:, 1])) == pytest.approx(0)

    # benchmark (calls callback very often)
    if benchmark is not None:
        benchmark(interface.callback, None, None, None, None, None)


def test_analyzer_fft_sine(out_buffer: bool, benchmark):  # type: ignore[no-untyped-def]
    """Test the accuracy of the fft based rms average.
    This test only performs well, if the RMS samples are a multiple of the sine period length.
    We ensure this by setting samples=int(interface.samplerate/freq)
    """
    gain = 0.25
    freq = 1000
    # create objects
    interface = asmu.TestInterface(samplerate=10*freq,
                                   blocksize=100)
    # reference sine
    sine = asmu.generator.Sine(interface, freq, out_buffer=out_buffer)
    gain_b = asmu.effect.Gain(interface, gain, in_buffer=False, out_buffer=False)

    # the window size can be chosen as whole numbered multiples of blocksize
    win = np.ones(interface.blocksize*20, dtype=np.float32)
    fft = asmu.analyzer.FFT(interface, win)

    # establish connections
    sine.output().connect(gain_b.input())

    sine.output().connect(fft.input(0))
    gain_b.output().connect(fft.input(1))

    # repeatedly call callback
    while True:
        interface.callback(None, None, None, None, None)  # type: ignore[arg-type]
        result = fft.get_fft(block=False)
        if result is not False:
            break

    rms = fft.fft2rms(result)
    fs, peaks = fft.fft2peak(result)
    print(rms, peaks)

    # check if peaks are correct
    assert rms[0] == pytest.approx(1/np.sqrt(2))
    assert rms[1] == pytest.approx(gain/np.sqrt(2))
    assert peaks[0] == pytest.approx(1)
    assert peaks[1] == pytest.approx(gain)
    assert fs[0] == pytest.approx(freq)
    assert fs[1] == pytest.approx(freq)

    # benchmark (calls callback very often)
    if benchmark is not None:
        benchmark(interface.callback, None, None, None, None, None)


def test_analyzer_fft_const(out_buffer: bool, benchmark):  # type: ignore[no-untyped-def]
    """Test the accuracy of the fft based rms average.
    This test only performs well, if the RMS samples are a multiple of the sine period length.
    We ensure this by setting samples=int(interface.samplerate/freq)
    """
    value = 0.25
    # create objects
    interface = asmu.TestInterface(samplerate=10000,
                                   blocksize=192)
    # reference sine
    const = asmu.generator.Constant(interface, value)

    # the window size can be chosen as whole numbered multiples of blocksize
    win = np.ones(1000)
    fft = asmu.analyzer.FFT(interface, win)

    # establish connections
    const.output().connect(fft.input(0))

    # repeatedly call callback
    while True:
        interface.callback(None, None, None, None, None)  # type: ignore[arg-type]
        result = fft.get_fft(block=False)
        if result is not False:
            break

    rms = fft.fft2rms(result)
    fs, peaks = fft.fft2peak(result)
    print(rms, fs, peaks)

    # check if peaks are correct
    assert rms[0] == pytest.approx(value, rel=1e-3)
    assert peaks[0] == pytest.approx(value, rel=1e-3)
    assert fs[0] == pytest.approx(0)

    # benchmark (calls callback very often)
    if benchmark is not None:
        benchmark(interface.callback, None, None, None, None, None)


if __name__ == "__main__":
    pass
    # test_analyzer_fft_tf(True, benchmark=None)
    # test_analyzer_fft_sine(False, benchmark=None)
    # test_analyzer_fft_const(False, benchmark=None)
