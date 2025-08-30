"""PyTest for the calibration analyzer CalIInput."""
from typing import Literal

import pytest

import asmu


def test_analyzer_caliinput(cal_mode: Literal["peak", "rms"], benchmark):  # type: ignore[no-untyped-def]
    Vp = 1  # the actual amplitude of the signal
    ampl = 0.5  # the amplitude of the dummy signal (usually measured by the interface)
    freq = 1000  # the freq of the dummy signal (usually measured by the interface)
    # create objects
    interface = asmu.TestInterface(samplerate=44100,
                                   blocksize=8192)
    iinput = asmu.io.IInput(interface, channel=1)

    sine = asmu.generator.Sine(interface, freq)
    gain05 = asmu.effect.Gain(interface, ampl)
    caliinput = asmu.analyzer.CalIInput(interface, Vp, "Vp", iinput=iinput, mode=cal_mode, gain=30)

    # establish connections
    sine.output().connect(gain05.input())
    gain05.output().connect(caliinput.input())

    # repeatedly call callback
    result = caliinput.evaluate(block=False)
    while result is False:
        interface.callback(None, None, None, None, None)  # type: ignore[arg-type]
        result = caliinput.evaluate(block=False)
    fV, cV = result

    # We used a sine with arbitrary amplitude 0.5 as our generated input signal, and a calibration value of 1Vp.
    # So to get from arbitrary to input voltage, cV should be 2.
    # The values are not perfect due to the limited window size.
    print(f"IInput: fV = {fV:.2f}Hz, cV = {cV:.2f}")
    assert fV == pytest.approx(freq), "Frequency deviates more than allowed range."
    assert cV == pytest.approx(Vp/ampl), "Amplitude deviates more than allowed range."

    # check if calibration values were correctly written to IInput
    assert fV == iinput.fV
    assert cV == iinput.cV
    assert 30 == iinput.gain

    # benchmark (calls callback very often)
    if benchmark is not None:
        benchmark(interface.callback, None, None, None, None, None)


if __name__ == "__main__":
    pass
    # test_analyzer_caliinput("peak", None)
    # test_analyzer_caliinput("rms", None)
