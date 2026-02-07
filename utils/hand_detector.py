"""
手部偵測模組：使用 MediaPipe 進行手部關鍵點追蹤

提供簡單的手部偵測接口，用於手勢識別。
"""

import cv2
import numpy as np
from typing import Optional, List, Tuple

try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    print("⚠️ MediaPipe 未安裝，請執行: pip install mediapipe")


class HandDetector:
    """手部偵測器
    
    使用 MediaPipe Hands 進行手部關鍵點檢測。
    """
    
    def __init__(
        self,
        max_num_hands: int = 2,
        min_detection_confidence: float = 0.7,
        min_tracking_confidence: float = 0.5,
        model_complexity: int = 1
    ):
        """初始化手部偵測器
        
        Args:
            max_num_hands: 最多偵測幾隻手 (1 或 2)
            min_detection_confidence: 偵測信心度閾值
            min_tracking_confidence: 追蹤信心度閾值
            model_complexity: 模型複雜度 (0=lite, 1=full)
        """
        if not MEDIAPIPE_AVAILABLE:
            raise RuntimeError("MediaPipe 未安裝")
        
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_num_hands,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
            model_complexity=model_complexity
        )
        
        self.results = None
    
    def detect(self, frame: np.ndarray) -> Optional[List[np.ndarray]]:
        """偵測手部關鍵點
        
        Args:
            frame: BGR 格式的影像 (OpenCV 格式)
            
        Returns:
            手部關鍵點列表，每個元素是 (21, 3) 的 numpy array，
            包含 21 個關鍵點的 (x, y, z) 座標。
            如果沒有偵測到手部，返回 None。
        """
        # 轉換為 RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # 偵測
        self.results = self.hands.process(frame_rgb)
        
        if not self.results.multi_hand_landmarks:
            return None
        
        # 提取關鍵點
        landmarks_list = []
        for hand_landmarks in self.results.multi_hand_landmarks:
            landmarks = np.array([
                [lm.x, lm.y, lm.z]
                for lm in hand_landmarks.landmark
            ])
            landmarks_list.append(landmarks)
        
        return landmarks_list
    
    def draw_landmarks(self, frame: np.ndarray) -> np.ndarray:
        """在影像上繪製手部關鍵點
        
        Args:
            frame: BGR 格式的影像
            
        Returns:
            繪製了關鍵點的影像
        """
        if self.results and self.results.multi_hand_landmarks:
            for hand_landmarks in self.results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style()
                )
        
        return frame
    
    def get_hand_info(self) -> List[Tuple[str, float]]:
        """獲取手部資訊（左/右手、信心度）
        
        Returns:
            [(handedness, confidence), ...] 列表
        """
        if not self.results or not self.results.multi_handedness:
            return []
        
        info = []
        for hand_info in self.results.multi_handedness:
            handedness = hand_info.classification[0].label  # "Left" or "Right"
            confidence = hand_info.classification[0].score
            info.append((handedness, confidence))
        
        return info
    
    def close(self):
        """關閉偵測器，釋放資源"""
        if self.hands:
            self.hands.close()
