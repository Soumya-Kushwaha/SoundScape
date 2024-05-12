import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import PySimpleGUI as sg

# Constants
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024

# Function to calculate RMS amplitude
def rms(data):
    return np.sqrt(np.mean(np.square(data)))

# Initialize PyAudio
p = pyaudio.PyAudio()

# Create the PySimpleGUI layout
layout = [
    [sg.Canvas(size=(400, 200), key='canvas')],
    [sg.Button('Start'), sg.Button('Stop'), sg.Button('Exit')],
    [sg.Text('Color Scheme:'), sg.Combo(['Default', 'Dark', 'Light'], default_value='Default', key='color_scheme')],
    [sg.Text('Threshold Level:'), sg.Slider(range=(0, 2000), default_value=1000, orientation='h', key='threshold')]
]

# Create the PySimpleGUI window
window = sg.Window('Audio Visualizer', layout)

# Function to update the plot
def update_plot(frame):
    data = np.frombuffer(stream.read(CHUNK), dtype=np.int16)
    rms_val = rms(data)
    ax.clear()
    ax.plot(np.arange(len(data)), data, color=color_scheme, alpha=0.7)
    ax.axhline(y=threshold, color='r', linestyle='--')
    ax.set_title(f'RMS Amplitude: {rms_val:.2f}')
    ax.set_xlabel('Time')
    ax.set_ylabel('Amplitude')
    ax.set_ylim(-32768, 32767)

# Function to start the visualization
def start_visualization():
    ani.event_source.start()

# Function to stop the visualization
def stop_visualization():
    ani.event_source.stop()

# Start the audio stream
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

# Create Matplotlib figure and axis
fig, ax = plt.subplots()
color_scheme = 'blue'  # Default color scheme
threshold = 1000  # Default threshold level

# Main loop
while True:
    event, values = window.read(timeout=10)
    if event in (sg.WIN_CLOSED, 'Exit'):
        break
    elif event == 'Start':
        start_visualization()
    elif event == 'Stop':
        stop_visualization()
    elif event == 'color_scheme':
        color_scheme = values['color_scheme']
    elif event == 'threshold':
        threshold = values['threshold']
    update_plot(None)
    window['canvas'].TKCanvas.draw()

# Close the window and terminate PyAudio
window.close()
stream.stop_stream()
stream.close()
p.terminate()
