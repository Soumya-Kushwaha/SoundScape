import tkinter as tk
import subprocess

# Function to center the window on the screen
def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()  # Get the screen width
    screen_height = window.winfo_screenheight()  # Get the screen height

    x_coordinate = (screen_width - width) // 2  # Calculate x coordinate for centered window
    y_coordinate = (screen_height - height) // 2  # Calculate y coordinate for centered window

    window.geometry(f"{width}x{height}+{x_coordinate}+{y_coordinate}")  # Set window geometry

# Function to create a styled button
def create_button(frame, text, command, bg, fg, font, row, column):
    button = tk.Button(frame, text=text, command=command, bg=bg, fg=fg, relief=tk.FLAT, font=font, bd=0)
    button.config(highlightbackground=bg, highlightcolor=bg, highlightthickness=2, borderwidth=0, padx=20, pady=10)
    button.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")  # Place button in grid
    button.bind("<Enter>", lambda e, b=button: b.config(bg="#444444"))  # Change button color on hover
    button.bind("<Leave>", lambda e, b=button: b.config(bg=bg))  # Restore button color on leave

# Function to run the visualizer script
def run_visualizer(script_name):
    subprocess.Popen(["python", script_name])  # Run the script as a subprocess

root = tk.Tk()  # Create the main window
root.title("Soundscape")  # Set the window title
root.configure(bg="#1e1e1e")  # Dark background color

button_bg = "#292929"  # Dark gray button background
button_fg = "#FFFFFF"  # White button text
button_font = ("Helvetica", 12)  # Button font

window_width = 600  # Window width
window_height = 400  # Window height
root.geometry(f"{window_width}x{window_height}")  # Set window size

center_window(root, window_width, window_height)  # Center the window

button_frame = tk.Frame(root, bg="#1e1e1e")  # Frame to hold the buttons
button_frame.place(relx=0.5, rely=0.5, anchor="center")  # Center the frame

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
    create_button(button_frame, text, lambda s=script: run_visualizer(s), button_bg, button_fg, button_font, row, column)  # Create and place button

root.mainloop()  # Run the main event loop
