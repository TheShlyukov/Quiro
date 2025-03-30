import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QSlider, QLabel, 
                            QFileDialog, QStyle, QListWidget, QSplitter)
from PyQt6.QtCore import Qt, QUrl, QDir
from PyQt6.QtGui import QIcon
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

class MediaPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Quiro")
        self.setGeometry(100, 100, 800, 600)
        
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
        
        # Load stylesheet
        self.load_stylesheet()

    def load_stylesheet(self):
        self.style_sheet = """/* Main window styling */
        QMainWindow {
            background-color: #2b2b2b;
        }

        /* Buttons styling */
        QPushButton {
            background-color: #3a3a3a;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            min-width: 40px;
            min-height: 40px;
        }

        QPushButton:hover {
            background-color: #4a4a4a;
        }

        QPushButton:pressed {
            background-color: #555555;
        }

        #openButton {
            background-color: #0078d7;
            font-weight: bold;
        }

        #openButton:hover {
            background-color: #0086f0;
        }

        #clearButton {
            background-color: #d73a49;
            font-weight: bold;
            min-height: 30px;
        }

        #clearButton:hover {
            background-color: #e25563;
        }

        #playButton, #stopButton, #volumeButton {
            background-color: #3a3a3a;
            border-radius: 20px;
        }

        /* Slider styling */
        QSlider {
            height: 20px;
        }

        QSlider::groove:horizontal {
            border: 1px solid #999999;
            height: 8px;
            background: #4a4a4a;
            margin: 2px 0;
            border-radius: 4px;
        }

        QSlider::handle:horizontal {
            background: #0078d7;
            border: 1px solid #0078d7;
            width: 16px;
            margin: -4px 0;
            border-radius: 8px;
        }

        QSlider::handle:horizontal:hover {
            background: #0086f0;
            border: 1px solid #0086f0;
        }

        #positionSlider::groove:horizontal {
            background: #333333;
        }

        #positionSlider::sub-page:horizontal {
            background: #0078d7;
            border-radius: 4px;
        }

        #volumeSlider::groove:horizontal {
            background: #333333;
        }

        #volumeSlider::sub-page:horizontal {
            background: #00a651;
            border-radius: 4px;
        }

        /* Time labels */
        #timeLabel {
            color: white;
            font-family: 'Arial';
            font-size: 12px;
            padding: 0 5px;
        }

        /* Now playing label */
        #nowPlayingLabel {
            color: white;
            font-family: 'Arial';
            font-size: 14px;
            font-weight: bold;
            padding: 10px;
        }

        /* Playlist styling */
        #playlistWidget {
            background-color: #333333;
            color: white;
            border: none;
            border-radius: 4px;
            alternate-background-color: #3a3a3a;
        }

        #playlistWidget::item {
            padding: 5px;
            border-radius: 2px;
        }

        #playlistWidget::item:selected {
            background-color: #0078d7;
            color: white;
        }

        #playlistWidget::item:hover {
            background-color: #444444;
        }

        /* Splitter styling */
        QSplitter::handle {
            background-color: #444444;
            height: 2px;
        }

        QSplitter::handle:hover {
            background-color: #0078d7;
        }

        /* Scrollbar styling */
        QScrollBar:vertical {
            border: none;
            background: #2b2b2b;
            width: 10px;
            margin: 0px;
        }

        QScrollBar::handle:vertical {
            background: #555555;
            min-height: 20px;
            border-radius: 5px;
        }

        QScrollBar::handle:vertical:hover {
            background: #666666;
        }

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }

        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: none;
        }

        /* File dialog styling */
        QFileDialog {
            background-color: #2b2b2b;
            color: white;
        }

        QFileDialog QListView, QFileDialog QTreeView {
            background-color: #333333;
            color: white;
        }

        QFileDialog QComboBox, QFileDialog QLineEdit {
            background-color: #3a3a3a;
            color: white;
            border: 1px solid #555555;
            border-radius: 3px;
            padding: 5px;
        }

        /* Message box styling */
        QMessageBox {
            background-color: #2b2b2b;
            color: white;
        }

        /* Tooltip styling */
        QToolTip {
            background-color: #2b2b2b;
            color: white;
            border: 1px solid #555555;
            padding: 5px;
        }
        """
        self.setStyleSheet(self.style_sheet)

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
            self.add_folder_to_playlist(folder_path)
    
    def add_folder_to_playlist(self, folder_path):
        audio_files = []
        dir = QDir(folder_path)
        
        # Set name filters for audio files
        filters = ["*.mp3", "*.wav", "*.flac", "*.ogg", "*.m4a"]
        dir.setNameFilters(filters)
        
        # Get all files matching the filters
        file_list = dir.entryInfoList(QDir.Filter.Files)
        
        for file_info in file_list:
            audio_files.append(file_info.absoluteFilePath())
        
        if audio_files:
            self.add_to_playlist(audio_files)
            if len(self.playlist) == len(audio_files):  # If these were the first tracks
                self.play_track(0)
    
    def add_to_playlist(self, file_paths):
        for file_path in file_paths:
            file_info = QUrl.fromLocalFile(file_path)
            file_name = os.path.basename(file_path)
            
            self.playlist.append({"url": file_info, "name": file_name, "path": file_path})
            self.playlist_widget.addItem(file_name)
    
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
            return
            
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()
    
    def stop(self):
        self.media_player.stop()
    
    def set_position(self, position):
        self.media_player.setPosition(position)
    
    def set_volume(self, volume):
        self.audio_output.setVolume(volume / 100.0)
    
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
