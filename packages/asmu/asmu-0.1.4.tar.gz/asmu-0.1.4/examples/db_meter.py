"""Live updating dB meter, requires pre calibrated microphone."""
from math import log10

import pyfiglet
from calibrate_pressure import calibrate_iinput_cPa

import asmu


def print_dB(fig: pyfiglet.Figlet, dB: float, previous_lines: int = 0) -> int:
    """Small helper function to display dB in the terminal.

    Args:
        dB: The value to display.
        previous_lines: The current cursor position (used to overwrite old display).

    Returns:
        The number of lines printed.
    """
    # Move the cursor up by the number of previous lines to overwrite
    if previous_lines:
        print(f"\033[{previous_lines}A", end="")  # Move cursor up
    rendered = fig.renderText(f"{dB:.1f}dB          ")
    print(rendered)  # Don't add extra newlines
    print("|    ,   " * 7 + "|")
    print("#" * round(dB / 2) + " " * round(100 - dB / 2))
    return rendered.count('\n') + 3  # Return how many lines were printed


if __name__ == "__main__":
    update = 0.5  # update time in seconds (averaging time)
    in_ch = 9  # microphone channel

    asetup = asmu.ASetup("./setups/db_meter.asmu")
    interface = asmu.Interface(device="ASIO MADIface USB",
                               analog_input_channels=[in_ch],
                               blocksize=8192,
                               samplerate=192000)
    asetup.interface = interface

    if input("Calibrate? (y|n)") == "y":
        print(f"Connect microphone in 94dB calibrator to input channel {in_ch}.")
        input("\tPress ENTER to start.")
        calibrate_iinput_cPa(interface, in_ch)
        asetup.save()
    else:
        asetup.load()

    rms = asmu.analyzer.RMS(interface, int(interface.samplerate*update))
    interface.iinput(ch=in_ch).connect(rms.input())

    line = 0
    fig = pyfiglet.Figlet(justify="center")
    stream = interface.start()
    try:
        mic = interface.iinput(ch=in_ch)
        assert mic.cPa is not None
        while True:
            val = rms.get_rms(timeout=update+1)*mic.cPa  # blocking
            dB = 20 * log10(val/2e-5)
            line = print_dB(fig, dB, line)
    except KeyboardInterrupt:
        pass
    finally:
        stream.stop()
        stream.close()
