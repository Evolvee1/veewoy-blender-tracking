import sys
import cv2
from PyQt5.QtWidgets import (
    QApplication, QLabel, QPushButton, QVBoxLayout, QWidget, QFileDialog,
    QTabWidget, QHBoxLayout, QLineEdit, QTextEdit, QSlider, QSizePolicy
)
from PyQt5.QtGui import QImage, QPixmap, QFontDatabase, QFont, QIcon
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt
import asyncio
import threading
import websockets
import json
import mediapipe as mp

class CameraTab(QWidget):
    def __init__(self, status_callback):
        super().__init__()
        self.status_callback = status_callback
        self.image_label = QLabel()
        self.image_label.setScaledContents(False)
        self.image_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.start_button = QPushButton("Start Camera")
        self.stop_button = QPushButton("Stop Camera")
        self.extract_button = QPushButton("Extract Pose to JSON")
        self.toggle_tracking_button = QPushButton("Toggle Tracking Overlay")
        self.tracking_enabled = False
        self.toggle_tracking_button.setCheckable(True)
        self.toggle_tracking_button.clicked.connect(self.toggle_tracking)
        self.output_line = QLineEdit()
        self.output_browse = QPushButton("Save As...")
        self.output_browse.clicked.connect(self.select_output)
        self.start_button.clicked.connect(self.start_camera)
        self.stop_button.clicked.connect(self.stop_camera)
        self.extract_button.clicked.connect(self.extract_pose)
        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        btn_row = QHBoxLayout()
        btn_row.addWidget(self.start_button)
        btn_row.addWidget(self.stop_button)
        btn_row.addWidget(self.toggle_tracking_button)
        layout.addLayout(btn_row)
        out_row = QHBoxLayout()
        out_row.addWidget(self.output_line)
        out_row.addWidget(self.output_browse)
        layout.addLayout(out_row)
        layout.addWidget(self.extract_button)
        self.setLayout(layout)
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.last_frame = None
        # MediaPipe pose
        self.mp_pose = mp.solutions.pose
        self.pose = None
        self.mp_drawing = mp.solutions.drawing_utils

    def toggle_tracking(self):
        self.tracking_enabled = not self.tracking_enabled
        if self.tracking_enabled:
            self.toggle_tracking_button.setText("Tracking ON")
            self.status_callback("Tracking overlay enabled.")
            if self.pose is None:
                try:
                    self.pose = self.mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)
                except Exception as e:
                    self.status_callback(f"Error initializing pose model: {e}")
                    self.pose = None
        else:
            self.toggle_tracking_button.setText("Tracking OFF")
            self.status_callback("Tracking overlay disabled.")
            if self.pose is not None:
                try:
                    self.pose.close()
                except Exception:
                    pass
                self.pose = None

    def select_output(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Keypoints JSON", "", "JSON Files (*.json)")
        if path:
            self.output_line.setText(path)

    def start_camera(self):
        self.cap = cv2.VideoCapture(0)
        self.timer.start(30)
        self.status_callback("Camera started.")

    def stop_camera(self):
        self.timer.stop()
        if self.cap:
            self.cap.release()
            self.cap = None
        if self.pose is not None:
            self.pose.close()
            self.pose = None
        self.status_callback("Camera stopped.")

    def update_frame(self):
        if self.cap:
            ret, frame = self.cap.read()
            if ret:
                # Always process tracking on new frame if enabled
                processed_frame = frame.copy()
                try:
                    if self.tracking_enabled and self.pose is not None:
                        image_rgb = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
                        results = self.pose.process(image_rgb)
                        if results and results.pose_landmarks:
                            self.mp_drawing.draw_landmarks(
                                processed_frame, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
                except Exception as e:
                    self.status_callback(f"Tracking error: {e}")
                self.last_frame = processed_frame
                self._update_preview_pixmap()

    def extract_pose(self):
        # Placeholder for pose extraction logic
        out_path = self.output_line.text()
        if not out_path:
            self.status_callback("Please select an output file.")
            return
        self.status_callback(f"Pose extraction (camera) would save to: {out_path}")
        # TODO: Integrate MediaPipe extraction here

    def resizeEvent(self, event):
        self._update_preview_pixmap()
        super().resizeEvent(event)

    def _update_preview_pixmap(self):
        if self.last_frame is not None:
            rgb = cv2.cvtColor(self.last_frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            bytes_per_line = ch * w
            qt_img = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_img)
            label_size = self.image_label.size()
            scaled_pixmap = pixmap.scaled(label_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(scaled_pixmap)

class VideoTab(QWidget):
    def __init__(self, status_callback):
        super().__init__()
        self.status_callback = status_callback
        self.video_line = QLineEdit()
        self.video_browse = QPushButton("Browse Video...")
        self.output_line = QLineEdit()
        self.output_browse = QPushButton("Save As...")
        self.extract_button = QPushButton("Extract Pose to JSON")
        self.preview_label = QLabel()
        self.preview_label.setScaledContents(False)
        self.preview_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.play_button = QPushButton("Play")
        self.pause_button = QPushButton("Pause")
        self.toggle_tracking_button = QPushButton("Toggle Tracking Overlay")
        self.toggle_tracking_button.setCheckable(True)
        self.toggle_tracking_button.setText("Tracking OFF")
        self.tracking_enabled = False
        self.toggle_tracking_button.clicked.connect(self.toggle_tracking)
        self.video_browse.clicked.connect(self.select_video)
        self.output_browse.clicked.connect(self.select_output)
        self.extract_button.clicked.connect(self.extract_pose)
        self.play_button.clicked.connect(self.play_video)
        self.pause_button.clicked.connect(self.pause_video)
        layout = QVBoxLayout()
        layout.addWidget(self.preview_label)
        in_row = QHBoxLayout()
        in_row.addWidget(self.video_line)
        in_row.addWidget(self.video_browse)
        layout.addLayout(in_row)
        out_row = QHBoxLayout()
        out_row.addWidget(self.output_line)
        out_row.addWidget(self.output_browse)
        layout.addLayout(out_row)
        btn_row = QHBoxLayout()
        btn_row.addWidget(self.play_button)
        btn_row.addWidget(self.pause_button)
        btn_row.addWidget(self.toggle_tracking_button)
        layout.addLayout(btn_row)
        layout.addWidget(self.extract_button)
        self.setLayout(layout)
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.current_frame = None
        self.mp_pose = mp.solutions.pose
        self.pose = None
        self.mp_drawing = mp.solutions.drawing_utils
        self.frame_pos = 0
        self.total_frames = 0
        self.fps = 30
        self.video_loaded = False

    def toggle_tracking(self):
        self.tracking_enabled = not self.tracking_enabled
        if self.tracking_enabled:
            self.toggle_tracking_button.setText("Tracking ON")
            self.status_callback("Tracking overlay enabled.")
            if self.pose is None:
                self.pose = self.mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)
        else:
            self.toggle_tracking_button.setText("Tracking OFF")
            self.status_callback("Tracking overlay disabled.")
            if self.pose is not None:
                self.pose.close()
                self.pose = None

    def select_video(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Video File", "", "Video Files (*.mp4 *.avi *.mov)")
        if path:
            self.video_line.setText(path)
            self.cap = cv2.VideoCapture(path)
            if self.cap.isOpened():
                self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
                self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30
                self.frame_pos = 0
                self.video_loaded = True
                self.status_callback(f"Loaded video: {path} ({self.total_frames} frames @ {self.fps:.2f} fps)")
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                self.update_frame()
            else:
                self.status_callback("Failed to load video.")
                self.video_loaded = False

    def play_video(self):
        if self.cap and self.video_loaded:
            self.timer.start(int(1000 / self.fps))
            self.status_callback("Playing video.")

    def pause_video(self):
        self.timer.stop()
        self.status_callback("Paused video.")

    def update_frame(self):
        if self.cap and self.video_loaded:
            ret, frame = self.cap.read()
            if not ret:
                self.timer.stop()
                self.status_callback("End of video.")
                return
            self.frame_pos += 1
            # Always process tracking on new frame if enabled
            processed_frame = frame.copy()
            if self.tracking_enabled and self.pose is not None:
                image_rgb = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
                results = self.pose.process(image_rgb)
                if results.pose_landmarks:
                    self.mp_drawing.draw_landmarks(
                        processed_frame, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
            self.current_frame = processed_frame
            self._update_preview_pixmap()

    def select_output(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Keypoints JSON", "", "JSON Files (*.json)")
        if path:
            self.output_line.setText(path)

    def extract_pose(self):
        video_path = self.video_line.text()
        out_path = self.output_line.text()
        if not video_path or not out_path:
            self.status_callback("Please select both video and output file.")
            return
        self.status_callback(f"Pose extraction (video) would run on: {video_path}, output: {out_path}")
        # TODO: Integrate MediaPipe extraction here

    def resizeEvent(self, event):
        self._update_preview_pixmap()
        super().resizeEvent(event)

    def _update_preview_pixmap(self):
        if self.current_frame is not None:
            rgb = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            bytes_per_line = ch * w
            qt_img = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_img)
            label_size = self.preview_label.size()
            scaled_pixmap = pixmap.scaled(label_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.preview_label.setPixmap(scaled_pixmap)

class AudioTab(QWidget):
    def __init__(self, status_callback):
        super().__init__()
        self.audio_line = QLineEdit()
        self.audio_browse = QPushButton("Browse Audio...")
        self.output_line = QLineEdit()
        self.output_browse = QPushButton("Save As...")
        self.extract_button = QPushButton("Extract Phonemes to JSON")
        self.audio_browse.clicked.connect(self.select_audio)
        self.output_browse.clicked.connect(self.select_output)
        self.extract_button.clicked.connect(self.extract_phonemes)
        layout = QVBoxLayout()
        in_row = QHBoxLayout()
        in_row.addWidget(self.audio_line)
        in_row.addWidget(self.audio_browse)
        layout.addLayout(in_row)
        out_row = QHBoxLayout()
        out_row.addWidget(self.output_line)
        out_row.addWidget(self.output_browse)
        layout.addLayout(out_row)
        layout.addWidget(self.extract_button)
        self.setLayout(layout)
        self.status_callback = status_callback

    def select_audio(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Audio File", "", "Audio Files (*.wav *.mp3)")
        if path:
            self.audio_line.setText(path)

    def select_output(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Phonemes JSON", "", "JSON Files (*.json)")
        if path:
            self.output_line.setText(path)

    def extract_phonemes(self):
        audio_path = self.audio_line.text()
        out_path = self.output_line.text()
        if not audio_path or not out_path:
            self.status_callback("Please select both audio and output file.")
            return
        self.status_callback(f"Phoneme extraction would run on: {audio_path}, output: {out_path}")
        # TODO: Integrate Whisper + Gentle extraction here

class LiveLinkServerThread(QThread):
    status_signal = pyqtSignal(str)

    def __init__(self, host='localhost', port=8765):
        super().__init__()
        self.host = host
        self.port = port
        self.running = False
        self.loop = None
        self.server = None

    async def handler(self, websocket, path):
        self.status_signal.emit(f"Client connected: {websocket.remote_address}")
        try:
            while self.running:
                # Send dummy pose/phoneme data as JSON
                data = {"type": "pose", "frame": 0, "keypoints": [{"x": 0.5, "y": 0.5}]}
                await websocket.send(json.dumps(data))
                await asyncio.sleep(0.1)
        except Exception as e:
            self.status_signal.emit(f"WebSocket error: {e}")

    async def start_server(self):
        self.server = await websockets.serve(self.handler, self.host, self.port)
        self.status_signal.emit(f"WebSocket server started at ws://{self.host}:{self.port}")
        await self.server.wait_closed()

    def run(self):
        self.running = True
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_until_complete(self.start_server())
        except Exception as e:
            self.status_signal.emit(f"Server error: {e}")
        finally:
            self.loop.close()

    def stop(self):
        self.running = False
        if self.server:
            self.loop.call_soon_threadsafe(self.server.close)
        self.status_signal.emit("WebSocket server stopped.")

class LiveLinkTab(QWidget):
    def __init__(self, status_callback):
        super().__init__()
        self.status_callback = status_callback
        self.server_thread = None
        self.start_button = QPushButton("Start Live Link Server")
        self.stop_button = QPushButton("Stop Live Link Server")
        self.start_button.clicked.connect(self.start_server)
        self.stop_button.clicked.connect(self.stop_server)
        layout = QVBoxLayout()
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        self.setLayout(layout)

    def start_server(self):
        if self.server_thread and self.server_thread.isRunning():
            self.status_callback("Server already running.")
            return
        self.server_thread = LiveLinkServerThread()
        self.server_thread.status_signal.connect(self.status_callback)
        self.server_thread.start()
        self.status_callback("Starting WebSocket server...")

    def stop_server(self):
        if self.server_thread:
            self.server_thread.stop()
            self.server_thread.quit()
            self.server_thread.wait()
            self.status_callback("WebSocket server stopped.")
        else:
            self.status_callback("Server not running.")

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Animation Extraction GUI")
        self.tabs = QTabWidget()
        self.status_box = QTextEdit()
        self.status_box.setReadOnly(True)
        self.camera_tab = CameraTab(self.update_status)
        self.video_tab = VideoTab(self.update_status)
        self.audio_tab = AudioTab(self.update_status)
        self.livelink_tab = LiveLinkTab(self.update_status)
        self.tabs.addTab(self.camera_tab, "Live Camera")
        self.tabs.addTab(self.video_tab, "Video File")
        self.tabs.addTab(self.audio_tab, "Audio/Phoneme")
        self.tabs.addTab(self.livelink_tab, "Live Link")
        self.font_slider = QSlider(Qt.Horizontal)
        self.font_slider.setMinimum(8)
        self.font_slider.setMaximum(32)
        self.font_slider.setValue(10)
        self.font_slider.setTickInterval(1)
        self.font_slider.setTickPosition(QSlider.TicksBelow)
        self.font_slider.valueChanged.connect(self.change_font_size)
        font_label = QLabel("Font Size:")
        font_row = QHBoxLayout()
        font_row.addStretch(1)
        font_row.addWidget(font_label)
        font_row.addWidget(self.font_slider)
        font_row.setAlignment(Qt.AlignRight)
        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        layout.addWidget(QLabel("Status:"))
        layout.addWidget(self.status_box)
        layout.addLayout(font_row)
        self.setLayout(layout)

    def update_status(self, msg):
        self.status_box.append(msg)

    def change_font_size(self, value):
        font = QApplication.instance().font()
        font.setPointSize(value)
        QApplication.instance().setFont(font)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # Set the app icon globally (shows in taskbar and window frame)
    app.setWindowIcon(QIcon('assets/veewoy.ico'))
    # Load Inter font
    font_id = QFontDatabase.addApplicationFont('assets/Inter-Regular.ttf')
    if font_id != -1:
        family = QFontDatabase.applicationFontFamilies(font_id)[0]
        app.setFont(QFont(family, 10))
    # Set dark style
    app.setStyleSheet('''
        QWidget {
            background-color: #232323;
            color: #F0F0F0;
            font-family: "Inter", sans-serif;
        }
        QTabWidget::pane, QTabBar::tab, QLineEdit, QTextEdit, QPushButton {
            border: 1px solid #353535;
            background-color: #2c2c2c;
        }
        QTabBar::tab:selected {
            background: #353535;
        }
        QTabBar::tab:!selected {
            background: #232323;
        }
        QLineEdit, QTextEdit {
            background-color: #232323;
            color: #F0F0F0;
        }
        QPushButton {
            background-color: #353535;
            color: #F0F0F0;
        }
        QLabel {
            color: #F0F0F0;
        }
    ''')
    win = MainWindow()
    win.setWindowIcon(QIcon('assets/veewoy.ico'))
    # Optionally show a system tray icon
    try:
        from PyQt5.QtWidgets import QSystemTrayIcon
        tray_icon = QSystemTrayIcon(QIcon('assets/veewoy.ico'), parent=win)
        tray_icon.setToolTip('Veewoy Animation Extraction')
        tray_icon.show()
    except Exception:
        pass
    win.show()
    sys.exit(app.exec_()) 