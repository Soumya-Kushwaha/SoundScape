import PySimpleGUI as sg
import pyaudio
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import soundfile as sf
import scipy.fft
import matplotlib.pyplot as plt
import subprocess

# VARS CONSTS:
_VARS = {
    "window": False,
    "stream": False,
    "audioData": np.array([]),
    "audioBuffer": np.array([]),
    "current_visualizer_process": None,
}

# pysimpleGUI INIT:
AppFont = "Helvetica"
sg.theme("DarkBlue3")

menu_layout = [
    ['Run Visualizers', ['Energy-Frequency-Visualizer', 'Waveform', 'Spectogram', 'Intensity-vs-Frequency-and-time']],
]

layout = [
    [sg.Menu(menu_layout)],
    [
        sg.Graph(
            canvas_size=(600, 600),
            graph_bottom_left=(-2, -2),
            graph_top_right=(102, 102),
            background_color="#809AB6",
            key="graph",
            tooltip="Frequency graph"
        )
    ],
    [sg.Text("Progress:", text_color='white', font=('Helvetica', 15, 'bold')), sg.ProgressBar(4000, orientation="h", size=(20, 20), key="-PROG-")],
    [
        sg.Button("Listen", font=AppFont, tooltip="Start listening"),
        sg.Button("Pause", font=AppFont, disabled=True, tooltip="Pause listening"),
        sg.Button("Resume", font=AppFont, disabled=True, tooltip="Resume listening"),
        sg.Button("Stop", font=AppFont, disabled=True, tooltip="Stop listening"),
        sg.Button("Save", font=AppFont, disabled=True, tooltip="Save the plot"),
        sg.Button("Exit", font=AppFont, tooltip="Exit the application"),
    ],
]

_VARS["window"] = sg.Window("Mic to energy-frequency plot", layout, finalize=True)
graph = _VARS["window"]["graph"]

# INIT vars:
CHUNK = 1024
RATE = 44100
INTERVAL = 1
TIMEOUT = 10
pAud = pyaudio.PyAudio()

# FUNCTIONS:

def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side="top", fill="both", expand=1)
    return figure_canvas_agg

def stop():
    if _VARS["stream"]:
        _VARS["stream"].stop_stream()
        _VARS["stream"].close()
        _VARS["stream"] = None
        _VARS["window"]["-PROG-"].update(0)
        _VARS["window"]["Stop"].Update(disabled=True)
        _VARS["window"]["Listen"].Update(disabled=False)
        _VARS["window"]["Pause"].Update(disabled=True)
        _VARS["window"]["Resume"].Update(disabled=True)
        _VARS["window"]["Save"].Update(disabled=True)

def pause():
    if _VARS["stream"].is_active():
        _VARS["stream"].stop_stream()
        _VARS["window"]["Pause"].Update(disabled=True)
        _VARS["window"]["Resume"].Update(disabled=False)

def resume():
    if not _VARS["stream"].is_active():
        _VARS["stream"].start_stream()
        _VARS["window"]["Pause"].Update(disabled=False)
        _VARS["window"]["Resume"].Update(disabled=True)

def save():
    folder = sg.popup_get_folder('Please select a directory to save the files')
    if folder:
        fig.savefig(f'{folder}/output.png')
        sg.popup('Success', f'Image saved as {folder}/output.png')
        sf.write(f'{folder}/output.wav', _VARS["audioBuffer"], RATE)
        sg.popup('Success', f'Audio saved as {folder}/output.wav')

def callback(in_data, frame_count, time_info, status):
    _VARS["audioData"] = np.frombuffer(in_data, dtype=np.int16)
    _VARS["audioBuffer"] = np.append(_VARS["audioBuffer"], _VARS["audioData"])
    return (in_data, pyaudio.paContinue)

def listen():
    _VARS["window"]["Stop"].Update(disabled=False)
    _VARS["window"]["Listen"].Update(disabled=True)
    _VARS["window"]["Pause"].Update(disabled=False)
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
fig, ax = plt.subplots()
fig_agg = draw_figure(graph.TKCanvas, fig)

# MAIN LOOP
while True:
    event, values = _VARS["window"].read(timeout=TIMEOUT)
    if event in (sg.WIN_CLOSED, "Exit"):
        stop()
        pAud.terminate()
        break
    if event == "Listen":
        listen()
    if event == "Pause":
        pause()
    if event == "Resume":
        resume()
    if event == "Stop":
        stop()
    if event == "Save":
        save()
    if event in ['Energy-Frequency-Visualizer', 'Waveform', 'Spectogram', 'Intensity-vs-Frequency-and-time']:
        close_current_visualizer()
        _VARS["current_visualizer_process"] = subprocess.Popen(['python', f'{event}.py'])
        _VARS["window"].close()
        break
    elif _VARS["audioData"].size != 0:
        _VARS["window"]["-PROG-"].update(np.amax(_VARS["audioData"]))
        yf = scipy.fft.fft(_VARS["audioData"])
        xf = np.linspace(0.0, RATE / 2, CHUNK // 2)
        ax.clear()
        energy = (2.0 / CHUNK * np.abs(yf[: CHUNK // 2]))**2  # Compute energy
        ax.plot(xf, energy, label='Energy Spectrum')
        ax.set_ylabel("Energy")
        ax.set_xlabel("Frequency [Hz]")
        ax.grid(True)
        ax.legend()
        fig_agg.draw()
