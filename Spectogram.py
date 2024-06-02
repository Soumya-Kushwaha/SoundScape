import PySimpleGUI as sg
import pyaudio
import numpy as np
import scipy.signal
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import subprocess

""" Real-Time Audio Spectrogram Plot """

# Global Variables and Constants
_VARS = {"window": None, "stream": None, "audio_data": np.array([]), "current_visualizer_process": None}

# PySimpleGUI Initialization
APP_FONT = "Any 16"
sg.theme("DarkBlue3")

MENU_LAYOUT = [
    ['Run Visualizers', ['Amplitude-Frequency-Visualizer', 'Waveform', 'Spectrogram', 'Intensity-vs-Frequency-and-time']],
]

LAYOUT = [
    [sg.Menu(MENU_LAYOUT)],
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
        sg.Button("Listen", font=APP_FONT),
        sg.Button("Stop", font=APP_FONT, disabled=True),
        sg.Button("Exit", font=APP_FONT),
    ],
]

_VARS["window"] = sg.Window("Mic to Spectrogram Plot + Max Level", LAYOUT, finalize=True)
GRAPH = _VARS["window"]["graph"]

# Audio Constants
CHUNK = 1024  # Samples
RATE = 44100  # Equivalent to Human Hearing at 40 kHz
INTERVAL = 1  # Sampling Interval in Seconds
TIMEOUT = 10  # In ms for the event loop

# Initialize PyAudio
pAud = pyaudio.PyAudio()

try:
    pAud.get_device_info_by_index(0)
except pyaudio.CoreError as e:
    print(f"Error initializing PyAudio: {e}")
    pAud = None

# Function to draw matplotlib figure on PySimpleGUI canvas
def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side="top", fill="both", expand=1)
    return figure_canvas_agg

# Function to stop the audio stream
def stop():
    if _VARS["stream"]:
        _VARS["stream"].stop_stream()
        _VARS["stream"].close()
        _VARS["stream"] = None
        _VARS["window"]["-PROG-"].update(0)
        _VARS["window"]["Stop"].update(disabled=True)
        _VARS["window"]["Listen"].update(disabled=False)

# PyAudio callback function
def audio_callback(in_data, frame_count, time_info, status):
    _VARS["audio_data"] = np.frombuffer(in_data, dtype=np.int16)
    return in_data, pyaudio.paContinue

# Function to start listening to the audio stream
def listen():
    _VARS["window"]["Stop"].update(disabled=False)
    _VARS["window"]["Listen"].update(disabled=True)
    _VARS["stream"] = pAud.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK,
        stream_callback=audio_callback,
    )
    _VARS["stream"].start_stream()

# Function to close the current visualizer process
def close_current_visualizer():
    if _VARS["current_visualizer_process"] and _VARS["current_visualizer_process"].poll() is None:
        _VARS["current_visualizer_process"].kill()

# Initialize Matplotlib figure
fig, ax = plt.subplots()
fig_agg = draw_figure(GRAPH.TKCanvas, fig)

# Main Event Loop
while True:
    event, values = _VARS["window"].read(timeout=TIMEOUT)
    if event in (sg.WIN_CLOSED, "Exit"):
        close_current_visualizer()
        stop()
        if pAud:
            pAud.terminate()
        break

    if event == "Listen":
        listen()

    if event == "Stop":
        stop()

    if event in ['Amplitude-Frequency-Visualizer', 'Waveform', 'Spectrogram', 'Intensity-vs-Frequency-and-time']:
        close_current_visualizer()
        _VARS["current_visualizer_process"] = subprocess.Popen(['python', f'{event}.py'])
        _VARS["window"].close()
        break

    # Update the spectrogram plot
    elif _VARS["audio_data"].size != 0:
        # Update volume meter
        _VARS["window"]["-PROG-"].update(np.amax(_VARS["audio_data"]))
        # Compute and plot spectrogram
        f, t, Sxx = scipy.signal.spectrogram(_VARS["audio_data"], fs=RATE)
        ax.clear()
        ax.pcolormesh(t, f, Sxx, shading="gouraud")
        ax.set_ylabel("Frequency [Hz]")
        ax.set_xlabel("Time [sec]")
        fig_agg.draw()
