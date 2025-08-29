"""This example calibrates the latency between given input and output."""
import time

from asmu_utils.correlation import get_corrs_sampleshifts

import asmu


def calibrate_latency(interface: "asmu.Interface",
                      in_ch: int,
                      out_ch: int) -> int:
    sineburst = asmu.generator.SineBurst(interface, 1000, 10)
    with asmu.AFile(interface, mode="w+", path="temp.wav", channels=2, temp=True) as afile:
        rec = asmu.analyzer.Recorder(interface, afile)

        sineburst.output().connect(interface.ioutput(ch=out_ch))
        sineburst.output().connect(rec.input(0))
        interface.iinput(ch=in_ch).connect(rec.input(1))

        stream = interface.start(end_frame=16)
        while stream.active:
            time.sleep(0.1)

        data = afile.data

    corrs, shifts = get_corrs_sampleshifts(data, data[:, 0], 10 / 1000 * interface.samplerate)
    assert shifts[0] == 0
    return shifts[1]


if __name__ == "__main__":
    in_ch = 3
    out_ch = 3
    interface = asmu.Interface(device="ASIO MADIface USB",
                               analog_input_channels=[in_ch],
                               analog_output_channels=[out_ch],
                               blocksize=8192,
                               samplerate=192000)
    latency = calibrate_latency(interface, in_ch, out_ch)
    print(f"Found latency = {latency}")
