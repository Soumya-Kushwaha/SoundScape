# SoundScape

Welcome to SoundScape, an innovative Python project that transforms your surroundings into a mesmerizing visual symphony in real-time, all with just the use of a microphone. Whether you're a seasoned sound enthusiast, an amateur explorer of acoustics, or simply curious about the world of sound, SoundScape offers an accessible and captivating tool for observation and experimentation. Dive into the immersive realm of sound waves, making it an invaluable companion for anyone eager to deepen their understanding of sound, all in a convenient, affordable, and user-friendly package.

## Table of Contents

- [SoundScape](#soundscape)
  - [Table of Contents](#table-of-contents)
  - [Inroduction \& Features](#inroduction--features)
  - [Visualizers(Processors)](#visualizersprocessors)
    - [Waveform](#waveform)
    - [Spectogram](#spectogram)
    - [Frequency v/s Amplitude](#frequency-vs-amplitude)
  - [Installation](#installation)
    - [Dependencies](#dependencies)
  - [Usage Guide](#usage-guide)
    - [LISTEN](#listen)
    - [STOP](#stop)
    - [EXIT](#exit)
  - [Contribution Guidelines](#contribution-guidelines)
  - [References](#references)
  - [Future Development](#future-development)

## Inroduction & Features

SoundScape is a fun Python project that visualizes the real-time audio recorded through a microphone, using the [PyAudio](https://pypi.org/project/PyAudio/) and [PySimpleGUI](https://pypi.org/project/PySimpleGUI/) libraries. It creates a dynamic and interactive soundscape that changes according to the sound input. You can use it to explore the sound properties of different environments, such as a busy street, a quiet park, or a noisy classroom.

SoundScape provides different visualizers(or processors) that allows users to observe and test different aspects and features of sound.

## Visualizers(Processors)

### Waveform

- This visualizer showcases the waveform of audio in real-time, providing users with a direct representation of sound amplitude over time. 
- It's essential for understanding the basic structure and dynamics of audio signals, making it an indispensable tool for sound enthusiasts and learners alike.
  
### Spectogram

- The spectogram visualizer illustrates the change in frequency across time, offering a detailed depiction of the frequency content of audio signals.
- This visualization is crucial for analyzing complex sound patterns and identifying specific frequencies present in audio recordings, making it invaluable for tasks like audio processing, music production, and scientific research.

### Frequency v/s Amplitude

- This visualizer dynamically displays the relationship between frequency and amplitude in real-time audio, allowing users to observe how different frequencies contribute to the overall sound intensity. 
- Understanding this relationship is essential for tasks such as sound equalization, noise reduction, and audio synthesis.

## Installation

To run SoundScape, ensure you have Python 3.6 or higher and pip installed on your system, along with a microphone.

### Dependencies

SoundScape relies on the following Python libraries:

- PyAudio
- PySimpleGUI
- NumPy
- SciPy
- Matplotlib

You can install these dependencies usign pip:

```pip install -r requirements.txt'```

*For  further information please refer to [```installation.md```](https://github.com/Soumya-Kushwaha/SoundScape/blob/main/Installation.md) file.*

## Usage Guide

- As you know by now SoundScape offers three visualization options.
- In order to use these visulizers, one needs to run their individual ```.py``` files.
  
1. WAVEFORM: ```python waveform.py```
2. SPECTROGRAM: ```python spectrogram.py```
3. AMPLITUDE V/S FREQUENCY: ```amplitude-frequency-visualizer.py```

Then, using these visualizers is quite intutive, each visualizer provides three buttons:

### LISTEN

Click on this button for enabling the visualizer to start listening the environment.

### STOP

To pause the visualizer to listen for the time being, click on this button.

### EXIT

Click on this button to destroy or close the visualizer window.

## Contribution Guidelines

Your contributions and suggestions are always welcome. For bug report and feature requests, please create an issue.

Please refer to the [```Contributing.md```](https://github.com/Soumya-Kushwaha/SoundScape/blob/main/Contribution.md) file for contribution details.

## References

Please refer to the [```References.md```](https://github.com/Soumya-Kushwaha/SoundScape/blob/main/References.md) file for details.

## Future Development

1. **UI Updates:** We plan to transition from PySimpleGUI to CustomTkinter for the user interface to increase flexibility and aesthetic appeal. This update will allow for more customization options and better integration with the overall design of the project.
2. **Additional Visualizers:** We're exploring the addition of new visualizers to expand the range of sound visualization options available in SoundScape.
3. **Performance Optimization:** We're committed to optimizing the performance of SoundScape to ensure smooth and efficient operation.
4. **Community Engagement:** We value community feedback and encourage users to share their ideas, suggestions, and contributions to help shape the future development of SoundScape.
