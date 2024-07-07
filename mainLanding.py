from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
import subprocess
import os

class SoundScapeApp(App):
    def build(self):
        self.current_visualizer_process = None

        # Define the initial layout
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        title = Label(text="Welcome to SoundScape", font_size=24, size_hint=(1, 0.2))
        subtitle = Label(text="Explore various audio visualizers", font_size=18, size_hint=(1, 0.1))

        description = TextInput(
            text=("SoundScape is an innovative application designed to transform audio data into stunning visualizations. "
                  "Choose from a variety of visualizers to unleash the power of audio visualizations!"),
            readonly=True,
            background_color=get_color_from_hex("#e1f5fe"),
            foreground_color=get_color_from_hex("#006064"),
            font_size=16,
            size_hint=(1, 0.3),
        )

        button_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.2), spacing=10)
        button_layout.add_widget(Button(text="Amplitude-Frequency Visualizer", on_press=self.launch_visualizer))
        button_layout.add_widget(Button(text="Waveform", on_press=self.launch_visualizer))
        button_layout.add_widget(Button(text="Spectrogram", on_press=self.launch_visualizer))
        button_layout.add_widget(Button(text="Intensity vs Frequency and Time", on_press=self.launch_visualizer))

        theme_button = Button(text="Change Theme", size_hint=(1, 0.1), background_color=(0, 1, 0, 1))
        theme_button.bind(on_press=self.change_theme)

        exit_button = Button(text="Exit", size_hint=(1, 0.1), background_color=(1, 0, 0, 1))
        exit_button.bind(on_press=self.stop)

        layout.add_widget(title)
        layout.add_widget(subtitle)
        layout.add_widget(description)
        layout.add_widget(button_layout)
        layout.add_widget(theme_button)
        layout.add_widget(exit_button)

        self.layout = layout
        self.theme_index = 0
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
            from kivy.graphics import Color, Rectangle
            Color(*theme["bg_color"])
            self.bg_rect = Rectangle(size=self.layout.size, pos=self.layout.pos)
            self.layout.bind(size=self._update_rect, pos=self._update_rect)
        
        for child in self.layout.children:
            if isinstance(child, Label):
                child.color = theme["fg_color"]
            if isinstance(child, Button):
                child.background_color = theme["bg_color"]
                child.color = theme["fg_color"]

    def _update_rect(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

    def launch_visualizer(self, instance):
        visualizer_scripts = {
            "Amplitude-Frequency Visualizer": "Amplitude-Frequency-Visualizer.py",
            "Waveform": "Waveform.py",
            "Spectrogram": "Spectogram.py",
            "Intensity vs Frequency and Time": "Intensity-vs-Frequency-and-Time.py"
        }
        
        script_name = instance.text
        script_path = visualizer_scripts.get(script_name)

        if script_path and os.path.exists(script_path):
            self.close_current_visualizer()
            self.current_visualizer_process = subprocess.Popen(['python', script_path])
        else:
            popup = Popup(title="File Not Found", content=Label(text=f"Script '{script_path}' not found!"), size_hint=(None, None), size=(400, 200))
            popup.open()

if __name__ == '__main__':
    SoundScapeApp().run()

