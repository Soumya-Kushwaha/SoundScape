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
        self.audioData = np.array([])
        self.current_visualizer_process = None

        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        self.graph = BoxLayout()
        self.graph.canvas.add(Color(0.5, 0.5, 0.5, 1))
        self.graph.canvas.add(Rectangle(size=(500, 500)))

        self.progress_bar = ProgressBar(max=4000, size_hint=(1, None), height=20)
        
        btn_layout = BoxLayout(size_hint=(1, None), height=50)
        self.listen_btn = Button(text="Listen", on_press=self.listen)
        self.stop_btn = Button(text="Stop", on_press=self.stop, disabled=True)
        self.exit_btn = Button(text="Exit", on_press=self.stop)

        btn_layout.add_widget(self.listen_btn)
        btn_layout.add_widget(self.stop_btn)
        btn_layout.add_widget(self.exit_btn)

        layout.add_widget(Label(text="Mic to Sound Intensity vs Frequency heatmap", font_size=24, size_hint=(1, 0.1)))
        layout.add_widget(self.graph)
        layout.add_widget(self.progress_bar)
        layout.add_widget(btn_layout)

        Clock.schedule_interval(self.update, 0.1)
        return layout

    def listen(self, instance):
        self.stop_btn.disabled = False
        self.listen_btn.disabled = True

        self.stream = pAud.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
            stream_callback=self.callback,
        )
        self.stream.start_stream()

    def stop(self, instance):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
            self.progress_bar.value = 0
            self.stop_btn.disabled = True
            self.listen_btn.disabled = False
        if self.current_visualizer_process:
            self.current_visualizer_process.kill()
            self.current_visualizer_process = None
        App.get_running_app().stop()

    def callback(self, in_data, frame_count, time_info, status):
        self.audioData = np.frombuffer(in_data, dtype=np.int16)
        return (in_data, pyaudio.paContinue)

    def update(self, dt):
        if self.audioData.size != 0:
            self.progress_bar.value = np.amax(self.audioData)
            intensity_data = self.compute_intensity_data(self.audioData)
            self.draw_heatmap(intensity_data)

    def compute_intensity_data(self, audio_data, window_size=1024, hop_size=512):
        num_frames = len(audio_data) // hop_size
        intensity_data = np.zeros((num_frames, window_size // 2))

        for i in range(num_frames):
            frame = audio_data[i * hop_size: (i + 1) * hop_size]
            intensity_data[i, :] = np.abs(np.fft.fft(frame)[:window_size // 2])
        return intensity_data

    def draw_heatmap(self, intensity_data):
        self.graph.canvas.clear()
        rows, cols = intensity_data.shape
        for row in range(rows):
            for col in range(cols):
                intensity = intensity_data[row, col]
                color = self.get_heatmap_color(intensity)
                x1 = col * 500 / cols
                y1 = 500 - (row + 1) * 500 / rows
                x2 = x1 + 500 / cols
                y2 = y1 + 500 / rows
                with self.graph.canvas:
                    Color(*color)
                    Rectangle(pos=(x1, y1), size=(x2 - x1, y2 - y1))

    def get_heatmap_color(self, intensity, threshold=0.0):
        cmap = [(0, 0, 1, 1), (0, 1, 0, 1), (1, 1, 0, 1), (1, 0, 0, 1)]
        if np.isnan(intensity):
            return (0.5, 0.5, 0.5, 1)
        intensity_norm = np.log1p(intensity) / 20
        color_index = min(int(intensity_norm * len(cmap)), len(cmap) - 1)
        return cmap[color_index]
if __name__=='__main__':
    CHUNK=1024
    RATE=44100
    INTERVAL=1
    TIMEOUT=10
    pAud = pyaudio.PyAudio()
    SoundScapeApp().run()
