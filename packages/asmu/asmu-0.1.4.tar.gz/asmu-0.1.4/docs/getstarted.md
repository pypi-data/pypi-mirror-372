# Get started

This page is dedicated to get you started with the **asmu** package. First, it is recommended to install the latest version of Python, which can be downloaded [here](https://www.python.org/). Check if you can run `python --version` and `pip --version` in your console, to verify the paths are configured correctly.

## Package installation

The package is available on the [Python Package Index](https://pypi.org/project/asmu/) and can be installed via

```sh
pip install asmu
```
This step should automatically install the required dependencies. To verify everything worked, run

```sh
python

>>> import asmu
>>> asmu.query_devices()
```
If you see a list of available audio devices you are **done**! If this raises an exception about PortAudio, continue with the next section.

### PortAudio installation

On some system PortAudio, the audio backend used for the communication with the sound device, has to be installed manually. The library can be downloaded [here](https://files.portaudio.com/download.html). After successful installation, try running the example above and see if everything works now.

On Unix you can also use:
```sh
apt install portaudio19-dev
```

### Audio device

If you are using a special soundcard or audio interface, be sure to install the correct drivers. After that you can check if the device is available by running the above example again.

!!! tip
    Some external audio interfaces are listed multiple times, because some of their channels are mapped to the host systems default drivers. Be sure to select the correct device, that typically has the used driver in their name, e.g. ASIO or CoreAudio. Double check if all available input and output channels are listed.

If everything works clone the examples from [GitLab](https://gitlab.com/felhub/asmu/-/tree/main/examples?ref_type=heads) and start playing with **asmu**!