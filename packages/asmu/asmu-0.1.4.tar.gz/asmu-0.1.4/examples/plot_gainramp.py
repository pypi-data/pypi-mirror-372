"""Simple program to test and visualize the ramp produced by the GainRamp effect."""
import matplotlib.pyplot as plt
import numpy as np

import asmu


def plot_gainramp():
    # create objects
    interface = asmu.TestInterface(samplerate=44100,
                                   blocksize=1024,
                                   analog_output_channels=[1])
    const = asmu.generator.Constant(interface, 1)
    gainramp = asmu.effect.GainRamp(interface, 0, 0.1, scale="log")

    # establish connections
    const.output().connect(gainramp.input())
    gainramp.output().connect(interface.ioutput(ch=1))

    # inti plot
    fig, ax = plt.subplots()

    # setup vectors
    outdata = np.empty((interface.blocksize, 1), dtype=np.float32)
    x = np.linspace(0, 1, interface.blocksize)

    # set gain
    gainramp.set_gain(1.0)

    # run callback loop
    for i in range(12):
        interface.callback(None, outdata, None, None, None)
        ax.plot(x + i, outdata, label=f"frame_{i}")

    # setup plot and show
    ax.set(title="GainRamp for gain = 1, step = 0.1, scale = \"log\"", xlabel="frames", ylabel="gain")
    ax.grid()
    ax.legend()

    fig.tight_layout()
    fig.savefig("docs/imgs/plot_gainramp.png", dpi=300)

    # Uncomment this if you want to see the plot
    # plt.show()


if __name__ == "__main__":
    plot_gainramp()
