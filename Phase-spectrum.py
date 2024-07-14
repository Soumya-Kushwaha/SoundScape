import PySimpleGUI as sg
import pyaudio
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import soundfile as sf
import matplotlib.pyplot as plt
import subprocess
import traceback
from scipy.fft import fft, fftfreq, fftshift

# VARS CONSTS:

_VARS = {
    "window": False,  # Variable to hold the PySimpleGUI window object
    "stream": False,  # Variable to hold the PyAudio stream object
    "audioData": np.array([]),  # Array to store incoming audio data samples
    "audioBuffer": np.array([]),  # Buffer to accumulate all recorded audio data
    "current_visualizer_process": None,  # Process handle for the currently running visualizer subprocess
}

# PySimpleGUI INIT:
AppFont = "Helvetica"  # Font style for the GUI
sg.theme("DarkBlue3")  # Setting the PySimpleGUI theme

# Menu layout for visualizers
menu_layout = [
    ['Run Visualizers', ['Amplitude-Frequency-Visualizer', 'Waveform', 'Spectrogram', 'Intensity-vs-Frequency-and-time', 'Phase-Spectrum']],
]

# Layout structure for the main window
layout = [
    [sg.Menu(menu_layout)],  # Menu bar to run different visualizers
    [
        sg.Graph(
            canvas_size=(600, 600),
            graph_bottom_left=(-2, -2),
            graph_top_right=(102, 102),
            background_color="#809AB6",
            key="graph",
            tooltip="Phase Spectrum graph"
        )
    ],
    [sg.Text("Progress:", text_color='white', font=('Helvetica', 15, 'bold')), sg.ProgressBar(4000, orientation="h", size=(20, 20), key="-PROG-")],
    [  # Control buttons for audio recording
        sg.Button("Listen", font=AppFont, tooltip="Start listening"),
        sg.Button("Pause", font=AppFont, disabled=True, tooltip="Pause listening"),
        sg.Button("Resume", font=AppFont, disabled=True, tooltip="Resume listening"),
        sg.Button("Stop", font=AppFont, disabled=True, tooltip="Stop listening"),
        sg.Button("Save", font=AppFont, disabled=True, tooltip="Save the plot"),
        sg.Button("Exit", font=AppFont, tooltip="Exit the application"),
    ],
]

# Creating the PySimpleGUI window
_VARS["window"] = sg.Window("Mic to phase spectrum plot", layout, finalize=True)
graph = _VARS["window"]["graph"]  # Graph element for displaying the phase spectrum

# INIT vars:
CHUNK = 1024  # Samples per chunk for audio processing
RATE = 44100  # Sampling rate in Hz
INTERVAL = 1  # Sampling interval in seconds
TIMEOUT = 10  # Timeout in milliseconds for event handling
pAud = pyaudio.PyAudio()  # PyAudio instance for audio input/output

# FUNCTIONS:

def draw_figure(canvas, figure):
    """Draws a matplotlib figure onto a PySimpleGUI canvas."""
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side="top", fill="both", expand=1)
    return figure_canvas_agg

def stop():
    """Stops the audio stream and resets UI elements."""
    if _VARS["stream"]:
        _VARS["stream"].stop_stream()
        _VARS["stream"].close()
        _VARS["stream"] = None
        _VARS["window"]["-PROG-"].update(0)
        _VARS["window"]["Stop"].Update(disabled=True)
        _VARS["window"]["Listen"].Update(disabled=False)

def pause():
    """Pauses the audio stream."""
    if _VARS["stream"] and _VARS["stream"].is_active():
        _VARS["stream"].stop_stream()
        _VARS["window"]["Pause"].Update(disabled=True)
        _VARS["window"]["Resume"].Update(disabled=False)

def resume():
    """Resumes the paused audio stream."""
    if _VARS["stream"] and not _VARS["stream"].is_active():
        _VARS["stream"].start_stream()
        _VARS["window"]["Pause"].Update(disabled=False)
        _VARS["window"]["Resume"].Update(disabled=True)

def save():
    """Saves the current phase spectrum plot and recorded audio to files."""
    # Ask the user for a directory to save the files
    folder = sg.popup_get_folder('Please select a directory to save the files')
    if folder:
        # Save the phase spectrum plot as an image file
        fig.savefig(f'{folder}/phase_spectrum_output.png')
        sg.popup('Success', f'Image saved as {folder}/phase_spectrum_output.png')
        # Save the recorded audio data to a WAV file
        sf.write(f'{folder}/phase_spectrum_output.wav', _VARS["audioBuffer"], RATE)
        sg.popup('Success', f'Audio saved as {folder}/phase_spectrum_output.wav')

def callback(in_data, frame_count, time_info, status):
    """Callback function for audio stream processing."""
    try:
        _VARS["audioData"] = np.frombuffer(in_data, dtype=np.int16)
        _VARS["audioBuffer"] = np.append(_VARS["audioBuffer"], _VARS["audioData"])
    except Exception as e:
        print("Error in callback:", e)
        traceback.print_exc()
    return (in_data, pyaudio.paContinue)

def listen():
    """Starts the audio stream for listening."""
    try:
        _VARS["window"]["Stop"].Update(disabled=False)
        _VARS["window"]["Pause"].Update(disabled=False)
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
    except Exception as e:
        sg.popup_error(f"Error: {e}")

def close_current_visualizer():
    """Closes the currently running visualizer subprocess."""
    if _VARS["current_visualizer_process"] and _VARS["current_visualizer_process"].poll() is None:
        _VARS["current_visualizer_process"].kill()

# INIT:
fig, ax = plt.subplots()  # create a figure and an axis object
fig_agg = draw_figure(graph.TKCanvas, fig)  # draw the figure on the graph

# MAIN LOOP
while True:
    event, values = _VARS["window"].read(timeout=TIMEOUT)

    # Handling different GUI events
    if event == "Exit" or event == sg.WIN_CLOSED:
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
    if event in ['Amplitude-Frequency-Visualizer', 'Waveform', 'Spectrogram', 'Intensity-vs-Frequency-and-time', 'Phase-Spectrum']:
        close_current_visualizer()
        _VARS["current_visualizer_process"] = subprocess.Popen(['python', f'{event}.py'])
        _VARS["window"].close()
        break
    elif _VARS["audioData"].size != 0:
        try:
            _VARS["window"]["-PROG-"].update(np.amax(_VARS["audioData"]))
            ax.clear()
            N = len(_VARS["audioData"])
            T = 1.0 / RATE
            yf = fft(_VARS["audioData"])
            xf = fftfreq(N, T)[:N//2]
            phase_spectrum = np.angle(yf[:N//2])
            ax.plot(xf, phase_spectrum)
            ax.set_title("Phase Spectrum")
            ax.set_ylabel("Phase [radians]")
            ax.set_xlabel("Frequency [Hz]")
            ax.grid(True)
            fig_agg.draw()
        except Exception as e:
            print("Error during plotting:", e)
            traceback.print_exc()
