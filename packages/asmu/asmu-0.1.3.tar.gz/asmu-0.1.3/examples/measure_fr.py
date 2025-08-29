import time
from typing import List, Optional, Tuple

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import scipy as sp
from asmu_utils.average import tbavg

import asmu


def record_noise_response(interface: "asmu.Interface",
                          name: str,
                          duration: int = 20):
    """Record the generated and measured noise signal to an AFile.

    Args:
        interface: Reference to an Interface instance.
        nam: The name for the measurement.
        duration: Measurement duration.
    """
    gen = asmu.generator.Noise(interface, weight="pink")

    with asmu.AFile(interface, mode="w", path=f"./recordings/{name}.wav", channels=2) as afile:
        rec = asmu.analyzer.Recorder(interface, afile)

        gen.output().connect(interface.ioutput())
        gen.output().connect(rec.input(0))

        interface.iinput().connect(rec.input(1))

        stream = interface.start(end_frame=round(duration * interface.samplerate / interface.blocksize))
        try:
            while stream.active:
                # wait
                time.sleep(0.1)
        except KeyboardInterrupt:
            stream.stop()
        stream.close()


def analyze_noise_response(interface: "asmu.Interface",
                           names: List[str],
                           frange: Tuple[float, float] = (20, 20000),
                           colors: Optional[List[str]] = None):
    """Analyze the frequency response from the measurements recorded to AFiles.

    Args:
        interface: Reference to an Interface instance.
        names: List of names of the measurements.
        frange: Tuple of desired frequency range.
        colors: List of colors, if None the default Matplotlib colors are used.
    """
    fig, ax = plt.subplots()

    if colors is None:
        # use standard tableu colors
        colors = plt.rcParams['axes.prop_cycle'].by_key()['color']

    for name, color in zip(names, colors):
        with asmu.AFile(interface, mode="r", path=f"./recordings/{name}.wav") as afile:
            indata = afile.data

            # init fft
            win = np.hanning(interface.samplerate)
            SFT = sp.signal.ShortTimeFFT(win,
                                         int(interface.samplerate / 2),
                                         interface.samplerate,
                                         fft_mode="onesided2X",
                                         scale_to="magnitude")

            # fft
            f = SFT.f
            iflim = np.where((f >= frange[0]) & (f <= frange[1]))
            fdata = SFT.stft(indata, axis=0)

            # compute transfer function
            fr = fdata[:, 0, :] / fdata[:, 1, :]
            fr = np.mean(fr, axis=1)

            # compute terzband average
            f_avg, fr_avg = tbavg(f, np.abs(fr), frange=frange)

            # normalize to 1kHz
            i1000 = np.argmin(np.abs(f_avg - 1000))
            fr /= np.abs(fr_avg[i1000])
            fr_avg /= np.abs(fr_avg[i1000])

            ax.loglog(f[iflim], np.abs(fr[iflim]), alpha=0.2, color=color)
            ax.loglog(f_avg, np.abs(fr_avg), "o-", label=name, color=color)

    # format plot
    dBticks = 10**(np.array([-20, -10, -6, -3, 0, 3, 6, 10, 20]) / 20)
    ax.set(xlabel="Frequency in Hz", ylabel="Gain in dB")
    ax.set_ylim(np.min(dBticks), np.max(dBticks))
    ax.set_yticks(dBticks)
    ax.yaxis.set_major_formatter(lambda x, pos: f"{20 * np.log10(x):.0f}")
    ax.yaxis.set_minor_locator(ticker.NullLocator())

    ftos = [10, 100, 1000, 10000]
    ftos_labels = ["10", "100", "1k", "10k"]
    ax.set_xlim(frange[0], frange[1])
    ax.set_xticks(ftos)
    ax.set_xticklabels(ftos_labels)
    ax.xaxis.set_minor_locator(ticker.LogLocator(base=10.0, subs='auto', numticks=10))
    ax.legend(ncol=3)
    ax.grid()

    fig.tight_layout()
    plt.show()


if __name__ == "__main__":
    SPEAKERS = ["spk_A", "spk_B"]
    in_ch = 9  # microphone
    out_ch = 1  # speaker

    interface = asmu.Interface(device=("ASIO Fireface", "ASIO Fireface"),
                               samplerate=192000,
                               blocksize=1024,
                               analog_input_channels=[in_ch],
                               analog_output_channels=[out_ch])
    for spk in SPEAKERS:
        input(f"Connect {spk} and press ENTER to start the measurement.")
        record_noise_response(interface, name=spk)
    analyze_noise_response(interface, SPEAKERS)
