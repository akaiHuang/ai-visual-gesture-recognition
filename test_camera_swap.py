#!/usr/bin/env python3
"""測試攝影機列表顯示"""
import subprocess
import cv2

def get_camera_names():
    """獲取攝影機名稱"""
    result = subprocess.run(
        ["system_profiler", "SPCameraDataType"],
        capture_output=True,
        text=True,
        timeout=3
    )
    
    camera_names = []
    for line in result.stdout.split('\n'):
        stripped = line.strip()
        if (("相機:" in stripped or "Camera:" in stripped) and 
            stripped.endswith(":") and 
            not stripped.startswith("Camera:")):
            name = stripped.rstrip(":")
            camera_names.append(name)
    
    # system_profiler 順序: [FaceTime HD, iPhone]
    # OpenCV 實際順序: 0=iPhone, 1=FaceTime HD
    # 反轉以配對
    return camera_names[::-1] if len(camera_names) > 1 else camera_names

def list_cameras():
    """列出攝影機"""
    camera_names = get_camera_names()
    
    print("📋 system_profiler 順序 (原始):")
    result = subprocess.run(["system_profiler", "SPCameraDataType"], capture_output=True, text=True)
    for line in result.stdout.split('\n'):
        if '相機:' in line or 'Camera:' in line:
            print(f"  {line.strip()}")
    
    print("\n📋 攝影機名稱 (反轉後):")
    for i, name in enumerate(camera_names):
        print(f"  {i}: {name}")
    
    print("\n🎥 OpenCV 實際攝影機:")
    available = []
    for i in range(3):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            available.append((i, width, height))
            print(f"  {i}: {width}x{height}")
            cap.release()
    
    print("\n🔄 交換後的顯示順序:")
    if len(available) >= 2:
        # 交換
        available[0], available[1] = available[1], available[0]
        if len(camera_names) >= 2:
            camera_names[0], camera_names[1] = camera_names[1], camera_names[0]
    
    for new_idx, (original_idx, width, height) in enumerate(available):
        if new_idx < len(camera_names):
            print(f"  位置 {new_idx}: {original_idx}: {camera_names[new_idx]} ({width}x{height})")

if __name__ == "__main__":
    list_cameras()
