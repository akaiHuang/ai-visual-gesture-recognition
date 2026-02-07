#!/bin/bash
# 帶 GPU 監控的啟動腳本
# 使用 sudo 啟動以獲取完整的 Metal GPU 使用率數據

echo "🚀 啟動手勢識別 Demo (含 GPU 監控)"
echo ""
echo "⚠️  注意：此腳本需要 sudo 權限以監控 GPU 使用率"
echo "   如果不需要 GPU 使用率數據，可以直接執行: python main.py"
echo ""

# 檢查虛擬環境
if [ ! -d "../.venv" ]; then
    echo "❌ 找不到虛擬環境: ../.venv"
    echo "請確保在正確的目錄中執行此腳本"
    exit 1
fi

# 啟動虛擬環境
source ../.venv/bin/activate

# 檢查 Python
if ! command -v python &> /dev/null; then
    echo "❌ Python 未找到"
    exit 1
fi

echo "✅ 虛擬環境已啟動"
echo "✅ Python 版本: $(python --version)"
echo ""

# 使用 sudo 運行 Python
# 需要保留環境變數以使用虛擬環境的 Python
sudo -E env "PATH=$PATH" python main.py
