import PySimpleGUI as sg
import subprocess

# Create the layout for the landing page
AppFont = "Helvetica 16"
sg.theme("DarkTeal12")

# Define button styles
button_style = {"font": AppFont, "button_color": ("white", "#1c86ee"), "expand_x": True,}

# Layout for the main landing page
layout = [
    [sg.Text("Welcome to SoundScape", font=("Helvetica", 24), justification="center", pad=(0, 20), expand_x=True)],
    [sg.Text("Explore various audio visualizers", font=("Helvetica", 14), justification="center", pad=(0, 10), expand_x=True)],
    [sg.Multiline("SoundScape is an innovative application designed to transform audio data into stunning visualizations. "
                  "Choose from a variety of visualizers to  unleash the power of audio visualizations!.",
                  font=("Helvetica", 14), justification="center", size=(50, 4), no_scrollbar=True, disabled=True, pad=(20, 20),
                  background_color="#e1f5fe", text_color="#006064", expand_x=True, expand_y=True)],
    [sg.Button("Amplitude-Frequency Visualizer", **button_style, pad=(10, 10),)],
    [sg.Button("Waveform", **button_style, pad=(10, 10))],
    [sg.Button("Spectrogram", **button_style, pad=(10, 10))],
    [sg.Button("Intensity vs Frequency and Time", **button_style, pad=(10, 10))],
    [sg.Button("Exit", font=AppFont, button_color=("white", "red"), pad=(10, 20), expand_x=True)]
]

# Create the main window with a fixed size and responsive settings
window = sg.Window("Welcome to SoundScape ", layout, finalize=True, element_justification="center", resizable=True, size=(800, 600))

# Function to close the current visualizer process
def close_current_visualizer(process):
    if process and process.poll() is None:
        process.kill()
        process.wait()

# Main loop
current_visualizer_process = None
while True:
    event, values = window.read()

    if event in (sg.WIN_CLOSED, "Exit"):
        close_current_visualizer(current_visualizer_process)
        break

    if event == "Amplitude-Frequency Visualizer":
        close_current_visualizer(current_visualizer_process)
        current_visualizer_process = subprocess.Popen(['python', 'Amplitude-Frequency-Visualizer.py'])
        window.close()
        break

    if event == "Waveform":
        close_current_visualizer(current_visualizer_process)
        current_visualizer_process = subprocess.Popen(['python', 'Waveform.py'])
        window.close()
        break

    if event == "Spectrogram":
        close_current_visualizer(current_visualizer_process)
        current_visualizer_process = subprocess.Popen(['python', 'spectogram.py'])
        window.close()
        break

    if event == "Intensity vs Frequency and Time":
        close_current_visualizer(current_visualizer_process)
        current_visualizer_process = subprocess.Popen(['python', 'Intensity-vs-Frequency-and-time.py'])
        window.close()
        break

window.close()
