import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Button

# Constants
CHUNK = 1024
RATE = 22050  # Sample rate
N_BARS = 50  # Number of bars in the visualization

# Initialize plot
fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(np.arange(N_BARS), np.zeros(N_BARS), color='blue')
ax.set_ylim(0, 1)
ax.set_xlim(0, N_BARS)
ax.set_title('Real-time Audio Bar Visualization')
ax.set_xlabel('Frequency Bins')
ax.set_ylabel('Amplitude')

# Global variables
is_paused = False
color_maps = ['blue', 'green', 'red', 'purple', 'orange']
color_map_index = 0
audio_data = np.zeros(CHUNK)

# Function to update the plot
def update(frame):
    global audio_data, is_paused, bars, color_maps, color_map_index
    if not is_paused:
        # Compute the FFT of the audio data
        fft_data = np.abs(np.fft.fft(audio_data)[:N_BARS])
        # Normalize the data
        fft_data = fft_data / np.max(fft_data)
        # Update the heights and colors of the bars
        for bar, height in zip(bars, fft_data):
            bar.set_height(height)
            bar.set_color(color_maps[color_map_index])
    return bars

# Callback function for audio input stream
def audio_callback(indata, frames, time, status):
    global audio_data
    if status:
        print(status)
    audio_data = indata[:, 0]

# Function to toggle pause/resume
def toggle_pause(event):
    global is_paused
    is_paused = not is_paused
    if is_paused:
        ax.set_title('Real-time Audio Bar Visualization (Paused)')
    else:
        ax.set_title('Real-time Audio Bar Visualization')

# Function to change color
def change_color(event):
    global color_map_index
    color_map_index = (color_map_index + 1) % len(color_maps)
    update(None)  # Force an update to apply the new color

# Add pause/resume button
ax_pause = plt.axes([0.81, 0.01, 0.1, 0.075])
btn_pause = Button(ax_pause, 'Pause/Resume')
btn_pause.on_clicked(toggle_pause)

# Add change color button
ax_color = plt.axes([0.61, 0.01, 0.15, 0.075])
btn_color = Button(ax_color, 'Change Color')
btn_color.on_clicked(change_color)

# Start the audio input stream
stream = sd.InputStream(callback=audio_callback, channels=1, samplerate=RATE, blocksize=CHUNK)
stream.start()

# Start the animation
ani = animation.FuncAnimation(fig, update, blit=False, interval=50)

# Show plot
plt.show()

# Stop the stream on exit
stream.stop()
stream.close()
