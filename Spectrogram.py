import PySimpleGUI as sg
import pyaudio
import numpy as np
import scipy.signal
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import queue

# Constants
CHUNK = 1024  # Samples per frame
RATE = 44100  # Sampling rate

# GUI Layout
sg.theme("DarkBlue3")

graph = sg.Graph(
    canvas_size=(500, 500),
    graph_bottom_left=(0, 0),
    graph_top_right=(RATE / 2, 5000),
    background_color="black",
    key="-GRAPH-",
)

layout = [
    [graph],
    [sg.ProgressBar(4000, orientation="h", size=(20, 20), key="-PROG-")],
    [
        sg.Button("Start", size=(10, 1)),
        sg.Button("Stop", size=(10, 1), disabled=True),
        sg.Button("Exit", size=(10, 1)),
    ],
]

# GUI Window
window = sg.Window("Real-time Audio Spectrogram", layout, finalize=True)

# PyAudio Initialization
p = pyaudio.PyAudio()
stream = p.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=RATE,
    input=True,
    frames_per_buffer=CHUNK,
)

# Buffer for audio data
audio_buffer = queue.Queue(maxsize=10)

# Plot initialization
fig, ax = plt.subplots()
fig_agg = FigureCanvasTkAgg(fig, window["-GRAPH-"].TKCanvas)

# Function to draw the spectrogram
def draw_spectrogram(audio_data):
    f, t, sxx = scipy.signal.spectrogram(audio_data, fs=RATE)
    ax.clear()
    ax.pcolormesh(t, f, 10 * np.log10(sxx), shading="gouraud")
    ax.set_ylabel("Frequency [Hz]")
    ax.set_xlabel("Time [sec]")
    fig_agg.draw()


# Thread to read audio data and update GUI
def audio_thread():
    while True:
        data = stream.read(CHUNK)
        audio_buffer.put(np.frombuffer(data, dtype=np.int16))


# Thread to update GUI with audio data
def update_gui_thread():
    while True:
        audio_data = audio_buffer.get()
        window["-PROG-"].update(np.max(audio_data))
        draw_spectrogram(audio_data)


# Main event loop
audio_processing = threading.Thread(target=audio_thread, daemon=True)
audio_processing.start()

update_gui = threading.Thread(target=update_gui_thread, daemon=True)
update_gui.start()

while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED or event == "Exit":
        break
    elif event == "Start":
        window["Start"].update(disabled=True)
        window["Stop"].update(disabled=False)
    elif event == "Stop":
        window["Start"].update(disabled=False)
        window["Stop"].update(disabled=True)

# Clean up
window.close()
stream.stop_stream()
stream.close()
p.terminate()

