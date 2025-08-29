"""PyTest for the calibration analyzer CalIOutput."""
from typing import Literal

import pytest

import asmu


def test_analyzer_calioutput(cal_mode: Literal["peak", "rms"], benchmark):  # type: ignore[no-untyped-def]
    Vp = 1  # the actual amplitude of the signal
    ampl = 0.5  # the amplitude of the dummy signal (usually measured by the interface)
    freq = 1000  # the freq of the dummy signal (usually measured by the interface)
    outgain = 0.1
    # create objects
    interface = asmu.TestInterface(samplerate=44100,
                                   blocksize=8192)
    iinput = asmu.io.IInput(interface, channel=1)
    iinput.cV = 2
    ioutput = asmu.io.IOutput(interface, channel=1)

    sine = asmu.generator.Sine(interface, freq)
    gain05 = asmu.effect.Gain(interface, ampl)
    calioutput = asmu.analyzer.CalIOutput(interface,
                                          outgain,
                                          "V",
                                          ioutput,
                                          iinput=iinput,
                                          mode=cal_mode,
                                          gain=30)

    # establish connections
    sine.output().connect(gain05.input())
    gain05.output().connect(calioutput.input())

    # repeatedly call callback
    result = calioutput.evaluate(block=False)
    while result is False:
        interface.callback(None, None, None, None, None)  # type: ignore[arg-type]
        result = calioutput.evaluate(block=False)
    fV, cV = result

    # We theoretically generated a sine with arbitrary amplitude 0.1
    # and recieved a sine with a voltage amplitude of arbitrary amplitude 0.5.
    # With the iinputs cV of 2 this results in 1Vp.
    # So to get from voltage to the arbitrary amplitude used by the interface, 1/cV should be 0.1, so cV should be 10.
    print(f"IOutput: fV = {fV:.2f}Hz, cV = {cV:.2f}")
    assert fV == pytest.approx(freq), "Frequency deviates more than allowed range."
    assert cV == pytest.approx(Vp/outgain), "Amplitude deviates more than allowed range."

    # check if calibration values were correctly written to IInput
    assert fV == ioutput.fV
    assert cV == ioutput.cV
    assert 30 == ioutput.gain

    # benchmark (calls callback very often)
    if benchmark is not None:
        benchmark(interface.callback, None, None, None, None, None)


if __name__ == "__main__":
    pass
    test_analyzer_calioutput("peak", None)
    # test_analyzer_calioutput("rms", None)
