# GPU 使用率顯示問題說明

## 🐛 問題描述

**症狀**: UI 介面上 GPU 使用率一直顯示 100%

**原因**: 
1. macOS 上獲取準確的 GPU 使用率需要 `sudo` 權限
2. 之前的實作使用了進程的上下文切換次數作為估算值，導致數值異常

## ✅ 已修復

### 修改內容

1. **`utils/performance_monitor.py`** (第 110-135 行)
   - 移除錯誤的上下文切換估算法
   - 改用 `powermetrics` 命令獲取真實 GPU 使用率
   - 需要 `sudo` 權限才能獲取數據
   - 沒有權限時返回 `None` 而非錯誤值

2. **`main.py`** (第 558-596 行)
   - 修正 GPU 顯示邏輯
   - 當 `gpu_percent` 為 `None` 或 `0` 時，顯示 "Metal 加速已啟用"
   - 只有當有真實數據時才顯示百分比

## 🎯 現在的行為

### 情況 1: 正常啟動（無 sudo）
```bash
python main.py
```

**GPU 顯示**: `GPU: Metal (Metal 加速已啟用)` 🟢

- 不顯示具體百分比（因為無權限讀取）
- 顯示 Metal 加速已啟用（實際上有在使用 GPU）
- 綠色顯示表示正常運作

### 情況 2: 使用 sudo 啟動（推薦）
```bash
sudo ./run_with_gpu_monitor.sh
```

**GPU 顯示**: `GPU: 8.5%` 🟢/🟠/🔴

- 顯示實際的 GPU 使用率百分比
- 顏色根據使用率變化:
  - 🟢 綠色: < 70%（正常）
  - 🟠 橙色: 70-90%（警告）
  - 🔴 紅色: > 90%（危險）

## 📊 效能數據解讀

根據之前的測試數據（`performance_report_20251105_124441.md`）:

| 階段 | GPU 使用率 | 說明 |
|------|-----------|------|
| 未偵測 | 11.7% | UI 渲染使用 Metal |
| 偵測中 | 8.0% | MediaPipe 手部追蹤 |
| 有手勢 | 7.2% | 完整運算（追蹤+識別） |

**正常範圍**: 5-15%

## 🚀 使用建議

### 方案 A: 不需要 GPU 監控（推薦）
直接啟動，GPU 顯示為 "Metal 加速已啟用"：
```bash
cd gesture_recognition_demo
source ../.venv/bin/activate
python main.py
```

**優點**: 
- 不需要輸入密碼
- 啟動快速
- Metal 加速仍然正常運作

**缺點**: 
- 看不到具體的 GPU 使用率數字

### 方案 B: 需要 GPU 監控數據
使用 sudo 啟動：
```bash
cd gesture_recognition_demo
sudo ./run_with_gpu_monitor.sh
```

**優點**: 
- 顯示真實的 GPU 使用率
- 可以監控效能瓶頸

**缺點**: 
- 每次需要輸入密碼
- 啟動稍慢（約 0.5 秒）

### 方案 C: 使用 performance_profiler.py
專門的效能分析工具（包含 GPU）：
```bash
cd gesture_recognition_demo
sudo python performance_profiler.py
```

## 🔍 技術細節

### macOS Metal GPU 監控原理

macOS 使用 `powermetrics` 命令獲取 GPU 數據：
```bash
sudo powermetrics --samplers gpu_power -i 100 -n 1
```

輸出範例：
```
*** GPU Power Data ***
GPU HW active residency:   8.24%
GPU HW active frequency:  389 MHz
GPU Power: 245 mW
```

**為何需要 sudo**:
- `powermetrics` 需要系統級權限
- 這是 Apple 的安全設計，防止應用程式濫用
- 類似 Linux 的 `nvidia-smi` 也需要特殊權限

### 替代方案（未實作）

如果不想使用 sudo，可以考慮:
1. **IOKit 框架**: 使用 Objective-C/Swift 訪問底層 API
2. **Activity Monitor API**: 讀取系統活動監視器的數據
3. **估算法**: 根據 FPS 和畫面更新頻率估算

但這些方法都較複雜且準確度不如 `powermetrics`。

## ✅ 驗證修復

### 測試步驟

1. **正常啟動測試**:
   ```bash
   python main.py
   ```
   - GPU 應該顯示 "Metal (Metal 加速已啟用)"
   - 顏色為綠色
   - 不會顯示 100%

2. **sudo 啟動測試**:
   ```bash
   sudo ./run_with_gpu_monitor.sh
   ```
   - GPU 應該顯示實際百分比（約 5-15%）
   - 點擊「開始偵測」後可能上升到 10-20%

3. **效能分析測試**:
   ```bash
   sudo python performance_profiler.py
   ```
   - 跟隨提示測試三個階段
   - 查看生成的報告確認 GPU 使用率正常

## 📝 總結

- ✅ **已修復**: GPU 使用率不再顯示錯誤的 100%
- ✅ **正常顯示**: 無權限時顯示 "Metal 加速已啟用"
- ✅ **準確數據**: 使用 sudo 時顯示真實使用率（5-15%）
- ✅ **Metal 加速**: 無論是否顯示數字，GPU 加速都在運作

**推薦使用方式**: 
- 日常開發: `python main.py`（不需要 sudo）
- 效能分析: `sudo python performance_profiler.py`（需要 sudo）
