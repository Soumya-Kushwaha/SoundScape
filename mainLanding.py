from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
from kivy.graphics import Color, Rectangle, RoundedRectangle
import subprocess
import os

class SoundScapeApp(App):
    def build(self):
        self.current_visualizer_process = None

        # Define the initial layout
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        title = Label(
            text="Welcome to SoundScape",
            font_size=32,
            size_hint=(1, 0.15),
            color=get_color_from_hex("#006064"),
            bold=True,
        )
        subtitle = Label(
            text="Explore various audio visualizers",
            font_size=24,
            size_hint=(1, 0.1),
            color=get_color_from_hex("#00838f"),
        )

        description = TextInput(
            text=("SoundScape is an innovative application designed to transform audio data into stunning visualizations. "),
            readonly=True,
            multiline=True,
            background_color=get_color_from_hex("#e1f5fe"),
            foreground_color=get_color_from_hex("#006064"),
            font_size=18,
            size_hint=(1, 0.3),
        )

        button_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.3), spacing=10)
        visualizers = [
            "Amplitude-Frequency Visualizer",
            "Waveform",
            "Spectrogram",
            "Intensity vs Frequency and Time",
            "Depth-Perspective Visualizer",
            "Chroma-Feature Visualizer"
            "Lissajous-Curves Visualizer",
            "Voxel-Grid Visualizer",
            "Chromagram Visualizer",
            "BarPlot Histogram Visualizer"
        ]
        for visualizer in visualizers:
            button = Button(
                text=visualizer,
                text_size=(None, None),
                halign='center',
                valign='middle',
                size_hint=(1, None),
                height=50,
                background_color=get_color_from_hex("#0288d1"),
                color=get_color_from_hex("#ffffff"),
                font_size=18,
            )
            button.bind(on_press=self.launch_visualizer)
            button_layout.add_widget(button)

        theme_button = Button(
            text="Change Theme",
            size_hint=(1, 0.1),
            background_color=get_color_from_hex("#00c853"),
            color=get_color_from_hex("#ffffff"),
            text_size=(None, None),
            halign='center',
            valign='middle',
            font_size=18,
        )
        theme_button.bind(on_press=self.change_theme)

        exit_button = Button(
            text="Exit",
            size_hint=(1, 0.1),
            background_color=get_color_from_hex("#d32f2f"),
            color=get_color_from_hex("#ffffff"),
            text_size=(None, None),
            halign='center',
            valign='middle',
            font_size=18,
        )
        exit_button.bind(on_press=self.stop)

        layout.add_widget(title)
        layout.add_widget(subtitle)
        layout.add_widget(description)
        layout.add_widget(button_layout)
        layout.add_widget(theme_button)
        layout.add_widget(exit_button)

        self.layout = layout
        self.theme_index = 0

        with layout.canvas.before:
            Color(1, 1, 1, 1)  # default background color
            self.bg_rect = RoundedRectangle(size=layout.size, pos=layout.pos, radius=[20])
            layout.bind(size=self._update_rect, pos=self._update_rect)

        return layout

    def close_current_visualizer(self):
        if self.current_visualizer_process and self.current_visualizer_process.poll() is None:
            self.current_visualizer_process.kill()
            self.current_visualizer_process.wait()

    def change_theme(self, instance):
        themes = [
            {"bg_color": [1, 1, 1, 1], "fg_color": [0, 0, 0, 1]},  # Light theme
            {"bg_color": [0, 0, 0, 1], "fg_color": [1, 1, 1, 1]},  # Dark theme
        ]
        self.theme_index = (self.theme_index + 1) % len(themes)
        theme = themes[self.theme_index]

        self.layout.canvas.before.clear()
        with self.layout.canvas.before:
            Color(*theme["bg_color"])
            self.bg_rect = RoundedRectangle(size=self.layout.size, pos=self.layout.pos, radius=[20])
        self._update_rect(self.layout, None)

        for child in self.layout.children:
            if isinstance(child, Label):
                child.color = theme["fg_color"]
            if isinstance(child, Button):
                child.background_color = theme["bg_color"]
                child.color = theme["fg_color"]
            if isinstance(child, TextInput):
                child.background_color = theme["bg_color"]
                child.foreground_color = theme["fg_color"]

    def _update_rect(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

    def launch_visualizer(self, instance):
        visualizer_scripts = {
            "Amplitude-Frequency Visualizer": "Amplitude-Frequency-Visualizer.py",
            "Waveform": "Waveform.py",
            "Spectrogram": "Spectrogram.py",
            "Intensity vs Frequency and Time": "Intensity-vs-Frequency-and-Time.py",
            "Depth-Perspective Visualizer": "Depth-Perspective-Visualizer.py",
            "Chroma-Feature Visualizer": "Chroma-Feature-Visualizer.py",
            "Lissajous-Curves Visualizer": "Lissajous-Curves-Visualizer.py",
            "Voxel-Grid Visualizer": "Voxel-Grid-Visualizer.py",
            "Chromagram Visualizer": "Chromagram.py",
            "BarPlot Histogram Visualizer": "barplot.py"
        }
        
        script_name = instance.text
        script_path = visualizer_scripts.get(script_name)

        if script_path and os.path.exists(script_path):
            self.close_current_visualizer()
            try:
                self.current_visualizer_process = subprocess.Popen(['python', script_path])
            except Exception as e:
                popup = Popup(title="Error", content=Label(text=f"Failed to launch '{script_path}': {e}"), size_hint=(None, None), size=(400, 200))
                popup.open()
        else:
            popup = Popup(title="File Not Found", content=Label(text=f"Script '{script_path}' not found!"), size_hint=(None, None), size=(400, 200))
            popup.open()

if __name__ == '__main__':
    SoundScapeApp().run()
