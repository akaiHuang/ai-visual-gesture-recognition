#!/usr/bin/env python3
"""快速啟動時間測試"""
import time
import sys

start = time.time()
print("開始測試啟動時間...")

# 測試各階段
t1 = time.time()
import config
print(f"✓ config 載入: {(time.time()-t1)*1000:.0f} ms")

t1 = time.time()
import cv2
print(f"✓ OpenCV 載入: {(time.time()-t1)*1000:.0f} ms")

t1 = time.time()
from PyQt6.QtWidgets import QApplication
print(f"✓ PyQt6 載入: {(time.time()-t1)*1000:.0f} ms")

t1 = time.time()
from utils.hand_detector import HandDetector
print(f"✓ HandDetector 載入: {(time.time()-t1)*1000:.0f} ms")

t1 = time.time()
from models.gesture_model import DummyModel
print(f"✓ GestureModel 載入: {(time.time()-t1)*1000:.0f} ms")

total = (time.time() - start) * 1000
print(f"\n總載入時間: {total:.0f} ms ({total/1000:.2f} 秒)")

if total < 3000:
    print("✅ 啟動速度: 優秀")
elif total < 6000:
    print("⚠️  啟動速度: 良好")
else:
    print("❌ 啟動速度: 需要優化")
