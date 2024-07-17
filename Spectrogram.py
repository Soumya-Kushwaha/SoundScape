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
    """Callback function for audio stream processing."""
    _VARS["audioData"] = np.frombuffer(in_data, dtype=np.int16)
    return (in_data, pyaudio.paContinue)

def listen():
    """Starts the audio stream for listening."""
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
    """Stops the audio stream."""
    if _VARS["stream"]:
        try:
            _VARS["stream"].stop_stream()
            _VARS["stream"].close()
        except Exception as e:
            print(f"Error stopping audio stream: {e}")
        finally:
            _VARS["stream"] = None

class SpectrogramApp(App):
    """Main Kivy application class for Spectrogram visualization."""

    def build(self):
        """Builds the Kivy application UI."""
        self.title = "Mic to Spectrogram Plot + Max Level"
        self.layout = BoxLayout(orientation='vertical')

        self.image = Image()  # Placeholder for displaying the spectrogram image
        self.layout.add_widget(self.image)

        self.progress = ProgressBar(max=4000)  # Progress bar for displaying max audio level
        self.layout.add_widget(self.progress)

        self.button_layout = BoxLayout(size_hint_y=0.2)
        
        self.listen_button = Button(text="Listen")  # Button to start listening to audio
        self.listen_button.bind(on_press=self.on_listen)
        self.button_layout.add_widget(self.listen_button)

        self.stop_button = Button(text="Stop", disabled=True)  # Button to stop audio stream
        self.stop_button.bind(on_press=self.on_stop)
        self.button_layout.add_widget(self.stop_button)

        self.save_button = Button(text="Save", disabled=True)  # Button to save spectrogram image
        self.save_button.bind(on_press=self.on_save)
        self.button_layout.add_widget(self.save_button)

        self.exit_button = Button(text="Exit")  # Button to exit the application
        self.exit_button.bind(on_press=self.on_exit)
        self.button_layout.add_widget(self.exit_button)
        
        self.layout.add_widget(self.button_layout)
        self.event = None  # Placeholder for scheduled update event

        return self.layout

    def on_listen(self, instance):
        """Event handler for starting the audio stream."""
        listen()
        if _VARS["stream"]:
            self.listen_button.disabled = True
            self.stop_button.disabled = False
            self.save_button.disabled = False
            self.event = Clock.schedule_interval(self.update, 0.1)  # Schedule periodic update
        else:
            print("Failed to start listening.")

    def on_stop(self, instance):
        """Event handler for stopping the audio stream."""
        stop()
        self.listen_button.disabled = False
        self.stop_button.disabled = True
        self.save_button.disabled = True
        if self.event:
            self.event.cancel()  # Cancel periodic update event
            self.event = None

    def on_save(self, instance):
        """Event handler for saving the spectrogram image."""
        content = BoxLayout(orientation='vertical')
        filechooser = FileChooserIconView()
        content.add_widget(filechooser)
        save_button = Button(text="Save", size_hint_y=0.2)
        content.add_widget(save_button)
        popup = Popup(title="Save as", content=content, size_hint=(0.9, 0.9))
        
        def save(instance):
            """Inner function for handling save button press."""
            if filechooser.selection:
                file_path = filechooser.selection[0]
                self.save_figure(file_path)  # Save the spectrogram to selected file path
                popup.dismiss()
        
        save_button.bind(on_press=save)
        popup.open()

    def on_exit(self, instance):
        """Event handler for exiting the application."""
        stop()
        if pAud:
            pAud.terminate()  # Terminate PyAudio instance
        App.get_running_app().stop()  # Stop the Kivy application

    def save_figure(self, file_path):
        """Generates and saves the spectrogram plot to a file."""
        fig, ax = plt.subplots()
        f, t, Sxx = scipy.signal.spectrogram(_VARS["audioData"], fs=RATE)
        ax.pcolormesh(t, f, Sxx, shading="gouraud")
        ax.set_ylabel("Frequency [Hz]")
        ax.set_xlabel("Time [sec]")
        plt.savefig(file_path)  # Save the spectrogram plot to the specified file path
        plt.close(fig)

    def update(self, dt):
        """Periodically updates the spectrogram display."""
        if _VARS["audioData"].size != 0:
            self.progress.value = np.amax(_VARS["audioData"])  # Update progress bar with max audio level
            f, t, Sxx = scipy.signal.spectrogram(_VARS["audioData"], fs=RATE)
            fig, ax = plt.subplots()
            ax.pcolormesh(t, f, Sxx, shading="gouraud")
            ax.set_ylabel("Frequency [Hz]")
            ax.set_xlabel("Time [sec]")
            buf = io.BytesIO()
            fig.savefig(buf, format='png')  # Save figure to a buffer as PNG
            buf.seek(0)
            img = plt.imread(buf, format='png')  # Read image from buffer
            buf.close()
            texture = Texture.create(size=(img.shape[1], img.shape[0]), colorfmt='rgb')
            texture.blit_buffer(img.tobytes(), colorfmt='rgb', bufferfmt='ubyte')  # Create texture from image buffer
            self.image.texture = texture  # Update the image widget with the new texture
            plt.close(fig)  # Close the figure to release resources

if __name__ == "__main__":
    SpectrogramApp().run()  # Run the Kivy application
