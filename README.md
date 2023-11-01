# Sound Player
This is a simple sound player application with a graphical user interface built in Python using PyQt5, Pygame, and other libraries. The application allows you to open and play audio files, as well as apply various audio effects, including volume adjustment, tempo change, noise filtering, and audio trimming.

## Table of contents
* [Requirements](#requirements)
* [Features](#features)
* [Usage](#usage)
* [Application Overview](#application-overview)
* [License](#license)

## Requirements
To run this application, you need the following Python libraries installed:
* PyQt5
* Pygame
* Pydub
* Numpy
* Scipy
* Matplotlib
* Wave
You can install them using the following command:
```
pip install PyQt5 pygame numpy scipy wave pydub matplotlib
```
To install the libraries, you need to have Python 3.6 or higher installed on your computer. You can download it from the official website: https://www.python.org/downloads/
To install pydub you will need to install ffmpeg. You can download it from the official website: https://ffmpeg.org/download.html. Or install it by ffmpeg-downloader, then head over to the ffmpeg folder and add bin folder to your PATH environment variable.

## Features
* Open and play audio files
* Apply volume adjustment
* Apply tempo change
* Apply noise filtering
* Apply audio trimming
* Save audio files
* Display audio waveform

## Usage
1. Run the application by running the provided script: pygame_player.py
2. Open an audio file by clicking on the "Open" button in the menu in the upper left corner of the application window. 
3. Use the following buttons to control audio playback:
   * "Play": Start or resume audio playback.
   * "Pause/Resume": Toggle between pausing and resuming playback.
   * "Stop": Stop audio playback.
   * "Play in Reverse": Play the audio file in reverse.
   * "Export Changed Sound": Export the modified audio with effects to a WAV file.
   * "Trim": Open a window to trim the audio by specifying start and end times.
   * "Submit volume factor and play with volume changed": Change the loudness (volume) of the audio.
   * "Submit tempo factor and play with tempo changed": Change the tempo (speed) of the audio.
   * "Submit noise cutoff strength (from 0 to 1) and play with noise filter": Apply a noise filter to the audio.
4. The application provides a graphical representation of the audio waveform.
5. You can monitor the current time of playback in the plot.
6. Use the "Trim" window to specify start and end times to trim the audio.
7. You can export the modified audio with effects using the "Export Changed Sound" button.

## Application Overview
This application provides a user-friendly interface for playing and modifying audio files. It supports a variety of audio formats and allows you to apply several audio effects in real-time. The graphical representation of the audio waveform helps you visualize the audio playback.

## License
This application is open-source and distributed under the MIT License. You are free to use, modify, and distribute it as needed. Please refer to the `LICENSE` file for more details.