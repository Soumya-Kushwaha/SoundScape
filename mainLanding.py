import PySimpleGUI as sg
import subprocess
import os  

# Create the layout for the landing page
AppFont = "Helvetica 16"

# Function to create the main layout
def create_layout():
    return [
        [sg.Text("Welcome to SoundScape", font=("Helvetica", 24), justification="center", pad=(0, 20), expand_x=True)],
        [sg.Text("Explore various audio visualizers", font=("Helvetica", 14), justification="center", pad=(0, 10), expand_x=True)],
        [sg.Multiline("SoundScape is an innovative application designed to transform audio data into stunning visualizations. "
                      "Choose from a variety of visualizers to unleash the power of audio visualizations!.",
                      font=("Helvetica", 14), justification="center", size=(60, 2), no_scrollbar=True, disabled=True, pad=(20, 20),
                      background_color="#e1f5fe", text_color="#006064", expand_x=True, expand_y=True)],
        [sg.Button("Amplitude-Frequency Visualizer", pad=(10, 10), key="Amplitude-Frequency Visualizer"),
         sg.Button("Waveform", pad=(10, 10), key="Waveform"),
         sg.Button("Spectrogram", pad=(10, 10), key="Spectrogram"),
         sg.Button("Intensity vs Frequency and Time", pad=(10, 10), key="Intensity vs Frequency and Time")],
        [sg.Button("Change Theme", pad=(10, 20), key="Change Theme", button_color=("white", "green"))],
        [sg.Button("Exit", size=(80,2), pad=(10, 10), key="Exit", button_color=("white", "red"), font=("Helvetica", 12), tooltip="Exit the application")],

    ]

# Create the main window with the initial layout
layout = create_layout()
window = sg.Window("Welcome to SoundScape ", layout, finalize=True, element_justification="center", resizable=False, size=(800, 600))

def close_current_visualizer(process):
    if process and process.poll() is None:
        process.kill()
        process.wait()

# new function made for changing the theme
def change_theme():
    print("Changing theme...")
    current_theme = sg.theme_list()
    current_theme_index = current_theme.index(sg.theme())
    next_theme_index = (current_theme_index + 1) % len(current_theme)
    sg.theme(current_theme[next_theme_index])
    
    global window
    layout = create_layout()  # layout chanfing
    window.close()
    window = sg.Window("Welcome to SoundScape ", layout, finalize=True, element_justification="center", resizable=False, size=(800, 600))
    
    print("Theme changed to:", current_theme[next_theme_index])

# Main loop
current_visualizer_process = None
while True:
    event, values = window.read()

    if event in (sg.WIN_CLOSED, "Exit"):
        close_current_visualizer(current_visualizer_process)
        break

    if event == "Change Theme":
        change_theme()

    visualizer_scripts = {
        "Amplitude-Frequency Visualizer": "Amplitude-Frequency-Visualizer.py",
        "Waveform": "Waveform.py",
        "Spectrogram": "Spectogram.py",
        "Intensity vs Frequency and Time": "Intensity-vs-Frequency-and-Time.py"
    }

    if event in visualizer_scripts:
        script_path = visualizer_scripts[event]
        if os.path.exists(script_path):
            close_current_visualizer(current_visualizer_process)
            current_visualizer_process = subprocess.Popen(['python', script_path])
            window.close()
            break
        else:
            sg.popup_error(f"Script '{script_path}' not found!", title="File Not Found")

window.close()