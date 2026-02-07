#!/usr/bin/env python3
"""
測試攝影機名稱獲取功能
"""
import subprocess
import cv2

def get_camera_names_macos():
    """獲取 macOS 攝影機名稱"""
    try:
        print("🔍 查詢攝影機資訊...")
        result = subprocess.run(
            ["system_profiler", "SPCameraDataType"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        print("\n📋 system_profiler 原始輸出:")
        print("=" * 60)
        print(result.stdout)
        print("=" * 60)
        
        # 解析攝影機名稱
        camera_names = []
        lines = result.stdout.split('\n')
        
        print("\n🔍 解析攝影機名稱:")
        for line in lines:
            stripped = line.strip()
            
            # 攝影機名稱格式: "    FaceTime HD相機:" 或 "    Akai's iphone相機:"
            if (("相機:" in stripped or "Camera:" in stripped) and 
                stripped.endswith(":") and 
                not stripped.startswith("Camera:")):
                
                name = stripped.rstrip(":")
                camera_names.append(name)
                print(f"  ✓ 找到: {name}")
        
        return camera_names
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        return []

def list_available_cameras():
    """列出可用的攝影機"""
    print("\n🎥 檢測可用攝影機...")
    print("=" * 60)
    
    available = []
    for i in range(5):  # 檢查 0-4
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            # 獲取攝影機解析度
            width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            available.append({
                'index': i,
                'resolution': f"{int(width)}x{int(height)}",
                'fps': fps
            })
            
            print(f"✅ 攝影機 {i}: {int(width)}x{int(height)} @ {fps:.0f} FPS")
            cap.release()
        else:
            print(f"❌ 攝影機 {i}: 不可用")
    
    print("=" * 60)
    return available

def main():
    print("""
╔═══════════════════════════════════════════════════════════╗
║           攝影機名稱測試工具                               ║
╚═══════════════════════════════════════════════════════════╝
""")
    
    # 獲取攝影機名稱
    names = get_camera_names_macos()
    
    # 列出可用攝影機
    available = list_available_cameras()
    
    # 配對名稱和索引
    print("\n📊 攝影機配對結果:")
    print("=" * 60)
    
    if names and available:
        for i, cam in enumerate(available):
            if i < len(names):
                print(f"  {cam['index']}: {names[i]}")
                print(f"     解析度: {cam['resolution']}")
                print(f"     FPS: {cam['fps']:.0f}")
            else:
                print(f"  {cam['index']}: 未知攝影機")
                print(f"     解析度: {cam['resolution']}")
            print()
    else:
        print("  ⚠️  無法配對攝影機名稱")
    
    print("=" * 60)
    
    # 給出建議
    print("\n💡 建議的下拉選單顯示格式:")
    print("=" * 60)
    for i, cam in enumerate(available):
        if i < len(names):
            print(f"  {cam['index']}: {names[i]} ({cam['resolution']})")
        else:
            print(f"  攝影機 {cam['index']} ({cam['resolution']})")
    print("=" * 60)

if __name__ == "__main__":
    main()
