import numpy as np
import pyaudio
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.graphics import Line, Color

# Constants
CHUNK = 1024
RATE = 44100

class WaveformWidget(Widget):
    def __init__(self, **kwargs):
        super(WaveformWidget, self).__init__(**kwargs)
        self.points = []  # Initialize points list for drawing waveform

    def update(self, data):
        """Update method to redraw waveform based on new audio data."""
        self.canvas.clear()  # Clear previous drawing on the canvas
        with self.canvas:
            Color(1, 0, 0)  # Set drawing color to red
            self.points = []  # Reset points list
            for i in range(len(data)):
                # Calculate points based on audio data and widget dimensions
                self.points.append((self.width * i / len(data), self.height / 2 + data[i] / 32768 * self.height / 2))
            Line(points=self.points)  # Draw line using calculated points

class AudioVisualizerApp(App):
    
    def build(self):
        # Initialize PyAudio
        self.pAud = pyaudio.PyAudio()
        try:
            self.pAud.get_device_info_by_index(0)
        except pyaudio.PyAudioError as e:
            print(f"Error initializing PyAudio: {e}")
            self.pAud = None
        
        # Main layout
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Waveform widget
        self.waveform = WaveformWidget()
        
        # Buttons
        self.listen_button = Button(text='Listen', size_hint=(None, None), size=(100, 50))
        self.listen_button.bind(on_press=self.listen)  # Bind listen method to button press
        
        self.stop_button = Button(text='Stop', size_hint=(None, None), size=(100, 50), disabled=True)
        self.stop_button.bind(on_press=self.stop)  # Bind stop method to button press
        
        self.exit_button = Button(text='Exit', size_hint=(None, None), size=(100, 50))
        self.exit_button.bind(on_press=self.close_app)  # Bind close_app method to button press
        
        self.button_layout = BoxLayout(size_hint=(1, None), height=50, spacing=10)
        self.button_layout.add_widget(self.listen_button)
        self.button_layout.add_widget(self.stop_button)
        self.button_layout.add_widget(self.exit_button)
        
        self.layout.add_widget(self.waveform)
        self.layout.add_widget(self.button_layout)
        
        Clock.schedule_interval(self.update_plot, 1.0 / 30.0)  # Schedule plot update every 1/30th of a second
        
        return self.layout
    
    def update_plot(self, dt):
        """Periodically update the waveform plot."""
        if hasattr(self, 'audioData') and self.audioData.size != 0:
            self.waveform.update(self.audioData)  # Update waveform widget with latest audio data
    
    def listen(self, instance):
        """Start listening to audio input."""
        self.stop_button.disabled = False  # Enable stop button
        self.listen_button.disabled = True  # Disable listen button
        if self.pAud:
            try:
                self.stream = self.pAud.open(
                    format=pyaudio.paInt16,
                    channels=1,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK,
                    stream_callback=self.callback,  # Set callback function for audio stream
                )
                self.stream.start_stream()  # Start audio stream
            except pyaudio.PyAudioError as e:
                print(f"Error opening stream: {e}")
                self.listen_button.disabled = False  # Re-enable listen button on error
                self.stop_button.disabled = True  # Disable stop button on error
    
    def stop(self, instance=None):
        """Stop audio input."""
        if hasattr(self, 'stream'):
            self.stream.stop_stream()  # Stop audio stream
            self.stream.close()  # Close audio stream
            del self.stream  # Delete stream object
            self.stop_button.disabled = True  # Disable stop button
            self.listen_button.disabled = False  # Enable listen button
    
    def callback(self, in_data, frame_count, time_info, status):
        """Callback function for audio stream processing."""
        self.audioData = np.frombuffer(in_data, dtype=np.int16)  # Convert input data to numpy array
        return (in_data, pyaudio.paContinue)  # Return input data to continue audio stream
    
    def close_app(self, instance):
        """Close the application."""
        self.stop()  # Stop audio stream
        if self.pAud:
            self.pAud.terminate()  # Terminate PyAudio instance
        App.get_running_app().stop()  # Stop the Kivy application
    
    def run_visualizer(self, visualizer):
        """Run an external visualizer."""
        self.stop()  # Stop audio stream
        subprocess.Popen(['python', visualizer])  # Launch external visualizer
        self.close_app(None)  # Close the application

if __name__ == '__main__':
    AudioVisualizerApp().run()  # Run the Kivy application
