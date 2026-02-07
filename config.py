"""
手勢識別 Demo 配置

包含 Metal 加速和效能優化設置。
"""

import os
import platform
from pathlib import Path

# 優化 Matplotlib 載入速度（使用專案內預建快取）
# 這樣可以完全跳過字型掃描,大幅加快啟動速度
# 注意: 必須在 import matplotlib 之前設定
_PROJECT_DIR = Path(__file__).parent
_MPL_CACHE_DIR = _PROJECT_DIR / "mpl-cache"

if _MPL_CACHE_DIR.exists():
    # 使用 setdefault 避免覆蓋已存在的環境變數
    os.environ.setdefault('MPLCONFIGDIR', str(_MPL_CACHE_DIR))
    print(f"✅ 使用預建 Matplotlib 快取: {_MPL_CACHE_DIR}")
else:
    # 後備方案: 使用臨時目錄
    os.environ.setdefault('MPLCONFIGDIR', '/tmp/matplotlib-gesture-demo')
    print("⚠️  預建快取不存在，使用臨時目錄")
    print(f"   提示: 執行 'python build_mpl_font_cache.py' 來生成快取")

# 檢測作業系統
IS_MACOS = platform.system() == "Darwin"

# Metal 加速配置（macOS）
if IS_MACOS:
    # 啟用 Metal 後端（PyQt6）
    os.environ["QSG_RHI_BACKEND"] = "metal"
    
    # MediaPipe GPU 加速
    os.environ["MEDIAPIPE_DISABLE_GPU"] = "0"
    
    print("✅ Metal 硬體加速已啟用")
    print("   - PyQt6: Metal 渲染後端")
    print("   - MediaPipe: Metal GPU 加速")
else:
    print("ℹ️  非 macOS 系統，使用預設配置")

# 攝影機設定
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 30

# MediaPipe 設定
MEDIAPIPE_MAX_HANDS = 2  # 支援雙手偵測
MEDIAPIPE_MIN_DETECTION_CONFIDENCE = 0.7
MEDIAPIPE_MIN_TRACKING_CONFIDENCE = 0.5
MEDIAPIPE_MODEL_COMPLEXITY = 0  # 0=lite(快速啟動), 1=full(更準確), 改為 0 加快啟動

# UI 更新頻率
UI_UPDATE_INTERVAL_MS = 33  # ~30 FPS

# 效能監控更新頻率
PERF_UPDATE_INTERVAL_MS = 1000  # 1 秒

# 效能警告閾值
PERF_CPU_WARNING = 70.0  # CPU %
PERF_CPU_DANGER = 100.0
PERF_MEMORY_WARNING = 500.0  # MB
PERF_MEMORY_DANGER = 1000.0
PERF_GPU_WARNING = 70.0  # GPU %
PERF_GPU_DANGER = 90.0
