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

import pyaudio  # Import PyAudio for audio input
import numpy as np  # Import NumPy for numerical operations
import soundfile as sf  # Import SoundFile for audio file handling
import scipy.fft  # Import SciPy for FFT operations
import matplotlib.pyplot as plt  # Import Matplotlib for plotting
import os  # Import OS for file system operations
import traceback  # Import traceback for error handling

# VARS CONSTS:
_VARS = {
    "stream": False,
    "audioData": np.array([]),
    "audioBuffer": np.array([]),
    "current_visualizer_process": None,
}

# INIT vars:
CHUNK = 1024  # Number of audio frames per buffer
RATE = 44100  # Sampling rate (samples per second)
INTERVAL = 1  # Interval for updates
TIMEOUT = 0.1  # Timeout for updates
pAud = pyaudio.PyAudio()  # Initialize PyAudio

def stop(instance=None):
    if _VARS["stream"]:
        _VARS["stream"].stop_stream()  # Stop the audio stream
        _VARS["stream"].close()  # Close the audio stream
        _VARS["stream"] = None  # Reset the stream variable
        progress_bar.value = 0  # Reset the progress bar
        btn_stop.disabled = True  # Disable the stop button
        btn_listen.disabled = False  # Enable the listen button
        btn_pause.disabled = True  # Disable the pause button
        btn_resume.disabled = True  # Disable the resume button
        btn_save.disabled = True  # Disable the save button

def pause(instance=None):
    if _VARS["stream"] and _VARS["stream"].is_active():
        _VARS["stream"].stop_stream()  # Stop the audio stream
        btn_pause.disabled = True  # Disable the pause button
        btn_resume.disabled = False  # Enable the resume button

def resume(instance=None):
    if _VARS["stream"] and not _VARS["stream"].is_active():
        _VARS["stream"].start_stream()  # Start the audio stream
        btn_pause.disabled = False  # Enable the pause button
        btn_resume.disabled = True  # Disable the resume button

def save(instance=None):
    folder = 'saved_files'  # Define the folder to save files
    if not os.path.exists(folder):
        os.makedirs(folder)  # Create the folder if it doesn't exist
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
        _VARS["audioData"] = np.frombuffer(in_data, dtype=np.int16)  # Convert audio data to NumPy array
        _VARS["audioBuffer"] = np.append(_VARS["audioBuffer"], _VARS["audioData"])  # Append audio data to buffer
    except Exception as e:
        print("Error in callback:", e)
        traceback.print_exc()
    return (in_data, pyaudio.paContinue)  # Continue the audio stream

def listen(instance=None):
    try:
        btn_stop.disabled = False  # Enable the stop button
        btn_listen.disabled = True  # Disable the listen button
        btn_pause.disabled = False  # Enable the pause button
        _VARS["stream"] = pAud.open(
            format=pyaudio.paInt16,  # 16-bit audio format
            channels=1,  # Mono audio
            rate=RATE,  # Sampling rate
            input=True,  # Input stream
            frames_per_buffer=CHUNK,  # Buffer size
            stream_callback=callback,  # Callback function for audio data
        )
        _VARS["stream"].start_stream()  # Start the audio stream
    except Exception as e:
        popup_message('Error', f"Error: {e}")

def popup_message(title, message):
    popup = Popup(title=title, content=Label(text=message), size_hint=(0.8, 0.8))  # Create a popup window
    popup.open()  # Open the popup window

class MicVisualizerApp(App):
    def build(self):
        global progress_bar, btn_listen, btn_pause, btn_resume, btn_stop, btn_save, fig, ax, canvas_img

        tab_panel = TabbedPanel(do_default_tab=False)  # Create a tab panel

        # Listening tab
        listening_tab = TabbedPanelItem(text='Listening')
        listening_layout = BoxLayout(orientation='vertical')

        btn_listen = Button(text='Listen', on_press=listen)  # Listen button
        btn_pause = Button(text='Pause', on_press=pause, disabled=True)  # Pause button
        btn_resume = Button(text='Resume', on_press=resume, disabled=True)  # Resume button
        btn_stop = Button(text='Stop', on_press=stop, disabled=True)  # Stop button
        btn_save = Button(text='Save', on_press=save, disabled=True)  # Save button
        btn_exit = Button(text='Exit', on_press=self.stop)  # Exit button

        progress_bar = ProgressBar(max=4000)  # Progress bar

        button_layout = BoxLayout(size_hint_y=None, height=50)  # Button layout
        button_layout.add_widget(btn_listen)
        button_layout.add_widget(btn_pause)
        button_layout.add_widget(btn_resume)
        button_layout.add_widget(btn_stop)
        button_layout.add_widget(btn_save)
        button_layout.add_widget(btn_exit)

        listening_layout.add_widget(Label(text='Progress:', size_hint_y=None, height=50))  # Progress label
        listening_layout.add_widget(progress_bar)  # Add progress bar to layout
        listening_layout.add_widget(button_layout)  # Add button layout to listening layout

        listening_tab.add_widget(listening_layout)  # Add listening layout to tab
        tab_panel.add_widget(listening_tab)  # Add listening tab to tab panel

        # Visualization tab
        visualization_tab = TabbedPanelItem(text='Visualization')
        visualization_layout = BoxLayout(orientation='vertical')

        fig, ax = plt.subplots()  # Create a Matplotlib figure and axes
        canvas_img = Image()  # Image widget for displaying the plot
        visualization_layout.add_widget(canvas_img)  # Add image widget to layout

        visualization_tab.add_widget(visualization_layout)  # Add visualization layout to tab
        tab_panel.add_widget(visualization_tab)  # Add visualization tab to tab panel

        # Settings tab
        settings_tab = TabbedPanelItem(text='Settings')
        settings_layout = BoxLayout(orientation='vertical')

        rate_label = Label(text='Sample Rate:')  # Sample rate label
        self.rate_input = TextInput(text=str(RATE), multiline=False)  # Sample rate input
        chunk_label = Label(text='Chunk Size:')  # Chunk size label
        self.chunk_input = TextInput(text=str(CHUNK), multiline=False)  # Chunk size input

        apply_button = Button(text='Apply', on_press=self.apply_settings)  # Apply button
        settings_layout.add_widget(rate_label)  # Add sample rate label to layout
        settings_layout.add_widget(self.rate_input)  # Add sample rate input to layout
        settings_layout.add_widget(chunk_label)  # Add chunk size label to layout
        settings_layout.add_widget(self.chunk_input)  # Add chunk size input to layout
        settings_layout.add_widget(apply_button)  # Add apply button to layout

        settings_tab.add_widget(settings_layout)  # Add settings layout to tab
        tab_panel.add_widget(settings_tab)  # Add settings tab to tab panel

        Clock.schedule_interval(self.update_plot, TIMEOUT)  # Schedule the update plot function

        return tab_panel  # Return the tab panel

    def apply_settings(self, instance):
        global RATE, CHUNK
        try:
            RATE = int(self.rate_input.text)  # Update the sample rate
            CHUNK = int(self.chunk_input.text)  # Update the chunk size
            popup_message('Settings Applied', 'Sample Rate and Chunk Size updated.')
        except ValueError:
            popup_message('Invalid Input', 'Please enter valid integer values.')

    def update_plot(self, dt):
        if _VARS["audioData"].size != 0:
            progress_bar.value = np.amax(_VARS["audioData"])  # Update the progress bar value
            yf = scipy.fft.fft(_VARS["audioData"])  # Perform FFT on the audio data
            xf = np.linspace(0.0, RATE / 2
