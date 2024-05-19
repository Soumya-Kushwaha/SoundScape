import PySimpleGUI as sg
import pyaudio
import numpy as np
import scipy.signal
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import queue

# Global variables
_VARS = {"window": None, "stream": None, "audioData": np.array([])}
audio_buffer = queue.Queue(maxsize=10)  # Buffer for audio data
stop_event = threading.Event()  # Event to signal stopping of the audio stream

# PySimpleGUI initialization
AppFont = "Any 16"
sg.theme("DarkBlue3")
layout = [
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
_VARS["window"] = sg.Window("Mic to spectrogram plot + Max Level", layout, finalize=True)

# PyAudio initialization
pAud = pyaudio.PyAudio()
CHUNK = 1024
RATE = 44100
INTERVAL = 1
TIMEOUT = 100 # Adjusted timeout value

def stop():
    if _VARS["stream"] is not None and _VARS["stream"].is_active():
        stop_event.set()  # Signal the audio processing thread to stop
        _VARS["stream"].stop_stream()
        _VARS["stream"].close()
        _VARS["stream"] = None
        _VARS["window"]["-PROG-"].update(0)
        _VARS["window"]["Stop"].update(disabled=True)
        _VARS["window"]["Listen"].update(disabled=False)
        stop_event.clear()  # Reset the event for the next use

def callback(in_data, frame_count, time_info, status):
    if stop_event.is_set():
        return (in_data, pyaudio.paComplete)
    audio_buffer.put(np.frombuffer(in_data, dtype=np.int16))
    return (in_data, pyaudio.paContinue)

def listen():
    _VARS["window"]["Stop"].update(disabled=False)
    _VARS["window"]["Listen"].update(disabled=True)
    _VARS["stream"] = pAud.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK,
        stream_callback=callback,
    )
    _VARS["stream"].start_stream()

def audio_processing(ax, fig_agg):
    while not stop_event.is_set():
        try:
            audio_data = audio_buffer.get(timeout=1)
            if audio_data.size != 0:
                _VARS["window"]["-PROG-"].update(np.amax(audio_data))
                f, t, Sxx = scipy.signal.spectrogram(audio_data, fs=RATE)
                ax.clear()
                ax.pcolormesh(t, f, Sxx, shading="gouraud")
                ax.set_ylabel("Frequency [Hz]")
                ax.set_xlabel("Time [sec]")
                fig_agg.draw()
        except queue.Empty:
            continue

def main():
    # Initialization
    fig, ax = plt.subplots()
    fig_agg = FigureCanvasTkAgg(fig, _VARS["window"]["graph"].TKCanvas)
    fig_agg.draw()
    fig_agg.get_tk_widget().pack(side="top", fill="both", expand=1)

    # Multithreading for audio processing
    audio_thread = threading.Thread(target=audio_processing, args=(ax, fig_agg))
    audio_thread.daemon = True
    audio_thread.start()

    # Event loop
    while True:
        event, values = _VARS["window"].read(timeout=TIMEOUT)
        if event == sg.WINDOW_CLOSED or event == "Exit":
            stop()
            pAud.terminate()
            break
        elif event == "Listen":
            listen()
        elif event == "Stop":
            stop()

if __name__ == "__main__":
    main()
