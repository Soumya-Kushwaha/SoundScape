import PySimpleGUI as sg
import pyaudio
import numpy as np
import scipy.fft
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

""" RealTime Audio Frequency plot """

# VARS CONSTS:
_VARS = {"window": False, "stream": False, "audioData": np.array([])}

# pysimpleGUI INIT:
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
_VARS["window"] = sg.Window("Mic to frequency plot + Max Level", layout, finalize=True)

graph = _VARS["window"]["graph"]

# INIT vars:
CHUNK = 1024  # Samples: 1024,  512, 256, 128
RATE = 44100  # Equivalent to Human Hearing at 40 kHz
INTERVAL = 1  # Sampling Interval in Seconds -> Interval to listen
TIMEOUT = 10  # In ms for the event loop
pAud = pyaudio.PyAudio()

# FUNCTIONS:


# PySimpleGUI plots:
def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side="top", fill="both", expand=1)
    return figure_canvas_agg


# pyaudio stream:
def stop():
    if _VARS["stream"]:
        _VARS["stream"].stop_stream()
        _VARS["stream"].close()
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


# INIT:
fig, ax = plt.subplots()  # create a figure and an axis object
fig_agg = draw_figure(graph.TKCanvas, fig)  # draw the figure on the graph

# MAIN LOOP
while True:
    event, values = _VARS["window"].read(timeout=TIMEOUT)
    if event == sg.WIN_CLOSED or event == "Exit":
        stop()
        pAud.terminate()
        break
    if event == "Listen":
        listen()
    if event == "Stop":
        stop()

    # Along with the global audioData variable, this
    # bit updates the frequency plot

    elif _VARS["audioData"].size != 0:
        # Update volume meter
        _VARS["window"]["-PROG-"].update(np.amax(_VARS["audioData"]))
        # Compute frequency spectrum
        yf = scipy.fft.fft(_VARS["audioData"])  # compute the discrete Fourier transform
        xf = np.linspace(0.0, RATE / 2, CHUNK // 2)  # create the frequency axis
        # Plot frequency spectrum
        ax.clear()  # clear the previous plot
        ax.plot(
            xf, 2.0 / CHUNK * np.abs(yf[: CHUNK // 2])
        )  # plot the frequency spectrum as a line graph
        ax.set_ylabel("Amplitude")  # set the y-axis label
        ax.set_xlabel("Frequency [Hz]")  # set the x-axis label
        fig_agg.draw()  # redraw the figure
