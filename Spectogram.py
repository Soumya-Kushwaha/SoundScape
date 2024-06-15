import PySimpleGUI as sg
import pyaudio
import numpy as np
import scipy.signal
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# gui-performance-enhancement
import threading
import queue
import subprocess




# Global variables
_VARS = {"window": None, "stream": None, "audioData": np.array([])}
audio_buffer = queue.Queue(maxsize=10)  # Buffer for audio data
stop_event = threading.Event()  # Event to signal stopping of the audio stream

 gui-performance-enhancement
# PySimpleGUI initialization
# VARS CONSTS:
_VARS = {"window": False, "stream": False, "audioData": np.array([]), "current_visualizer_process": None}

# pysimpleGUI INIT:
AppFont = "Any 16"
sg.theme("DarkBlue3")

menu_layout = [
    ['Run Visualizers', ['Amplitude-Frequency-Visualizer', 'Waveform', 'Spectrogram', 'Intensity-vs-Frequency-and-time']],
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
_VARS["window"] = sg.Window("Mic to spectrogram plot + Max Level", layout, finalize=True)
 gui-performance-enhancement
graph = _VARS["window"]["graph"]

# PyAudio initialization
pAud = pyaudio.PyAudio()
CHUNK = 1024
RATE = 44100
INTERVAL = 1
TIMEOUT = 100  # Adjusted timeout value

def stop():
    if _VARS["stream"] is not None and _VARS["stream"].is_active():
        stop_event.set()  # Signal the audio processing thread to stop
        _VARS["stream"].stop_stream()
        _VARS["stream"].close()
        _VARS["stream"] = None
        _VARS["window"]["-PROG-"].update(0)
 gui-performance-enhancement
        _VARS["window"]["Stop"].update(disabled=True)
        _VARS["window"]["Listen"].update(disabled=False)
        stop_event.clear()  # Reset the event for the next use


        _VARS["window"]["Stop"].Update(disabled=True)
        _VARS["window"]["Listen"].Update(disabled=False)

# callback:

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

 gui-performance-enhancement
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

    def close_current_visualizer():
    if _VARS["current_visualizer_process"] and _VARS["current_visualizer_process"].poll() is None:
        _VARS["current_visualizer_process"].kill()


# INIT:
fig, ax = plt.subplots()  # create a figure and an axis object
fig_agg = draw_figure(graph.TKCanvas, fig)  # draw the figure on the graph


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
    # bit updates the spectrogram plot
    elif _VARS["audioData"].size != 0:
        # Update volume meter
        _VARS["window"]["-PROG-"].update(np.amax(_VARS["audioData"]))
        # Compute spectrogram
        f, t, Sxx = scipy.signal.spectrogram(_VARS["audioData"], fs=RATE)
        # Plot spectrogram
        ax.clear()  # clear the previous plot
        ax.pcolormesh(
            t, f, Sxx, shading="gouraud"
        )  # plot the spectrogram as a colored mesh
        ax.set_ylabel("Frequency [Hz]")  # set the y-axis label
        ax.set_xlabel("Time [sec]")  # set the x-axis label
        fig_agg.draw()  # redraw the figure

