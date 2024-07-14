import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window
import pyaudio
import numpy as np
import subprocess

class SoundScapeApp(App):
    def build(self):
        self.stream = None
        self.audioData = np.array([])  # Initialize audio data
        self.current_visualizer_process = None

        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        self.graph = BoxLayout(size_hint=(1, 0.6))  # Graph for heatmap
        self.graph.bind(size=self.update_heatmap_size)  # Update heatmap size on resize

        self.progress_bar = ProgressBar(max=4000, size_hint=(1, None), height=20)  # Progress bar

        btn_layout = BoxLayout(size_hint=(1, None), height=50)  # Button layout
        self.listen_btn = Button(text="Listen", on_press=self.listen, font_size=20)  # Listen button
        self.stop_btn = Button(text="Stop", on_press=self.stop, disabled=True, font_size=20)  # Stop button
        self.exit_btn = Button(text="Exit", on_press=self.stop, font_size=20)  # Exit button

        btn_layout.add_widget(self.listen_btn)
        btn_layout.add_widget(self.stop_btn)
        btn_layout.add_widget(self.exit_btn)

        layout.add_widget(Label(text="Mic to Sound Intensity vs Frequency Heatmap", font_size=30, size_hint=(1, 0.1)))  # Title label
        layout.add_widget(self.graph)
        layout.add_widget(self.progress_bar)
        layout.add_widget(btn_layout)

        Clock.schedule_interval(self.update, 0.1)  # Schedule update function
        return layout

    def listen(self, instance):
        self.stop_btn.disabled = False  # Enable stop button
        self.listen_btn.disabled = True  # Disable listen button

        self.stream = pAud.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
            stream_callback=self.callback,
        )
        self.stream.start_stream()  # Start audio stream

    def stop(self, instance):
        if self.stream:
            self.stream.stop_stream()  # Stop audio stream
            self.stream.close()  # Close audio stream
            self.stream = None
            self.progress_bar.value = 0  # Reset progress bar
            self.stop_btn.disabled = True  # Disable stop button
            self.listen_btn.disabled = False  # Enable listen button
        if self.current_visualizer_process:
            self.current_visualizer_process.kill()  # Kill current visualizer process
            self.current_visualizer_process = None
        App.get_running_app().stop()  # Stop the app

    def callback(self, in_data, frame_count, time_info, status):
        self.audioData = np.frombuffer(in_data, dtype=np.int16)  # Convert audio data to numpy array
        return (in_data, pyaudio.paContinue)

    def update(self, dt):
        if self.audioData.size != 0:
            self.progress_bar.value = np.amax(self.audioData)  # Update progress bar
            intensity_data = self.compute_intensity_data(self.audioData)  # Compute intensity data
            self.draw_heatmap(intensity_data)  # Draw heatmap

    def compute_intensity_data(self, audio_data, window_size=1024, hop_size=512):
        num_frames = len(audio_data) // hop_size
        intensity_data = np.zeros((num_frames, window_size // 2))

        for i in range(num_frames):
            frame = audio_data[i * hop_size: (i + 1) * hop_size]
            intensity_data[i, :] = np.abs(np.fft.fft(frame)[:window_size // 2])  # Compute FFT and store intensity
        return intensity_data

    def draw_heatmap(self, intensity_data):
        self.graph.canvas.clear()  # Clear the graph canvas
        rows, cols = intensity_data.shape
        graph_width, graph_height = self.graph.size

        for row in range(rows):
            for col in range(cols):
                intensity = intensity_data[row, col]
                color = self.get_heatmap_color(intensity)  # Get color for intensity
                x1 = col * graph_width / cols
                y1 = graph_height - (row + 1) * graph_height / rows
                x2 = x1 + graph_width / cols
                y2 = y1 + graph_height / rows
                with self.graph.canvas:
                    Color(*color)
                    Rectangle(pos=(x1, y1), size=(x2 - x1, y2 - y1))  # Draw rectangle with computed color

    def get_heatmap_color(self, intensity, threshold=0.0):
        cmap = [(0, 0, 1, 1), (0, 1, 0, 1), (1, 1, 0, 1), (1, 0, 0, 1)]  # Color map
        if np.isnan(intensity):
            return (0.5, 0.5, 0.5, 1)  # Return gray for NaN values
        intensity_norm = np.log1p(intensity) / 20  # Normalize intensity
        color_index = min(int(intensity_norm * len(cmap)), len(cmap) - 1)  # Get color index
        return cmap[color_index]

    def update_heatmap_size(self, instance, value):
        self.draw_heatmap(np.zeros((10, 10)))  # Draw empty heatmap on resize

if __name__ == '__main__':
    CHUNK = 1024  # Samples per frame
    RATE = 44100  # Sampling rate
    INTERVAL = 1  # Interval in seconds
    TIMEOUT = 10  # Timeout in ms
    pAud = pyaudio.PyAudio()  # Initialize PyAudio
    SoundScapeApp().run()  # Run the app
