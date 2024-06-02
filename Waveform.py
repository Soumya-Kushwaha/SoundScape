import PySimpleGUI as sg
import pyaudio
import numpy as np
import subprocess

""" RealTime Audio Waveform plot """

# Constants and Variables
_VARS = {
    "window": None,
    "stream": None,
    "audioData": np.array([]),
    "current_visualizer_process": None
}

# PySimpleGUI Initialization
APP_FONT = "Any 16"
sg.theme("DarkBlue3")

# Menu Layout
menu_layout = [
    ['Run Visualizers', [
        'Amplitude-Frequency-Visualizer', 
        'Waveform', 
        'Spectrogram', 
        'Intensity-vs-Frequency-and-time']
    ]
]

# Main Layout
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
        sg.Button("Listen", font=APP_FONT),
        sg.Button("Stop", font=APP_FONT, disabled=True),
        sg.Button("Exit", font=APP_FONT),
    ],
]

# Initialize Window
_VARS["window"] = sg.Window("Mic to waveform plot + Max Level", layout, finalize=True)
graph = _VARS["window"]["graph"]

# Audio Parameters
CHUNK = 1024
RATE = 44100
INTERVAL = 1
TIMEOUT = 10

# Initialize PyAudio
pAud = pyaudio.PyAudio()
try:
    pAud.get_device_info_by_index(0)
except pyaudio.CoreError as e:
    print(f"Error initializing PyAudio: {e}")
    pAud = None

# Function to draw axes
def draw_axes(data_range_min=0, data_range_max=100):
    graph.DrawLine((0, 50), (100, 50))
    graph.DrawLine((0, data_range_min), (0, data_range_max))

# Function to stop audio stream
def stop_stream():
    if _VARS["stream"]:
        _VARS["stream"].stop_stream()
        _VARS["stream"].close()
        _VARS["stream"] = None
        _VARS["window"]["-PROG-"].update(0)
        _VARS["window"]["Stop"].update(disabled=True)
        _VARS["window"]["Listen"].update(disabled=False)

# PyAudio callback function
def audio_callback(in_data, frame_count, time_info, status):
    _VARS["audioData"] = np.frombuffer(in_data, dtype=np.int16)
    return (in_data, pyaudio.paContinue)

# Function to start listening to audio
def start_listening():
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
def close_visualizer():
    if _VARS["current_visualizer_process"] and _VARS["current_visualizer_process"].poll() is None:
        _VARS["current_visualizer_process"].terminate()
        _VARS["current_visualizer_process"].wait()
        _VARS["current_visualizer_process"] = None

# Initialize plot
draw_axes()

# Main Event Loop
while True:
    event, _ = _VARS["window"].read(timeout=TIMEOUT)
    
    if event in (sg.WIN_CLOSED, "Exit"):
        close_visualizer()
        stop_stream()
        pAud.terminate()
        break

    if event == "Listen":
        start_listening()

    if event == "Stop":
        stop_stream()

    if event in ['Amplitude-Frequency-Visualizer', 'Waveform', 'Spectrogram', 'Intensity-vs-Frequency-and-time']:
        close_visualizer()
        script_name = event.replace(' ', '-').lower() + '.py'
        _VARS["current_visualizer_process"] = subprocess.Popen(['python', script_name])
        _VARS["window"].close()
        break

    # Update the waveform plot
    elif _VARS["audioData"].size != 0:
        _VARS["window"]["-PROG-"].update(np.amax(_VARS["audioData"]))
        graph.erase()
        draw_axes()
        for x in range(CHUNK):
            graph.DrawCircle(
                (x, (_VARS["audioData"][x] / 100) + 50),
                0.4,
                line_color="blue",
                fill_color="blue",
            )

_VARS["window"].close()
