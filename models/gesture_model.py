"""
可擴充的 AI 手勢識別模型接口

提供統一的模型接口，支援不同的機器學習模型實作。
"""

from abc import ABC, abstractmethod
import numpy as np
from typing import Optional, Dict, Any, List, Tuple


class GestureModel(ABC):
    """手勢識別模型基類
    
    所有手勢識別模型都應該繼承此類並實作 predict 方法。
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """初始化模型
        
        Args:
            model_path: 模型檔案路徑（可選）
        """
        self.model_path = model_path
        self.is_loaded = False
    
    @abstractmethod
    def load_model(self) -> bool:
        """載入模型
        
        Returns:
            是否載入成功
        """
        pass
    
    @abstractmethod
    def predict(self, landmarks: np.ndarray) -> Dict[str, Any]:
        """預測手勢
        
        Args:
            landmarks: 手部關鍵點，shape 為 (21, 3) 或 (21, 2)
            
        Returns:
            預測結果字典，至少包含:
            {
                'gesture': str,  # 手勢名稱
                'confidence': float,  # 信心度 (0-1)
                'details': Any  # 其他詳細資訊（可選）
            }
        """
        pass
    
    def preprocess(self, landmarks: np.ndarray) -> np.ndarray:
        """預處理關鍵點資料（可覆寫）
        
        Args:
            landmarks: 原始關鍵點資料
            
        Returns:
            預處理後的資料
        """
        return landmarks


class DummyModel(GestureModel):
    """示範用的假模型
    
    根據手部位置簡單判斷手勢（僅供測試）。
    """
    
    def __init__(self):
        super().__init__(model_path=None)
        self.gestures = [
            "握拳 👊",
            "張開手掌 🖐️",
            "比讚 👍",
            "比 YA ✌️",
            "比 OK 👌",
            "指向 👉"
        ]
    
    def load_model(self) -> bool:
        """載入模型（假模型無需載入）"""
        self.is_loaded = True
        return True
    
    def predict(self, landmarks: np.ndarray) -> Dict[str, Any]:
        """改進的規則式手勢判斷
        
        使用更精確的手指彎曲度判斷，提高準確率。
        """
        if not self.is_loaded:
            self.load_model()
        
        # 計算每根手指是否伸直
        fingers_up = self._count_fingers(landmarks)
        
        # 計算手指彎曲角度
        finger_angles = self._calculate_finger_angles(landmarks)
        
        # 根據手指狀態判斷手勢
        gesture, confidence = self._recognize_gesture(fingers_up, finger_angles, landmarks)
        
        return {
            'gesture': gesture,
            'confidence': confidence,
            'details': {
                'fingers_up': fingers_up,
                'finger_angles': [float(a) for a in finger_angles]
            }
        }
    
    def _count_fingers(self, landmarks: np.ndarray) -> List[bool]:
        """判斷每根手指是否伸直
        
        Returns:
            [拇指, 食指, 中指, 無名指, 小指] 的伸直狀態
        """
        fingers = []
        
        # 拇指：比較指尖(4)和指根(2)的 x 座標
        thumb_tip = landmarks[4]
        thumb_mcp = landmarks[2]
        thumb_extended = abs(thumb_tip[0] - thumb_mcp[0]) > 0.04
        fingers.append(thumb_extended)
        
        # 其他四指：比較指尖和第二關節的 y 座標
        finger_tips = [8, 12, 16, 20]  # 食指、中指、無名指、小指
        finger_pips = [6, 10, 14, 18]  # 對應的第二關節
        
        for tip_idx, pip_idx in zip(finger_tips, finger_pips):
            extended = landmarks[tip_idx][1] < landmarks[pip_idx][1]
            fingers.append(extended)
        
        return fingers
    
    def _calculate_finger_angles(self, landmarks: np.ndarray) -> List[float]:
        """計算每根手指的彎曲角度"""
        angles = []
        
        # 計算五根手指的角度
        finger_joints = [
            [1, 2, 4],    # 拇指
            [5, 6, 8],    # 食指
            [9, 10, 12],  # 中指
            [13, 14, 16], # 無名指
            [17, 18, 20]  # 小指
        ]
        
        for joints in finger_joints:
            a = landmarks[joints[0]][:2]
            b = landmarks[joints[1]][:2]
            c = landmarks[joints[2]][:2]
            
            ba = a - b
            bc = c - b
            
            cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
            angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
            angles.append(np.degrees(angle))
        
        return angles
    
    def _recognize_gesture(self, fingers_up: List[bool], finger_angles: List[float], landmarks: np.ndarray) -> Tuple[str, float]:
        """根據手指狀態識別手勢"""
        
        # 握拳：所有手指彎曲
        if not any(fingers_up):
            return "握拳 👊", 0.95
        
        # 張開手掌：所有手指伸直
        if all(fingers_up):
            return "張開手掌 🖐️", 0.95
        
        # 比讚：只有拇指伸直
        if fingers_up[0] and not any(fingers_up[1:]):
            return "比讚 👍", 0.95
        
        # 比 YA：食指和中指伸直
        if fingers_up[1] and fingers_up[2] and not fingers_up[3] and not fingers_up[4]:
            return "比 YA ✌️", 0.90
        
        # 比 OK：拇指和食指接觸形成圓圈
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        distance = np.linalg.norm(thumb_tip[:2] - index_tip[:2])
        if distance < 0.05 and fingers_up[2] and fingers_up[3] and fingers_up[4]:
            return "比 OK 👌", 0.85
        
        # 指向：只有食指伸直
        if fingers_up[1] and not fingers_up[2] and not fingers_up[3] and not fingers_up[4]:
            return "指向 👉", 0.90
        
        # 小指伸直 (搖滾手勢或打招呼)
        if fingers_up[4] and not fingers_up[2] and not fingers_up[3]:
            return "搖滾 🤘", 0.85
        
        # 三根手指
        if sum(fingers_up[1:]) == 3:
            return "三 ☝️", 0.80
        
        # 預設：未知手勢
        return "未知 🤔", 0.50


class MLModel(GestureModel):
    """機器學習模型接口（預留）
    
    可以在這裡實作 LSTM、Transformer 或其他深度學習模型。
    """
    
    def __init__(self, model_path: str):
        super().__init__(model_path)
        self.model = None
    
    def load_model(self) -> bool:
        """載入訓練好的模型"""
        # TODO: 實作模型載入
        # 例如：self.model = torch.load(self.model_path)
        print(f"TODO: 載入模型 {self.model_path}")
        return False
    
    def predict(self, landmarks: np.ndarray) -> Dict[str, Any]:
        """使用模型預測"""
        if not self.is_loaded:
            raise RuntimeError("模型尚未載入")
        
        # TODO: 實作模型預測
        # 例如：
        # features = self.preprocess(landmarks)
        # output = self.model(features)
        # gesture = self.decode_output(output)
        
        return {
            'gesture': "未實作",
            'confidence': 0.0,
            'details': {}
        }
