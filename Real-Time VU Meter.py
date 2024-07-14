import PySimpleGUI as sg
import pyaudio
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import soundfile as sf

# Global variables
_VARS = {
    "window": False,  # Placeholder for the PySimpleGUI window object
    "stream": False,  # Placeholder for the PyAudio stream object
    "audioData": np.array([]),  # Array to store incoming audio data samples
    "audioBuffer": np.array([]),  # Buffer to accumulate all recorded audio data
}

AppFont = "Helvetica"  # Font style for the GUI
sg.theme("DarkBlue3")  # Setting the PySimpleGUI theme

# GUI layout structure
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

_VARS["window"] = sg.Window("Mic to VU Meter", layout, finalize=True)  # Creating the PySimpleGUI window
graph_vu_meter = _VARS["window"]["graph_vu_meter"]  # Graph element for displaying the VU Meter

# Audio processing constants
CHUNK = 1024  # Samples per chunk for audio processing
RATE = 44100  # Sampling rate in Hz
INTERVAL = 1  # Sampling interval in seconds
TIMEOUT = 10  # Timeout in milliseconds for event handling
NOISE_FLOOR = 1e-6  # Minimum level to avoid log(0) error
pAud = pyaudio.PyAudio()  # PyAudio instance for audio input/output

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
        _VARS["window"]["-PROG-"].update(0)
        _VARS["window"]["Stop"].Update(disabled=True)
        _VARS["window"]["Listen"].Update(disabled=False)

def pause():
    """Pauses the audio stream."""
    if _VARS["stream"].is_active():
        _VARS["stream"].stop_stream()
        _VARS["window"]["Pause"].Update(disabled=True)
        _VARS["window"]["Resume"].Update(disabled=False)

def resume():
    """Resumes the paused audio stream."""
    if not _VARS["stream"].is_active():
        _VARS["stream"].start_stream()
        _VARS["window"]["Pause"].Update(disabled=False)
        _VARS["window"]["Resume"].Update(disabled=True)

def save():
    """Saves the current VU Meter plot and recorded audio to files."""
    folder = sg.popup_get_folder('Please select a directory to save the files')
    if folder:
        fig_vu_meter.savefig(f'{folder}/vu_meter.png')
        sg.popup('Success', f'Image saved as {folder}/vu_meter.png')
        sf.write(f'{folder}/output.wav', _VARS["audioBuffer"], RATE)
        sg.popup('Success', f'Audio saved as {folder}/output.wav')

def callback(in_data, frame_count, time_info, status):
    """Callback function for audio stream processing."""
    _VARS["audioData"] = np.frombuffer(in_data, dtype=np.int16)
    _VARS["audioBuffer"] = np.append(_VARS["audioBuffer"], _VARS["audioData"])
    return (in_data, pyaudio.paContinue)

def listen():
    """Starts the audio stream for listening."""
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

fig_vu_meter, ax_vu_meter = plt.subplots()  # Creating a figure and axis object for VU Meter
fig_vu_meter_agg = draw_figure(graph_vu_meter.TKCanvas, fig_vu_meter)  # Drawing the figure on the GUI canvas

# Main event loop
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

    elif _VARS["audioData"].size != 0:
        # Calculate RMS and convert to dB for VU Meter display
        rms = np.sqrt(np.mean(np.square(_VARS["audioData"])))
        vu_level = 20 * np.log10(max(rms, NOISE_FLOOR)) + 3

        normalized_vu_level = max(vu_level, 0)  # Ensure VU level is non-negative
        
        _VARS["window"]["-PROG-"].update(normalized_vu_level)  # Update the progress bar with VU level
        
        ax_vu_meter.clear()
        ax_vu_meter.barh(['VU Meter'], [normalized_vu_level], color='green')  # Display VU Meter level
        ax_vu_meter.set_xlim(0, 80)
        ax_vu_meter.set_xlabel("Level (dB)")
        ax_vu_meter.grid(True)
        
        fig_vu_meter_agg.draw()  # Redraw the VU Meter plot on the canvas
