import sys
import time as tm
import scipy.signal as signal
import numpy as np
import pygame
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QFileDialog, QAction, \
    QMessageBox
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
        self.reverse_button = None
        self.sound = None
        self.timer = None
        self.stop_button = None
        self.toggle_button = None
        self.play_button = None
        self.ax = None
        self.canvas = None
        self.figure = None
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
        self.setWindowTitle("Sound Player")
        self.setGeometry(100, 100, 800, 600)

        # Set the application icon
        icon = QIcon("corgi.png")  # Replace with the path to your icon
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

        # Add buttons to the layout
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addWidget(self.play_button)
        layout.addWidget(self.toggle_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.reverse_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Connect button clicks to event handlers
        self.play_button.clicked.connect(self.play_sound)
        self.toggle_button.clicked.connect(self.toggle_play_sound)
        self.stop_button.clicked.connect(self.stop_sound)
        self.reverse_button.clicked.connect(self.play_reverse_sound)

        # Initialize a timer to update the plot
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(10)  # Update the plot every 10 ms

        # Disable playback, pause, and stop buttons initially
        self.play_button.setEnabled(False)
        self.toggle_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.reverse_button.setEnabled(False)

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
                try:
                    print("Playing in reverse from the end")
                    sound_data = pygame.sndarray.samples(self.sound)
                    reversed_data = np.flip(sound_data)
                    reversed_data_contiguous = np.ascontiguousarray(reversed_data)
                    reversed_sound = pygame.sndarray.make_sound(reversed_data_contiguous)
                    self.sound = reversed_sound
                    self.sound.play()
                    self.start_time = tm.time()
                except Exception as e:
                    show_message("Error", f"An error occurred while playing in reverse: {str(e)}")
                    return

            self.is_playing = True
            self.paused = False




if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = SoundPlayer()
    player.show()
    sys.exit(app.exec_())
