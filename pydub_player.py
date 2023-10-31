import sys
import time as tm
import numpy as np

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QFileDialog, QAction, QMessageBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from pydub import AudioSegment
from pydub.playback import play

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
    A simple sound player application with a graphical user interface using Pydub.
    """

    def __init__(self):
        super().__init__()

        # Initialize the Pydub audio segment
        self.audio = None
        self.timer = None
        self.stop_button = None
        self.toggle_button = None
        self.play_button = None
        self.ax = None
        self.canvas = None
        self.figure = None

        # Path to the sound file (initially empty)
        self.audio_file_path = None

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

        # Add buttons to the layout
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addWidget(self.play_button)
        layout.addWidget(self.toggle_button)
        layout.addWidget(self.stop_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Connect button clicks to event handlers
        self.play_button.clicked.connect(self.play_sound)
        self.toggle_button.clicked.connect(self.toggle_play_sound)
        self.stop_button.clicked.connect(self.stop_sound)

        # Initialize a timer to update the plot
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(10)  # Update the plot every 10 ms

        # Disable playback, pause, and stop buttons initially
        self.play_button.setEnabled(False)
        self.toggle_button.setEnabled(False)
        self.stop_button.setEnabled(False)

    def open_audio_file(self):
        """
        Open a file dialog to choose an audio file for playback.
        """
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Audio File", "",
                                                   "Audio Files (*.ogg *.wav *.mp3);;All Files (*)", options=options)
        show_message("File Loaded", "The file was successfully loaded.")

        if file_name:
            self.audio_file_path = file_name
            self.load_audio_file()
            self.play_button.setEnabled(True)
            self.toggle_button.setEnabled(True)
            self.stop_button.setEnabled(True)

    def load_audio_file(self):
        """
        Load the selected audio file and reset playback variables.
        """
        self.audio = AudioSegment.from_file(self.audio_file_path)
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
                self.audio = self.audio[self.paused_position:]
            else:
                print("Playing from the beginning")
            play(self.audio)
            self.start_time = tm.time()
            self.is_playing = True
            self.paused = False

    def toggle(self):
        """
        Toggle between pause and resume playback.
        """
        if self.paused:
            print("Resuming")
            self.audio = self.audio[self.paused_position:]
            current_time = tm.time()
            elapsed_pause_time = current_time - self.paused_time
            self.start_time += elapsed_pause_time
        else:
            print("Pausing")
            self.paused_position = (tm.time() - self.start_time) * 1000
            self.audio = self.audio[self.paused_position:]
            self.paused_time = tm.time()
        self.paused = not self.paused

    def stop_sound(self):
        """
        Stop the audio playback and reset playback variables.
        """
        if not self.audio_file_path:
            show_message("Error", "Please choose an audio file before stopping.")
            return

        print("Stopping playback")
        self.is_playing = False
        self.start_time = 0
        self.paused = False
        self.paused_time = 0

    def update_plot(self):
        """
        Update the audio waveform plot and check for the end of playback.
        """
        if self.is_playing and not self.paused:
            current_time = tm.time() - self.start_time
            sound_duration = len(self.audio) / 1000  # Convert duration to seconds
            current_time = min(current_time, sound_duration)
            time = np.linspace(0, len(self.audio) / 1000, num=len(self.audio))

            self.ax.clear()
            self.ax.plot(time, self.audio.get_array_of_samples(), linewidth=1)
            self.ax.axvline(x=current_time, color="red", linestyle=":", label="Current Time")
            self.ax.set_xlabel("Time (s)")
            self.ax.set_ylabel("Amplitude")
            self.ax.legend(loc="upper right")
            self.canvas.draw()

            if current_time >= sound_duration:
                self.stop_sound()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = SoundPlayer()
    player.show()
    sys.exit(app.exec_())
