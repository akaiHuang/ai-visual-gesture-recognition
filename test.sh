#!/bin/bash
# 測試手勢識別 Demo 的快速腳本

echo "🧪 手勢識別 Demo 測試指南"
echo "================================"
echo ""

# 檢查 Python
echo "1️⃣ 檢查 Python 版本..."
python --version
echo ""

# 檢查虛擬環境
echo "2️⃣ 檢查虛擬環境..."
if [ -d "../.venv" ]; then
    echo "✅ 虛擬環境存在"
    source ../.venv/bin/activate
else
    echo "❌ 請先建立虛擬環境: cd .. && python -m venv .venv"
    exit 1
fi
echo ""

# 檢查依賴
echo "3️⃣ 檢查關鍵依賴..."
python -c "import cv2; print('✅ OpenCV:', cv2.__version__)" 2>/dev/null || echo "❌ OpenCV 未安裝"
python -c "import mediapipe; print('✅ MediaPipe:', mediapipe.__version__)" 2>/dev/null || echo "❌ MediaPipe 未安裝"
python -c "from PyQt6.QtWidgets import QApplication; print('✅ PyQt6 已安裝')" 2>/dev/null || echo "❌ PyQt6 未安裝"
echo ""

# 安裝缺少的依賴
read -p "是否安裝/更新依賴？(y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📦 安裝依賴..."
    pip install -r requirements.txt
    echo ""
fi

# 測試手部偵測器
echo "4️⃣ 測試手部偵測器..."
python -c "
from utils.hand_detector import MEDIAPIPE_AVAILABLE
if MEDIAPIPE_AVAILABLE:
    print('✅ 手部偵測器可用')
else:
    print('❌ MediaPipe 不可用')
"
echo ""

# 測試模型
echo "5️⃣ 測試 AI 模型..."
python -c "
from models.gesture_model import DummyModel
import numpy as np

model = DummyModel()
model.load_model()
print('✅ 模型載入成功')

# 測試預測
landmarks = np.random.rand(21, 3)
result = model.predict(landmarks)
print(f'✅ 測試預測: {result[\"gesture\"]} (信心度: {result[\"confidence\"]:.2f})')
"
echo ""

echo "================================"
echo "✅ 測試完成！"
echo ""
echo "📝 使用說明："
echo "   ./run.sh           # 啟動應用程式"
echo "   python main.py     # 直接執行"
echo ""
