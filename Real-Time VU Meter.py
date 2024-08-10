import PySimpleGUI as sg
import pyaudio
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import soundfile as sf
import scipy.fftpack
import librosa.display
import requests
import io
from pydub import AudioSegment
import soundfile as sf
from scipy.signal import convolve

# Constants and Variables
CHUNK = 1024
RATE = 44100
INTERVAL = 1
TIMEOUT = 10
NOISE_FLOOR = 1e-6
_VARS = {"window": False, "stream": False, "audioData": np.array([]), "audioBuffer": np.array([]), "mode": "VU", "channels": 1}

AppFont = "Helvetica"
sg.theme("DarkBlue3")

# Layout
layout = [
    [sg.Graph(canvas_size=(600, 300), graph_bottom_left=(-2, -2), graph_top_right=(102, 102), background_color="#809AB6", key="graph_audio", tooltip="Audio Visualization")],
    [sg.Text("Progress:", text_color='white', font=('Helvetica', 15, 'bold')), sg.ProgressBar(100, orientation="h", size=(20, 20), key="-PROG-")],
    [sg.Button("Listen", font=AppFont, tooltip="Start listening"), sg.Button("Pause", font=AppFont, disabled=True, tooltip="Pause listening"), sg.Button("Resume", font=AppFont, disabled=True, tooltip="Resume listening"), sg.Button("Stop", font=AppFont, disabled=True, tooltip="Stop listening"), sg.Button("Save", font=AppFont, disabled=True, tooltip="Save the plot"), sg.Button("Exit", font=AppFont, tooltip="Exit the application")],
    [sg.Combo(["VU", "Waveform", "Spectrum", "Spectrogram"], default_value="VU", key="view_mode", tooltip="Select visualization mode"), sg.Checkbox("Echo", key="echo"), sg.Checkbox("Reverb", key="reverb"), sg.Checkbox("Stereo", key="stereo")],
    [sg.Text("Stream URL:", size=(10, 1)), sg.InputText(key="stream_url", size=(40, 1)), sg.Button("Stream", font=AppFont, tooltip="Stream audio from URL")]
]

_VARS["window"] = sg.Window("Audio Visualizer", layout, finalize=True)
graph_audio = _VARS["window"]["graph_audio"]

# PyAudio Instance
pAud = pyaudio.PyAudio()

# Helper Functions
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
        _VARS["window"]["Pause"].Update(disabled=True)
        _VARS["window"]["Resume"].Update(disabled=True)

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
        fig_audio.savefig(f'{folder}/audio_visualization.png')
        sg.popup('Success', f'Image saved as {folder}/audio_visualization.png')
        sf.write(f'{folder}/output.wav', _VARS["audioBuffer"], RATE)
        sg.popup('Success', f'Audio saved as {folder}/output.wav')

def callback(in_data, frame_count, time_info, status):
    audio_data = np.frombuffer(in_data, dtype=np.int16)
    if _VARS["channels"] == 2:
        audio_data = audio_data.reshape(-1, 2)
    if _VARS["audioBuffer"].size == 0:
        _VARS["audioBuffer"] = audio_data
    else:
        _VARS["audioBuffer"] = np.vstack((_VARS["audioBuffer"], audio_data))
    _VARS["audioData"] = audio_data
    return (in_data, pyaudio.paContinue)

def listen():
    _VARS["window"]["Stop"].Update(disabled=False)
    _VARS["window"]["Listen"].Update(disabled=True)
    _VARS["window"]["Pause"].Update(disabled=False)
    _VARS["window"]["Save"].Update(disabled=False)
    _VARS["channels"] = 2 if _VARS["window"]["stereo"].get() else 1
    _VARS["stream"] = pAud.open(format=pyaudio.paInt16, channels=_VARS["channels"], rate=RATE, input=True, frames_per_buffer=CHUNK, stream_callback=callback)
    _VARS["stream"].start_stream()

def apply_effects(data):
    if _VARS["window"]["echo"].get():
        data = np.concatenate([data, data])
    if _VARS["window"]["reverb"].get():
        reverb_kernel = np.random.normal(size=5000)
        data = convolve(data, reverb_kernel, mode='full')[:len(data)]
    return data

def update_vu():
    rms = np.sqrt(np.mean(np.square(_VARS["audioData"])))
    vu_level = 20 * np.log10(max(rms, NOISE_FLOOR)) + 3
    normalized_vu_level = max(vu_level, 0)
    _VARS["window"]["-PROG-"].update(normalized_vu_level)
    ax_audio.clear()
    ax_audio.barh(['VU Meter'], [normalized_vu_level], color='green')
    ax_audio.set_xlim(0, 80)
    ax_audio.set_xlabel("Level (dB)")
    ax_audio.grid(True)
    fig_audio_agg.draw()

def update_waveform():
    ax_audio.clear()
    ax_audio.plot(_VARS["audioData"])
    ax_audio.set_xlabel("Samples")
    ax_audio.set_ylabel("Amplitude")
    fig_audio_agg.draw()

def update_spectrum():
    N = len(_VARS["audioData"])
    T = 1.0 / RATE
    yf = scipy.fftpack.fft(_VARS["audioData"])
    xf = np.linspace(0.0, 1.0/(2.0*T), N//2)
    ax_audio.clear()
    ax_audio.plot(xf, 2.0/N * np.abs(yf[:N//2]))
    ax_audio.set_xlabel('Frequency (Hz)')
    ax_audio.set_ylabel('Amplitude')
    ax_audio.grid(True)
    fig_audio_agg.draw()

def update_spectrogram():
    ax_audio.clear()
    ax_audio.specgram(_VARS["audioData"], Fs=RATE)
    ax_audio.set_xlabel('Time (s)')
    ax_audio.set_ylabel('Frequency (Hz)')
    fig_audio_agg.draw()

def switch_view():
    mode = _VARS["window"]["view_mode"].get()
    if mode == "VU":
        update_vu()
    elif mode == "Waveform":
        update_waveform()
    elif mode == "Spectrum":
        update_spectrum()
    elif mode == "Spectrogram":
        update_spectrogram()

def stream_audio(url):
    response = requests.get(url)
    audio = AudioSegment.from_file(io.BytesIO(response.content))
    data = np.array(audio.get_array_of_samples())
    _VARS["audioBuffer"] = data
    _VARS["audioData"] = data
    while True:
        switch_view()
        if _VARS["window"].read(timeout=TIMEOUT)[0] == "Exit":
            break

# Main Loop
fig_audio, ax_audio = plt.subplots()
fig_audio_agg = draw_figure(graph_audio.TKCanvas, fig_audio)

while True:
    event, values = _VARS["window"].read(timeout=TIMEOUT)
    if event == "Exit" or event == sg.WIN_CLOSED:
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
    if event == "Stream":
        stream_audio(values["stream_url"])
    if event == "view_mode":
        switch_view()
    if _VARS["audioData"].size != 0:
        _VARS["audioData"] = apply_effects(_VARS["audioData"])
        switch_view()
