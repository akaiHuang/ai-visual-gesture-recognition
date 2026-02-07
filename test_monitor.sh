#!/bin/bash
# 手勢識別 Demo - 測試與監控腳本
# 同時啟動應用程式和效能監控

echo "🚀 手勢識別 Demo - 測試與監控"
echo "================================"
echo ""

# 檢查是否在正確的目錄
if [ ! -f "main.py" ]; then
    echo "❌ 請在 gesture_recognition_demo 目錄中執行此腳本"
    exit 1
fi

# 1. 先執行驗證
echo "📋 步驟 1: 系統驗證"
echo "---"
python verify.py
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ 系統驗證失敗，請先解決問題"
    exit 1
fi

echo ""
echo "================================"
echo ""

# 2. 詢問測試模式
echo "請選擇測試模式:"
echo "  1) 只運行應用程式（手動測試）"
echo "  2) 運行應用程式 + 背景效能監控"
echo "  3) 運行完整效能基準測試"
echo ""
read -p "選擇 (1/2/3): " choice

case $choice in
    1)
        # 模式 1: 只運行應用程式
        echo ""
        echo "🎮 啟動應用程式..."
        echo "---"
        echo "提示："
        echo "  - 點擊「開始偵測」按鈕"
        echo "  - 觀察右下角的效能監控面板"
        echo "  - 查看 CPU、記憶體、GPU 使用率"
        echo "  - 按 Ctrl+C 停止"
        echo ""
        python main.py
        ;;
    
    2)
        # 模式 2: 應用程式 + 背景監控
        echo ""
        echo "📊 模式 2: 應用程式 + 背景效能監控"
        echo "---"
        
        # 創建日誌目錄
        LOG_DIR="test_logs"
        mkdir -p "$LOG_DIR"
        TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
        LOG_FILE="$LOG_DIR/perf_monitor_${TIMESTAMP}.log"
        
        echo "日誌檔案: $LOG_FILE"
        echo ""
        
        # 啟動背景監控
        echo "🔄 啟動背景效能監控..."
        (
            echo "效能監控開始: $(date)" > "$LOG_FILE"
            echo "================================" >> "$LOG_FILE"
            echo "" >> "$LOG_FILE"
            
            while true; do
                python -c "
from utils.performance_monitor import PerformanceMonitor
import time

monitor = PerformanceMonitor()
metrics = monitor.get_metrics()

timestamp = time.strftime('%H:%M:%S')
print(f'[{timestamp}] CPU: {metrics.cpu_percent:5.1f}% | Memory: {metrics.memory_mb:6.1f} MB | GPU: {metrics.gpu_percent if metrics.gpu_percent else 0.0:5.1f}%')
" >> "$LOG_FILE" 2>&1
                sleep 2
            done
        ) &
        MONITOR_PID=$!
        
        echo "✅ 背景監控已啟動 (PID: $MONITOR_PID)"
        echo ""
        echo "🎮 啟動應用程式..."
        echo "---"
        echo "提示："
        echo "  - 應用程式運行時，背景會記錄效能數據"
        echo "  - 關閉應用程式後會顯示效能統計"
        echo "  - 日誌檔案: $LOG_FILE"
        echo ""
        
        # 運行主程式
        python main.py
        
        # 停止背景監控
        echo ""
        echo "⏹️  停止背景監控..."
        kill $MONITOR_PID 2>/dev/null
        
        # 顯示統計
        echo ""
        echo "📊 效能統計："
        echo "---"
        if [ -f "$LOG_FILE" ]; then
            echo "記錄數: $(grep -c "CPU:" "$LOG_FILE")"
            echo ""
            echo "CPU 使用率:"
            grep "CPU:" "$LOG_FILE" | awk '{print $4}' | sed 's/%//' | awk '
                BEGIN { sum=0; max=0; min=999; n=0 }
                { sum+=$1; if($1>max) max=$1; if($1<min) min=$1; n++ }
                END { if(n>0) printf "  平均: %.1f%%\n  最大: %.1f%%\n  最小: %.1f%%\n", sum/n, max, min }
            '
            echo ""
            echo "記憶體使用:"
            grep "Memory:" "$LOG_FILE" | awk '{print $7}' | awk '
                BEGIN { sum=0; max=0; min=99999; n=0 }
                { sum+=$1; if($1>max) max=$1; if($1<min) min=$1; n++ }
                END { if(n>0) printf "  平均: %.1f MB\n  最大: %.1f MB\n  最小: %.1f MB\n", sum/n, max, min }
            '
            echo ""
            echo "完整日誌: $LOG_FILE"
        fi
        ;;
    
    3)
        # 模式 3: 完整基準測試
        echo ""
        echo "🧪 模式 3: 完整效能基準測試"
        echo "---"
        echo "此測試將："
        echo "  1. 測試閒置效能 (10秒)"
        echo "  2. 測試 MediaPipe 手部偵測 (15秒)"
        echo "  3. 測試完整流程（偵測+識別）(15秒)"
        echo ""
        read -p "確定要執行？(y/N): " confirm
        
        if [[ $confirm =~ ^[Yy]$ ]]; then
            echo ""
            python benchmark.py
        else
            echo "已取消"
        fi
        ;;
    
    *)
        echo "無效的選擇"
        exit 1
        ;;
esac

echo ""
echo "================================"
echo "✅ 測試完成"
echo ""
