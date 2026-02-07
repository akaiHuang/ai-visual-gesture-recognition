#!/usr/bin/env python
"""
效能基準測試工具

測試手勢識別 Demo 在不同情況下的效能表現。
"""

import time
import sys
from utils.performance_monitor import PerformanceTracker


def run_idle_test(duration: int = 10):
    """測試閒置狀態效能
    
    Args:
        duration: 測試時長（秒）
    """
    print(f"\n{'='*60}")
    print("測試 1: 閒置狀態效能")
    print(f"{'='*60}")
    print(f"測試時長: {duration} 秒\n")
    
    tracker = PerformanceTracker()
    
    for i in range(duration):
        tracker.record()
        print(f"[{i+1}/{duration}] 記錄效能數據...")
        time.sleep(1)
    
    tracker.print_statistics()
    return tracker.get_statistics()


def run_mediapipe_test(duration: int = 15):
    """測試 MediaPipe 手部偵測效能
    
    Args:
        duration: 測試時長（秒）
    """
    print(f"\n{'='*60}")
    print("測試 2: MediaPipe 手部偵測效能")
    print(f"{'='*60}")
    print(f"測試時長: {duration} 秒\n")
    
    try:
        from utils.hand_detector import HandDetector, MEDIAPIPE_AVAILABLE
        import cv2
        
        if not MEDIAPIPE_AVAILABLE:
            print("❌ MediaPipe 不可用，跳過此測試")
            return None
        
        print("🎥 開啟攝影機...")
        camera = cv2.VideoCapture(0)
        if not camera.isOpened():
            print("❌ 無法開啟攝影機，跳過此測試")
            return None
        
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        print("🤚 初始化手部偵測器...")
        detector = HandDetector(
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        
        print("▶️  開始測試...\n")
        
        tracker = PerformanceTracker()
        start_time = time.time()
        frame_count = 0
        
        while time.time() - start_time < duration:
            ret, frame = camera.read()
            if not ret:
                break
            
            # 偵測手部
            frame = cv2.flip(frame, 1)
            landmarks_list = detector.detect(frame)
            frame = detector.draw_landmarks(frame)
            
            frame_count += 1
            
            # 每秒記錄一次效能
            if frame_count % 30 == 0:
                tracker.record()
                elapsed = time.time() - start_time
                print(f"[{elapsed:.1f}s] 已處理 {frame_count} 幀")
        
        camera.release()
        detector.close()
        
        print(f"\n✅ 總共處理 {frame_count} 幀")
        print(f"   平均 FPS: {frame_count / duration:.1f}")
        
        tracker.print_statistics()
        return tracker.get_statistics()
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        return None


def run_full_pipeline_test(duration: int = 15):
    """測試完整流程效能（手部偵測 + AI 模型）
    
    Args:
        duration: 測試時長（秒）
    """
    print(f"\n{'='*60}")
    print("測試 3: 完整流程效能（偵測 + AI 識別）")
    print(f"{'='*60}")
    print(f"測試時長: {duration} 秒\n")
    
    try:
        from utils.hand_detector import HandDetector, MEDIAPIPE_AVAILABLE
        from models.gesture_model import DummyModel
        import cv2
        
        if not MEDIAPIPE_AVAILABLE:
            print("❌ MediaPipe 不可用，跳過此測試")
            return None
        
        print("🎥 開啟攝影機...")
        camera = cv2.VideoCapture(0)
        if not camera.isOpened():
            print("❌ 無法開啟攝影機，跳過此測試")
            return None
        
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        print("🤚 初始化手部偵測器...")
        detector = HandDetector()
        
        print("🤖 載入 AI 模型...")
        model = DummyModel()
        model.load_model()
        
        print("▶️  開始測試...\n")
        
        tracker = PerformanceTracker()
        start_time = time.time()
        frame_count = 0
        detection_count = 0
        
        while time.time() - start_time < duration:
            ret, frame = camera.read()
            if not ret:
                break
            
            # 偵測手部
            frame = cv2.flip(frame, 1)
            landmarks_list = detector.detect(frame)
            frame = detector.draw_landmarks(frame)
            
            # AI 識別
            if landmarks_list:
                landmarks = landmarks_list[0]
                result = model.predict(landmarks)
                detection_count += 1
            
            frame_count += 1
            
            # 每秒記錄一次效能
            if frame_count % 30 == 0:
                tracker.record()
                elapsed = time.time() - start_time
                print(f"[{elapsed:.1f}s] 已處理 {frame_count} 幀，識別 {detection_count} 次")
        
        camera.release()
        detector.close()
        
        print(f"\n✅ 總共處理 {frame_count} 幀，識別 {detection_count} 次")
        print(f"   平均 FPS: {frame_count / duration:.1f}")
        print(f"   手部偵測率: {detection_count / frame_count * 100:.1f}%")
        
        tracker.print_statistics()
        return tracker.get_statistics()
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """主程式"""
    print("\n" + "🎯 手勢識別 Demo - 效能基準測試".center(60, "="))
    print()
    
    # 顯示系統資訊
    from utils.performance_monitor import PerformanceMonitor
    monitor = PerformanceMonitor()
    info = monitor.get_system_info()
    
    print("系統資訊:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # 執行測試
    results = {}
    
    # 測試 1: 閒置
    results['idle'] = run_idle_test(duration=10)
    
    # 測試 2: MediaPipe
    results['mediapipe'] = run_mediapipe_test(duration=15)
    
    # 測試 3: 完整流程
    results['full'] = run_full_pipeline_test(duration=15)
    
    # 總結
    print("\n" + "="*60)
    print("測試總結")
    print("="*60)
    
    if results['idle']:
        print(f"\n閒置狀態:")
        print(f"  CPU: {results['idle']['cpu_avg']:.1f}% (最大: {results['idle']['cpu_max']:.1f}%)")
        print(f"  記憶體: {results['idle']['memory_avg_mb']:.1f} MB")
    
    if results['mediapipe']:
        print(f"\nMediaPipe 偵測:")
        print(f"  CPU: {results['mediapipe']['cpu_avg']:.1f}% (最大: {results['mediapipe']['cpu_max']:.1f}%)")
        print(f"  記憶體: {results['mediapipe']['memory_avg_mb']:.1f} MB")
    
    if results['full']:
        print(f"\n完整流程:")
        print(f"  CPU: {results['full']['cpu_avg']:.1f}% (最大: {results['full']['cpu_max']:.1f}%)")
        print(f"  記憶體: {results['full']['memory_avg_mb']:.1f} MB")
    
    print("\n" + "="*60)
    print("✅ 所有測試完成！")
    print("="*60 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  測試被使用者中斷")
        sys.exit(0)
