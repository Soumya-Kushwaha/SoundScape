import PySimpleGUI as sg
import subprocess

# Initialize constants and styles
APP_FONT = "Helvetica 16"
sg.theme("DarkTeal12")

BUTTON_STYLE = {"font": APP_FONT, "button_color": ("white", "#1c86ee"), "expand_x": True}

# Define the layout for the main landing page
layout = [
    [sg.Text("Welcome to SoundScape", font=("Helvetica", 24), justification="center", pad=(0, 20), expand_x=True)],
    [sg.Text("Explore various audio visualizers", font=("Helvetica", 14), justification="center", pad=(0, 10), expand_x=True)],
    [sg.Multiline(
        "SoundScape is an innovative application designed to transform audio data into stunning visualizations. "
        "Choose from a variety of visualizers to unleash the power of audio visualizations!",
        font=("Helvetica", 14), justification="center", size=(50, 4), no_scrollbar=True, disabled=True, pad=(20, 20),
        background_color="#e1f5fe", text_color="#006064", expand_x=True, expand_y=True
    )],
    [sg.Button("Amplitude-Frequency Visualizer", **BUTTON_STYLE, pad=(10, 10))],
    [sg.Button("Waveform", **BUTTON_STYLE, pad=(10, 10))],
    [sg.Button("Spectrogram", **BUTTON_STYLE, pad=(10, 10))],
    [sg.Button("Intensity vs Frequency and Time", **BUTTON_STYLE, pad=(10, 10))],
    [sg.Button("Exit", font=APP_FONT, button_color=("white", "red"), pad=(10, 20), expand_x=True)]
]

# Create the main window
window = sg.Window("Welcome to SoundScape", layout, finalize=True, element_justification="center", resizable=True, size=(800, 600))

# Function to close the current visualizer process
def close_current_visualizer(process):
    if process and process.poll() is None:
        process.kill()
        process.wait()

# Main event loop
current_visualizer_process = None
while True:
    event, _ = window.read()

    if event in (sg.WIN_CLOSED, "Exit"):
        close_current_visualizer(current_visualizer_process)
        break

    if event in ["Amplitude-Frequency Visualizer", "Waveform", "Spectrogram", "Intensity vs Frequency and Time"]:
        close_current_visualizer(current_visualizer_process)
        script_name = event.replace(" ", "-") + ".py"
        current_visualizer_process = subprocess.Popen(['python', script_name])
        window.close()
        break

window.close()

