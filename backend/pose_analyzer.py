"""
AI 瑜珈教練系統 - 姿勢分析模組
使用 MediaPipe 進行姿勢估計與分析
"""

import math
import numpy as np
from typing import List, Dict, Tuple, Optional
import mediapipe as mp

# MediaPipe Pose 解決方案
mp_pose = mp.solutions.pose

# Landmark 索引常數（基於 MediaPipe Pose 的 33 個關鍵點）
class PoseLandmark:
    NOSE = 0
    LEFT_EYE_INNER = 1
    LEFT_EYE = 2
    LEFT_EYE_OUTER = 3
    RIGHT_EYE_INNER = 4
    RIGHT_EYE = 5
    RIGHT_EYE_OUTER = 6
    LEFT_EAR = 7
    RIGHT_EAR = 8
    MOUTH_LEFT = 9
    MOUTH_RIGHT = 10
    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12
    LEFT_ELBOW = 13
    RIGHT_ELBOW = 14
    LEFT_WRIST = 15
    RIGHT_WRIST = 16
    LEFT_PINKY = 17
    RIGHT_PINKY = 18
    LEFT_INDEX = 19
    RIGHT_INDEX = 20
    LEFT_THUMB = 21
    RIGHT_THUMB = 22
    LEFT_HIP = 23
    RIGHT_HIP = 24
    LEFT_KNEE = 25
    RIGHT_KNEE = 26
    LEFT_ANKLE = 27
    RIGHT_ANKLE = 28
    LEFT_HEEL = 29
    RIGHT_HEEL = 30
    LEFT_FOOT_INDEX = 31
    RIGHT_FOOT_INDEX = 32


def calculate_angle(a: Dict, b: Dict, c: Dict) -> float:
    """
    計算三點 a-b-c 的夾角（度數）
    
    Args:
        a: 第一個點 {x, y, z, visibility}
        b: 中間點（夾角頂點）{x, y, z, visibility}
        c: 第三個點 {x, y, z, visibility}
    
    Returns:
        float: 夾角度數 (0-180)
    """
    # 提取 x, y 座標
    a_pos = np.array([a['x'], a['y']])
    b_pos = np.array([b['x'], b['y']])
    c_pos = np.array([c['x'], c['y']])
    
    # 計算向量
    ba = a_pos - b_pos
    bc = c_pos - b_pos
    
    # 計算夾角（弧度）
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
    cosine_angle = np.clip(cosine_angle, -1.0, 1.0)  # 避免數值誤差
    angle = np.arccos(cosine_angle)
    
    # 轉換為度數
    return np.degrees(angle)


def get_landmark(landmarks: List[Dict], index: int) -> Dict:
    """取得指定索引的 landmark"""
    return landmarks[index]


def check_warrior_ii(landmarks: List[Dict]) -> Dict:
    """
    檢查 Warrior II（戰士二式）姿勢
    
    標準：
    - 雙臂水平展開（肩膀-手肘-手腕約 170-180 度）
    - 前腿膝蓋彎曲 90 度
    - 後腿伸直
    - 軀幹直立
    
    Returns:
        Dict: {
            'pose_name': str,
            'correct': bool,
            'score': int (0-100),
            'feedback': str,
            'details': dict
        }
    """
    try:
        # 取得關鍵點
        left_shoulder = get_landmark(landmarks, PoseLandmark.LEFT_SHOULDER)
        left_elbow = get_landmark(landmarks, PoseLandmark.LEFT_ELBOW)
        left_wrist = get_landmark(landmarks, PoseLandmark.LEFT_WRIST)
        
        right_shoulder = get_landmark(landmarks, PoseLandmark.RIGHT_SHOULDER)
        right_elbow = get_landmark(landmarks, PoseLandmark.RIGHT_ELBOW)
        right_wrist = get_landmark(landmarks, PoseLandmark.RIGHT_WRIST)
        
        left_hip = get_landmark(landmarks, PoseLandmark.LEFT_HIP)
        left_knee = get_landmark(landmarks, PoseLandmark.LEFT_KNEE)
        left_ankle = get_landmark(landmarks, PoseLandmark.LEFT_ANKLE)
        
        right_hip = get_landmark(landmarks, PoseLandmark.RIGHT_HIP)
        right_knee = get_landmark(landmarks, PoseLandmark.RIGHT_KNEE)
        right_ankle = get_landmark(landmarks, PoseLandmark.RIGHT_ANKLE)
        
        # 計算手臂角度（應接近 180 度，即伸直）
        left_arm_angle = calculate_angle(left_shoulder, left_elbow, left_wrist)
        right_arm_angle = calculate_angle(right_shoulder, right_elbow, right_wrist)
        
        # 計算腿部角度
        left_leg_angle = calculate_angle(left_hip, left_knee, left_ankle)
        right_leg_angle = calculate_angle(right_hip, right_knee, right_ankle)
        
        # 評分邏輯
        score = 100
        feedback_points = []
        
        # 檢查手臂是否伸直（170-180 度）
        if not (170 <= left_arm_angle <= 180):
            score -= 15
            feedback_points.append("左手臂需要更伸直")
        
        if not (170 <= right_arm_angle <= 180):
            score -= 15
            feedback_points.append("右手臂需要更伸直")
        
        # 檢查腿部（一腿彎曲約 90 度，一腿伸直約 170-180 度）
        # 判斷哪條腿是前腿（彎曲）
        if left_leg_angle < right_leg_angle:
            # 左腿是前腿
            if not (80 <= left_leg_angle <= 110):
                score -= 20
                feedback_points.append("前腿（左腿）膝蓋應彎曲成 90 度")
            if not (160 <= right_leg_angle <= 180):
                score -= 15
                feedback_points.append("後腿（右腿）應保持伸直")
        else:
            # 右腿是前腿
            if not (80 <= right_leg_angle <= 110):
                score -= 20
                feedback_points.append("前腿（右腿）膝蓋應彎曲成 90 度")
            if not (160 <= left_leg_angle <= 180):
                score -= 15
                feedback_points.append("後腿（左腿）應保持伸直")
        
        # 確保分數不低於 0
        score = max(0, score)
        
        # 判斷是否正確
        correct = score >= 70
        
        # 生成回饋
        if score >= 90:
            feedback = "完美的 Warrior II！姿勢非常標準。"
        elif score >= 70:
            feedback = "很好！" + "，".join(feedback_points) if feedback_points else "保持這個姿勢。"
        else:
            feedback = "需要調整：" + "，".join(feedback_points)
        
        return {
            'pose_name': 'Warrior II',
            'correct': correct,
            'score': int(score),
            'feedback': feedback,
            'details': {
                'left_arm_angle': round(left_arm_angle, 1),
                'right_arm_angle': round(right_arm_angle, 1),
                'left_leg_angle': round(left_leg_angle, 1),
                'right_leg_angle': round(right_leg_angle, 1),
            }
        }
        
    except Exception as e:
        return {
            'pose_name': 'Warrior II',
            'correct': False,
            'score': 0,
            'feedback': f'姿勢分析錯誤：{str(e)}',
            'details': {}
        }


def check_tree_pose(landmarks: List[Dict]) -> Dict:
    """
    檢查 Tree Pose（樹式）姿勢
    
    標準：
    - 單腿站立，另一腿彎曲腳掌貼於支撐腿大腿內側
    - 雙手合十於胸前或高舉過頭
    - 身體保持直立平衡
    
    Returns:
        Dict: 姿勢分析結果
    """
    try:
        # 取得關鍵點
        left_hip = get_landmark(landmarks, PoseLandmark.LEFT_HIP)
        left_knee = get_landmark(landmarks, PoseLandmark.LEFT_KNEE)
        left_ankle = get_landmark(landmarks, PoseLandmark.LEFT_ANKLE)
        
        right_hip = get_landmark(landmarks, PoseLandmark.RIGHT_HIP)
        right_knee = get_landmark(landmarks, PoseLandmark.RIGHT_KNEE)
        right_ankle = get_landmark(landmarks, PoseLandmark.RIGHT_ANKLE)
        
        left_shoulder = get_landmark(landmarks, PoseLandmark.LEFT_SHOULDER)
        left_wrist = get_landmark(landmarks, PoseLandmark.LEFT_WRIST)
        
        # 計算腿部角度
        left_leg_angle = calculate_angle(left_hip, left_knee, left_ankle)
        right_leg_angle = calculate_angle(right_hip, right_knee, right_ankle)
        
        # 判斷哪條腿是支撐腿（較直的那條）
        if left_leg_angle > right_leg_angle:
            # 左腿支撐，右腿彎曲
            support_leg = "left"
            support_angle = left_leg_angle
            bent_angle = right_leg_angle
        else:
            # 右腿支撐，左腿彎曲
            support_leg = "right"
            support_angle = right_leg_angle
            bent_angle = left_leg_angle
        
        # 評分
        score = 100
        feedback_points = []
        
        # 支撐腿應接近伸直（160-180 度）
        if not (160 <= support_angle <= 180):
            score -= 20
            feedback_points.append("支撐腿需要伸直")
        
        # 彎曲腿應彎曲（30-90 度）
        if not (30 <= bent_angle <= 90):
            score -= 25
            feedback_points.append("彎曲腿的角度需要調整")
        
        # 檢查平衡（簡單檢查：手腕高度應接近）
        wrist_height_diff = abs(left_wrist['y'] - landmarks[PoseLandmark.RIGHT_WRIST]['y'])
        if wrist_height_diff > 0.1:
            score -= 15
            feedback_points.append("保持身體平衡，雙手高度一致")
        
        score = max(0, score)
        correct = score >= 70
        
        if score >= 90:
            feedback = "完美的 Tree Pose！平衡感極佳。"
        elif score >= 70:
            feedback = "不錯！" + "，".join(feedback_points) if feedback_points else "保持平衡。"
        else:
            feedback = "需要調整：" + "，".join(feedback_points)
        
        return {
            'pose_name': 'Tree Pose',
            'correct': correct,
            'score': int(score),
            'feedback': feedback,
            'details': {
                'support_leg': support_leg,
                'support_angle': round(support_angle, 1),
                'bent_angle': round(bent_angle, 1),
            }
        }
        
    except Exception as e:
        return {
            'pose_name': 'Tree Pose',
            'correct': False,
            'score': 0,
            'feedback': f'姿勢分析錯誤：{str(e)}',
            'details': {}
        }


def check_downward_dog(landmarks: List[Dict]) -> Dict:
    """
    檢查 Downward Dog（下犬式）姿勢
    
    標準：
    - 身體呈倒 V 字形
    - 雙手與雙腳著地，臀部抬高
    - 手臂與軀幹接近一直線
    - 腿部盡量伸直
    
    Returns:
        Dict: 姿勢分析結果
    """
    try:
        # 取得關鍵點
        left_shoulder = get_landmark(landmarks, PoseLandmark.LEFT_SHOULDER)
        left_elbow = get_landmark(landmarks, PoseLandmark.LEFT_ELBOW)
        left_wrist = get_landmark(landmarks, PoseLandmark.LEFT_WRIST)
        left_hip = get_landmark(landmarks, PoseLandmark.LEFT_HIP)
        left_knee = get_landmark(landmarks, PoseLandmark.LEFT_KNEE)
        left_ankle = get_landmark(landmarks, PoseLandmark.LEFT_ANKLE)
        
        right_shoulder = get_landmark(landmarks, PoseLandmark.RIGHT_SHOULDER)
        right_hip = get_landmark(landmarks, PoseLandmark.RIGHT_HIP)
        right_knee = get_landmark(landmarks, PoseLandmark.RIGHT_KNEE)
        
        # 計算角度
        # 上半身角度（肩膀-臀部-膝蓋應小於 90 度，形成倒 V）
        left_body_angle = calculate_angle(left_shoulder, left_hip, left_knee)
        
        # 腿部角度（應接近伸直）
        left_leg_angle = calculate_angle(left_hip, left_knee, left_ankle)
        right_leg_angle = calculate_angle(right_hip, right_knee, landmarks[PoseLandmark.RIGHT_ANKLE])
        
        # 手臂角度（應伸直）
        left_arm_angle = calculate_angle(left_shoulder, left_elbow, left_wrist)
        right_arm_angle = calculate_angle(right_shoulder, landmarks[PoseLandmark.RIGHT_ELBOW], landmarks[PoseLandmark.RIGHT_WRIST])
        
        # 評分
        score = 100
        feedback_points = []
        
        # 檢查倒 V 形狀（身體角度應小於 90 度）
        if not (30 <= left_body_angle <= 80):
            score -= 25
            feedback_points.append("臀部需要抬高，形成倒 V 字形")
        
        # 檢查腿部伸直
        if not (160 <= left_leg_angle <= 180):
            score -= 15
            feedback_points.append("左腿需要伸直")
        if not (160 <= right_leg_angle <= 180):
            score -= 15
            feedback_points.append("右腿需要伸直")
        
        # 檢查手臂伸直
        if not (160 <= left_arm_angle <= 180):
            score -= 15
            feedback_points.append("左手臂需要伸直")
        if not (160 <= right_arm_angle <= 180):
            score -= 15
            feedback_points.append("右手臂需要伸直")
        
        score = max(0, score)
        correct = score >= 70
        
        if score >= 90:
            feedback = "完美的 Downward Dog！姿勢標準。"
        elif score >= 70:
            feedback = "不錯！" + "，".join(feedback_points) if feedback_points else "保持這個姿勢。"
        else:
            feedback = "需要調整：" + "，".join(feedback_points)
        
        return {
            'pose_name': 'Downward Dog',
            'correct': correct,
            'score': int(score),
            'feedback': feedback,
            'details': {
                'body_angle': round(left_body_angle, 1),
                'left_leg_angle': round(left_leg_angle, 1),
                'right_leg_angle': round(right_leg_angle, 1),
                'left_arm_angle': round(left_arm_angle, 1),
                'right_arm_angle': round(right_arm_angle, 1),
            }
        }
        
    except Exception as e:
        return {
            'pose_name': 'Downward Dog',
            'correct': False,
            'score': 0,
            'feedback': f'姿勢分析錯誤：{str(e)}',
            'details': {}
        }


def analyze_pose(landmarks: List[Dict], pose_hint: Optional[str] = None) -> Dict:
    """
    統一姿勢分析介面
    
    Args:
        landmarks: MediaPipe 偵測到的 33 個關鍵點
        pose_hint: 姿勢提示（可選），如果提供則只檢查該姿勢
    
    Returns:
        Dict: 姿勢分析結果
    """
    if len(landmarks) != 33:
        return {
            'pose_name': 'Unknown',
            'correct': False,
            'score': 0,
            'feedback': 'Landmark 數量錯誤，應為 33 個點',
            'details': {}
        }
    
    # 如果有姿勢提示，直接檢查該姿勢
    if pose_hint:
        if pose_hint == "Warrior II":
            return check_warrior_ii(landmarks)
        elif pose_hint == "Tree Pose":
            return check_tree_pose(landmarks)
        elif pose_hint == "Downward Dog":
            return check_downward_dog(landmarks)
    
    # 否則，嘗試所有姿勢並回傳分數最高的
    results = [
        check_warrior_ii(landmarks),
        check_tree_pose(landmarks),
        check_downward_dog(landmarks)
    ]
    
    # 選擇分數最高的姿勢
    best_result = max(results, key=lambda x: x['score'])
    
    # 如果所有姿勢分數都很低，回傳未知姿勢
    if best_result['score'] < 50:
        return {
            'pose_name': 'Unknown',
            'correct': False,
            'score': 0,
            'feedback': '無法識別標準瑜珈姿勢，請調整姿勢',
            'details': {}
        }
    
    return best_result


# MediaPipe Pose 初始化類別
class PoseAnalyzer:
    """姿勢分析器類別，封裝 MediaPipe Pose"""
    
    def __init__(self, min_detection_confidence=0.5, min_tracking_confidence=0.5):
        """
        初始化姿勢分析器
        
        Args:
            min_detection_confidence: 最小偵測信心度
            min_tracking_confidence: 最小追蹤信心度
        """
        self.pose = mp_pose.Pose(
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
    
    def process_frame(self, frame):
        """
        處理單一影格，提取姿勢關鍵點
        
        Args:
            frame: OpenCV 影格 (BGR)
        
        Returns:
            List[Dict]: 33 個 landmark 或 None
        """
        # 轉換為 RGB（MediaPipe 使用 RGB）
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # 處理影像
        results = self.pose.process(frame_rgb)
        
        # 提取 landmarks
        if results.pose_landmarks:
            landmarks = []
            for lm in results.pose_landmarks.landmark:
                landmarks.append({
                    'x': lm.x,
                    'y': lm.y,
                    'z': lm.z,
                    'visibility': lm.visibility
                })
            return landmarks
        
        return None
    
    def close(self):
        """關閉姿勢分析器"""
        self.pose.close()


if __name__ == "__main__":
    # 測試範例
    import cv2
    
    # 建立測試用的 landmarks（正常站立姿勢）
    test_landmarks = [{'x': 0.5, 'y': 0.2, 'z': 0, 'visibility': 1.0} for _ in range(33)]
    
    # 測試姿勢分析
    result = analyze_pose(test_landmarks, pose_hint="Warrior II")
    print(f"姿勢：{result['pose_name']}")
    print(f"正確：{result['correct']}")
    print(f"分數：{result['score']}")
    print(f"回饋：{result['feedback']}")
    print(f"詳情：{result['details']}")
