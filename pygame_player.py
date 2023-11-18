import sys
import time as tm

import numpy as np
import wave
import pygame
import scipy.signal as signal
from scipy.io.wavfile import write
import librosa.display

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QFileDialog, QAction, \
    QMessageBox, QLabel, QLineEdit, QGridLayout, QHBoxLayout, QDialog


def show_message(title, message):
    """
    Show a message box with the given title and message.

    Args:
        title (str): The title of the message box.
        message (str): The message to display in the box.
    """
    msg_box = QMessageBox()
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.exec_()


class SoundPlayer(QMainWindow):
    """
    A simple sound player application with a graphical user interface.
    """

    def __init__(self):
        super().__init__()

        # Initialize the pygame library

        self.sound = None
        self.timer = None
        self.ax = None
        self.canvas = None
        self.figure = None
        self.trim_window = None
        pygame.init()

        # Path to the sound file (initially empty)
        self.audio_file_path = None

        # Initialize the sound player
        pygame.mixer.init()

        # Initialize the graphical user interface
        self.init_ui()

        # Variables to track the start time of playback, playback state, and pause state
        self.start_time = 0
        self.is_playing = False
        self.paused = False
        self.paused_time = 0
        self.paused_position = 0

    def init_ui(self):
        """
        Initialize the user interface elements and layout.
        """
        # Set the window title and size
        self.setWindowTitle("Sound Player")
        self.setGeometry(100, 100, 1200, 900)

        # Set the application icon
        icon = QIcon("corgi.png")
        self.setWindowIcon(icon)

        # Create a menu
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")

        # File open action
        open_action = QAction("Open File", self)
        open_action.triggered.connect(self.open_audio_file)
        file_menu.addAction(open_action)

        # Create and configure the plot (added outside the view)
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.canvas.setParent(self)
        self.canvas.setVisible(False)

        # Create buttons
        self.play_button = QPushButton("Play")
        self.toggle_button = QPushButton("Pause/Resume")
        self.stop_button = QPushButton("Stop")
        self.reverse_button = QPushButton("Play in Reverse")
        # self.plot_spectrogram_button = QPushButton("Create spectogram plot")
        # self.show_spectrogram_button = QPushButton("Show spectogram plot")
        self.plot_and_show_spectrogram_button = QPushButton("Create and show spectogram plot")
        self.save_audio_file_button = QPushButton("Save audio file")

        # Create a label and input field for specifying loudness factor
        self.volume_label = QLabel("Loudness Factor:")
        self.volume_input = QLineEdit()
        self.volume_submit_button = QPushButton("Submit volume factor and play with volume changed")
        self.volume_submit_button.clicked.connect(lambda: self.change_volume(self.volume_input.text()))

        self.tempo_label = QLabel("Tempo Factor:")
        self.tempo_input = QLineEdit()
        self.tempo_submit_button = QPushButton("Submit tempo factor and play with tempo changed")
        self.tempo_submit_button.clicked.connect(lambda: self.change_tempo(self.tempo_input.text()))

        self.noise_label = QLabel(
            "Noise Cutoff Strength (from 0 to 1, 0.1 more hearable effect, 0.9 less hearable effect):")
        self.noise_input = QLineEdit()
        self.noise_submit_button = QPushButton("Submit noise cutoff strength. Play with noise filter")
        self.noise_submit_button.clicked.connect(lambda: self.noise_filter(self.noise_input.text()))

        self.fade_in_label = QLabel("Fade in time")
        self.fade_in_input = QLineEdit()
        self.fade_in_submit_button = QPushButton("Submit fade in time")
        self.fade_in_submit_button.clicked.connect(lambda: self.fade_in(self.fade_in_input.text()))

        self.fade_out_label = QLabel("Fade out time")
        self.fade_out_input = QLineEdit()
        self.fade_out_submit_button = QPushButton("Submit fade out time")
        self.fade_out_submit_button.clicked.connect(lambda: self.fade_out(self.fade_out_input.text()))

        # Add buttons to the layout
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addWidget(self.play_button)
        layout.addWidget(self.toggle_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.reverse_button)

        # Add tempo label, input and tempo submit button to the layout
        layout.addWidget(self.tempo_label)
        layout.addWidget(self.tempo_input)
        layout.addWidget(self.tempo_submit_button)

        # Add volume label, input and volume submit button to the layout
        layout.addWidget(self.volume_label)
        layout.addWidget(self.volume_input)
        layout.addWidget(self.volume_submit_button)

        # Add noise label, input and noise submit button to the layout
        layout.addWidget(self.noise_label)
        layout.addWidget(self.noise_input)
        layout.addWidget(self.noise_submit_button)

        layout.addWidget(self.fade_in_label)
        layout.addWidget(self.fade_in_input)
        layout.addWidget(self.fade_in_submit_button)

        layout.addWidget(self.fade_out_label)
        layout.addWidget(self.fade_out_input)
        layout.addWidget(self.fade_out_submit_button)

        layout.addWidget(self.plot_and_show_spectrogram_button)
        layout.addWidget(self.save_audio_file_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Connect button clicks to event handlers
        self.play_button.clicked.connect(self.play_sound)
        self.toggle_button.clicked.connect(self.toggle_play_sound)
        self.stop_button.clicked.connect(self.stop_sound)
        self.reverse_button.clicked.connect(self.play_reverse_sound)
        self.plot_and_show_spectrogram_button.clicked.connect(lambda: self.plot_and_show_spectrogram("spectrogram.png"))
        self.save_audio_file_button.clicked.connect(lambda: self.save_audio_file("output.wav"))

        # Initialize a timer to update the plot
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(100)  # Update the plot every 100 ms

        # Disable playback, pause, and stop buttons initially
        self.play_button.setEnabled(False)
        self.toggle_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.reverse_button.setEnabled(False)

        self.volume_submit_button.setEnabled(False)
        self.tempo_submit_button.setEnabled(False)
        self.noise_submit_button.setEnabled(False)

        self.fade_in_submit_button.setEnabled(False)
        self.fade_out_submit_button.setEnabled(False)
        self.plot_and_show_spectrogram_button.setEnabled(False)
        self.save_audio_file_button.setEnabled(False)

    def open_audio_file(self):
        """
        Open a file dialog to choose an audio file for playback.
        """
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Audio File", "",
                                                   "Audio Files (*.wav);;All Files (*)", options=options)

        if file_name:
            self.audio_file_path = file_name
            self.output_file_path = "output.wav"
            self.load_audio_file()
            self.play_button.setEnabled(True)
            self.toggle_button.setEnabled(True)
            self.stop_button.setEnabled(True)
            self.reverse_button.setEnabled(True)
            self.fade_in_submit_button.setEnabled(True)
            self.fade_out_submit_button.setEnabled(True)
            self.plot_and_show_spectrogram_button.setEnabled(True)
            self.save_audio_file_button.setEnabled(True)

            self.volume_submit_button.setEnabled(True)
            self.tempo_submit_button.setEnabled(True)
            self.noise_submit_button.setEnabled(True)

    def load_audio_file(self):
        """
        Load the selected audio file and reset playback variables.
        """
        pygame.mixer.init()
        self.sound = pygame.mixer.Sound(self.audio_file_path)
        self.start_time = 0
        self.is_playing = False
        self.paused = False
        self.paused_time = 0
        self.paused_position = 0
        self.sample_rate = wave.open(self.audio_file_path).getframerate()
        self.channel_count = wave.open(self.audio_file_path).getnchannels()

    def toggle_play_sound(self):
        """
        Toggle between pause and resume playback if the sound is playing.
        """
        if not self.is_playing:
            show_message("Error", "You can't pause if the sound is not playing.")
        else:
            self.toggle()

    def play_sound(self):
        """
        Play the loaded audio file from the beginning
        """

        self.canvas.setVisible(True)
        if not self.is_playing:

            print("Starting playback")

            length_seconds = pygame.mixer.Sound(self.audio_file_path).get_length()

            if self.paused:
                print("Resuming")
                pygame.mixer.unpause()
            else:
                print("Playing from the beginning")
                self.sound = pygame.mixer.Sound(self.audio_file_path)
                self.sound.play()
                self.start_time = tm.time()
            self.is_playing = True
            self.paused = False

    def toggle(self):
        """
        Toggle between pause and resume playback.
        """
        if self.paused:
            print("Resuming")
            pygame.mixer.unpause()
            current_time = tm.time()
            elapsed_pause_time = current_time - self.paused_time
            self.start_time += elapsed_pause_time
        else:
            print("Pausing")
            pygame.mixer.pause()
            self.paused_time = tm.time()
            self.paused_position = pygame.mixer.music.get_pos() / 1000
        self.paused = not self.paused

    def stop_sound(self):
        """
        Stop the audio playback and reset playback variables.
        """

        print("Stopping playback")
        pygame.mixer.stop()
        self.is_playing = False
        self.start_time = 0
        self.paused = False
        self.paused_time = 0

    def update_plot(self):
        """
        Update the audio waveform plot and check for the end of playback.
        """
        if self.is_playing and not self.paused:
            y, sr = pygame.sndarray.samples(self.sound), pygame.mixer.get_init()[0]
            current_time = tm.time() - self.start_time
            sound_duration = len(y) / sr
            current_time = min(current_time, sound_duration)
            time = np.linspace(0, len(y) / sr, num=len(y))

            self.ax.clear()
            self.ax.plot(time, y, linewidth=1)
            self.ax.axvline(x=current_time, color="red", linestyle=":", label="Current Time")
            self.ax.set_xlabel("Time (s)")
            self.ax.set_ylabel("Amplitude")
            self.ax.legend(loc="upper right")
            self.canvas.draw()

            if current_time >= sound_duration:
                self.stop_sound()

    def play_reverse_sound(self):
        """
        Play the loaded audio file in reverse.
        """

        self.canvas.setVisible(True)
        if not self.is_playing:

            print("Starting reverse playback")
            if self.paused:
                print("Resuming reverse playback")
                pygame.mixer.unpause()
            else:

                print("Playing in reverse from the end")
                sound_data = pygame.sndarray.samples(self.sound)
                reversed_data = np.flip(sound_data)
                reversed_data_contiguous = np.ascontiguousarray(reversed_data)
                reversed_sound = pygame.sndarray.make_sound(reversed_data_contiguous)
                self.sound = reversed_sound
                self.sound.play()
                self.start_time = tm.time()

            self.is_playing = True
            self.paused = False

    def change_volume(self, volume_factor):
        """
        play the loaded audio file with changed volume.
        """
        try:
            volume_factor = float(volume_factor)
        except ValueError:
            show_message("Error", "Please enter a valid number for the volume factor.")
            return

        self.canvas.setVisible(True)
        if not self.is_playing:

            print("Starting playback with changed volume")
            if self.paused:
                print("Resuming playback with changed volume")
                pygame.mixer.unpause()
            else:

                print("Playing with changed volume ")
                sound_data = pygame.sndarray.samples(self.sound)
                volumed_data = np.multiply(sound_data, volume_factor)
                volumed_data = volumed_data.astype(np.int16)

                volumed_data_contiguous = np.ascontiguousarray(volumed_data)
                volumed_sound = pygame.sndarray.make_sound(volumed_data_contiguous)
                self.sound = volumed_sound
                self.sound.play()
                self.start_time = tm.time()

            self.is_playing = True
            self.paused = False

    def change_tempo(self, tempo_factor):
        """
        Play the loaded audio slower.
        """
        try:
            tempo_factor = float(tempo_factor)
        except ValueError:
            show_message("Error", "Please enter a valid number for the speed factor.")
            return

        self.canvas.setVisible(True)
        if not self.is_playing:

            print("Starting playback with changed tempo")
            if self.paused:
                print("Resuming playback with changed tempo")
                pygame.mixer.unpause()
            else:

                print("Playing slower with changed tempo")

                sound_data = pygame.sndarray.samples(self.sound)

                changed_tempo_data = signal.resample(sound_data, int(sound_data.shape[0] * 1 / tempo_factor), axis=0)

                # cast slower_data to int16
                changed_tempo_data = changed_tempo_data.astype(np.int16)

                slower_data_contiguous = np.ascontiguousarray(changed_tempo_data)
                slower_sound = pygame.sndarray.make_sound(slower_data_contiguous)

                self.sound = slower_sound
                self.sound.play()
                self.start_time = tm.time()

            self.is_playing = True
            self.paused = False

    def noise_filter(self, noise_cutoff_frequency):
        """
        Play the loaded audio file with noise filter.
        """
        try:
            noise_cutoff_frequency = float(noise_cutoff_frequency)
            noise_cutoff_frequency = np.clip(noise_cutoff_frequency, 0, 1)
        except ValueError:
            show_message("Error", "Please enter a valid number for the noise cutoff strength (from 0 to 1).")
            return

        self.canvas.setVisible(True)
        if not self.is_playing:

            print("Starting playback with noise filter")
            if self.paused:
                print("Resuming playback with noise filter")
                pygame.mixer.unpause()
            else:

                print("Playing with noise filter")

                sound_data = pygame.sndarray.samples(self.sound)

                # filter the sound data

                b, a = signal.butter(5, noise_cutoff_frequency, 'low', analog=False)
                filtered_data = signal.filtfilt(b, a, sound_data, axis=0)

                # cast filtered_data to int16
                filtered_data = filtered_data.astype(np.int16)

                filtered_data_contiguous = np.ascontiguousarray(filtered_data)
                filtered_sound = pygame.sndarray.make_sound(filtered_data_contiguous)

                self.sound = filtered_sound
                self.sound.play()
                self.start_time = tm.time()

            self.is_playing = True
            self.paused = False

    def fade_in(self, duration_seconds):
        """
        Apply a fade-in effect to the loaded audio file without shortening the original audio.
        """
        try:
            duration_seconds = float(duration_seconds)
        except ValueError:
            show_message("Error", "Please enter a valid number for the duration.")
            return

        # Check if the user-entered duration is longer than the audio duration
        audio_duration = self.sound.get_length()

        if duration_seconds > audio_duration:
            show_message("Error", "Fade-in duration exceeds audio duration.")
            return

        if not self.is_playing:
            print("Starting playback with fade-in effect")
            if self.paused:
                print("Resuming playback with fade-in effect")
                pygame.mixer.unpause()
            else:
                sound_data = pygame.sndarray.samples(self.sound)
                total_samples = sound_data.shape[0]

                # Calculate the number of samples for the fade-in effect using self.sample_rate
                fade_in_samples = int(duration_seconds * self.sample_rate)
                fade_in_samples = min(fade_in_samples, total_samples)

                # Create a fade-in envelope
                fade_in_envelope = np.linspace(0, 1, fade_in_samples)

                # Apply the fade-in effect to the audio data
                sound_data[:fade_in_samples] = sound_data[:fade_in_samples] * fade_in_envelope[:, np.newaxis]
                volumed_data_contiguous = np.ascontiguousarray(sound_data)
                volumed_sound = pygame.sndarray.make_sound(volumed_data_contiguous)
                self.sound = volumed_sound
                self.sound.play()
                self.start_time = tm.time()

            self.is_playing = True
            self.paused = False

    def fade_out(self, duration_seconds):
        """
        Apply a fade-out effect to the loaded audio file.
        """
        try:
            duration_seconds = float(duration_seconds)
        except ValueError:
            show_message("Error", "Please enter a valid number for the duration.")
            return

        # Check if the user-entered duration is longer than the audio duration
        audio_duration = self.sound.get_length()

        # Check if the user-entered duration is longer than the audio duration
        if duration_seconds > audio_duration:
            show_message("Error", "Fade-out duration exceeds audio duration.")
            return

        self.canvas.setVisible(True)
        if not self.is_playing:

            print("Starting playback with fade-out effect")
            if self.paused:
                print("Resuming playback with fade-out effect")
                pygame.mixer.unpause()
            else:
                sound_data = pygame.sndarray.samples(self.sound)
                total_samples = sound_data.shape[0]

                # Calculate the number of samples for the fade-out effect using self.sample_rate
                fade_out_samples = int(duration_seconds * self.sample_rate)
                fade_out_samples = min(fade_out_samples, total_samples)

                # Create a fade-out envelope
                fade_out_envelope = np.linspace(1, 0, fade_out_samples)

                # Reshape the fade-out envelope to match the shape of sound_data
                fade_out_envelope = fade_out_envelope[:, np.newaxis]

                # Determine the starting point for the fade-out effect
                start_index = total_samples - fade_out_samples

                # Apply the fade-out effect to the audio data
                volumed_data = sound_data.copy()
                volumed_data[start_index:] = np.multiply(volumed_data[start_index:], fade_out_envelope)
                volumed_data = volumed_data.astype(np.int16)

                volumed_data_contiguous = np.ascontiguousarray(volumed_data)
                volumed_sound = pygame.sndarray.make_sound(volumed_data_contiguous)
                self.sound = volumed_sound
                self.sound.play()
                self.start_time = tm.time()

            self.is_playing = True
            self.paused = False

    def plot_and_show_spectrogram(self, save_path="spectrogram.png"):
        """
        Plot and show the spectrogram of the loaded audio file.
        """
        # Load audio data
        y, sr = librosa.load(self.output_file_path, sr=self.sample_rate)

        # Compute the spectrogram
        D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)

        # Get the time axis
        times = librosa.times_like(D)

        # Plot the spectrogram
        plt.figure(figsize=(12, 6))
        librosa.display.specshow(D, sr=sr, x_coords=times, x_axis='time', y_axis='log')
        plt.colorbar(format='%+2.0f dB')
        plt.title('Spectrogram')

        # Save the spectrogram image
        plt.savefig(save_path)
        plt.close()

        # Create a new window (QDialog)
        spectrogram_window = QDialog(self)
        spectrogram_window.setWindowTitle('Spectrogram Window')

        # Load the saved spectrogram image
        pixmap = QPixmap(save_path)

        # Create a QLabel and set the pixmap
        label = QLabel(spectrogram_window)
        label.setPixmap(pixmap)

        # Set up layout
        layout = QVBoxLayout(spectrogram_window)
        layout.addWidget(label)

        spectrogram_window.exec_()

    def save_audio_file(self, output_file_path):
        """
        Save the loaded audio file to a WAV file.
        """
        # Get the raw sound data from the pygame.mixer.Sound object
        sound_array = pygame.sndarray.array(self.sound)
        sound_array = sound_array[::2]

        # Save the sound data to a WAV file using scipy
        write(output_file_path, self.sample_rate, sound_array)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = SoundPlayer()
    player.show()
    sys.exit(app.exec_())
