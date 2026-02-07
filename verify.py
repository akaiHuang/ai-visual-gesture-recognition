#!/usr/bin/env python
"""
快速驗證 Metal 加速和效能監控功能
"""

import sys
import os

print("🔍 系統檢查")
print("="*60)

# 1. 檢查作業系統
import platform
os_name = platform.system()
print(f"作業系統: {os_name}")
if os_name == "Darwin":
    print(f"版本: {platform.mac_ver()[0]}")
    print(f"架構: {platform.machine()}")
    print("✅ macOS 系統，Metal 加速可用")
else:
    print("ℹ️  非 macOS 系統，Metal 不可用")

print()

# 2. 載入配置
print("🔧 載入配置...")
try:
    import config
    print("✅ 配置載入成功")
    if hasattr(config, 'IS_MACOS'):
        print(f"   Metal 加速: {'已啟用' if config.IS_MACOS else '不可用'}")
    print(f"   攝影機解析度: {config.CAMERA_WIDTH}x{config.CAMERA_HEIGHT}")
    print(f"   UI 更新頻率: {1000/config.UI_UPDATE_INTERVAL_MS:.1f} FPS")
except Exception as e:
    print(f"❌ 配置載入失敗: {e}")
    sys.exit(1)

print()

# 3. 測試效能監控
print("📊 測試效能監控...")
try:
    from utils.performance_monitor import PerformanceMonitor
    monitor = PerformanceMonitor()
    print("✅ 效能監控初始化成功")
    
    # 取得系統資訊
    info = monitor.get_system_info()
    print(f"   CPU: {info.get('cpu_count')} 核心")
    print(f"   記憶體: {info.get('total_memory_gb')} GB")
    
    if monitor.gpu_available:
        print(f"   GPU: {info.get('gpu_name', 'Unknown')}")
        print(f"   GPU 類型: {info.get('gpu_type', monitor.gpu_type)}")
    else:
        print("   GPU: 不可用")
    
    # 取得效能數據
    print("\n   測試效能讀取...")
    metrics = monitor.get_metrics()
    print(f"   CPU: {metrics.cpu_percent:.1f}%")
    print(f"   記憶體: {metrics.memory_mb:.1f} MB")
    if metrics.gpu_percent is not None:
        print(f"   GPU: {metrics.gpu_percent:.1f}%")
    
except Exception as e:
    print(f"❌ 效能監控測試失敗: {e}")
    import traceback
    traceback.print_exc()

print()

# 4. 檢查 MediaPipe
print("🤚 檢查 MediaPipe...")
try:
    from utils.hand_detector import MEDIAPIPE_AVAILABLE
    if MEDIAPIPE_AVAILABLE:
        print("✅ MediaPipe 可用")
        if os_name == "Darwin":
            gpu_status = os.environ.get("MEDIAPIPE_DISABLE_GPU", "1")
            if gpu_status == "0":
                print("   Metal GPU 加速: 已啟用")
            else:
                print("   Metal GPU 加速: 未啟用")
    else:
        print("❌ MediaPipe 不可用")
except Exception as e:
    print(f"⚠️  MediaPipe 檢查失敗: {e}")

print()

# 5. 檢查依賴
print("📦 檢查關鍵依賴...")
deps = {
    'cv2': 'OpenCV',
    'numpy': 'NumPy',
    'PyQt6': 'PyQt6',
    'psutil': 'psutil',
}

all_ok = True
for module, name in deps.items():
    try:
        __import__(module)
        print(f"✅ {name}")
    except ImportError:
        print(f"❌ {name} - 未安裝")
        all_ok = False

print()
print("="*60)

if all_ok:
    print("✅ 所有檢查通過！可以執行 main.py")
    print()
    print("執行指令:")
    print("  python main.py")
    print()
else:
    print("⚠️  部分檢查失敗，請安裝缺少的依賴:")
    print("  pip install -r requirements.txt")
    print()
