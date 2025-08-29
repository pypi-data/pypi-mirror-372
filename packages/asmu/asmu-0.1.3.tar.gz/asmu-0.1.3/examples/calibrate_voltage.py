"""This example can be used to calibrate an Interface IInput and IOutput channel for voltage."""
import asmu


def calibrate_iinput_cV(interface: "asmu.Interface",
                        in_ch: int):
    calcV = asmu.analyzer.CalIInput(interface, 1, "Vp", gain=0)
    interface.iinput(ch=in_ch).connect(calcV.input())

    stream = interface.start()
    result = calcV.evaluate()  # blocking
    stream.stop()
    stream.close()
    del calcV  # disconnect
    print(result)
    print(f"cV = {interface.iinput(ch=in_ch).cV}")
    print(f"fV = {interface.iinput(ch=in_ch).fV}")


def calibrate_ioutput_cV(interface: "asmu.Interface",
                         in_ch: int,
                         out_ch: int):
    outgain = 0.1
    sine = asmu.generator.Sine(interface, 1000)
    gain = asmu.effect.Gain(interface, outgain)
    calcV = asmu.analyzer.CalIOutput(interface, outgain, "V", interface.ioutput(ch=out_ch), gain=0)
    sine.output().connect(gain.input())
    gain.output().connect(interface.ioutput(ch=out_ch))
    interface.iinput(ch=in_ch).connect(calcV.input())

    stream = interface.start()
    result = calcV.evaluate()  # blocking
    stream.stop()
    stream.close()
    del calcV  # disconnect
    print(result)
    print(f"cV = {interface.ioutput(ch=out_ch).cV}")
    print(f"fV = {interface.ioutput(ch=out_ch).fV}")


if __name__ == "__main__":
    in_ch = 3
    out_ch = 3
    interface = asmu.Interface(device="ASIO MADIface USB",
                               analog_input_channels=[in_ch],
                               analog_output_channels=[out_ch],
                               blocksize=8192,
                               samplerate=192000)

    print(f"Connect a 1Vp sine generator to input channel {in_ch}.")
    input("\tPress ENTER to start.")
    calibrate_iinput_cV(interface, in_ch)

    print(f"Disconnect the funtion generator and connect the input channel {in_ch} to the output channel {out_ch}?")
    input("\tPress ENTER to start.")
    calibrate_ioutput_cV(interface, in_ch, out_ch)

    if input("Start generator? (y|n)") == "y":
        # verify if everything worked correctly
        sine = asmu.generator.Sine(interface, 1000)
        Vp = 0.5  # set desired peak amplitude

        cV = interface.ioutput().cV
        assert cV is not None
        gain = asmu.effect.Gain(interface, Vp / cV)
        sine.output().connect(gain.input())
        gain.output().connect(interface.ioutput(ch=out_ch))

        print("Starting sine generator...")
        stream = interface.start()
        print(f"You now should measure a {Vp:.2f}Vp sine wave on the output channel {interface.ioutput().channel}.")
        input("\tPress ENTER to stop.")
        stream.stop()
        stream.close()
