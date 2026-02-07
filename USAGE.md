# 手勢識別 Demo - 使用範例

## 快速開始

### 方法 1: 使用啟動腳本（推薦）

```bash
cd gesture_recognition_demo
./run.sh
```

### 方法 2: 直接執行

```bash
cd gesture_recognition_demo
source ../.venv/bin/activate  # 啟動虛擬環境
python main.py
```

### 方法 3: 測試環境

```bash
cd gesture_recognition_demo
./test.sh  # 執行完整的環境測試
```

## 使用流程

### 1. 啟動應用程式

執行後會看到視窗界面：
- 左側：攝影機預覽區域
- 右側：手勢識別結果顯示

### 2. 開始偵測

1. 點擊「**開始偵測**」按鈕
2. 允許攝影機權限（首次使用）
3. 將手放在攝影機前

### 3. 觀察結果

右側會即時顯示：
- **手勢名稱**：如「握拳 👊」、「張開手掌 🖐️」
- **信心度**：0-100%，顏色標示（綠色=高、橙色=中、紅色=低）
- **手部資訊**：Left/Right 左/右手

### 4. 停止偵測

點擊「**停止偵測**」按鈕結束偵測

## 支援的手勢（DummyModel）

目前 Demo 模型支援以下手勢：

| 手勢 | 描述 | 判斷方式 |
|-----|------|---------|
| 握拳 👊 | 五指收攏 | 指尖與手腕距離 < 0.15 |
| 張開手掌 🖐️ | 五指伸展 | 指尖與手腕距離 > 0.25 且均勻 |
| 比讚 👍 | 拇指伸出 | 拇指距離 > 平均距離 × 1.2 |
| 比 YA ✌️ | 食指中指伸出 | （隨機示範） |
| 比 OK 👌 | 拇指食指成圈 | （隨機示範） |
| 指向 👉 | 食指伸出 | （隨機示範） |

> **注意**：DummyModel 是簡化的規則式模型，僅供展示。實際應用建議訓練自己的機器學習模型。

## 開發自己的模型

### 步驟 1: 創建模型類別

在 `models/` 目錄下創建新檔案 `my_model.py`：

```python
from models.gesture_model import GestureModel
import numpy as np

class MyGestureModel(GestureModel):
    def __init__(self, model_path):
        super().__init__(model_path)
        self.gesture_names = [
            "手勢A",
            "手勢B",
            "手勢C",
        ]
    
    def load_model(self) -> bool:
        # 載入你的模型（PyTorch、TensorFlow 等）
        # self.model = load_your_model(self.model_path)
        self.is_loaded = True
        return True
    
    def predict(self, landmarks: np.ndarray):
        # 使用模型預測
        # output = self.model.predict(landmarks)
        
        return {
            'gesture': self.gesture_names[0],
            'confidence': 0.95,
            'details': {}
        }
```

### 步驟 2: 替換模型

修改 `main.py` 中的 `init_model()` 方法：

```python
def init_model(self):
    try:
        # 原本：self.model = DummyModel()
        from models.my_model import MyGestureModel
        self.model = MyGestureModel(model_path="models/my_model.pth")
        
        self.model.load_model()
        self.status_label.setText("狀態: 自定義模型載入完成")
    except Exception as e:
        self.status_label.setText(f"狀態: 模型載入失敗 - {e}")
```

### 步驟 3: 測試模型

```bash
python main.py
```

## 手部關鍵點說明

MediaPipe Hands 提供 21 個手部關鍵點：

```
     8   12  16  20    (指尖)
     |   |   |   |
     7   11  15  19
     |   |   |   |
     6   10  14  18
     |   |   |   |
  4  5   9   13  17
  |  |   |   |   |
  3  |   |   |   |
  |  |   |   |   |
  2  |   |   |   |
  |  0---+---+---+---- 手腕
  1

0: 手腕 (Wrist)
1-4: 拇指 (Thumb)
5-8: 食指 (Index)
9-12: 中指 (Middle)
13-16: 無名指 (Ring)
17-20: 小指 (Pinky)
```

每個關鍵點包含：
- `x`: 水平位置 (0-1)
- `y`: 垂直位置 (0-1)
- `z`: 深度（相對於手腕）

## 效能調整

### 降低 CPU 使用率

修改 `main.py` 中的 FPS：

```python
# 原本：self.timer.start(33)  # ~30 FPS
# 改為：
self.timer.start(66)  # ~15 FPS（降低 CPU）
```

### 調整偵測信心度

修改 `start_detection()` 方法：

```python
self.detector = HandDetector(
    max_num_hands=1,
    min_detection_confidence=0.5,  # 降低可提高偵測率
    min_tracking_confidence=0.3,   # 降低可提高追蹤流暢度
)
```

### 降低攝影機解析度

```python
# 原本：640x480
self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
```

## 常見問題

### Q: MediaPipe 載入很慢？

A: 首次載入需要 10-15 秒（macOS 字體掃描），這是正常現象。後續啟動會快很多。

### Q: 攝影機權限被拒絕？

A: macOS 需要在「系統偏好設定 > 安全性與隱私 > 攝影機」中授予權限。

### Q: 手勢識別不準確？

A: DummyModel 僅為示範。建議：
1. 收集訓練資料（使用主專案的錄影功能）
2. 訓練自己的模型
3. 替換為自定義模型

### Q: 如何新增更多手勢？

A: 兩種方法：
1. **規則式**：修改 `DummyModel.predict()` 加入新規則
2. **機器學習**：訓練模型並實作 `MLModel` 類別

### Q: 如何整合到主專案？

A: 這是獨立功能，可以：
1. 保持獨立使用
2. 將訓練好的模型整合回主專案的 `motion_recorder.py`
3. 作為主專案的預覽/測試工具

## 下一步

1. **收集資料**：使用主專案的錄影功能收集手勢資料
2. **訓練模型**：使用 PyTorch/TensorFlow 訓練分類器
3. **整合模型**：將訓練好的模型載入此 Demo
4. **調整參數**：根據實際效果微調信心度、FPS 等參數
5. **擴充功能**：新增手勢歷史、資料匯出等功能

## 技術支援

如果遇到問題，請檢查：
1. Python 版本（建議 3.11+）
2. 依賴套件版本（`pip list`）
3. 攝影機是否正常工作（`ls /dev/video*` 或系統設定）
4. 控制台錯誤訊息
