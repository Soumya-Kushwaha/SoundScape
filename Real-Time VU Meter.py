import PySimpleGUI as sg
import pyaudio
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import soundfile as sf

_VARS = {"window": False, "stream": False, "audioData": np.array([]), "audioBuffer": np.array([])}

AppFont = "Helvetica"
sg.theme("DarkBlue3")

layout = [
    [
        sg.Graph(
            canvas_size=(600, 300),
            graph_bottom_left=(-2, -2),
            graph_top_right=(102, 102),
            background_color="#809AB6",
            key="graph_vu_meter",
            tooltip="VU Meter"
        )
    ],
    [sg.Text("Progress:", text_color='white', font=('Helvetica', 15, 'bold')), sg.ProgressBar(100, orientation="h", size=(20, 20), key="-PROG-")],  
    [
        sg.Button("Listen", font=AppFont, tooltip="Start listening"),
        sg.Button("Pause", font=AppFont, disabled=True, tooltip="Pause listening"),
        sg.Button("Resume", font=AppFont, disabled=True, tooltip="Resume listening"),
        sg.Button("Stop", font=AppFont, disabled=True, tooltip="Stop listening"),
        sg.Button("Save", font=AppFont, disabled=True, tooltip="Save the plot"),
        sg.Button("Exit", font=AppFont, tooltip="Exit the application"),
    ],
]

_VARS["window"] = sg.Window("Mic to VU Meter", layout, finalize=True)  
graph_vu_meter = _VARS["window"]["graph_vu_meter"]

CHUNK = 1024
RATE = 44100
INTERVAL = 1
TIMEOUT = 10
NOISE_FLOOR = 1e-6
pAud = pyaudio.PyAudio()

def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side="top", fill="both", expand=1)
    return figure_canvas_agg

def stop():
    if _VARS["stream"]:
        _VARS["stream"].stop_stream()
        _VARS["stream"].close()
        _VARS["window"]["-PROG-"].update(0)
        _VARS["window"]["Stop"].Update(disabled=True)
        _VARS["window"]["Listen"].Update(disabled=False)

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
        fig_vu_meter.savefig(f'{folder}/vu_meter.png')
        sg.popup('Success', f'Image saved as {folder}/vu_meter.png')
        sf.write(f'{folder}/output.wav', _VARS["audioBuffer"], RATE)
        sg.popup('Success', f'Audio saved as {folder}/output.wav')

def callback(in_data, frame_count, time_info, status):
    _VARS["audioData"] = np.frombuffer(in_data, dtype=np.int16)
    _VARS["audioBuffer"] = np.append(_VARS["audioBuffer"], _VARS["audioData"])
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

fig_vu_meter, ax_vu_meter = plt.subplots()
fig_vu_meter_agg = draw_figure(graph_vu_meter.TKCanvas, fig_vu_meter)

while True:
    event, values = _VARS["window"].read(timeout=TIMEOUT)
    if event == "Exit":
        stop()
        pAud.terminate()
        break
    if event == sg.WIN_CLOSED:
        stop()
        pAud.terminate()
        break
    if event == "Listen":
        listen()
        _VARS["window"]["Save"].Update(disabled=False)
    if event == "Pause":
        pause()
    if event == "Resume":
        resume()
    if event == "Stop":
        stop()
    if event == "Save":
        save()

    elif _VARS["audioData"].size != 0:
        rms = np.sqrt(np.mean(np.square(_VARS["audioData"])))
        vu_level = 20 * np.log10(max(rms, NOISE_FLOOR)) + 3

        normalized_vu_level = max(vu_level, 0)
        
        _VARS["window"]["-PROG-"].update(normalized_vu_level)
        
        ax_vu_meter.clear()
        ax_vu_meter.barh(['VU Meter'], [normalized_vu_level], color='green')
        ax_vu_meter.set_xlim(0, 80)
        ax_vu_meter.set_xlabel("Level (dB)")
        ax_vu_meter.grid(True)
        
        fig_vu_meter_agg.draw()