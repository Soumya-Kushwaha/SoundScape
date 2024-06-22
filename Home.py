import PySimpleGUI as sg
import subprocess
import sys

# Create the layout for the landing page
AppFont = "Helvetica 16"
sg.theme("DarkTeal12")
sg.Sizer(800, 800)

# Define button styles
button_style = {"font": AppFont, "button_color": ("white", "#1c86ee"), "expand_x": True}

# Layout for the buttons
button_layout = [
    [sg.Button("Amplitude-Frequency Visualizer", **button_style, pad=(10, 10))],
    [sg.Button("Waveform", **button_style, pad=(10, 10))],
    [sg.Button("Spectrogram", **button_style, pad=(10, 10))],
    [sg.Button("Intensity vs Frequency and Time", **button_style, pad=(10, 10))],
    [sg.Button("Real-Time VU Meter", **button_style, pad=(10, 10))],  # New button for Triangle Wave
   ]

# Layout for the main landing page
layout = [
    [sg.Text("Welcome to SoundScape", font=("Helvetica", 24), justification="center", pad=(0, 5), expand_x=True)],
    [sg.Text("Explore various audio visualizers", font=("Helvetica", 14), justification="center", pad=(0, 5), expand_x=True)],
    [sg.Multiline("SoundScape is an innovative application designed to transform audio data into stunning visualizations. "
                  "Choose from a variety of visualizers to unleash the power of audio visualizations!.",
                  font=("Helvetica", 14), justification="center", size=(50, 4), no_scrollbar=True, disabled=True, pad=(10, 10),
                  background_color="#e1f5fe", text_color="#006064", expand_x=True, expand_y=True)],
    [sg.Column(button_layout, size=(390, 300), scrollable=True, vertical_scroll_only=True), sg.Image(filename='mediafiles/soundwaveimg.png', key='-IMAGE-', size=(390, 300))],  # Add the PNG image here
    [sg.Button("Exit", font=AppFont, button_color=("white", "red"), pad=(10, 10), expand_x=True)]  # Adjusted padding
]

# Create the main window with a fixed size and responsive settings
window = sg.Window("Welcome to SoundScape", layout, finalize=True, element_justification="center", resizable=True, size=(800, 600))

# Function to close the current visualizer process
def close_current_visualizer(process):
    if process and process.poll() is None:
        process.kill()
        process.wait()

# Main loop
current_visualizer_process = None

while True:
    event, values = window.read(timeout=100)  # Use a timeout to periodically check the process

    if event in (sg.WIN_CLOSED, "Exit"):
        close_current_visualizer(current_visualizer_process)
        break

    if event in ["Amplitude-Frequency Visualizer", "Waveform", "Spectrogram", "Intensity vs Frequency and Time","Real-Time VU Meter", "Sine Wave", "Square Wave", "Triangle Wave", "Sawtooth Wave"]:
        close_current_visualizer(current_visualizer_process)
        
        # Mapping event to corresponding script names
        script_mapping = {
            "Amplitude-Frequency Visualizer": "Amplitude-Frequency-Visualizer.py",
            "Waveform": "Waveform.py",
            "Spectrogram": "Spectrogram.py",
            "Intensity vs Frequency and Time": "Intensity-vs-Frequency-and-time.py",
            "Real-Time VU Meter": "Real-Time VU Meter.py",  # Added button for "Triangle Wave"
        }

        script_name = script_mapping[event]
        current_visualizer_process = subprocess.Popen([sys.executable, script_name])

window.close()
