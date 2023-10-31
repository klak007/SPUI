import sys
import time as tm
import numpy as np
import pyaudio
import soundfile

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QFileDialog, QAction, \
    QMessageBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


def show_message(title, message):
    msg_box = QMessageBox()
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.exec_()


class SoundPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.audio = None
        self.timer = None
        self.stop_button = None
        self.toggle_button = None
        self.play_button = None
        self.ax = None
        self.canvas = None
        self.figure = None
        self.audio_file_path = None
        self.start_time = 0
        self.is_playing = False
        self.paused = False
        self.paused_time = 0
        self.paused_position = 0
        self.paudio = None
        self.stream = None

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Sound Player")
        self.setGeometry(100, 100, 800, 600)

        icon = QIcon("corgi.png")  # Replace with the path to your icon
        self.setWindowIcon(icon)

        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")

        open_action = QAction("Open File", self)
        open_action.triggered.connect(self.open_audio_file)
        file_menu.addAction(open_action)

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.canvas.setParent(self)
        self.canvas.setVisible(False)

        self.play_button = QPushButton("Play")
        self.toggle_button = QPushButton("Pause/Resume")
        self.stop_button = QPushButton("Stop")

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addWidget(self.play_button)
        layout.addWidget(self.toggle_button)
        layout.addWidget(self.stop_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.play_button.clicked.connect(self.play_sound)
        self.toggle_button.clicked.connect(self.toggle_play_sound)
        self.stop_button.clicked.connect(self.stop_sound)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(10)

        self.play_button.setEnabled(False)
        self.toggle_button.setEnabled(False)
        self.stop_button.setEnabled(False)

    def open_audio_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Audio File", "",
                                                   "Audio Files (*.wav *.flac *.ogg *.mp3);;All Files (*)",
                                                   options=options)
        show_message("File Loaded", "The file was successfully loaded.")

        if file_name:
            self.audio_file_path = file_name
            self.load_audio_file()
            self.play_button.setEnabled(True)
            self.toggle_button.setEnabled(True)
            self.stop_button.setEnabled(True)

    def load_audio_file(self):
        if not self.audio_file_path:
            show_message("Error", "Please choose an audio file before loading.")
            return

        try:
            self.audio, self.sample_rate = soundfile.read(self.audio_file_path)
        except Exception as e:
            show_message("Error", f"An error occurred while loading the audio file: {str(e)}")
            return

        self.start_time = 0
        self.is_playing = False
        self.paused = False
        self.paused_time = 0
        self.paused_position = 0

    def toggle_play_sound(self):
        if not self.is_playing:
            show_message("Error", "You can't pause if the sound is not playing.")
        else:
            self.toggle()

    def play_sound(self):
        if not self.audio_file_path:
            show_message("Error", "Please choose an audio file before playing.")
            return

        self.canvas.setVisible(True)
        if not self.is_playing:
            print("Starting playback")
            if self.paused:
                print("Resuming")
                try:
                    self.stream.start_stream()
                except Exception as e:
                    show_message("Playback Error", f"An error occurred during playback: {str(e)}")
            else:
                print("Playing from the beginning")
                try:
                    self.paudio = pyaudio.PyAudio()
                    channels = self.audio.shape[1] if len(self.audio.shape) > 1 else 1
                    self.stream = self.paudio.open(
                        format=pyaudio.paFloat32,
                        channels=channels,
                        rate=self.sample_rate,
                        output=True
                    )
                except Exception as e:
                    show_message("Playback Error", f"An error occurred during playback initialization: {str(e)}")
                    return  # Exit playback if initialization fails

                try:
                    self.stream.start_stream()
                    self.stream.write(self.audio.tobytes())
                except Exception as e:
                    show_message("Playback Error", f"An error occurred during playback: {str(e)}")

            self.start_time = tm.time()
            self.is_playing = True
            self.paused = False

    def toggle(self):
        if self.paused:
            print("Resuming")
            self.stream.start_stream()
            current_time = tm.time()
            elapsed_pause_time = current_time - self.paused_time
            self.start_time += elapsed_pause_time
        else:
            print("Pausing")
            self.stream.stop_stream()
            self.paused_time = tm.time()
        self.paused = not self.paused

    def stop_sound(self):
        if not self.audio_file_path:
            show_message("Error", "Please choose an audio file before stopping.")
            return

        print("Stopping playback")
        if self.is_playing:
            self.is_playing = False
            if self.stream is not None:
                self.stream.stop_stream()
                self.stream.close()
            if self.paudio is not None:
                self.paudio.terminate()
        self.start_time = 0
        self.paused = False
        self.paused_time = 0

    def update_plot(self):
        if self.is_playing and not self.paused:
            current_time = tm.time() - self.start_time
            sound_duration = len(self.audio) / self.sample_rate
            current_time = min(current_time, sound_duration)
            time = np.linspace(0, sound_duration, len(self.audio))

            self.ax.clear()
            self.ax.plot(time, self.audio, linewidth=1)
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
