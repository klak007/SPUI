import sys
import time as tm
import scipy.signal as signal
import numpy as np
import wave
import pygame
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QFileDialog, QAction, \
    QMessageBox, QLabel, QLineEdit, QGridLayout, QHBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


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
        # Initialize a variable to hold the trim window
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
        self.setWindowTitle("Sound Player")
        self.setGeometry(100, 100, 800, 600)

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

        # create button that leads to the window for trimming

        # Create buttons
        self.play_button = QPushButton("Play")
        self.toggle_button = QPushButton("Pause/Resume")
        self.stop_button = QPushButton("Stop")
        self.reverse_button = QPushButton("Play in Reverse")

        self.trim_button = QPushButton("Trim")
        self.trim_button.clicked.connect(self.open_trim_window)

        self.saveas_button = QPushButton("Save As")


        # Create a label and input field for specifying loudness factor
        self.volume_label = QLabel("Loudness Factor:")
        self.volume_input = QLineEdit()
        self.volume_submit_button = QPushButton("Submit volume factor and play with volume changed")
        self.volume_submit_button.clicked.connect(lambda: self.change_volume(self.volume_input.text()))

        self.tempo_label = QLabel("Tempo Factor:")
        self.tempo_input = QLineEdit()
        self.tempo_submit_button = QPushButton("Submit tempo factor and play with tempo changed")
        self.tempo_submit_button.clicked.connect(lambda: self.change_tempo(self.tempo_input.text()))

        self.noise_label = QLabel("Noise Cutoff Frequency:")
        self.noise_input = QLineEdit()
        self.noise_submit_button = QPushButton("Submit noise cutoff strength (from 0 to 1). and play with noise filter")
        self.noise_submit_button.clicked.connect(lambda: self.noise_filter(self.noise_input.text()))

        # Add buttons to the layout
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addWidget(self.play_button)
        layout.addWidget(self.toggle_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.reverse_button)
        layout.addWidget(self.trim_button)
        layout.addWidget(self.saveas_button)

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

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Connect button clicks to event handlers
        self.play_button.clicked.connect(self.play_sound)
        self.toggle_button.clicked.connect(self.toggle_play_sound)
        self.stop_button.clicked.connect(self.stop_sound)
        self.reverse_button.clicked.connect(self.play_reverse_sound)
        self.saveas_button.clicked.connect(self.saveas)

        # Initialize a timer to update the plot
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(10)  # Update the plot every 10 ms

        # Disable playback, pause, and stop buttons initially
        self.play_button.setEnabled(False)
        self.toggle_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.reverse_button.setEnabled(False)
        self.trim_button.setEnabled(False)
        self.saveas_button.setEnabled(False)

        self.volume_submit_button.setEnabled(False)
        self.tempo_submit_button.setEnabled(False)
        self.noise_submit_button.setEnabled(False)

    def open_audio_file(self):
        """
        Open a file dialog to choose an audio file for playback.
        """
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Audio File", "",
                                                   "Audio Files (*.ogg *.wav *.mp3);;All Files (*)", options=options)

        if file_name:
            self.audio_file_path = file_name
            self.load_audio_file()
            self.play_button.setEnabled(True)
            self.toggle_button.setEnabled(True)
            self.stop_button.setEnabled(True)
            self.reverse_button.setEnabled(True)
            self.trim_button.setEnabled(True)
            self.saveas_button.setEnabled(True)

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
        Play the loaded audio file, either from the beginning or resume from a pause.
        """
        if not self.audio_file_path:
            show_message("Error", "Please choose an audio file before playing.")
            return

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
        if not self.audio_file_path:
            show_message("Error", "Please choose an audio file before stopping.")
            return

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
        if not self.audio_file_path:
            show_message("Error", "Please choose an audio file before playing in reverse.")
            return

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
        if not self.audio_file_path:
            show_message("Error", "Please choose an audio file before changing loudness.")
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
        if not self.audio_file_path:
            show_message("Error", "Please choose an audio file before playing in reverse.")
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
        if not self.audio_file_path:
            show_message("Error", "Please choose an audio file before playing in reverse.")
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
    def trim(self, start_time, end_time):
        """
        Trim the sound to the given start and end times.
        """
        if not self.audio_file_path:
            show_message("Error", "Please choose an audio file before trimming.")
            return

        if not self.is_playing:
            show_message("Error", "Please play the audio before trimming.")
            return

        self.canvas.setVisible(True)
        if self.paused:
            show_message("Error", "Please resume the audio before trimming.")
            return

        print("Trimming")
        pygame.mixer.stop()
        sound_data = pygame.sndarray.samples(self.sound)
        start_index = int(start_time * 1000)
        end_index = int(end_time * 1000)
        sound_data = sound_data[start_index:end_index]
        sound_data_contiguous = np.ascontiguousarray(sound_data)
        self.sound = pygame.sndarray.make_sound(sound_data_contiguous)
        self.sound.play()
        self.start_time = tm.time()

    def saveas(self, output_filename):
        """
        Save the sound to a file.
        """
        if not self.audio_file_path:
            show_message("Error", "Please choose an audio file before saving.")
            return

        # Create a Pygame Sound object from the sound data
        sound_data = pygame.sndarray.samples(self.sound)
        sound = pygame.sndarray.make_sound(sound_data)

        # Initialize Pygame Mixer
        pygame.mixer.init(frequency=sample_rate, size=sample_width * 8, channels=channels)

        # Play the sound to Pygame Mixer
        sound.play()

        # Wait until the sound finishes playing
        pygame.time.wait(int(sound.get_length() * 1000))

        # Stop Pygame Mixer
        pygame.mixer.quit()

        # Save the sound data as a WAV file
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(sample_width)
            wf.setframerate(sample_rate)
            wf.writeframes(sound_data.tobytes())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = SoundPlayer()
    player.show()
    sys.exit(app.exec_())
