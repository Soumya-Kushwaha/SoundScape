*This file contains the instructions for installing and running the SoundScape project on your system.*

## Requirements
To run SoundScape, you need to have Python 3.6 or higher and pip installed on your system. You also need a microphone and speakers or headphones to interact with the soundscape.

## Dependencies
SoundScape depends on the following Python libraries:

- PyAudio: for recording and playing audio
- PySimpleGUI: for creating the soundscape visualization
- NumPy: for numerical computations
- SciPy: for signal processing
- Matplotlib: for creating canvases

You can install these dependencies using the following command in your terminal:
```
pip install -r requirements.txt
```

Alternatively, you can clone this repository and install the dependencies manually:
```
git clone https://github.com/Soumya-Kushwaha/SoundScape.git
cd SoundScape
pip install -r requirements.txt
```

## Running the project
*Soundscape consists of multiple files with different use cases:*

### Files can be used directly from their source code or eveyting can be accesed from Index.py

### 1. Waveform
This file simply visualizes the waveform of audio detected in real time. To view the waveform, run the code:
```
python waveform.py
```

### 2. Spectogram
This file visualizes the spectogram of the audio detected in real time. To view the spectogram, run the code:
```
python spectogram.py
```

### 3. Amplitude vs Frequency
This file visualizes the amplitude v/s frequency of the audio detected in real time. To view the amplitude v/s frequency graph, run the code:
```
python amplitude-frequency-visualizer.py
```

<br>

*These codes will open a new output window that displays the soundscape visualization. You can use your microphone to interact with the soundscape. The soundscape will change its shape, color, and movement according to the sound input.*
