#!/usr/bin/env python
"""
實時效能監控工具

在終端機持續顯示效能數據，適合監控應用程式運行狀態。
"""

import sys
import time
import os
from datetime import datetime
from utils.performance_monitor import PerformanceMonitor, PerformanceTracker

def clear_screen():
    """清除終端機螢幕"""
    os.system('clear' if os.name != 'nt' else 'cls')

def get_bar(percent, width=20):
    """生成進度條
    
    Args:
        percent: 百分比 (0-100)
        width: 進度條寬度
    """
    filled = int(width * percent / 100)
    bar = '█' * filled + '░' * (width - filled)
    
    # 顏色
    if percent < 50:
        color = '\033[92m'  # 綠色
    elif percent < 80:
        color = '\033[93m'  # 黃色
    else:
        color = '\033[91m'  # 紅色
    
    reset = '\033[0m'
    return f"{color}{bar}{reset}"

def main():
    """主程式"""
    print("\n🔍 實時效能監控")
    print("按 Ctrl+C 停止監控\n")
    time.sleep(1)
    
    monitor = PerformanceMonitor()
    tracker = PerformanceTracker()
    
    # 顯示系統資訊
    info = monitor.get_system_info()
    print("系統資訊:")
    print(f"  CPU: {info.get('cpu_count')} 核心")
    print(f"  記憶體: {info.get('total_memory_gb')} GB")
    if monitor.gpu_available:
        print(f"  GPU: {info.get('gpu_name', 'Unknown')} ({info.get('gpu_type', 'N/A')})")
    print()
    
    input("按 Enter 開始監控...")
    
    start_time = time.time()
    sample_count = 0
    
    try:
        while True:
            clear_screen()
            
            # 取得效能數據
            metrics = monitor.get_metrics()
            tracker.record()
            sample_count += 1
            elapsed = time.time() - start_time
            
            # 標題
            print("═" * 70)
            print("🔍 實時效能監控".center(70))
            print("═" * 70)
            print()
            
            # 時間資訊
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"時間: {current_time}  |  運行時長: {elapsed:.0f}秒  |  採樣: {sample_count}")
            print()
            
            # CPU
            cpu_bar = get_bar(metrics.cpu_percent)
            print(f"CPU 使用率:    {cpu_bar}  {metrics.cpu_percent:5.1f}%")
            
            # 記憶體
            mem_percent = (metrics.memory_mb / float(info.get('total_memory_gb', 1)) / 1024 * 100)
            mem_bar = get_bar(mem_percent)
            print(f"記憶體使用:    {mem_bar}  {metrics.memory_mb:6.1f} MB ({metrics.memory_percent:4.1f}%)")
            
            # GPU
            if metrics.gpu_percent is not None:
                gpu_bar = get_bar(metrics.gpu_percent)
                gpu_text = f"{metrics.gpu_percent:5.1f}%"
                if metrics.gpu_memory_mb is not None and metrics.gpu_memory_mb > 0:
                    gpu_text += f" | {metrics.gpu_memory_mb:.0f} MB"
                print(f"GPU 使用率:    {gpu_bar}  {gpu_text}")
            elif monitor.gpu_available:
                print(f"GPU:           \033[92m✓ {monitor.gpu_type} 加速已啟用\033[0m")
            else:
                print(f"GPU:           N/A")
            
            print()
            
            # 統計數據
            if sample_count > 1:
                stats = tracker.get_statistics()
                print("─" * 70)
                print("統計數據:")
                print()
                print(f"  CPU 使用率:     平均 {stats['cpu_avg']:5.1f}%  |  最大 {stats['cpu_max']:5.1f}%  |  最小 {stats['cpu_min']:5.1f}%")
                print(f"  記憶體使用:     平均 {stats['memory_avg_mb']:6.1f} MB  |  最大 {stats['memory_max_mb']:6.1f} MB")
                if 'gpu_avg' in stats:
                    print(f"  GPU 使用率:     平均 {stats['gpu_avg']:5.1f}%  |  最大 {stats['gpu_max']:5.1f}%")
            
            print()
            print("─" * 70)
            print("提示: 按 Ctrl+C 停止監控並查看完整統計")
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  監控已停止\n")
        
        # 顯示最終統計
        if sample_count > 0:
            tracker.print_statistics()
        
        print("✅ 監控完成\n")

if __name__ == "__main__":
    main()
