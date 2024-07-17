from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.image import Image
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.textinput import TextInput

import pyaudio
import numpy as np
import soundfile as sf
import scipy.fft
import matplotlib.pyplot as plt
import os

# Dictionary to hold global variables
_VARS = {
    "stream": None,  # Audio stream
    "audioData": np.array([]),  # Current audio data
    "audioBuffer": np.array([]),  # Buffer to store all audio data
    "current_visualizer_process": None,  # Placeholder for visualizer process
}

# Constants for audio processing
CHUNK = 1024  # Number of audio samples per frame
RATE = 44100  # Sampling rate (samples per second)
pAud = pyaudio.PyAudio()  # Initialize PyAudio

# Function to stop audio streaming
def stop(instance):
    if _VARS["stream"]:
        _VARS["stream"].stop_stream()  # Stop the stream
        _VARS["stream"].close()  # Close the stream
        _VARS["stream"] = None
        progress_bar.value = 0  # Reset the progress bar
        btn_listen.disabled = False
        btn_pause.disabled = True
        btn_resume.disabled = True
        btn_stop.disabled = True
        btn_save.disabled = True

# Function to pause audio streaming
def pause(instance):
    if _VARS["stream"] and _VARS["stream"].is_active():
        _VARS["stream"].stop_stream()  # Stop the stream
        btn_pause.disabled = True
        btn_resume.disabled = False

# Function to resume audio streaming
def resume(instance):
    if _VARS["stream"] and not _VARS["stream"].is_active():
        _VARS["stream"].start_stream()  # Start the stream
        btn_pause.disabled = False
        btn_resume.disabled = True

# Function to save audio and plot data
def save(instance):
    folder = 'saved_files'
    if not os.path.exists(folder):
        os.makedirs(folder)  # Create folder if it doesn't exist
    try:
        # Save the plot as an image file
        fig.savefig(f'{folder}/output.png')
        popup_message('Success', f'Image saved as {folder}/output.png')

        # Save the audio data as a WAV file
        sf.write(f'{folder}/output.wav', _VARS["audioBuffer"], RATE)
        popup_message('Success', f'Audio saved as {folder}/output.wav')
    except Exception as e:
        popup_message('Error saving files', str(e))

# Callback function to handle audio stream input
def callback(in_data, frame_count, time_info, status):
    _VARS["audioData"] = np.frombuffer(in_data, dtype=np.int16)  # Convert audio data to NumPy array
    _VARS["audioBuffer"] = np.append(_VARS["audioBuffer"], _VARS["audioData"])  # Append data to buffer
    return (in_data, pyaudio.paContinue)

# Function to start listening to audio
def listen(instance):
    try:
        btn_listen.disabled = True
        btn_pause.disabled = False
        btn_stop.disabled = False
        _VARS["stream"] = pAud.open(
            format=pyaudio.paInt16,  # Audio format
            channels=1,  # Number of audio channels
            rate=RATE,  # Sampling rate
            input=True,  # Set stream as input
            frames_per_buffer=CHUNK,  # Number of samples per frame
            stream_callback=callback,  # Set callback function
        )
        _VARS["stream"].start_stream()  # Start the audio stream
    except Exception as e:
        popup_message('Error starting the stream', str(e))

# Function to close the current visualizer process
def close_current_visualizer():
    if _VARS["current_visualizer_process"] and _VARS["current_visualizer_process"].poll() is None:
        _VARS["current_visualizer_process"].kill()  # Terminate the visualizer process

# Function to display a popup message
def popup_message(title, message):
    popup = Popup(title=title, content=Label(text=message), size_hint=(0.8, 0.8))
    popup.open()

# Main application class
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

        Clock.schedule_interval(self.update_plot, 0.1)  # Schedule plot update

        return tab_panel

    def apply_settings(self, instance):
        global RATE, CHUNK
        try:
            RATE = int(self.rate_input.text)  # Update sampling rate
            CHUNK = int(self.chunk_input.text)  # Update chunk size
            popup_message('Settings Applied', 'Sample Rate and Chunk Size updated.')
        except ValueError:
            popup_message('Invalid Input', 'Please enter valid integer values.')

    def update_plot(self, dt):
        if _VARS["audioData"].size != 0:
            progress_bar.value = np.amax(_VARS["audioData"])  # Update progress bar
            yf = scipy.fft.fft(_VARS["audioData"])  # Perform FFT on audio data
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
        fig.canvas.draw()  # Draw the canvas
        width, height = fig.canvas.get_width_height()
        buf = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
        buf = buf.reshape(height, width, 3)

        texture = Texture.create(size=(width, height))
        texture.blit_buffer(buf.tostring(), colorfmt='rgb', bufferfmt='ubyte')
        texture.flip_vertical()

        canvas_img.texture = texture

    def on_stop(self):
        stop(None)  # Stop audio streaming
        if _VARS["current_visualizer_process"]:
            close_current_visualizer()
        pAud.terminate()  # Terminate PyAudio

if __name__ == '__main__':
    app = MicVisualizerApp()
    app.run()
