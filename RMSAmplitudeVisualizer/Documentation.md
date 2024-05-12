# Audio Visualizer Documentation

## Overview
The Audio Visualizer is a Python application designed to display the root mean square (RMS) amplitude of an audio signal in real-time. It provides a graphical representation of the audio input, allowing users to visualize the perceived loudness of the audio.

## Features

- Real-time visualization of RMS amplitude.
- Customization options for color schemes and threshold levels.
- Start and stop controls for the visualization.
- User-friendly graphical interface built with PySimpleGUI.
  
## Requirements

- Python 3.x
- PyAudio
- NumPy
- Matplotlib
- PySimpleGUI

You can install these dependencies using pip:

```
pip install pyaudio numpy matplotlib PySimpleGUI
```

## Usage
*Follow the given steps to use the RMS Amplitude Visualizer.*

### 1.Run the Script
Execute the Python script provided for the visualizer. To use it, write the following code:
```
python audio_visualizer.py
```

### 2.Interface Overview
- Upon running the script, a window titled "Audio Visualizer" will appear.
- The window consists of:
  -A canvas displaying the real-time plot of the audio signal's RMS amplitude.
  -Buttons for controlling the visualization: "Start", "Stop", and "Exit".
  -Customization options for color scheme and threshold level.

### 3.Start Visualization
- Click the "Start" button to initiate the visualization.
- You should see a plot displaying the RMS amplitude of the audio signal over time.

### 4. Audio Input:
- Ensure your computer has a functional microphone or audio input device connected.
- Speak into the microphone or play audio through the input device.
- Observe how the plot reflects changes in the RMS amplitude corresponding to the input audio.

### 5.Customization:
- Use the "Color Scheme" dropdown menu to select different color schemes for the plot.
- Adjust the "Threshold Level" slider to set a threshold for the RMS amplitude. The threshold line will be displayed on the plot.

### 6.Pause Visualization:
Click the "Stop" button to pause the visualization. The plot will stop updating, but the window remains open.

### 7.Resume Visualization:
Click the "Start" button again to resume the visualization and continue displaying the real-time plot.

### 8.Exit the Application:
Click the "Exit" button to close the visualizer window and terminate the application.

