#!/usr/bin/env python3
"""
啟動時間分析工具

測量應用程式從執行到視窗顯示的完整啟動時間。
"""

import subprocess
import time
import sys
from datetime import datetime


def measure_startup_time(runs=5):
    """測量多次啟動時間並計算平均值"""
    
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║              手勢識別 Demo 啟動時間分析                    ║
║                                                           ║
║  此工具將測量應用程式的完整啟動時間                        ║
║  包含：模組載入、視窗初始化、UI 渲染等                     ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
""")
    
    print(f"📊 開始測試（共 {runs} 次）\n")
    
    startup_times = []
    
    for i in range(runs):
        print(f"🔄 第 {i+1}/{runs} 次啟動測試...")
        
        # 記錄開始時間
        start_time = time.time()
        
        # 啟動程式並捕獲輸出
        try:
            # 使用 timeout 防止程式卡住
            result = subprocess.run(
                ["python", "main.py"],
                capture_output=True,
                text=True,
                timeout=10  # 10秒超時
            )
            
            # 從輸出中提取啟動時間
            output = result.stdout
            
            # 尋找 "🚀 總啟動時間:" 行
            for line in output.split('\n'):
                if "🚀 總啟動時間:" in line:
                    # 提取時間（格式: "🚀 總啟動時間: 1234.5 ms (1.23 秒)"）
                    parts = line.split(':')[1].strip().split()[0]
                    startup_ms = float(parts)
                    startup_times.append(startup_ms)
                    print(f"   ✅ 啟動時間: {startup_ms:.1f} ms")
                    break
            else:
                print(f"   ⚠️  無法解析啟動時間")
            
            # 等待一下再進行下一次測試
            time.sleep(1)
            
        except subprocess.TimeoutExpired:
            print(f"   ❌ 超時（程式可能需要手動關閉）")
        except Exception as e:
            print(f"   ❌ 錯誤: {e}")
    
    if not startup_times:
        print("\n❌ 無法收集到有效的啟動時間數據")
        print("\n💡 提示：請確保:")
        print("   1. 虛擬環境已啟動")
        print("   2. 所有依賴已安裝")
        print("   3. main.py 包含啟動時間測量代碼")
        return
    
    # 計算統計數據
    min_time = min(startup_times)
    max_time = max(startup_times)
    avg_time = sum(startup_times) / len(startup_times)
    
    print(f"\n{'='*60}")
    print(f"📊 啟動時間統計 (基於 {len(startup_times)} 次測試)")
    print(f"{'='*60}")
    print(f"  最快: {min_time:.1f} ms ({min_time/1000:.2f} 秒)")
    print(f"  最慢: {max_time:.1f} ms ({max_time/1000:.2f} 秒)")
    print(f"  平均: {avg_time:.1f} ms ({avg_time/1000:.2f} 秒)")
    print(f"{'='*60}")
    
    # 評估啟動速度
    print("\n🎯 啟動速度評估:")
    if avg_time < 2000:
        print("   ✅ 優秀 (< 2 秒)")
    elif avg_time < 4000:
        print("   ⚠️  良好 (2-4 秒)")
    elif avg_time < 6000:
        print("   ⚠️  可接受 (4-6 秒)")
    else:
        print("   ❌ 緩慢 (> 6 秒)")
    
    # 提供優化建議
    if avg_time > 4000:
        print("\n💡 優化建議:")
        print("   1. 使用 lite 模型: config.py 中設置")
        print("      MEDIAPIPE_MODEL_COMPLEXITY = 0")
        print("   2. 延遲載入: 將 MediaPipe 改為按需載入")
        print("   3. 減少匯入: 移除不必要的模組")
    
    # 儲存結果
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"performance_logs/startup_time_{timestamp}.txt"
    
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"啟動時間測試報告\n")
            f.write(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"測試次數: {len(startup_times)}\n\n")
            f.write(f"最快: {min_time:.1f} ms\n")
            f.write(f"最慢: {max_time:.1f} ms\n")
            f.write(f"平均: {avg_time:.1f} ms\n\n")
            f.write(f"詳細數據:\n")
            for i, t in enumerate(startup_times, 1):
                f.write(f"  第 {i} 次: {t:.1f} ms\n")
        
        print(f"\n💾 結果已儲存: {report_file}")
    except Exception as e:
        print(f"\n⚠️  無法儲存結果: {e}")


def quick_test():
    """快速測試（單次）"""
    print("\n🚀 快速啟動測試（單次）\n")
    print("請觀察終端輸出的啟動時間資訊...")
    print("程式啟動後，請手動關閉視窗以返回此工具\n")
    
    input("按 Enter 開始...")
    
    subprocess.run(["python", "main.py"])


if __name__ == "__main__":
    print("\n請選擇測試模式:")
    print("  1. 快速測試 (啟動一次，手動關閉)")
    print("  2. 完整測試 (自動啟動5次，需要手動關閉每次)")
    print("  3. 取消")
    
    choice = input("\n請輸入選項 (1-3): ").strip()
    
    if choice == "1":
        quick_test()
    elif choice == "2":
        print("\n⚠️  注意：每次啟動後需要手動關閉視窗才能繼續下一次測試\n")
        input("按 Enter 繼續...")
        measure_startup_time(runs=5)
    else:
        print("\n已取消")
