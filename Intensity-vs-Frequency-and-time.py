import PySimpleGUI as sg
import pyaudio
import numpy as np
import scipy.fft
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import subprocess


"""Realtime Sound Intensity vs Frequency heatmap"""
# VARS CONSTS:
_VARS = {"window": False, "stream": False, "audioData": np.array([]), "current_visualizer_process": None}

# pysimpleGUI INIT:
AppFont = "Any 16"
sg.theme("DarkBlue3")

menu_layout = [
    ['Run Visualizers', ['Amplitude-Frequency-Visualizer', 'Waveform', 'Spectogram','Intensity-vs-Frequency-and-time']],
]

layout = [
    [sg.Menu(menu_layout)],
    [
        sg.Graph(
            canvas_size=(500, 500),
            graph_bottom_left=(-2, -2),
            graph_top_right=(102, 102),
            background_color="#809AB6",
            key="graph",
        )
    ],
    [sg.ProgressBar(4000, orientation="h", size=(20, 20), key="-PROG-")],
    [
        sg.Button("Listen", font=AppFont),
        sg.Button("Stop", font=AppFont, disabled=True),
        sg.Button("Exit", font=AppFont),
    ],
]
_VARS["window"] = sg.Window("Mic to Sound Intensity vs Frequency heatmap", layout, finalize=True)
graph = _VARS["window"]["graph"]

# INIT vars:
CHUNK = 1024  # Samples: 1024,  512, 256, 128
RATE = 44100  # Equivalent to Human Hearing at 40 kHz
INTERVAL = 1  # Sampling Interval in Seconds -> Interval to listen
TIMEOUT = 10  # In ms for the event loop
pAud = pyaudio.PyAudio()

# PySimpleGUI plots:
def drawHeatMapWithLabels(intensity_data):
    graph.erase()  # Clear previous heatmap
    rows, cols = intensity_data.shape

    # Draw labels for frequency axis
    for row in range(rows):
        graph.DrawText(f"{row * (RATE / 2) / rows:.0f} Hz", (105, 100 - row * 100 / rows))

    # Draw labels for time axis
    for col in range(cols):
        graph.DrawText(f"{col * INTERVAL:.1f} sec", (col * 100 / cols, -5))

    # Draw heatmap
    for row in range(rows):
        for col in range(cols):
            intensity = intensity_data[row, col]
            color = getHeatMapColor(intensity)
            x1 = col * 100 / cols
            y1 = 100 - (row + 1) * 100 / rows
            x2 = x1 + 100 / cols
            y2 = y1 + 100 / rows
            graph.DrawRectangle((x1, y1), (x2, y2), line_color=color, fill_color=color)

# pyaudio stream:
def stop():
    if _VARS["stream"]:
        _VARS["stream"].stop_stream()
        _VARS["stream"].close()
        _VARS["stream"] = None
        _VARS["window"]["-PROG-"].update(0)
        _VARS["window"]["Stop"].Update(disabled=True)
        _VARS["window"]["Listen"].Update(disabled=False)

# callback:
def callback(in_data, frame_count, time_info, status):
    _VARS["audioData"] = np.frombuffer(in_data, dtype=np.int16)
    return (in_data, pyaudio.paContinue)

def listen():
    _VARS["window"]["Stop"].Update(disabled=False)
    _VARS["window"]["Listen"].Update(disabled=True)
    _VARS["stream"] = pAud.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK,
        stream_callback=callback,
    )
    _VARS["stream"].start_stream()

def close_current_visualizer():
    if _VARS["current_visualizer_process"] and _VARS["current_visualizer_process"].poll() is None:
        _VARS["current_visualizer_process"].kill()

# INIT:

def initHeatMap(graph, rate, interval, rows, cols):

    # Clear previous drawing

    graph.erase()

    #Initial setup for the heatmap

    for row in range(rows):

        graph.DrawText(f"{row * (rate / 2) / rows:.0f} Hz", (105, 100 - row * 100 / rows))



    # Draw labels for time axis

    for col in range(cols):

        graph.DrawText(f"{col * interval:.1f} sec", (col * 100 / cols, -5))



# Call the initHeatMap function to initialize the heatmap

rows = 10  # Number of rows in the heatmap

cols = 10  # Number of columns in the heatmap

initHeatMap(graph, RATE, INTERVAL, rows, cols)

# Function to get heatmap color
def getHeatMapColor(intensity, threshold=0.0, cmap=None):
    # Default color map
    if cmap is None:
        cmap = ["#0000ff", "#00ff00", "#ffff00", "#ff0000"]  # Blue to Red gradient
    
    # Determining color based on intensity and thresholds
    if np.isnan(intensity):
        return "#808080"  # Gray color for NaN values
    else:
        # Normalizing intensity to fit within the colormap range
        intensity_norm = np.log1p(intensity) / 20  # Logarithmic scale for better visualization
        color_index = min(int(intensity_norm * len(cmap)), len(cmap) - 1)
        return cmap[color_index]

def compute_intensity_data(audio_data, window_size=1024, hop_size=512):
    num_frames = len(audio_data) // hop_size
    intensity_data = np.zeros((num_frames, window_size // 2))

    for i in range(num_frames):
        frame = audio_data[i * hop_size: (i + 1) * hop_size]
        intensity_data[i, :] = np.abs(np.fft.fft(frame)[:window_size // 2])  # Magnitude spectrum
    return intensity_data

# MAIN LOOP
while True:
    event, values = _VARS["window"].read(timeout=TIMEOUT)
    if event in (sg.WIN_CLOSED, "Exit"):
        close_current_visualizer()
        stop()
        pAud.terminate()
        break
    if event == "Listen":
        listen()
    if event == "Stop":
        stop()
    if event == 'Amplitude-Frequency-Visualizer':
        close_current_visualizer()
        _VARS["current_visualizer_process"] = subprocess.Popen(['python', 'Amplitude-Frequency-Visualizer.py'])
        _VARS["window"].close()  
        break 
    if event == 'Waveform':
        close_current_visualizer()
        _VARS["current_visualizer_process"] = subprocess.Popen(['python', 'Waveform.py'])
        _VARS["window"].close()  
        break 
    if event == 'Spectogram':
        close_current_visualizer()
        _VARS["current_visualizer_process"] = subprocess.Popen(['python', 'Spectogram.py'])
        _VARS["window"].close()  
        break 
    if event == 'Intensity-vs-Frequency-and-time':
        close_current_visualizer()
        _VARS["current_visualizer_process"] = subprocess.Popen(['python', 'Intensity-vs-Frequency-and-time.py'])
        _VARS["window"].close()  
        break 

    # Along with the global audioData variable, this
    # bit updates the waveform plotf
    elif _VARS["audioData"].size != 0:
        # Update volume meter
        _VARS["window"]["-PROG-"].update(np.amax(_VARS["audioData"]))
        
        # Compute intensity data for heatmap
        intensity_data = compute_intensity_data(_VARS["audioData"])
        
        # Draw heatmap
        drawHeatMapWithLabels(intensity_data)

_VARS["window"].close()
