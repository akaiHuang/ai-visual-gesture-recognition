#!/bin/bash
# 啟動手勢識別 Demo

echo "🚀 啟動手勢識別 Demo..."
echo ""

# 檢查虛擬環境
if [ ! -d "../.venv" ]; then
    echo "⚠️  找不到虛擬環境，請先在主專案中建立虛擬環境"
    echo "    cd .. && python -m venv .venv"
    exit 1
fi

# 啟動虛擬環境
source ../.venv/bin/activate

# 檢查依賴
echo "📦 檢查依賴套件..."
pip install -q -r requirements.txt

# 執行程式
echo ""
echo "✅ 啟動應用程式"
echo "---"
python main.py
