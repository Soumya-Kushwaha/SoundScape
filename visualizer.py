import numpy as np
import librosa
import matplotlib.pyplot as plt
import librosa.display

def chroma_feature_visualizer(audio_path):
    # Load the audio file
    y, sr = librosa.load(audio_path)
    
    # Compute the Short-Time Fourier Transform (STFT)
    stft = np.abs(librosa.stft(y))
    
    # Compute chroma features from the STFT
    chroma = librosa.feature.chroma_stft(S=stft, sr=sr)
    
    # Convert the chroma features to decibel scale for better visualization
    chroma_db = librosa.power_to_db(chroma, ref=np.max)
    
    # Plot the chroma features
    plt.figure(figsize=(10, 4))
    librosa.display.specshow(chroma_db, x_axis='time', y_axis='chroma', cmap='coolwarm')
    plt.colorbar(format='%+2.0f dB')
    plt.title('Chroma Features')
    plt.tight_layout()
    plt.show()

# Example usage
audio_path = 'path_to_your_audio_file.wav'
chroma_feature_visualizer(audio_path)
