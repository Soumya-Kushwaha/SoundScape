from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.image import Image

import pyaudio
import numpy as np
import soundfile as sf
import scipy.fft
import matplotlib.pyplot as plt
import subprocess
import os

# vars:
_VARS = {
    "stream": None,
    "audioData": np.array([]),
    "audioBuffer": np.array([]),
    "current_visualizer_process": None,
}

# INIT vars:
CHUNK = 1024
RATE = 44100
pAud = pyaudio.PyAudio()

# FUNCTIONS:
def stop(instance):
    if _VARS["stream"]:
        _VARS["stream"].stop_stream()
        _VARS["stream"].close()
        _VARS["stream"] = None
        progress_bar.value = 0
        btn_listen.disabled = False
        btn_pause.disabled = True
        btn_resume.disabled = True
        btn_stop.disabled = True
        btn_save.disabled = True

def pause(instance):
    if _VARS["stream"] and _VARS["stream"].is_active():
        _VARS["stream"].stop_stream()
        btn_pause.disabled = True
        btn_resume.disabled = False

def resume(instance):
    if _VARS["stream"] and not _VARS["stream"].is_active():
        _VARS["stream"].start_stream()
        btn_pause.disabled = False
        btn_resume.disabled = True

def save(instance):
    folder = 'saved_files'
    if not os.path.exists(folder):
        os.makedirs(folder)
    try:
        # Save the plot as an image file
        fig.savefig(f'{folder}/output.png')
        popup_message('Success', f'Image saved as {folder}/output.png')

        # Save the audio data as a WAV file
        sf.write(f'{folder}/output.wav', _VARS["audioBuffer"], RATE)
        popup_message('Success', f'Audio saved as {folder}/output.wav')
    except Exception as e:
        popup_message('Error saving files', str(e))

def callback(in_data, frame_count, time_info, status):
    _VARS["audioData"] = np.frombuffer(in_data, dtype=np.int16)
    _VARS["audioBuffer"] = np.append(_VARS["audioBuffer"], _VARS["audioData"])
    return (in_data, pyaudio.paContinue)

def listen(instance):
    try:
        btn_listen.disabled = True
        btn_pause.disabled = False
        btn_stop.disabled = False
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
        popup_message('Error starting the stream', str(e))

def close_current_visualizer():
    if _VARS["current_visualizer_process"] and _VARS["current_visualizer_process"].poll() is None:
        _VARS["current_visualizer_process"].kill()

def popup_message(title, message):
    popup = Popup(title=title, content=Label(text=message), size_hint=(0.8, 0.8))
    popup.open()

class MicVisualizerApp(App):
    def build(self):
        global progress_bar, btn_listen, btn_pause, btn_resume, btn_stop, btn_save, fig, ax, canvas_img

        layout = BoxLayout(orientation='vertical')

        btn_listen = Button(text='Listen', on_press=listen)
        btn_pause = Button(text='Pause', on_press=pause, disabled=True)
        btn_resume = Button(text='Resume', on_press=resume, disabled=True)
        btn_stop = Button(text='Stop', on_press=stop, disabled=True)
        btn_save = Button(text='Save', on_press=save, disabled=True)
        btn_exit = Button(text='Exit', on_press=self.stop)

        progress_bar = ProgressBar(max=4000)

        button_layout = BoxLayout(size_hint_y=None, height=50)
        button_layout.add_widget(btn_listen)
        button_layout.add_widget(btn_pause)
        button_layout.add_widget(btn_resume)
        button_layout.add_widget(btn_stop)
        button_layout.add_widget(btn_save)
        button_layout.add_widget(btn_exit)

        layout.add_widget(Label(text='Progress:', size_hint_y=None, height=50))
        layout.add_widget(progress_bar)
        layout.add_widget(button_layout)

        fig, ax = plt.subplots()
        canvas_img = Image()
        layout.add_widget(canvas_img)

        Clock.schedule_interval(self.update_plot, 0.1)

        return layout

    def update_plot(self, dt):
        if _VARS["audioData"].size != 0:
            progress_bar.value = np.amax(_VARS["audioData"])
            yf = scipy.fft.fft(_VARS["audioData"])
            xf = np.linspace(0.0, RATE / 2, CHUNK // 2)
            ax.clear()
            energy = (2.0 / CHUNK * np.abs(yf[: CHUNK // 2]))**2  # Compute energy
            ax.plot(xf, energy, label='Energy Spectrum')
            ax.set_ylabel("Energy")
            ax.set_xlabel("Frequency [Hz]")
            ax.grid(True)
            ax.legend()
            
            self.update_canvas()

    def update_canvas(self):
        fig.canvas.draw()
        width, height = fig.canvas.get_width_height()
        buf = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
        buf = buf.reshape(height, width, 3)

        texture = Texture.create(size=(width, height))
        texture.blit_buffer(buf.tostring(), colorfmt='rgb', bufferfmt='ubyte')
        texture.flip_vertical()

        canvas_img.texture = texture

    def on_stop(self):
        stop(None)
        if _VARS["current_visualizer_process"]:
            close_current_visualizer()
        pAud.terminate()

if __name__ == '__main__':
    app = MicVisualizerApp()
    app.run()
