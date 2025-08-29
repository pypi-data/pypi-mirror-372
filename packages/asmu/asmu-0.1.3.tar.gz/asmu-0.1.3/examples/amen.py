"""Groove out to the beats and rythms of the legendary amen break and a funky baseline.
Try to sing along, your masterpiece is recorded under `./recordings/amen_recording.wav`
When you are finished press Strg + C to stop and save the recording.
HAVE FUN!"""
import asmu


def main():
    # create interface
    interface = asmu.Interface(samplerate=44100,
                               blocksize=256,
                               analog_input_channels=[1],
                               analog_output_channels=[1, 2])
    # open files
    with asmu.AFile(interface, mode="r", path="./recordings/amen.wav", channels=2) as drum_afile, \
            asmu.AFile(interface, mode="w+", path="./recordings/amen_recording.wav", channels=2) as rec_afile:
        # create objects
        bass = asmu.generator.Sine(interface, 98)
        drums = asmu.generator.Player(interface, drum_afile, loop=True)
        sumL = asmu.effect.Sum(interface)
        sumR = asmu.effect.Sum(interface)
        bassRamp = asmu.effect.GainRamp(interface, 1, 0.1, scale="log", in_buffer=False)
        rec = asmu.analyzer.Recorder(interface, rec_afile)

        # establish connections
        bass.output().connect(bassRamp.input(0))

        drums.output(0).connect(sumL.input(0))
        drums.output(1).connect(sumR.input(0))
        bassRamp.output(0).connect(sumL.input(1))
        bassRamp.output(0).connect(sumR.input(1))
        interface.iinput(ch=1).connect(sumL.input(2))
        interface.iinput(ch=1).connect(sumR.input(2))

        sumL.output().connect(interface.ioutput(ch=1))
        sumR.output().connect(interface.ioutput(ch=2))

        sumL.output().connect(rec.input(0))
        sumR.output().connect(rec.input(1))

        # start audio for precisely N frames
        stream = interface.start(end_frame=1000)

        # sequencer
        try:
            bar = 1
            while stream.active:
                if drums.looped(timeout=1):
                    print(f"looped bar= {bar}")
                    match bar:
                        case 0:
                            bassRamp.set_gain(1.0)
                            bass.set_frequency(98)  # G2
                        case 1:
                            bass.set_frequency(65.4)  # C2
                        case 2:
                            bass.set_frequency(49)  # G1
                        case 3:
                            bassRamp.set_gain(0.5)
                    bar += 1
                    bar %= 4
        except KeyboardInterrupt:
            stream.stop()
        stream.close()


if __name__ == "__main__":
    main()
