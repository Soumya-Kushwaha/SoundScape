import pyaudio
import numpy as np
import scipy.signal
import matplotlib.pyplot as plt
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.graphics.texture import Texture
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.uix.filechooser import FileChooserIconView
import io

# Global Variables
_VARS = {"stream": None, "audioData": np.array([])}
CHUNK = 1024
RATE = 44100

# Initialize PyAudio
try:
    pAud = pyaudio.PyAudio()
    pAud.get_device_info_by_index(0)
except pyaudio.PyAudioError as e:
    print(f"Error initializing PyAudio: {e}")
    pAud = None

def callback(in_data, frame_count, time_info, status):
    _VARS["audioData"] = np.frombuffer(in_data, dtype=np.int16)
    return (in_data, pyaudio.paContinue)

def listen():
    if pAud:
        try:
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
            print(f"Error starting audio stream: {e}")
            _VARS["stream"] = None
    else:
        print("PyAudio is not initialized.")

def stop():
    if _VARS["stream"]:
        try:
            _VARS["stream"].stop_stream()
            _VARS["stream"].close()
        except Exception as e:
            print(f"Error stopping audio stream: {e}")
        finally:
            _VARS["stream"] = None

class SpectrogramApp(App):
    def build(self):
        self.title = "Mic to Spectrogram Plot + Max Level"
        self.layout = BoxLayout(orientation='vertical')

        self.image = Image()
        self.layout.add_widget(self.image)

        self.progress = ProgressBar(max=4000)
        self.layout.add_widget(self.progress)

        self.button_layout = BoxLayout(size_hint_y=0.2)
        
        self.listen_button = Button(text="Listen")
        self.listen_button.bind(on_press=self.on_listen)
        self.button_layout.add_widget(self.listen_button)

        self.stop_button = Button(text="Stop", disabled=True)
        self.stop_button.bind(on_press=self.on_stop)
        self.button_layout.add_widget(self.stop_button)

        self.save_button = Button(text="Save", disabled=True)
        self.save_button.bind(on_press=self.on_save)
        self.button_layout.add_widget(self.save_button)

        self.exit_button = Button(text="Exit")
        self.exit_button.bind(on_press=self.on_exit)
        self.button_layout.add_widget(self.exit_button)
        
        self.layout.add_widget(self.button_layout)
        self.event = None

        return self.layout

    def on_listen(self, instance):
        listen()
        if _VARS["stream"]:
            self.listen_button.disabled = True
            self.stop_button.disabled = False
            self.save_button.disabled = False
            self.event = Clock.schedule_interval(self.update, 0.1)
        else:
            print("Failed to start listening.")

    def on_stop(self, instance):
        stop()
        self.listen_button.disabled = False
        self.stop_button.disabled = True
        self.save_button.disabled = True
        if self.event:
            self.event.cancel()
            self.event = None

    def on_save(self, instance):
        content = BoxLayout(orientation='vertical')
        filechooser = FileChooserIconView()
        content.add_widget(filechooser)
        save_button = Button(text="Save", size_hint_y=0.2)
        content.add_widget(save_button)
        popup = Popup(title="Save as", content=content, size_hint=(0.9, 0.9))
        
        def save(instance):
            if filechooser.selection:
                file_path = filechooser.selection[0]
                self.save_figure(file_path)
                popup.dismiss()
        
        save_button.bind(on_press=save)
        popup.open()

    def on_exit(self, instance):
        stop()
        if pAud:
            pAud.terminate()
        App.get_running_app().stop()

    def save_figure(self, file_path):
        fig, ax = plt.subplots()
        f, t, Sxx = scipy.signal.spectrogram(_VARS["audioData"], fs=RATE)
        ax.pcolormesh(t, f, Sxx, shading="gouraud")
        ax.set_ylabel("Frequency [Hz]")
        ax.set_xlabel("Time [sec]")
        plt.savefig(file_path)
        plt.close(fig)

    def update(self, dt):
        if _VARS["audioData"].size != 0:
            self.progress.value = np.amax(_VARS["audioData"])
            f, t, Sxx = scipy.signal.spectrogram(_VARS["audioData"], fs=RATE)
            fig, ax = plt.subplots()
            ax.pcolormesh(t, f, Sxx, shading="gouraud")
            ax.set_ylabel("Frequency [Hz]")
            ax.set_xlabel("Time [sec]")
            buf = io.BytesIO()
            fig.savefig(buf, format='png')
            buf.seek(0)
            img = plt.imread(buf, format='png')
            buf.close()
            texture = Texture.create(size=(img.shape[1], img.shape[0]), colorfmt='rgb')
            texture.blit_buffer(img.tobytes(), colorfmt='rgb', bufferfmt='ubyte')
            self.image.texture = texture
            plt.close(fig)

if __name__ == "__main__":
    SpectrogramApp().run()
