import pygame
import random
import numpy as np
import pyaudio

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("3D Particle System with Audio")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Particle settings
NUM_PARTICLES = 1000
MAX_DEPTH = 800

# PyAudio settings
CHUNK = 1024
RATE = 44100
audio_data = None

# PyAudio initialization
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

# Particle class
class Particle:
    def __init__(self):
        self.x = random.uniform(-WIDTH // 2, WIDTH // 2)
        self.y = random.uniform(-HEIGHT // 2, HEIGHT // 2)
        self.z = random.uniform(1, MAX_DEPTH)

    def update(self, audio_level):
        self.z -= audio_level * 50
        if self.z <= 0:
            self.z = MAX_DEPTH
            self.x = random.uniform(-WIDTH // 2, WIDTH // 2)
            self.y = random.uniform(-HEIGHT // 2, HEIGHT // 2)

    def draw(self, screen):
        f = 200 / self.z
        x = int(WIDTH / 2 + self.x * f)
        y = int(HEIGHT / 2 + self.y * f)
        size = int((1 - self.z / MAX_DEPTH) * 5)
        if size < 1:
            size = 1
        pygame.draw.circle(screen, WHITE, (x, y), size)

# Create particles
particles = [Particle() for _ in range(NUM_PARTICLES)]

# Main loop
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(BLACK)

    # Read audio data from microphone
    audio_data = np.frombuffer(stream.read(CHUNK), dtype=np.int16)
    audio_level = np.abs(audio_data).mean() / 32767.0  # Calculate audio level

    # Update and draw particles
    for particle in particles:
        particle.update(audio_level)
        particle.draw(screen)

    pygame.display.flip()
    clock.tick(60)

# Close PyAudio stream and terminate PyAudio
stream.stop_stream()
stream.close()
p.terminate()
pygame.quit()
