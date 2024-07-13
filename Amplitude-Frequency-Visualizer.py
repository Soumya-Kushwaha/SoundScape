from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.graphics.texture import Texture

import pyaudio
import numpy as np
import soundfile as sf
import scipy.fft
import matplotlib.pyplot as plt
import os
import traceback

# VARS CONSTS:
_VARS = {
    "stream": False,
    "audioData": np.array([]),
    "audioBuffer": np.array([]),
    "current_visualizer_process": None,
}

# INIT vars:
CHUNK = 1024
RATE = 44100
INTERVAL = 1
TIMEOUT = 0.1
pAud = pyaudio.PyAudio()

def stop(instance=None):
    if _VARS["stream"]:
        _VARS["stream"].stop_stream()
        _VARS["stream"].close()
        _VARS["stream"] = None
        progress_bar.value = 0
        btn_stop.disabled = True
        btn_listen.disabled = False
        btn_pause.disabled = True
        btn_resume.disabled = True
        btn_save.disabled = True

def pause(instance=None):
    if _VARS["stream"] and _VARS["stream"].is_active():
        _VARS["stream"].stop_stream()
        btn_pause.disabled = True
        btn_resume.disabled = False

def resume(instance=None):
    if _VARS["stream"] and not _VARS["stream"].is_active():
        _VARS["stream"].start_stream()
        btn_pause.disabled = False
        btn_resume.disabled = True

def save(instance=None):
    folder = 'saved_files'
    if not os.path.exists(folder):
        os.makedirs(folder)
    try:
        # Save the figure as an image file
        fig.savefig(f'{folder}/output.png')
        popup_message('Success', f'Image saved as {folder}/output.png')

        # Save the recorded audio data to a file
        sf.write(f'{folder}/output.wav', _VARS["audioBuffer"], RATE)
        popup_message('Success', f'Audio saved as {folder}/output.wav')
    except Exception as e:
        popup_message('Error saving files', str(e))

def callback(in_data, frame_count, time_info, status):
    try:
        _VARS["audioData"] = np.frombuffer(in_data, dtype=np.int16)
        _VARS["audioBuffer"] = np.append(_VARS["audioBuffer"], _VARS["audioData"])
    except Exception as e:
        print("Error in callback:", e)
        traceback.print_exc()
    return (in_data, pyaudio.paContinue)

def listen(instance=None):
    try:
        btn_stop.disabled = False
        btn_listen.disabled = True
        btn_pause.disabled = False
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
        popup_message('Error', f"Error: {e}")

def popup_message(title, message):
    popup = Popup(title=title, content=Label(text=message), size_hint=(0.8, 0.8))
    popup.open()

class MicVisualizerApp(App):
    def build(self):
        global progress_bar, btn_listen, btn_pause, btn_resume, btn_stop, btn_save, fig, ax, canvas_img

        tab_panel = TabbedPanel(do_default_tab=False)

        # Listening tab
        listening_tab = TabbedPanelItem(text='Listening')
        listening_layout = BoxLayout(orientation='vertical')

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

        listening_layout.add_widget(Label(text='Progress:', size_hint_y=None, height=50))
        listening_layout.add_widget(progress_bar)
        listening_layout.add_widget(button_layout)

        listening_tab.add_widget(listening_layout)
        tab_panel.add_widget(listening_tab)

        # Visualization tab
        visualization_tab = TabbedPanelItem(text='Visualization')
        visualization_layout = BoxLayout(orientation='vertical')

        fig, ax = plt.subplots()
        canvas_img = Image()
        visualization_layout.add_widget(canvas_img)

        visualization_tab.add_widget(visualization_layout)
        tab_panel.add_widget(visualization_tab)

        # Settings tab
        settings_tab = TabbedPanelItem(text='Settings')
        settings_layout = BoxLayout(orientation='vertical')

        rate_label = Label(text='Sample Rate:')
        self.rate_input = TextInput(text=str(RATE), multiline=False)
        chunk_label = Label(text='Chunk Size:')
        self.chunk_input = TextInput(text=str(CHUNK), multiline=False)

        apply_button = Button(text='Apply', on_press=self.apply_settings)
        settings_layout.add_widget(rate_label)
        settings_layout.add_widget(self.rate_input)
        settings_layout.add_widget(chunk_label)
        settings_layout.add_widget(self.chunk_input)
        settings_layout.add_widget(apply_button)

        settings_tab.add_widget(settings_layout)
        tab_panel.add_widget(settings_tab)

        Clock.schedule_interval(self.update_plot, TIMEOUT)

        return tab_panel

    def apply_settings(self, instance):
        global RATE, CHUNK
        try:
            RATE = int(self.rate_input.text)
            CHUNK = int(self.chunk_input.text)
            popup_message('Settings Applied', 'Sample Rate and Chunk Size updated.')
        except ValueError:
            popup_message('Invalid Input', 'Please enter valid integer values.')

    def update_plot(self, dt):
        if _VARS["audioData"].size != 0:
            progress_bar.value = np.amax(_VARS["audioData"])
            yf = scipy.fft.fft(_VARS["audioData"])
            xf = np.linspace(0.0, RATE / 2, CHUNK // 2)
            ax.clear()
            ax.plot(
                xf, 2.0 / CHUNK * np.abs(yf[: CHUNK // 2]), label='Frequency Spectrum'
            )
            ax.set_title("Frequency Spectrum")
            ax.set_ylabel("Amplitude")
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
