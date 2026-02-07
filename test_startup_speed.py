#!/usr/bin/env python3
"""測試啟動時間"""
import time
import sys

print("=" * 60)
print("⏱️  啟動時間測試")
print("=" * 60)

# 第一階段: 匯入基礎模組
t0 = time.time()
import os
from pathlib import Path
t1 = time.time()
print(f"1️⃣  基礎模組: {(t1-t0)*1000:.0f} ms")

# 第二階段: 匯入 config (包含 Matplotlib 快取設定)
t0 = time.time()
import config
t1 = time.time()
print(f"2️⃣  Config (含 MPL 快取): {(t1-t0)*1000:.0f} ms")

# 第三階段: 匯入 PyQt6
t0 = time.time()
from PyQt6.QtWidgets import QApplication
t1 = time.time()
print(f"3️⃣  PyQt6: {(t1-t0)*1000:.0f} ms")

# 第四階段: 匯入 OpenCV
t0 = time.time()
import cv2
t1 = time.time()
print(f"4️⃣  OpenCV: {(t1-t0)*1000:.0f} ms")

# 第五階段: 匯入 MediaPipe
t0 = time.time()
try:
    import mediapipe as mp
    t1 = time.time()
    print(f"5️⃣  MediaPipe: {(t1-t0)*1000:.0f} ms")
except:
    print("5️⃣  MediaPipe: 未安裝")

# 第六階段: 匯入 Matplotlib (最慢的部分)
t0 = time.time()
import matplotlib
import matplotlib.pyplot as plt
t1 = time.time()
print(f"6️⃣  Matplotlib: {(t1-t0)*1000:.0f} ms")
print(f"   快取目錄: {matplotlib.get_cachedir()}")

# 第七階段: 建立 QApplication
t0 = time.time()
app = QApplication(sys.argv)
t1 = time.time()
print(f"7️⃣  QApplication 初始化: {(t1-t0)*1000:.0f} ms")

print("=" * 60)
print("✅ 所有模組載入完成")
print("=" * 60)
