<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/PyQt6-6.5+-41CD52?style=for-the-badge&logo=qt&logoColor=white" alt="PyQt6" />
  <img src="https://img.shields.io/badge/MediaPipe-0.10+-00A6D6?style=for-the-badge&logo=google&logoColor=white" alt="MediaPipe" />
  <img src="https://img.shields.io/badge/OpenCV-4.8+-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white" alt="OpenCV" />
  <img src="https://img.shields.io/badge/Apple_Metal-GPU_Accelerated-000000?style=for-the-badge&logo=apple&logoColor=white" alt="Metal" />
</p>

# AI Visual Gesture Recognition

### Real-time Hand Tracking and Gesture Classification System

> A desktop application that performs **real-time hand detection, landmark tracking, and gesture classification** using computer vision and AI, with native **macOS Metal GPU acceleration**.
>
> AI 驅動的即時手勢辨識系統 -- 結合 MediaPipe 手部追蹤與自訂手勢分類模型，支援 macOS Metal 硬體加速。

---

## Highlights / 專案亮點

| Feature | Description |
|---------|-------------|
| **Real-time Hand Tracking** | MediaPipe 驅動的 21 點手部關鍵點追蹤，支援雙手同時偵測 |
| **8 Gesture Types** | 辨識握拳、張開手掌、比讚、YA、OK、指向、搖滾、三指等手勢 |
| **Confidence Scoring** | 每個手勢附帶信心度分數 (0-1)，基於手指彎曲角度精確計算 |
| **Metal GPU Acceleration** | macOS 原生 Metal 後端加速 PyQt6 渲染與 MediaPipe 推論 |
| **Performance Dashboard** | 即時監控 CPU、記憶體、GPU 使用率，含警告閾值系統 |
| **Extensible Model API** | 抽象基類設計，支援無縫替換為 LSTM / Transformer 等深度學習模型 |

---

## Architecture / 系統架構

```
ai-visual-gesture-recognition/
│
├── main.py                          # Desktop App (737 lines)
│                                    # PyQt6 主視窗、攝影機串流、
│                                    # UI 佈局、即時預覽與手勢顯示
│
├── config.py                        # Configuration
│                                    # Metal 加速、攝影機參數、
│                                    # MediaPipe 設定、效能閾值
│
├── models/
│   └── gesture_model.py             # Gesture AI Model (239 lines)
│                                    # GestureModel 抽象基類
│                                    # DummyModel - 規則式 8 手勢辨識
│                                    # MLModel - 深度學習模型接口（預留）
│
├── utils/
│   ├── hand_detector.py             # Hand Detection (130 lines)
│   │                                # MediaPipe Hands 封裝
│   │                                # 21 關鍵點提取、左右手辨識
│   │
│   └── performance_monitor.py       # Performance Monitor (318 lines)
│                                    # CPU/Memory/GPU 即時監控
│                                    # macOS Metal GPU 專用監控
│
├── benchmark.py                     # Benchmark Suite
│                                    # 效能評估與壓力測試
│
├── screenshot/                      # Demo Screenshots
│   └── (5 screenshots)
│
└── requirements.txt                 # Dependencies
```

---

## Tech Stack / 技術棧

```
  Vision        MediaPipe Hands  |  21-point landmark tracking
  Detection     OpenCV 4.8+  |  Real-time camera feed processing
  UI Framework  PyQt6 6.5+  |  Native desktop application
  GPU Accel.    macOS Metal backend  |  QSG_RHI_BACKEND=metal
  Monitoring    psutil + subprocess  |  CPU / Memory / Metal GPU
  Model API     Abstract Base Class  ->  Rule-based / ML pluggable
```

---

## Gesture Recognition / 手勢辨識

### Supported Gestures / 支援的手勢類型

| Gesture | Chinese | Detection Method | Confidence |
|---------|---------|-----------------|------------|
| **Fist** | 握拳 | All fingers curled | 0.95 |
| **Open Palm** | 張開手掌 | All fingers extended | 0.95 |
| **Thumbs Up** | 比讚 | Only thumb extended | 0.95 |
| **Peace / YA** | 比 YA | Index + middle extended | 0.90 |
| **OK** | 比 OK | Thumb-index circle + 3 fingers up | 0.85 |
| **Pointing** | 指向 | Only index extended | 0.90 |
| **Rock** | 搖滾 | Pinky extended, others curled | 0.85 |
| **Three** | 三 | Three fingers extended | 0.80 |

### Recognition Pipeline / 辨識流程

```
Camera Frame                         Gesture Output
    |                                     ^
    v                                     |
 [BGR -> RGB]                     [Gesture + Confidence]
    |                                     ^
    v                                     |
 [MediaPipe Hands]               [Rule Engine / ML Model]
    |                                     ^
    v                                     |
 [21 Landmarks (x,y,z)]  --->  [Finger Extension Detection]
                                [Joint Angle Calculation]
                                [Thumb-Index Distance]
```

---

## Quick Start / 快速開始

### 1. Install Dependencies / 安裝依賴

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

**Dependencies / 依賴套件:**

| Package | Version | Purpose |
|---------|---------|---------|
| `opencv-python` | >= 4.8.0 | Camera capture & image processing |
| `numpy` | >= 1.24.0 | Numerical computation |
| `mediapipe` | >= 0.10.0 | Hand landmark detection |
| `PyQt6` | >= 6.5.0 | Desktop UI framework |
| `psutil` | >= 5.9.0 | System performance monitoring |
| `gputil` | >= 1.4.0 | GPU monitoring (optional) |

### 2. Run the Application / 啟動應用

```bash
python main.py
```

Or use the provided script:

```bash
chmod +x run.sh
./run.sh
```

### 3. Usage / 使用方式

```
1. Select a camera source from the dropdown
   從下拉選單選擇攝影機

2. Click "Start Detection" to begin hand tracking
   點擊「開始偵測」啟動手部追蹤

3. Hold your hand in front of the camera
   將手放在攝影機前方

4. Recognized gestures appear in real-time with confidence scores
   辨識結果與信心度即時顯示
```

---

## Performance / 效能表現

### Metal GPU Acceleration (macOS)

The system automatically enables Apple Metal acceleration on macOS:

```python
# Enabled in config.py
os.environ["QSG_RHI_BACKEND"] = "metal"       # PyQt6 Metal rendering
os.environ["MEDIAPIPE_DISABLE_GPU"] = "0"      # MediaPipe GPU inference
```

### Performance Thresholds / 效能警告閾值

| Metric | Warning | Danger |
|--------|---------|--------|
| CPU Usage | 70% | 100% |
| Memory | 500 MB | 1000 MB |
| GPU Usage | 70% | 90% |

### Benchmarking / 效能測試

```bash
python benchmark.py
```

---

## Model Architecture / 模型架構

The project uses a **pluggable model interface** via abstract base class:

```python
class GestureModel(ABC):
    """Abstract base class for gesture recognition models"""

    @abstractmethod
    def predict(self, landmarks: np.ndarray) -> Dict[str, Any]:
        """Input: (21, 3) landmarks -> Output: {gesture, confidence, details}"""
        pass

# Current: Rule-based recognition using finger angles
class DummyModel(GestureModel): ...

# Future: Drop-in ML model replacement
class MLModel(GestureModel): ...    # LSTM / Transformer / CNN
```

### Finger Detection Algorithm / 手指偵測演算法

```
For each finger (index, middle, ring, pinky):
    extended = tip.y < pip.y    (fingertip above second joint)

For thumb:
    extended = |tip.x - mcp.x| > 0.04    (horizontal displacement)

Joint angles calculated via:
    angle = arccos( dot(BA, BC) / (|BA| * |BC|) )
```

---

## Configuration / 設定參數

All configurable via `config.py`:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `CAMERA_WIDTH` | 640 | Camera resolution width |
| `CAMERA_HEIGHT` | 480 | Camera resolution height |
| `CAMERA_FPS` | 30 | Target frame rate |
| `MEDIAPIPE_MAX_HANDS` | 2 | Max simultaneous hands |
| `MEDIAPIPE_MIN_DETECTION_CONFIDENCE` | 0.7 | Detection threshold |
| `MEDIAPIPE_MIN_TRACKING_CONFIDENCE` | 0.5 | Tracking threshold |
| `MEDIAPIPE_MODEL_COMPLEXITY` | 0 | 0=lite (fast), 1=full (accurate) |
| `UI_UPDATE_INTERVAL_MS` | 33 | UI refresh rate (~30 FPS) |

---

## Project Stats / 專案統計

```
Total Files:     35
Language:        Python + PyQt6
Main App:        737 lines (main.py)
Model Layer:     239 lines (gesture_model.py)
Hand Detector:   130 lines (hand_detector.py)
Perf. Monitor:   318 lines (performance_monitor.py)
```

---

## License

MIT License

---

<p align="center">
  <sub>Built with MediaPipe, PyQt6, and OpenCV for real-time computer vision research.</sub>
  <br />
  <sub>結合 MediaPipe、PyQt6 與 OpenCV 打造的即時電腦視覺研究應用。</sub>
</p>
