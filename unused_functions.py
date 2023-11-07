# def open_trim_window(self):
#     """
#     Open a window to trim the audio.
#     """
#     self.trim_window = QMainWindow()
#     self.trim_window.setWindowTitle("Trim Audio")
#     self.trim_window.setGeometry(300, 200, 400, 300)
#
#     # Create two input fields with labels for start and end time
#     start_label = QLabel("Start Time:")
#     end_label = QLabel("End Time:")
#     start_input = QLineEdit()
#     end_input = QLineEdit()
#     submit_button = QPushButton("Submit")
#     submit_button.clicked.connect(lambda: self.trim(start_input.text(), end_input.text()))
#
#     # Create a horizontal layout for the input fields and button
#     input_button_layout = QHBoxLayout()
#     input_button_layout.addWidget(start_label)
#     input_button_layout.addWidget(start_input)
#     input_button_layout.addWidget(end_label)
#     input_button_layout.addWidget(end_input)
#
#     # Add the input fields and button layout to the main layout
#     layout = QGridLayout()
#     layout.addLayout(input_button_layout, 0, 0)
#
#     # Add the "Submit" button in the middle of the width
#     layout.addWidget(submit_button, 1, 0, 1, 2, alignment=Qt.AlignHCenter)
#
#     # Create a widget to contain the layout
#     widget = QWidget()
#     widget.setLayout(layout)
#
#     # Set the widget as the central widget of the new window
#     self.trim_window.setCentralWidget(widget)
#
#     self.trim_window.show()
#
#
#     def close_trim_window(self):
#         """
#         Close the trim window.
#         """
#         if self.trim_window:
#             self.trim_window.close()
#             self.trim_window = None
#
#     def init_ui(self)
        # self.export_button = QPushButton("Export Changed Sound")

        # self.trim_button = QPushButton("Trim")
        # self.trim_button.clicked.connect(self.open_trim_window)

        # self.echo_delay_label = QLabel("Echo Delay:")
        # self.echo_delay_input = QLineEdit()
        # self.echo_attenuation_label = QLabel("Echo Attenuation:")
        # self.echo_attenuation_input = QLineEdit()
        # self.echo_submit_button = QPushButton("Submit echo delay and attenuation and play with echo effect")
        # self.echo_submit_button.clicked.connect(
        #     lambda: self.add_echo_effect(self.echo_delay_input.text(), self.echo_attenuation_input.text()))


        # layout.addWidget(self.trim_button)
        # layout.addWidget(self.export_button)


        # # Add echo label, input and echo submit button to the layout
        # layout.addWidget(self.echo_delay_label)
        # layout.addWidget(self.echo_delay_input)
        # layout.addWidget(self.echo_attenuation_label)
        # layout.addWidget(self.echo_attenuation_input)
        #
        # layout.addWidget(self.echo_submit_button)

        # self.export_button.clicked.connect(lambda: self.export_changed_sound("changed_sound.wav"))

        # self.echo_submit_button.setEnabled(False)
        # self.export_button.setEnabled(False)
        # self.trim_button.setEnabled(False)

        # self.export_button.setEnabled(True)
        # self.trim_button.setEnabled(True)
        # self.echo_submit_button.setEnabled(True)

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
