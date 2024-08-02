import numpy as np
import sounddevice as sd
import librosa
import librosa.display
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Button

# Constants
CHUNK = 1024
RATE = 22050  # Sample rate

# Initialize plot
fig, ax = plt.subplots()
chroma_data = np.zeros((12, CHUNK // 2))
img = librosa.display.specshow(chroma_data, sr=RATE, x_axis='time', y_axis='chroma', ax=ax, cmap='viridis')
fig.colorbar(img, ax=ax)
ax.set_title('Chromagram')
ax.set_xlabel('Time')
ax.set_ylabel('Pitch Class')

is_paused = False
color_maps = ['viridis', 'inferno', 'plasma', 'magma', 'cividis']
color_map_index = 0

# Function to initialize the plot
def init():
    ax.set_xlim(0, CHUNK // 2)
    ax.set_ylim(0, 1)
    return ax,

# Function to update the plot
def update(frame):
    global chroma_data, is_paused, img
    if not is_paused:
        chromagram = librosa.feature.chroma_stft(y=audio_data, sr=RATE, n_fft=CHUNK, hop_length=CHUNK // 2)
        ax.clear()
        img = librosa.display.specshow(chromagram, sr=RATE, x_axis='time', y_axis='chroma', ax=ax, cmap=color_maps[color_map_index])
        ax.set_title('Chromagram')
    return [img]

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
        ax.set_title('Chromagram (Paused)')
    else:
        ax.set_title('Chromagram')

# Function to change color map
def change_colormap(event):
    global color_map_index
    color_map_index = (color_map_index + 1) % len(color_maps)
    # Force a redraw with the new colormap
    update(None)

# Add pause/resume button
ax_pause = plt.axes([0.81, 0.01, 0.1, 0.075])
btn_pause = Button(ax_pause, 'Pause/Resume')
btn_pause.on_clicked(toggle_pause)

# Add change color map button
ax_colormap = plt.axes([0.61, 0.01, 0.15, 0.075])
btn_colormap = Button(ax_colormap, 'Change Color Map')
btn_colormap.on_clicked(change_colormap)

# Initialize audio buffer
audio_data = np.zeros(CHUNK)

# Start the audio input stream
stream = sd.InputStream(callback=audio_callback, channels=1, samplerate=RATE, blocksize=CHUNK)
stream.start()

# Start the animation
ani = animation.FuncAnimation(fig, update, init_func=init, blit=False, interval=50)

# Show plot
plt.show()

# Stop the stream on exit
stream.stop()
stream.close()
