![alt text](https://github.com/TheShlyukov/Quiro/blob/main/Quiro_window.png)

# Quiro Audio Player
Quiro is a modern, lightweight audio player built with PyQt6. It features a clean, dark-themed interface and supports various audio formats.

## Features
* Clean, modern dark interface
* Support for multiple audio formats (MP3, WAV, FLAC, OGG, M4A)
* Playlist management
* Folder import - add all audio files from a folder at once
* Basic playback controls (play/pause, stop, next/previous)
* Volume control
* Seeking through tracks
* Time display

## Installation
### Prerequisites
Make sure you have Python 3.9+ installed on your system.

### Setup
Clone the repository:
```bash
git clone https://github.com/TheShlyukov/Quiro
cd Quiro-main
```

Install the required dependencies:
```bash
pip install -r requirements.txt
```

### Running the Application
```bash
python Quiro.py
```

### Building an Executable
You can build a standalone executable using PyInstaller:

```bash
pip install pyinstaller
pyinstaller --onefile --icon=Quiro.png Quiro.py
#Then put Quiro.png and styles.qss next to Quiro binary (dist/Quiro)
```

**Note:** `--windowed` removes the console window, and `--icon` sets the application icon.

The executable will be created in the `dist` directory.

## Usage
* **Open File:** Add a single audio file to the playlist
* **Open Folder:** Add all audio files from a folder to the playlist
* **Play/Pause:** Toggle playback of the current track
* **Stop:** Stop playback
* **Previous/Next:** Navigate between tracks in the playlist
* **Volume Control:** Adjust the volume using the slider
* **Seek:** Navigate through the current track using the position slider
* **Clear Playlist:** Remove all tracks from the playlist

## Supported File Formats
* MP3 (.mp3)
* WAV (.wav)
* FLAC (.flac)
* OGG Vorbis (.ogg)
* M4A (.m4a)

## Requirements
See `requirements.txt` for a list of dependencies.

## Acknowledgments
* PyQt6 for the GUI framework
* Qt for the design inspiration
