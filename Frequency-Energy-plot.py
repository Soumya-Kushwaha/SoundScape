import PySimpleGUI as sg
import pyaudio
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import soundfile as sf
import scipy.fft
import matplotlib.pyplot as plt

# VARS CONSTS:
_VARS = {"window": False, "stream": False, "audioData": np.array([]), "audioBuffer": np.array([])}

# PySimpleGUI INIT:
AppFont = "Helvetica"
sg.theme("DarkBlue3")

# Layout for the GUI
layout = [
    [
        sg.Graph(
            canvas_size=(600, 600),
            graph_bottom_left=(-2, -2),
            graph_top_right=(102, 102),
            background_color="#809AB6",
            key="graph",
            tooltip="Frequency vs Energy graph"  # Tooltip added
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

# Create the main window
_VARS["window"] = sg.Window("Mic to Frequency vs Energy plot", layout, finalize=True)  
graph = _VARS["window"]["graph"]

# INIT vars:
CHUNK = 1024  # Number of samples per frame
RATE = 44100  # Sampling rate in Hz
INTERVAL = 1  # Sampling interval in seconds
TIMEOUT = 10  # Event loop timeout in ms
pAud = pyaudio.PyAudio()  # Initialize PyAudio

# FUNCTIONS:

# Function to draw a figure on the canvas
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
        _VARS["window"]["-PROG-"].update(0)
        _VARS["window"]["Stop"].Update(disabled=True)
        _VARS["window"]["Listen"].Update(disabled=False)

# Function to pause the audio stream
def pause():
    if _VARS["stream"].is_active():
        _VARS["stream"].stop_stream()
        _VARS["window"]["Pause"].Update(disabled=True)
        _VARS["window"]["Resume"].Update(disabled=False)

# Function to resume the audio stream
def resume():
    if not _VARS["stream"].is_active():
        _VARS["stream"].start_stream()
        _VARS["window"]["Pause"].Update(disabled=False)
        _VARS["window"]["Resume"].Update(disabled=True)

# Function to save the plot and audio data
def save():
    # Ask the user for a directory to save the files
    folder = sg.popup_get_folder('Please select a directory to save the files')
    if folder:
        # Save the plot as an image file
        fig.savefig(f'{folder}/output.png')
        sg.popup('Success', f'Image saved as {folder}/output.png')
        # Save the recorded audio data as a WAV file
        sf.write(f'{folder}/output.wav', _VARS["audioBuffer"], RATE)
        sg.popup('Success', f'Audio saved as {folder}/output.wav')

# Callback function for the audio stream
def callback(in_data, frame_count, time_info, status):
    _VARS["audioData"] = np.frombuffer(in_data, dtype=np.int16)
    _VARS["audioBuffer"] = np.append(_VARS["audioBuffer"], _VARS["audioData"])
    return (in_data, pyaudio.paContinue)

# Function to start listening to the audio stream
def listen():
    _VARS["window"]["Stop"].Update(disabled=False)
    _VARS["window"]["Listen"].Update(disabled=True)
    _VARS["stream"] = pAud.open(
        format=pyaudio.paInt16,  # Audio format
        channels=1,  # Number of audio channels
        rate=RATE,  # Sampling rate
        input=True,  # Input stream
        frames_per_buffer=CHUNK,  # Number of samples per frame
        stream_callback=callback,  # Callback function
    )
    _VARS["stream"].start_stream()  # Start the audio stream

# Initialize the plot
fig, ax = plt.subplots()  
fig_agg = draw_figure(graph.TKCanvas, fig) 

# MAIN LOOP
while True:
    event, values = _VARS["window"].read(timeout=TIMEOUT)
    if event == "Exit":
        stop()
        pAud.terminate()
        break
    # Handle closing of the application
    if event == sg.WIN_CLOSED :
        _VARS["stream"].stop_stream()
        _VARS["stream"].close()
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
        _VARS["window"]["-PROG-"].update(np.amax(_VARS["audioData"]))
        yy = scipy.fft.fft(_VARS["audioData"])  
        xx = np.linspace(0.0, RATE / 2, CHUNK // 2)  
        ax.clear()  
        
        # Calculate the energy spectrum
        energy = np.abs(yy[:CHUNK // 2]) ** 2

        # Plot frequency vs energy
        ax.plot(xx, energy, label='Frequency vs Energy')
        
        # Update axis labels
        ax.set_ylabel("Energy")
        ax.set_xlabel("Frequency [Hz]")
        
        ax.grid(True)  # Enable gridlines
        ax.legend()  # Add a legend
        fig_agg.draw()  # Redraw the figure
