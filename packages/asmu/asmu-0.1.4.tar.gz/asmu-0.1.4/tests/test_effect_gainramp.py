"""PyTest for the GainRamp effect, with "log" scale and for all buffer settings."""

import numpy as np

import asmu


def test_effect_gainramp(in_buffer: bool, out_buffer: bool, benchmark) -> None:  # type: ignore[no-untyped-def]
    step = 0.1
    # create objects
    interface = asmu.TestInterface(samplerate=44100,
                                   blocksize=1024,
                                   analog_output_channels=[1])
    const = asmu.generator.Constant(interface, 1)
    gainramp = asmu.effect.GainRamp(interface,
                                    0,
                                    step,
                                    scale="log",
                                    in_buffer=in_buffer,
                                    out_buffer=out_buffer)

    # establish connections
    const.output().connect(gainramp.input())
    gainramp.output().connect(interface.ioutput(ch=1))

    # setup vector for callback to write to
    outdata = np.empty((interface.blocksize, 1), dtype=np.float32)

    # call callback once (_inc() is not called)
    interface.callback(None, outdata, None, None, None)  # type: ignore[arg-type]

    # set new gain
    set_gain = 0.9
    gainramp.set_gain(set_gain)

    # for the second callback call _inc() is called with the new gain
    interface.callback(None, outdata, None, None, None)  # type: ignore[arg-type]

    # check if logarithmic step was performed correctly
    log_step = 10**(step + np.log10(1 / 9)) - 1 / 9
    assert abs(outdata[-1, 0] - log_step) < 1e-6

    # benchmark (calls callback very often)
    benchmark(interface.callback, None, outdata, None, None, None)

    # check if set_gain was reached
    assert abs(outdata[-1, 0] - set_gain) < 1e-6


if __name__ == "__main__":
    pass
    # test_effect_gainramp(True, False, lambda x, *args: [x(*args) for _ in range(100)][0])
