import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import pyaudio
import threading

FRAME_SIZE = 2048
HOP_SIZE = 512
SR = 22050 
BUFFER_SIZE = 10 

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paFloat32, channels=1, rate=SR, input=True, frames_per_buffer=HOP_SIZE)

# Initialize the plot
fig, ax = plt.subplots()
chroma_data = np.zeros((12, BUFFER_SIZE))
img = ax.imshow(chroma_data, aspect='auto', cmap='inferno', origin='lower')
fig.colorbar(img, ax=ax)
ax.set_title('Chroma Feature Visualizer')
ax.set_xlabel('Time')
ax.set_ylabel('Pitch Class')

is_paused = False

# Function to update the plot
def update(frame):
    global chroma_data, is_paused
    if not is_paused:
        data = np.frombuffer(stream.read(HOP_SIZE), dtype=np.float32)
        chroma = librosa.feature.chroma_stft(y=data, sr=SR, n_fft=FRAME_SIZE, hop_length=HOP_SIZE)
        chroma_db = librosa.amplitude_to_db(chroma, ref=np.max)
        chroma_data = np.roll(chroma_data, -1, axis=1)
        chroma_data[:, -1] = np.mean(chroma_db, axis=1)
        img.set_data(chroma_data)
    return [img]

# Function to toggle pause/resume
def toggle_pause(event):
    global is_paused
    is_paused = not is_paused

# Adding a button to pause/resume
ax_pause = plt.axes([0.81, 0.01, 0.1, 0.075])
btn_pause = plt.Button(ax_pause, 'Pause/Resume')
btn_pause.on_clicked(toggle_pause)

# Function to adjust color map
def change_colormap(event):
    current_cmap = img.get_cmap().name
    new_cmap = 'inferno' if current_cmap == 'viridis' else 'viridis'
    img.set_cmap(new_cmap)
    fig.canvas.draw()

# Adding a button to change color map
ax_colormap = plt.axes([0.61, 0.01, 0.15, 0.075])
btn_colormap = plt.Button(ax_colormap, 'Change Color Map')
btn_colormap.on_clicked(change_colormap)

# Create an animation
ani = FuncAnimation(fig, update, frames=BUFFER_SIZE, blit=True, interval=50)

# Start the plot
plt.show()

# Close the stream when done
stream.stop_stream()
stream.close()
p.terminate()
