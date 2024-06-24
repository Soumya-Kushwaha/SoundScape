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
        self.points = []

    def update(self, data):
        self.canvas.clear()
        with self.canvas:
            Color(1, 0, 0)
            self.points = []
            for i in range(len(data)):
                self.points.append((self.width * i / len(data), self.height / 2 + data[i] / 32768 * self.height / 2))
            Line(points=self.points)

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
        self.listen_button.bind(on_press=self.listen)
        
        self.stop_button = Button(text='Stop', size_hint=(None, None), size=(100, 50), disabled=True)
        self.stop_button.bind(on_press=self.stop)
        
        self.exit_button = Button(text='Exit', size_hint=(None, None), size=(100, 50))
        self.exit_button.bind(on_press=self.close_app)
        
        self.button_layout = BoxLayout(size_hint=(1, None), height=50, spacing=10)
        self.button_layout.add_widget(self.listen_button)
        self.button_layout.add_widget(self.stop_button)
        self.button_layout.add_widget(self.exit_button)
        
        self.layout.add_widget(self.waveform)
        self.layout.add_widget(self.button_layout)
        
        Clock.schedule_interval(self.update_plot, 1.0 / 30.0)  # Update plot every 1/30th of a second
        
        return self.layout
    
    def update_plot(self, dt):
        if hasattr(self, 'audioData') and self.audioData.size != 0:
            self.waveform.update(self.audioData)
    
    def listen(self, instance):
        self.stop_button.disabled = False
        self.listen_button.disabled = True
        if self.pAud:
            try:
                self.stream = self.pAud.open(
                    format=pyaudio.paInt16,
                    channels=1,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK,
                    stream_callback=self.callback,
                )
                self.stream.start_stream()
            except pyaudio.PyAudioError as e:
                print(f"Error opening stream: {e}")
                self.listen_button.disabled = False
                self.stop_button.disabled = True
    
    def stop(self, instance=None):
        if hasattr(self, 'stream'):
            self.stream.stop_stream()
            self.stream.close()
            del self.stream
            self.stop_button.disabled = True
            self.listen_button.disabled = False
    
    def callback(self, in_data, frame_count, time_info, status):
        self.audioData = np.frombuffer(in_data, dtype=np.int16)
        return (in_data, pyaudio.paContinue)
    
    def close_app(self, instance):
        self.stop()
        if self.pAud:
            self.pAud.terminate()
        App.get_running_app().stop()
    
    def run_visualizer(self, visualizer):
        self.stop()
        subprocess.Popen(['python', visualizer])
        self.close_app(None)

if __name__ == '__main__':
    AudioVisualizerApp().run()
