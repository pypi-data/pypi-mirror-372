"""This example can be used to calibrate an Interface IInput and IOutput channel for pressure."""
from math import sqrt

import asmu


def calibrate_iinput_cPa(interface: "asmu.Interface",
                         in_ch: int):
    calcPa = asmu.analyzer.CalIInput(interface, 94, "SPL", gain=30)
    interface.iinput(ch=in_ch).connect(calcPa.input())

    stream = interface.start()
    result = calcPa.evaluate()  # blocking
    while result is False:
        result = calcPa.evaluate()
    stream.stop()
    stream.close()
    del calcPa  # disconnect
    print(f"cPa = {interface.iinput(ch=in_ch).cPa}")
    print(f"fPa = {interface.iinput(ch=in_ch).fPa}")
    print(f"datePa = {interface.iinput(ch=in_ch).datePa}")


def calibrate_ioutput_cPa(interface: "asmu.Interface",
                          in_ch: int,
                          out_ch: int):
    outgain = 0.01
    sine = asmu.generator.Sine(interface, 1000)
    gain = asmu.effect.Gain(interface, outgain)
    calcPa = asmu.analyzer.CalIOutput(interface, outgain, "Pa", interface.ioutput(ch=out_ch), gain=0)
    sine.output().connect(gain.input())
    gain.output().connect(interface.ioutput(ch=out_ch))
    interface.iinput(ch=in_ch).connect(calcPa.input())

    stream = interface.start()
    result = calcPa.evaluate()
    while result is False:
        result = calcPa.evaluate()
    stream.stop()
    stream.close()
    del calcPa  # disconnect
    print(f"cPa = {interface.ioutput(ch=out_ch).cPa}")
    print(f"fPa = {interface.ioutput(ch=out_ch).fPa}")
    print(f"datePa = {interface.ioutput(ch=out_ch).datePa}")


if __name__ == "__main__":
    in_ch = 9
    out_ch = 3
    interface = asmu.Interface(device="ASIO MADIface USB",
                               analog_input_channels=[in_ch],
                               analog_output_channels=[out_ch],
                               blocksize=8192,
                               samplerate=192000)

    print(f"Connect microphone in 94dB calibrator to input channel {in_ch}.")
    input("\tPress ENTER to start.")
    calibrate_iinput_cPa(interface, in_ch)

    print(f"Remove the microphone from the calibrater and place it \
next to a source driven by to the output channel {out_ch}?")
    input("\tPress ENTER to start.")
    calibrate_ioutput_cPa(interface, in_ch, out_ch)

    if input("Start generator? (y|n)") == "y":
        # verify if everything worked correctly
        sine = asmu.generator.Sine(interface, 1000)
        SPL = 85  # dB
        Pap = 2e-5 * 10**(SPL / 20) * sqrt(2)  # set desired peak amplitude

        cPa = interface.ioutput().cPa
        assert cPa is not None
        gain = asmu.effect.Gain(interface, Pap / cPa)
        sine.output().connect(gain.input())
        gain.output().connect(interface.ioutput(ch=out_ch))

        print("Starting sine generator...")
        stream = interface.start()
        print(f"You now should measure a {SPL:.2f}dB sine wave on the output channel {interface.ioutput().channel}.")
        input("\tPress ENTER to stop.")
        stream.stop()
        stream.close()
