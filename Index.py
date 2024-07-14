import tkinter as tk
import subprocess

def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x_coordinate = (screen_width - width) // 2
    y_coordinate = (screen_height - height) // 2

    window.geometry(f"{width}x{height}+{x_coordinate}+{y_coordinate}")

def create_button(frame, text, command, bg, fg, font, row, column):
    button = tk.Button(frame, text=text, command=command, bg=bg, fg=fg, relief=tk.FLAT, font=font, bd=0)
    button.config(highlightbackground=bg, highlightcolor=bg, highlightthickness=2, borderwidth=0, padx=20, pady=10)
    button.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")
    button.bind("<Enter>", lambda e, b=button: b.config(bg="#444444"))  # Change button color on hover
    button.bind("<Leave>", lambda e, b=button: b.config(bg=bg))  # Restore button color on leave

def run_visualizer(script_name):
    subprocess.Popen(["python", script_name])

root = tk.Tk()
root.title("Soundscape")
root.configure(bg="#1e1e1e")  # Dark background color

button_bg = "#292929"  # Dark gray
button_fg = "#FFFFFF"  # White
button_font = ("Helvetica", 12)  # Button font

window_width = 600
window_height = 400
root.geometry(f"{window_width}x{window_height}")

center_window(root, window_width, window_height)

button_frame = tk.Frame(root, bg="#1e1e1e")  # Dark background color
button_frame.place(relx=0.5, rely=0.5, anchor="center")

# Define button texts and corresponding script names
buttons = [
    ("Spectogram", "Spectogram.py"),
    ("Waveform", "Waveform.py"),
    ("Amplitude vs Frequency", "Amplitude-Frequency-Visualizer.py"),
    ("Intensity vs Frequency", "Intensity-vs-Frequency-and-time.py")
]

# Create buttons in a matrix layout
for i, (text, script) in enumerate(buttons):
    row, column = divmod(i, 2)  # 2 buttons per row
    create_button(button_frame, text, lambda s=script: run_visualizer(s), button_bg, button_fg, button_font, row, column)

root.mainloop()
