import numpy as np
import pyaudio
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.graphics import Color, Line, PushMatrix, PopMatrix, Translate
import random

# Constants
CHUNK = 1024
RATE = 44100
GRID_SIZE = (5, 5, 5)

class VoxelGridWidget(Widget):
    def __init__(self, **kwargs):
        super(VoxelGridWidget, self).__init__(**kwargs)
        self.grid_size = GRID_SIZE
        self.audio_intensity = 0
        self.random_cell = (0, 0, 0)
        self.bind(size=self.update_voxel_grid, pos=self.update_voxel_grid)

    def update_voxel_grid(self, *args):
        self.canvas.clear()
        self.center_grid()

    def center_grid(self):
        voxel_size = min(self.width / (self.grid_size[0] * 2), self.height / (self.grid_size[1] * 2))  # Ensure the grid occupies the whole screen
        base_voxel_size = voxel_size  # Base size for voxels
        self.random_cell = (random.randint(0, self.grid_size[0] - 1), 
                            random.randint(0, self.grid_size[1] - 1), 
                            random.randint(0, self.grid_size[2] - 1))
        x_offset = (self.width - self.grid_size[0] * voxel_size * 1.5) / 2
        y_offset = (self.height - self.grid_size[1] * voxel_size * 1.5) / 2

        with self.canvas:
            for x in range(self.grid_size[0]):
                for y in range(self.grid_size[1]):
                    for z in range(self.grid_size[2]):
                        if (x, y, z) == self.random_cell:
                            # Map audio intensity to a color gradient from blue to red
                            r = self.audio_intensity
                            g = 0
                            b = 1 - self.audio_intensity
                            Color(r, g, b)
                            size = base_voxel_size * (1 + 5 * self.audio_intensity)  # Size based on intensity
                        else:
                            brightness = 0.2 + 0.8 * self.audio_intensity  # Adjust color brightness based on intensity
                            Color(brightness, brightness, brightness)
                            size = base_voxel_size

                        self.draw_voxel(x, y, z, size, x_offset, y_offset)

    def draw_voxel(self, x, y, z, size, x_offset, y_offset):
        x_start = x * size * 1.5 + x_offset
        y_start = y * size * 1.5 + y_offset

        # Draw a square to represent the voxel
        with self.canvas:
            PushMatrix()
            Translate(x_start, y_start)
            Line(rectangle=(0, 0, size, size), width=1.5)
            PopMatrix()

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

        # Voxel grid widget
        self.voxel_grid_widget = VoxelGridWidget()

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

        self.layout.add_widget(self.voxel_grid_widget)
        self.layout.add_widget(self.button_layout)

        Clock.schedule_interval(self.update_plot, 1.0 / 30.0)  # Update plot every 1/30th of a second

        return self.layout

    def update_plot(self, dt):
        if hasattr(self, 'audioData') and self.audioData.size != 0:
            intensity = np.abs(self.audioData).mean() / 32767.0
            self.voxel_grid_widget.audio_intensity = intensity
            self.voxel_grid_widget.update_voxel_grid()

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

if __name__ == '__main__':
    AudioVisualizerApp().run()
