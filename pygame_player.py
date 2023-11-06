import sys
import time as tm

import numpy as np
import wave
import pygame
import scipy.signal as signal

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QFileDialog, QAction, \
    QMessageBox, QLabel, QLineEdit, QGridLayout, QHBoxLayout


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

    def open_trim_window(self):
        """
        Open a window to trim the audio.
        """
        self.trim_window = QMainWindow()
        self.trim_window.setWindowTitle("Trim Audio")
        self.trim_window.setGeometry(300, 200, 400, 300)

        # Create two input fields with labels for start and end time
        start_label = QLabel("Start Time:")
        end_label = QLabel("End Time:")
        start_input = QLineEdit()
        end_input = QLineEdit()
        submit_button = QPushButton("Submit")
        submit_button.clicked.connect(lambda: self.trim(start_input.text(), end_input.text()))

        # Create a horizontal layout for the input fields and button
        input_button_layout = QHBoxLayout()
        input_button_layout.addWidget(start_label)
        input_button_layout.addWidget(start_input)
        input_button_layout.addWidget(end_label)
        input_button_layout.addWidget(end_input)

        # Add the input fields and button layout to the main layout
        layout = QGridLayout()
        layout.addLayout(input_button_layout, 0, 0)

        # Add the "Submit" button in the middle of the width
        layout.addWidget(submit_button, 1, 0, 1, 2, alignment=Qt.AlignHCenter)

        # Create a widget to contain the layout
        widget = QWidget()
        widget.setLayout(layout)

        # Set the widget as the central widget of the new window
        self.trim_window.setCentralWidget(widget)

        self.trim_window.show()

    def close_trim_window(self):
        """
        Close the trim window.
        """
        if self.trim_window:
            self.trim_window.close()
            self.trim_window = None

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

        # self.export_button = QPushButton("Export Changed Sound")

        # self.trim_button = QPushButton("Trim")
        # self.trim_button.clicked.connect(self.open_trim_window)

        # Create a label and input field for specifying loudness factor
        self.volume_label = QLabel("Loudness Factor:")
        self.volume_input = QLineEdit()
        self.volume_submit_button = QPushButton("Submit volume factor and play with volume changed")
        self.volume_submit_button.clicked.connect(lambda: self.change_volume(self.volume_input.text()))

        self.tempo_label = QLabel("Tempo Factor:")
        self.tempo_input = QLineEdit()
        self.tempo_submit_button = QPushButton("Submit tempo factor and play with tempo changed")
        self.tempo_submit_button.clicked.connect(lambda: self.change_tempo(self.tempo_input.text()))

        self.noise_label = QLabel("Noise Cutoff Strength (from 0 to 1, 0.1 more hearable effect, 0.9 less hearable effect):")
        self.noise_input = QLineEdit()
        self.noise_submit_button = QPushButton("Submit noise cutoff strength. Play with noise filter")
        self.noise_submit_button.clicked.connect(lambda: self.noise_filter(self.noise_input.text()))

        # self.echo_delay_label = QLabel("Echo Delay:")
        # self.echo_delay_input = QLineEdit()
        # self.echo_attenuation_label = QLabel("Echo Attenuation:")
        # self.echo_attenuation_input = QLineEdit()
        # self.echo_submit_button = QPushButton("Submit echo delay and attenuation and play with echo effect")
        # self.echo_submit_button.clicked.connect(
        #     lambda: self.add_echo_effect(self.echo_delay_input.text(), self.echo_attenuation_input.text()))

        self.fade_in_label = QLabel("Fade in time")
        self.fade_in_input = QLineEdit()
        self.fade_in_submit_button = (QPushButton("Submit fade in time"))
        self.fade_in_submit_button.clicked.connect(lambda: self.fade_in(self.fade_in_input.text()))

        self.fade_out_label = QLabel("Fade out time")
        self.fade_out_input = QLineEdit()
        self.fade_out_submit_button = (QPushButton("Submit fade out time"))
        self.fade_out_submit_button.clicked.connect(lambda: self.fade_out(self.fade_out_input.text()))

        # Add buttons to the layout
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addWidget(self.play_button)
        layout.addWidget(self.toggle_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.reverse_button)

        # layout.addWidget(self.trim_button)
        # layout.addWidget(self.export_button)

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

        # # Add echo label, input and echo submit button to the layout
        # layout.addWidget(self.echo_delay_label)
        # layout.addWidget(self.echo_delay_input)
        # layout.addWidget(self.echo_attenuation_label)
        # layout.addWidget(self.echo_attenuation_input)
        #
        # layout.addWidget(self.echo_submit_button)

        layout.addWidget(self.fade_in_label)
        layout.addWidget(self.fade_in_input)
        layout.addWidget(self.fade_in_submit_button)

        layout.addWidget(self.fade_out_label)
        layout.addWidget(self.fade_out_input)
        layout.addWidget(self.fade_out_submit_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Connect button clicks to event handlers
        self.play_button.clicked.connect(self.play_sound)
        self.toggle_button.clicked.connect(self.toggle_play_sound)
        self.stop_button.clicked.connect(self.stop_sound)
        self.reverse_button.clicked.connect(self.play_reverse_sound)

        # self.export_button.clicked.connect(lambda: self.export_changed_sound("changed_sound.wav"))

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
        # self.echo_submit_button.setEnabled(False)
        self.fade_in_submit_button.setEnabled(False)
        self.fade_out_submit_button.setEnabled(False)
        # self.export_button.setEnabled(False)
        # self.trim_button.setEnabled(False)



    def open_audio_file(self):
        """
        Open a file dialog to choose an audio file for playback.
        """
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Audio File", "",
                                                   "Audio Files (*.wav);;All Files (*)", options=options)

        if file_name:
            self.audio_file_path = file_name
            self.load_audio_file()
            self.play_button.setEnabled(True)
            self.toggle_button.setEnabled(True)
            self.stop_button.setEnabled(True)
            self.reverse_button.setEnabled(True)
            # self.echo_submit_button.setEnabled(True)
            self.fade_in_submit_button.setEnabled(True)
            self.fade_out_submit_button.setEnabled(True)
            # self.export_button.setEnabled(True)
            # self.trim_button.setEnabled(True)

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

    # def export_changed_sound(self, output_file_path):
    #     """
    #     Export the changed sound with effects to a file.
    #
    #     Args:
    #         output_file_path (str): The path where the exported sound file will be saved.
    #     """
    #     if not self.sound:
    #         show_message("Error", "No sound is loaded to export.")
    #         return
    #
    #     if self.paused:
    #         show_message("Error", "Please resume the audio with effects before exporting.")
    #         return
    #
    #     # Stop the current playback
    #     pygame.mixer.stop()
    #
    #     # Export the sound with effects to the specified file
    #     sound = pygame.sndarray.samples(self.sound)
    #     sound = AudioSegment.from_numpy_array(sound) # dont use this, its pydub
    #     sound.export(output_file_path, format="wav")
    #
    #     # Display a success message
    #     show_message("Export Successful", f"The changed sound has been exported to {output_file_path}")

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

    def add_echo_effect(self, delay, attenuation):
        """
        Add an echo effect to the loaded audio file.
        """
        try:
            delay = float(delay)
            attenuation = float(attenuation)
        except ValueError:
            show_message("Error", "Please enter valid numbers for delay and attenuation.")
            return

        self.canvas.setVisible(True)

        if not self.is_playing:
            print("Adding echo effect")
            sound_data = pygame.sndarray.samples(self.sound)

            # Calculate the length of the echo in samples
            echo_length = int(delay * self.sample_rate)
            print("Calculating echo length", delay, self.sample_rate)

            # Initialize an array for the echo data
            echo_data = np.zeros_like(sound_data)

            # Add the echo effect to the sound
            for i in range(echo_length, len(sound_data)):
                echo_data[i] = sound_data[i] + attenuation * sound_data[i - echo_length]

            # Combine the original and echo data
            combined_data = np.clip(sound_data + echo_data, -32768, 32767)

            combined_data_contiguous = np.ascontiguousarray(combined_data)
            combined_sound = pygame.sndarray.make_sound(combined_data_contiguous)

            self.sound = combined_sound
            self.sound.play()
            self.start_time = tm.time()

            self.is_playing = True
            self.paused = False

    # def trim(self, start_time, end_time):
    #     """
    #     Trim the sound to the given start and end times.
    #     """
    #
    #     if not self.is_playing:
    #         show_message("Error", "Please play the audio before trimming.")
    #         return
    #
    #     self.canvas.setVisible(True)
    #     if self.paused:
    #         show_message("Error", "Please resume the audio before trimming.")
    #         return
    #
    #     print("Trimming")
    #     pygame.mixer.stop()
    #     sound_data = pygame.sndarray.samples(self.sound)
    #     start_index = int(start_time * 1000)
    #     end_index = int(end_time * 1000)
    #     sound_data = sound_data[start_index:end_index]
    #     sound_data_contiguous = np.ascontiguousarray(sound_data)
    #     self.sound = pygame.sndarray.make_sound(sound_data_contiguous)
    #     self.sound.play()
    #     self.start_time = tm.time()

    def fade_in(self, duration_seconds):
        """
        Apply a fade-in effect to the loaded audio file.
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
            show_message("Error", "Fade-in duration exceeds audio duration.")
            return

        self.canvas.setVisible(True)
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

                # Reshape the fade-in envelope to match the shape of sound_data
                fade_in_envelope = fade_in_envelope[:, np.newaxis]

                # Reshape sound_data to match the shape of fade_in_envelope
                sound_data = sound_data[:fade_in_samples]

                # Apply the fade-in effect to the audio data
                volumed_data = np.multiply(sound_data, fade_in_envelope)
                volumed_data = volumed_data.astype(np.int16)

                volumed_data_contiguous = np.ascontiguousarray(volumed_data)
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

    def plot_spectrogram(audio_data, sample_rate):
        """
        Generate and display a spectrogram of the audio data.
        """
        # Calculate the spectrogram using the scipy.signal.spectrogram function
        f, t, Sxx = signal.spectrogram(audio_data, sample_rate)

        # Plot the spectrogram
        plt.figure(figsize=(10, 5))
        plt.pcolormesh(t, f, 10 * np.log10(Sxx), shading='auto', cmap='viridis')
        plt.title('Spectrogram')
        plt.xlabel('Time (s)')
        plt.ylabel('Frequency (Hz)')
        plt.colorbar(label='Power/Frequency (dB/Hz)')
        plt.tight_layout()
        plt.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = SoundPlayer()
    player.show()
    sys.exit(app.exec_())
