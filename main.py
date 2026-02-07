"""
手勢識別 Demo 主程式

一個獨立的視窗應用程式，展示即時手勢識別功能。
支援 macOS Metal 硬體加速。
"""

import sys
import time

# 記錄啟動開始時間
_startup_start_time = time.time()

# 必須在導入 PyQt6 之前設置 Metal 後端
import config  # 這會設置環境變數

_after_config_time = time.time()
print(f"⏱️  配置載入: {(_after_config_time - _startup_start_time)*1000:.1f} ms")

import cv2
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QPushButton, QLabel, QComboBox
)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QImage, QPixmap

_after_imports_time = time.time()
print(f"⏱️  PyQt6/OpenCV 載入: {(_after_imports_time - _after_config_time)*1000:.1f} ms")

from utils.hand_detector import HandDetector, MEDIAPIPE_AVAILABLE
from models.gesture_model import DummyModel
from utils.performance_monitor import PerformanceMonitor

_after_modules_time = time.time()
print(f"⏱️  自定義模組載入: {(_after_modules_time - _after_imports_time)*1000:.1f} ms")


class GestureRecognitionWindow(QMainWindow):
    """手勢識別主視窗"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("手勢識別 Demo")
        self.setGeometry(100, 100, 900, 600)
        
        # 初始化變數
        self.camera = None
        self.detector = None
        self.model = None
        self.is_detecting = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        
        # 效能監控
        self.performance_monitor = PerformanceMonitor()
        self.perf_timer = QTimer()
        self.perf_timer.timeout.connect(self.update_performance)
        self.perf_timer.start(config.PERF_UPDATE_INTERVAL_MS)
        
        print(f"📊 效能監控已啟動")
        if self.performance_monitor.gpu_available:
            print(f"   GPU 類型: {self.performance_monitor.gpu_type}")
        
        # 設置 UI
        self.setup_ui()
        
        # 初始化模型
        self.init_model()
    
    def setup_ui(self):
        """設置使用者界面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主要布局
        main_layout = QHBoxLayout(central_widget)
        
        # 左側：攝影機預覽
        left_layout = QVBoxLayout()
        
        self.camera_label = QLabel("攝影機預覽")
        self.camera_label.setMinimumSize(640, 480)
        self.camera_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.camera_label.setStyleSheet("""
            QLabel {
                background-color: #2b2b2b;
                color: #888;
                border: 2px solid #444;
                border-radius: 5px;
                font-size: 16px;
            }
        """)
        left_layout.addWidget(self.camera_label)
        
        # 控制按鈕
        button_layout = QHBoxLayout()
        
        # 攝影機選擇下拉選單
        camera_select_layout = QHBoxLayout()
        camera_label = QLabel("攝影機:")
        camera_label.setStyleSheet("font-size: 12px; color: #666;")
        camera_select_layout.addWidget(camera_label)
        
        self.camera_combo = QComboBox()
        self.camera_combo.setMinimumHeight(30)
        self.camera_combo.addItems(self._list_cameras())
        self.camera_combo.setStyleSheet("""
            QComboBox {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 5px;
                font-size: 12px;
            }
        """)
        camera_select_layout.addWidget(self.camera_combo)
        left_layout.addLayout(camera_select_layout)
        
        self.start_button = QPushButton("開始偵測")
        self.start_button.setMinimumHeight(40)
        self.start_button.clicked.connect(self.toggle_detection)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        button_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("停止偵測")
        self.stop_button.setMinimumHeight(40)
        self.stop_button.clicked.connect(self.stop_detection)
        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:pressed {
                background-color: #c1150a;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        button_layout.addWidget(self.stop_button)
        
        left_layout.addLayout(button_layout)
        
        # 右側：手勢資訊
        right_layout = QVBoxLayout()
        
        # 標題
        title_label = QLabel("🤖 手勢識別結果")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #333;
                padding: 10px;
            }
        """)
        right_layout.addWidget(title_label)
        
        # 手勢名稱顯示
        gesture_container = QWidget()
        gesture_container.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                border: 2px solid #ddd;
                border-radius: 10px;
            }
        """)
        gesture_layout = QVBoxLayout(gesture_container)
        
        self.gesture_label = QLabel("等待偵測...")
        self.gesture_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.gesture_label.setStyleSheet("""
            QLabel {
                font-size: 48px;
                font-weight: bold;
                color: #2196F3;
                padding: 30px;
                background-color: white;
                border-radius: 8px;
            }
        """)
        gesture_layout.addWidget(self.gesture_label)
        
        right_layout.addWidget(gesture_container)
        
        # 信心度顯示
        self.confidence_label = QLabel("信心度: --")
        self.confidence_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #666;
                padding: 10px;
            }
        """)
        right_layout.addWidget(self.confidence_label)
        
        # 手部資訊
        self.hand_info_label = QLabel("手部: --")
        self.hand_info_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #888;
                padding: 10px;
            }
        """)
        right_layout.addWidget(self.hand_info_label)
        
        # 狀態資訊
        self.status_label = QLabel("狀態: 就緒")
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #999;
                padding: 10px;
                border-top: 1px solid #ddd;
            }
        """)
        right_layout.addWidget(self.status_label)
        
        # 效能監控資訊
        perf_container = QWidget()
        perf_container.setStyleSheet("""
            QWidget {
                background-color: #f9f9f9;
                border: 1px solid #e0e0e0;
                border-radius: 5px;
                margin-top: 10px;
            }
        """)
        perf_layout = QVBoxLayout(perf_container)
        
        perf_title = QLabel("📊 效能監控")
        perf_title.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #555;
                padding: 5px;
            }
        """)
        perf_layout.addWidget(perf_title)
        
        self.cpu_label = QLabel("CPU: --")
        self.cpu_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #666;
                padding: 3px 10px;
            }
        """)
        perf_layout.addWidget(self.cpu_label)
        
        self.memory_label = QLabel("記憶體: --")
        self.memory_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #666;
                padding: 3px 10px;
            }
        """)
        perf_layout.addWidget(self.memory_label)
        
        self.gpu_label = QLabel("GPU: --")
        self.gpu_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #666;
                padding: 3px 10px;
            }
        """)
        perf_layout.addWidget(self.gpu_label)
        
        right_layout.addWidget(perf_container)
        
        right_layout.addStretch()
        
        # 將左右布局加入主布局
        main_layout.addLayout(left_layout, 2)  # 左側佔 2/3
        main_layout.addLayout(right_layout, 1)  # 右側佔 1/3
    
    def _list_cameras(self):
        """列出可用的攝影機及其名稱
        
        注意: 攝影機順序已調整,讓 FaceTime HD 為索引 0
        """
        cameras = []
        
        # macOS 使用 system_profiler 獲取攝影機名稱
        camera_names_original = self._get_camera_names_macos()
        
        # system_profiler 輸出順序: [FaceTime HD, iPhone]
        # OpenCV 實際順序: 0=iPhone, 1=FaceTime HD
        # 需要反轉才能正確配對
        camera_names = camera_names_original[::-1] if len(camera_names_original) > 1 else camera_names_original
        
        # 先檢測所有可用攝影機
        available_cameras = []
        for i in range(10):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                available_cameras.append((i, width, height))
                cap.release()
        
        # 如果有兩個攝影機,交換它們的順序
        # 讓 FaceTime HD 變成索引 0
        if len(available_cameras) >= 2:
            available_cameras[0], available_cameras[1] = available_cameras[1], available_cameras[0]
            # 同時交換名稱
            if len(camera_names) >= 2:
                camera_names[0], camera_names[1] = camera_names[1], camera_names[0]
        
        # 建立顯示列表
        for new_idx, (original_idx, width, height) in enumerate(available_cameras):
            if new_idx < len(camera_names):
                name = camera_names[new_idx]
                cameras.append(f"{original_idx}: {name} ({width}x{height})")
            else:
                cameras.append(f"{original_idx}: 攝影機 {original_idx} ({width}x{height})")
        
        if not cameras:
            cameras.append("0: 攝影機 0 (預設)")
        
        return cameras
    
    def _get_camera_names_macos(self):
        """獲取 macOS 攝影機名稱列表"""
        import platform
        if platform.system() != "Darwin":
            return []
        
        try:
            import subprocess
            # 使用 system_profiler 獲取攝影機資訊
            result = subprocess.run(
                ["system_profiler", "SPCameraDataType"],
                capture_output=True,
                text=True,
                timeout=3
            )
            
            # 解析輸出，尋找攝影機名稱
            camera_names = []
            lines = result.stdout.split('\n')
            
            for line in lines:
                stripped = line.strip()
                
                # 攝影機名稱格式: "    FaceTime HD相機:" 或 "    Akai's iphone相機:"
                # 特徵: 有縮排、包含"相機"或"Camera"、結尾是冒號
                if (("相機:" in stripped or "Camera:" in stripped) and 
                    stripped.endswith(":") and 
                    not stripped.startswith("Camera:")):  # 排除 "Camera:" 標題
                    
                    # 移除冒號
                    name = stripped.rstrip(":")
                    camera_names.append(name)
            
            # 如果解析失敗,嘗試簡單方法
            if not camera_names:
                # 查找包含 "Model ID" 的行來推斷有多少攝影機
                model_count = result.stdout.count("Model ID:")
                for i in range(model_count):
                    camera_names.append(f"攝影機 {i}")
            
            return camera_names
            
        except Exception as e:
            print(f"⚠️  無法獲取攝影機名稱: {e}")
            return []
    
    def init_model(self):
        """初始化 AI 模型"""
        try:
            self.model = DummyModel()
            self.model.load_model()
            self.status_label.setText("狀態: 模型載入完成（Demo 模式）")
            print("✅ AI 模型載入完成")
        except Exception as e:
            self.status_label.setText(f"狀態: 模型載入失敗 - {e}")
            print(f"❌ 模型載入失敗: {e}")
    
    def toggle_detection(self):
        """切換偵測狀態"""
        if not self.is_detecting:
            self.start_detection()
        else:
            self.stop_detection()
    
    def start_detection(self):
        """開始手勢偵測"""
        if not MEDIAPIPE_AVAILABLE:
            self.status_label.setText("錯誤: MediaPipe 未安裝")
            return
        
        try:
            # 獲取選擇的攝影機編號
            # 格式: "0: FaceTime HD相機 (1920x1080)" -> 提取數字 0
            camera_text = self.camera_combo.currentText()
            
            # 提取冒號前的數字
            if ":" in camera_text:
                camera_index = int(camera_text.split(":")[0])
            else:
                # 後備方案: 尋找數字
                import re
                match = re.search(r'\d+', camera_text)
                camera_index = int(match.group()) if match else 0
            
            # 開啟攝影機
            self.camera = cv2.VideoCapture(camera_index)
            if not self.camera.isOpened():
                self.status_label.setText(f"錯誤: 無法開啟攝影機 {camera_index}")
                return
            
            # 設置攝影機解析度（使用配置）
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAMERA_WIDTH)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAMERA_HEIGHT)
            
            # 初始化手部偵測器（使用配置）
            self.detector = HandDetector(
                max_num_hands=config.MEDIAPIPE_MAX_HANDS,
                min_detection_confidence=config.MEDIAPIPE_MIN_DETECTION_CONFIDENCE,
                min_tracking_confidence=config.MEDIAPIPE_MIN_TRACKING_CONFIDENCE,
                model_complexity=config.MEDIAPIPE_MODEL_COMPLEXITY
            )
            
            # 更新狀態
            self.is_detecting = True
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.camera_combo.setEnabled(False)  # 🔒 偵測中禁用攝影機選單
            self.status_label.setText("狀態: 偵測中...")
            
            # 啟動定時器（使用配置）
            self.timer.start(config.UI_UPDATE_INTERVAL_MS)
            
            print("✅ 開始手勢偵測")
            print(f"   攝影機: {config.CAMERA_WIDTH}x{config.CAMERA_HEIGHT} @ {config.CAMERA_FPS} FPS")
            print(f"   更新頻率: {1000/config.UI_UPDATE_INTERVAL_MS:.1f} FPS")
            
        except Exception as e:
            self.status_label.setText(f"錯誤: {e}")
            print(f"❌ 啟動失敗: {e}")
    
    def stop_detection(self):
        """停止手勢偵測"""
        self.is_detecting = False
        self.timer.stop()
        
        if self.camera:
            self.camera.release()
            self.camera = None
        
        if self.detector:
            self.detector.close()
            self.detector = None
        
        # 更新 UI
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.camera_combo.setEnabled(True)  # 🔓 停止後重新啟用攝影機選單
        self.camera_label.setText("攝影機預覽")
        self.gesture_label.setText("等待偵測...")
        self.confidence_label.setText("信心度: --")
        self.hand_info_label.setText("手部: --")
        self.status_label.setText("狀態: 已停止")
        
        print("⏸️ 停止手勢偵測")
    
    def update_frame(self):
        """更新攝影機畫面並進行手勢識別"""
        if not self.camera or not self.is_detecting:
            return
        
        # 讀取攝影機畫面
        ret, frame = self.camera.read()
        if not ret:
            self.status_label.setText("錯誤: 無法讀取攝影機畫面")
            return
        
        # 翻轉畫面（鏡像效果）
        frame = cv2.flip(frame, 1)
        
        # 偵測手部
        landmarks_list = self.detector.detect(frame)
        
        # 繪製手部關鍵點
        frame = self.detector.draw_landmarks(frame)
        
        # 如果偵測到手部，進行手勢識別
        if landmarks_list:
            # 處理所有偵測到的手
            gestures_text = []
            
            for i, landmarks in enumerate(landmarks_list):
                # AI 模型預測
                if self.model and self.model.is_loaded:
                    result = self.model.predict(landmarks)
                    
                    # 獲取對應的手部資訊
                    hand_info = self.detector.get_hand_info()
                    if i < len(hand_info):
                        handedness, conf = hand_info[i]
                        hand_label = "🫱 右手" if handedness == "Right" else "🫲 左手"
                        gestures_text.append(f"{hand_label}: {result['gesture']}")
                    else:
                        gestures_text.append(f"手 {i+1}: {result['gesture']}")
            
            # 更新手勢顯示
            if len(gestures_text) == 1:
                self.gesture_label.setText(gestures_text[0].split(': ')[1])
                # 顯示信心度
                result = self.model.predict(landmarks_list[0])
                self.confidence_label.setText(f"信心度: {result['confidence']:.1%}")
                
                # 根據信心度改變顏色
                if result['confidence'] > 0.8:
                    color = "#4CAF50"  # 綠色
                elif result['confidence'] > 0.6:
                    color = "#FF9800"  # 橙色
                else:
                    color = "#F44336"  # 紅色
            else:
                # 雙手模式：顯示兩個手勢
                self.gesture_label.setText("\n".join(gestures_text))
                self.confidence_label.setText(f"偵測到 {len(gestures_text)} 隻手")
                color = "#2196F3"  # 藍色
            
            self.gesture_label.setStyleSheet(f"""
                QLabel {{
                    font-size: {'36px' if len(gestures_text) > 1 else '48px'};
                    font-weight: bold;
                    color: {color};
                    padding: 30px;
                    background-color: white;
                    border-radius: 8px;
                }}
            """)
            
            # 顯示手部資訊
            hand_info = self.detector.get_hand_info()
            if hand_info:
                hand_texts = []
                for handedness, conf in hand_info:
                    hand_label = "右手" if handedness == "Right" else "左手"
                    hand_texts.append(f"{hand_label} ({conf:.0%})")
                self.hand_info_label.setText("手部: " + ", ".join(hand_texts))
        else:
            self.gesture_label.setText("未偵測到手部")
            self.gesture_label.setStyleSheet("""
                QLabel {
                    font-size: 48px;
                    font-weight: bold;
                    color: #999;
                    padding: 30px;
                    background-color: white;
                    border-radius: 8px;
                }
            """)
            self.confidence_label.setText("信心度: --")
            self.hand_info_label.setText("手部: --")
        
        # 轉換為 Qt 格式並顯示
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        bytes_per_line = ch * w
        qt_image = QImage(
            frame_rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888
        )
        pixmap = QPixmap.fromImage(qt_image)
        self.camera_label.setPixmap(
            pixmap.scaled(
                self.camera_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        )
    
    def update_performance(self):
        """更新效能監控顯示"""
        try:
            metrics = self.performance_monitor.get_metrics()
            
            # 更新 CPU 標籤
            cpu_color = self._get_perf_color(
                metrics.cpu_percent, 
                config.PERF_CPU_WARNING, 
                config.PERF_CPU_DANGER
            )
            self.cpu_label.setText(f"CPU: {metrics.cpu_percent:.1f}%")
            self.cpu_label.setStyleSheet(f"""
                QLabel {{
                    font-size: 12px;
                    color: {cpu_color};
                    font-weight: bold;
                    padding: 3px 10px;
                }}
            """)
            
            # 更新記憶體標籤
            mem_color = self._get_perf_color(
                metrics.memory_mb, 
                config.PERF_MEMORY_WARNING, 
                config.PERF_MEMORY_DANGER
            )
            self.memory_label.setText(
                f"記憶體: {metrics.memory_mb:.1f} MB ({metrics.memory_percent:.1f}%)"
            )
            self.memory_label.setStyleSheet(f"""
                QLabel {{
                    font-size: 12px;
                    color: {mem_color};
                    font-weight: bold;
                    padding: 3px 10px;
                }}
            """)
            
            # 更新 GPU 標籤
            if metrics.gpu_percent is not None and metrics.gpu_percent > 0:
                gpu_color = self._get_perf_color(
                    metrics.gpu_percent, 
                    config.PERF_GPU_WARNING, 
                    config.PERF_GPU_DANGER
                )
                gpu_text = f"GPU: {metrics.gpu_percent:.1f}%"
                if metrics.gpu_memory_mb is not None and metrics.gpu_memory_mb > 0:
                    gpu_text += f" | {metrics.gpu_memory_mb:.0f} MB"
                self.gpu_label.setText(gpu_text)
                self.gpu_label.setStyleSheet(f"""
                    QLabel {{
                        font-size: 12px;
                        color: {gpu_color};
                        font-weight: bold;
                        padding: 3px 10px;
                    }}
                """)
            else:
                # 顯示 GPU 類型但無具體數據
                if self.performance_monitor.gpu_available:
                    gpu_type = self.performance_monitor.gpu_type or "Unknown"
                    self.gpu_label.setText(f"GPU: {gpu_type} (Metal 加速已啟用)")
                    self.gpu_label.setStyleSheet("""
                        QLabel {
                            font-size: 12px;
                            color: #4CAF50;
                            font-weight: bold;
                            padding: 3px 10px;
                        }
                    """)
                else:
                    self.gpu_label.setText("GPU: N/A")
                    self.gpu_label.setStyleSheet("""
                        QLabel {
                            font-size: 12px;
                            color: #999;
                            padding: 3px 10px;
                        }
                    """)
        except Exception as e:
            print(f"效能監控更新失敗: {e}")
    
    def _get_perf_color(self, value: float, warning_threshold: float, danger_threshold: float) -> str:
        """根據數值返回顏色
        
        Args:
            value: 當前數值
            warning_threshold: 警告閾值
            danger_threshold: 危險閾值
            
        Returns:
            顏色代碼
        """
        if value < warning_threshold:
            return "#4CAF50"  # 綠色 - 良好
        elif value < danger_threshold:
            return "#FF9800"  # 橙色 - 警告
        else:
            return "#F44336"  # 紅色 - 危險
    
    def closeEvent(self, event):
        """視窗關閉時清理資源"""
        self.perf_timer.stop()
        self.stop_detection()
        event.accept()


def main():
    """主程式入口"""
    app = QApplication(sys.argv)
    
    # 設置應用程式樣式
    app.setStyle('Fusion')
    
    _before_window_time = time.time()
    window = GestureRecognitionWindow()
    _after_window_time = time.time()
    print(f"⏱️  視窗初始化: {(_after_window_time - _before_window_time)*1000:.1f} ms")
    
    window.show()
    
    _total_startup_time = time.time() - _startup_start_time
    print(f"\n🚀 總啟動時間: {_total_startup_time*1000:.1f} ms ({_total_startup_time:.2f} 秒)")
    print(f"{'='*60}\n")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
