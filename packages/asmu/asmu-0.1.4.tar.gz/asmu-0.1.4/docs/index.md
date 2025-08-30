---
hide:
  - toc
---
# Acoustic Signal Measurement Utilities

The **asmu** Python package enables multichannel real-time audio playback, processing and recording. It is implemented in pure Python with a few additional packages:

- [numpy](https://pypi.org/project/numpy/) - Is the fundamental package for scientific computing, array manipulation and signal processing.
- [sounddevice](https://pypi.org/project/sounddevice/) - Is a Python wrapper for the [PortAudio](https://www.portaudio.com/) functions. It is used for the communication with the soundcard or audio interface.
- [soundfile](https://pypi.org/project/soundfile/) - Is an audio library to read and write sound files through [libsndfile](http://www.mega-nerd.com/libsndfile/).

The main focus of **asmu** is modularity and easy expandability. It provides a few base classes, to implement nearly every "audio processor". Additionally, **asmu** offer some pre implemented audio processors, that can be used right away.



## Class Structure

!!! quote "General philosophy"
    **asmu** uses a two layer structure:

    - **Audio Layer:** [ACore](api/asmu_acore.md) classes with minimal functionality that run in the audio thread and are repeatedly called by the callback function.
    - **User Layer:** [Processors](api/asmu_processor.md) with [Inputs and Outputs](api/asmu_io.md) that are connected like analog audio devices. These classes also contain (slower) convenience functions.

In general each Processor houses an ACore class. These *blocks* can be connected to send and receive time-signal audio buffers with arbitrary `np.float32` unit between [-1, 1].
This simplifies the buffer structure and allows correct read/write from/to audio files.

If real units are required, scaling factors are stored in the respective interface analog input (IInput) and interface analog output (IOutput) and can be applied where needed (but never on the buffer itself).

![Class Structure](imgs/classes.svg)
