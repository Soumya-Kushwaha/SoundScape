import tkinter as tk
import subprocess

def run_spec():
    subprocess.Popen(["python", "Spectogram.py"])

def run_wave():
    subprocess.Popen(["python", "Waveform.py"])

def run_AvsF():
    subprocess.Popen(["python", "Amplitude-Frequency-Visualizer.py"])

def run_IvsF():
    subprocess.Popen(["python", "Intensity-vs-Frequency-and-time.py"])

def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x_coordinate = (screen_width - width) // 2
    y_coordinate = (screen_height - height) // 2

    window.geometry(f"{width}x{height}+{x_coordinate}+{y_coordinate}")

root = tk.Tk()
root.title("Soundscape")
root.configure(bg="#1e1e1e")  # Dark background color

button_bg = "#292929"  # Dark gray
button_fg = "#FFFFFF"  # White
button_font = ("Helvetica", 12)  # Button font
button_radius = 10  # Button corner radius

window_width = 600
window_height = 400
root.geometry(f"{window_width}x{window_height}")

center_window(root, window_width, window_height)

button_frame = tk.Frame(root, bg="#1e1e1e")  # Dark background color
button_frame.place(relx=0.5, rely=0.5, anchor="center")

# Define button texts and corresponding commands
buttons = [
    ("Spectogram", run_spec),
    ("Waveform", run_wave),
    ("Amplitude vs Frequency", run_AvsF),
    ("Intensity vs Frequency", run_IvsF)
]

# Create buttons in a matrix layout
for i, (text, command) in enumerate(buttons):
    row, column = divmod(i, 2)  # 2 buttons per row
    button = tk.Button(button_frame, text=text, command=command, bg=button_bg, fg=button_fg, relief=tk.FLAT, font=button_font, bd=0)
    button.config(highlightbackground=button_bg, highlightcolor=button_bg, highlightthickness=2, borderwidth=0, padx=20, pady=10)
    button.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")
    button.bind("<Enter>", lambda e, b=button: b.config(bg="#444444"))  # Change button color on hover
    button.bind("<Leave>", lambda e, b=button: b.config(bg=button_bg))  # Restore button color on leave

root.mainloop()