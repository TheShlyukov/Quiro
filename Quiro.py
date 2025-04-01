import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QSlider, QLabel, 
                            QFileDialog, QStyle, QListWidget, QSplitter,
                            QProgressDialog, QStatusBar)
from PyQt6.QtCore import Qt, QUrl, QDir, QThread, pyqtSignal, QRunnable, QThreadPool, QObject, QTimer
from PyQt6.QtGui import QIcon
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

os.environ["QT_MEDIA_BACKEND"] = "gstreamer"

# Worker signal class for thread communication
class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(str)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)

# Worker class for background tasks
class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
            self.signals.result.emit(result)
        except Exception as e:
            self.signals.error.emit(str(e))
        finally:
            self.signals.finished.emit()

# File processor worker with progress updates
class FileProcessorWorker(QRunnable):
    def __init__(self, file_paths):
        super(FileProcessorWorker, self).__init__()
        self.file_paths = file_paths
        self.signals = WorkerSignals()

    def run(self):
        try:
            processed_files = []
            for i, file_path in enumerate(self.file_paths):
                file_info = QUrl.fromLocalFile(file_path)
                file_name = os.path.basename(file_path)
                
                processed_files.append({"url": file_info, "name": file_name, "path": file_path})
                
                # Emit progress signal for UI updates
                self.signals.progress.emit(i + 1)
            
            self.signals.result.emit(processed_files)
        except Exception as e:
            self.signals.error.emit(str(e))
        finally:
            self.signals.finished.emit()

class MediaPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Quiro")
        self.setWindowIcon(QIcon("Quiro.png"))
        self.setGeometry(100, 100, 800, 600)
        self.setMinimumSize(800, 600)
        
        # Initialize thread pool for background tasks
        self.threadpool = QThreadPool()
        
        # Create media player and audio output
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Create splitter for playlist and controls
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Create playlist widget
        self.playlist_widget = QListWidget()
        self.playlist_widget.setAlternatingRowColors(True)
        self.playlist_widget.doubleClicked.connect(self.playlist_item_double_clicked)
        self.playlist_widget.setObjectName("playlistWidget")
        
        # Create playlist controls layout
        playlist_controls = QHBoxLayout()
        
        # Add clear playlist button
        self.clear_playlist_button = QPushButton("Clear Playlist")
        self.clear_playlist_button.clicked.connect(self.clear_playlist)
        self.clear_playlist_button.setObjectName("clearButton")
        playlist_controls.addWidget(self.clear_playlist_button)
        
        playlist_controls.addStretch()
        
        # Create playlist container
        playlist_container = QWidget()
        playlist_layout = QVBoxLayout(playlist_container)
        playlist_layout.addWidget(self.playlist_widget)
        playlist_layout.addLayout(playlist_controls)
        
        # Add playlist container to splitter
        splitter.addWidget(playlist_container)
        
        # Create controls container
        controls_container = QWidget()
        controls_layout = QVBoxLayout(controls_container)
        
        # Now playing label
        self.now_playing_label = QLabel("No track playing")
        self.now_playing_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.now_playing_label.setObjectName("nowPlayingLabel")
        controls_layout.addWidget(self.now_playing_label)
        
        # Create slider and time labels layout
        slider_layout = QHBoxLayout()
        
        # Create time labels
        self.current_time_label = QLabel("00:00")
        self.current_time_label.setObjectName("timeLabel")
        self.total_time_label = QLabel("00:00")
        self.total_time_label.setObjectName("timeLabel")
        
        # Create slider for seeking
        self.position_slider = QSlider(Qt.Orientation.Horizontal)
        self.position_slider.setRange(0, 0)
        self.position_slider.sliderMoved.connect(self.set_position)
        self.position_slider.setObjectName("positionSlider")
        
        # Add widgets to slider layout
        slider_layout.addWidget(self.current_time_label)
        slider_layout.addWidget(self.position_slider)
        slider_layout.addWidget(self.total_time_label)
        
        # Add slider layout to controls layout
        controls_layout.addLayout(slider_layout)
        
        # Create buttons layout
        buttons_layout = QHBoxLayout()
        
        # Create buttons with icons from system theme
        self.open_file_button = QPushButton("Open File")
        self.open_file_button.clicked.connect(self.open_file)
        self.open_file_button.setObjectName("openButton")
        
        self.open_folder_button = QPushButton("Open Folder")
        self.open_folder_button.clicked.connect(self.open_folder)
        self.open_folder_button.setObjectName("openButton")
        
        self.play_button = QPushButton()
        self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.play_button.clicked.connect(self.toggle_play)
        self.play_button.setObjectName("playButton")
        
        self.stop_button = QPushButton()
        self.stop_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaStop))
        self.stop_button.clicked.connect(self.stop)
        self.stop_button.setObjectName("stopButton")
        
        self.prev_button = QPushButton()
        self.prev_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSkipBackward))
        self.prev_button.clicked.connect(self.play_previous)
        self.prev_button.setObjectName("playButton")
        
        self.next_button = QPushButton()
        self.next_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSkipForward))
        self.next_button.clicked.connect(self.play_next)
        self.next_button.setObjectName("playButton")
        
        # Volume slider
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_slider.setMaximumWidth(100)
        self.volume_slider.valueChanged.connect(self.set_volume)
        self.volume_slider.setObjectName("volumeSlider")
        
        # Volume icon
        self.volume_button = QPushButton()
        self.volume_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolume))
        self.volume_button.setObjectName("volumeButton")
        
        # Add widgets to buttons layout
        buttons_layout.addWidget(self.open_file_button)
        buttons_layout.addWidget(self.open_folder_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.prev_button)
        buttons_layout.addWidget(self.play_button)
        buttons_layout.addWidget(self.stop_button)
        buttons_layout.addWidget(self.next_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.volume_button)
        buttons_layout.addWidget(self.volume_slider)
        
        # Add buttons layout to controls layout
        controls_layout.addLayout(buttons_layout)
        
        # Add controls container to splitter
        splitter.addWidget(controls_container)
        
        # Set initial splitter sizes
        splitter.setSizes([400, 200])
        
        # Add splitter to main layout
        main_layout.addWidget(splitter)
        
        # Add status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Connect media player signals
        self.media_player.positionChanged.connect(self.position_changed)
        self.media_player.durationChanged.connect(self.duration_changed)
        self.media_player.playbackStateChanged.connect(self.state_changed)
        self.media_player.mediaStatusChanged.connect(self.media_status_changed)
        
        # Set initial volume
        self.audio_output.setVolume(0.7)
        
        # Playlist management
        self.playlist = []
        self.current_track_index = -1
        
        # Progress dialog for loading operations
        self.progress_dialog = None
        
        # Timer for status messages
        self.status_timer = QTimer()
        self.status_timer.setSingleShot(True)
        self.status_timer.timeout.connect(self.clear_status)
        
        # Load stylesheet
        self.load_stylesheet()

        self.media_player.errorOccurred.connect(self.handle_media_error)

    def handle_media_error(self, error, error_msg):
        self.show_status_message(f" Error: {error_msg}", 5000)

    def load_stylesheet(self):
        try:
            # Try to load stylesheet from external file
            with open("style.qss", "r") as f:
                self.style_sheet = f.read()
                self.setStyleSheet(self.style_sheet)
        except FileNotFoundError:
            # If file not found, use default stylesheet
            print("Style file not found, Using \"Null\" style")


    def show_status_message(self, message, timeout=3000):
        """Show a message in the status bar for a specified time"""
        self.status_bar.showMessage(message)
        self.status_timer.start(timeout)
    
    def clear_status(self):
        """Clear the status bar message"""
        self.status_bar.clearMessage()

    def open_file(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("Audio files (*.mp3 *.wav *.flac *.ogg *.m4a)")
        file_dialog.setViewMode(QFileDialog.ViewMode.List)
        
        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]
            self.add_to_playlist([file_path])
            if len(self.playlist) == 1:  # If this is the first track, play it
                self.play_track(0)
    
    def open_folder(self):
        folder_dialog = QFileDialog(self)
        folder_dialog.setFileMode(QFileDialog.FileMode.Directory)
        
        if folder_dialog.exec():
            folder_path = folder_dialog.selectedFiles()[0]
            
            # Show status message instead of progress dialog
            self.show_status_message(f"Scanning folder: {os.path.basename(folder_path)}...")
            
            # Create worker for folder scanning
            worker = Worker(self.scan_folder_for_audio, folder_path)
            worker.signals.result.connect(self.process_folder_scan_result)
            worker.signals.finished.connect(self.folder_scan_finished)
            worker.signals.error.connect(self.handle_worker_error)
            
            # Execute the worker
            self.threadpool.start(worker)
    
    def handle_worker_error(self, error_msg):
        print(f"Worker error: {error_msg}")
        self.show_status_message(f"Error: {error_msg}", 5000)
    
    def scan_folder_for_audio(self, folder_path):
        audio_files = []
        dir = QDir(folder_path)
        
        # Set name filters for audio files
        filters = ["*.mp3", "*.wav", "*.flac", "*.ogg", "*.m4a"]
        dir.setNameFilters(filters)
        
        # Get all files matching the filters
        file_list = dir.entryInfoList(QDir.Filter.Files)
        
        for file_info in file_list:
            audio_files.append(file_info.absoluteFilePath())
        
        return audio_files
    
    def process_folder_scan_result(self, audio_files):
        if audio_files:
            self.add_to_playlist(audio_files)
            self.show_status_message(f"Added {len(audio_files)} tracks to playlist")
            if self.current_track_index == -1:  # If no track is currently selected
                self.play_track(0)
        else:
            self.show_status_message("No audio files found in folder", 5000)
    
    def folder_scan_finished(self):
        pass  # No dialog to close
    
    def add_to_playlist(self, file_paths):
        # For small number of files, process directly without dialog
        if len(file_paths) <= 50:
            processed_files = []
            for file_path in file_paths:
                file_info = QUrl.fromLocalFile(file_path)
                file_name = os.path.basename(file_path)
                processed_files.append({"url": file_info, "name": file_name, "path": file_path})
            
            self.update_playlist_with_processed_files(processed_files)
        else:
            # Only show progress dialog for large number of files
            self.progress_dialog = QProgressDialog("Adding files to playlist...", "Cancel", 0, len(file_paths), self)
            self.progress_dialog.setWindowTitle("Adding Files")
            self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
            self.progress_dialog.setMinimumDuration(500)  # Show after 500ms
            self.progress_dialog.setValue(0)
            
            # Create worker for adding files
            worker = FileProcessorWorker(file_paths)
            worker.signals.result.connect(self.update_playlist_with_processed_files)
            worker.signals.progress.connect(self.update_add_files_progress)
            worker.signals.finished.connect(self.add_files_finished)
            worker.signals.error.connect(self.handle_worker_error)
            
            # Execute the worker
            self.threadpool.start(worker)
    
    def process_files_for_playlist(self, file_paths):
        processed_files = []
        for i, file_path in enumerate(file_paths):
            file_info = QUrl.fromLocalFile(file_path)
            file_name = os.path.basename(file_path)
            
            processed_files.append({"url": file_info, "name": file_name, "path": file_path})
            
            # Не пытаемся отправлять сигналы прогресса здесь,
            # так как у MediaPlayer нет атрибута signals
        
        return processed_files
    
    def update_add_files_progress(self, value):
        if self.progress_dialog and self.progress_dialog.isVisible():
            self.progress_dialog.setValue(value)
    
    def update_playlist_with_processed_files(self, processed_files):
        # Add the processed files to the playlist
        for file_data in processed_files:
            self.playlist.append(file_data)
            self.playlist_widget.addItem(file_data["name"])
    
    def add_files_finished(self):
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None
    
    def clear_playlist(self):
        self.stop()
        self.playlist = []
        self.playlist_widget.clear()
        self.current_track_index = -1
        self.now_playing_label.setText("No track playing")
        
        # Clear the media source to fix the bug
        self.media_player.setSource(QUrl())
        
        # Reset time labels and slider
        self.current_time_label.setText("00:00")
        self.total_time_label.setText("00:00")
        self.position_slider.setValue(0)
        self.position_slider.setRange(0, 0)
        
        self.show_status_message("Playlist cleared")
    
    def playlist_item_double_clicked(self, index):
        self.play_track(index.row())
    
    def play_track(self, index):
        if 0 <= index < len(self.playlist):
            self.current_track_index = index
            self.playlist_widget.setCurrentRow(index)
            track = self.playlist[index]
            self.media_player.setSource(track["url"])
            self.now_playing_label.setText(f"Now Playing: {track['name']}")
            self.play()
    
    def play_next(self):
        if self.playlist:
            next_index = (self.current_track_index + 1) % len(self.playlist)
            self.play_track(next_index)
    
    def play_previous(self):
        if self.playlist:
            prev_index = (self.current_track_index - 1) % len(self.playlist)
            self.play_track(prev_index)
    
    def media_status_changed(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.play_next()
    
    def play(self):
        self.media_player.play()
    
    def toggle_play(self):
        if not self.playlist:
            # If playlist is empty, don't try to play anything
            self.show_status_message("No tracks in playlist")
            return
            
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.pause()
            self.show_status_message("Paused")
        else:
            # If no track is currently selected (current_track_index == -1),
            # start playing the first track in the playlist
            if self.current_track_index == -1 and self.playlist:
                self.play_track(0)
            else:
                self.media_player.play()
                self.show_status_message("Playing")
    
    def stop(self):
        self.media_player.stop()
        if self.playlist:
            self.show_status_message("Stopped")
    
    def set_position(self, position):
        self.media_player.setPosition(position)
    
    def set_volume(self, volume):
        self.audio_output.setVolume(volume / 100.0)
        self.show_status_message(f"Volume: {volume}%", 1000)
    
    def position_changed(self, position):
        self.position_slider.setValue(position)
        
        # Update time label
        seconds = position // 1000
        minutes = seconds // 60
        seconds %= 60
        self.current_time_label.setText(f"{minutes:02d}:{seconds:02d}")
    
    def duration_changed(self, duration):
        self.position_slider.setRange(0, duration)
        
        # Update total time label
        seconds = duration // 1000
        minutes = seconds // 60
        seconds %= 60
        self.total_time_label.setText(f"{minutes:02d}:{seconds:02d}")
    
    def state_changed(self, state):
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
        else:
            self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = MediaPlayer()
    player.show()
    sys.exit(app.exec())
