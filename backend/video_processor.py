"""
AI 瑜珈教練系統 - 影片處理模組
負責相機擷取、影片錄製、合併與標註
"""

import cv2
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional, Dict
import logging

from config import (
    CAMERA_INDEX, CAMERA_WIDTH, CAMERA_HEIGHT, CAMERA_FPS,
    VIDEO_SESSIONS_DIR, VIDEO_SEGMENTS_DIR
)

# 設定日誌
logger = logging.getLogger(__name__)


class CameraCapture:
    """USB 相機即時擷取類別"""
    
    def __init__(self, camera_index=CAMERA_INDEX, width=CAMERA_WIDTH, height=CAMERA_HEIGHT, fps=CAMERA_FPS):
        """
        初始化相機
        
        Args:
            camera_index: 相機索引
            width: 影像寬度
            height: 影像高度
            fps: 幀率
        """
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.fps = fps
        self.cap = None
        
    def start(self) -> bool:
        """
        啟動相機
        
        Returns:
            bool: 是否成功啟動
        """
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            
            if not self.cap.isOpened():
                logger.error(f"無法開啟相機 {self.camera_index}")
                return False
            
            # 設定解析度
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.cap.set(cv2.CAP_PROP_FPS, self.fps)
            
            logger.info(f"相機已啟動：{self.width}x{self.height} @ {self.fps} FPS")
            return True
            
        except Exception as e:
            logger.error(f"相機啟動失敗：{e}")
            return False
    
    def read_frame(self) -> Optional[np.ndarray]:
        """
        讀取一幀影像
        
        Returns:
            np.ndarray: 影像幀（BGR 格式）或 None
        """
        if self.cap is None or not self.cap.isOpened():
            return None
        
        ret, frame = self.cap.read()
        if not ret:
            logger.warning("無法讀取影像幀")
            return None
        
        return frame
    
    def stop(self):
        """停止相機"""
        if self.cap is not None:
            self.cap.release()
            logger.info("相機已停止")
    
    def __del__(self):
        """析構函數"""
        self.stop()


class VideoRecorder:
    """影片錄製類別"""
    
    def __init__(self, output_path: Path, width: int, height: int, fps: int = CAMERA_FPS):
        """
        初始化影片錄製器
        
        Args:
            output_path: 輸出影片路徑
            width: 影片寬度
            height: 影片高度
            fps: 幀率
        """
        self.output_path = output_path
        self.width = width
        self.height = height
        self.fps = fps
        self.writer = None
        self.frame_count = 0
        
    def start(self) -> bool:
        """
        開始錄製
        
        Returns:
            bool: 是否成功開始
        """
        try:
            # 確保輸出目錄存在
            self.output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 設定編碼器（H.264）
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 或使用 'avc1' for H.264
            
            self.writer = cv2.VideoWriter(
                str(self.output_path),
                fourcc,
                self.fps,
                (self.width, self.height)
            )
            
            if not self.writer.isOpened():
                logger.error(f"無法建立影片寫入器：{self.output_path}")
                return False
            
            logger.info(f"開始錄製影片：{self.output_path}")
            return True
            
        except Exception as e:
            logger.error(f"影片錄製器初始化失敗：{e}")
            return False
    
    def write_frame(self, frame: np.ndarray):
        """
        寫入一幀影像
        
        Args:
            frame: 影像幀
        """
        if self.writer is not None and self.writer.isOpened():
            self.writer.write(frame)
            self.frame_count += 1
    
    def stop(self):
        """停止錄製"""
        if self.writer is not None:
            self.writer.release()
            logger.info(f"影片錄製完成：{self.output_path}，共 {self.frame_count} 幀")
    
    def __del__(self):
        """析構函數"""
        self.stop()


def add_annotations(frame: np.ndarray, pose_name: str, score: int, feedback: str) -> np.ndarray:
    """
    在影格上疊加文字與分數標註
    
    Args:
        frame: 原始影格
        pose_name: 姿勢名稱
        score: 分數 (0-100)
        feedback: 回饋文字
    
    Returns:
        np.ndarray: 標註後的影格
    """
    annotated_frame = frame.copy()
    height, width = frame.shape[:2]
    
    # 設定字體
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    # 根據分數選擇顏色
    if score >= 90:
        color = (0, 255, 0)  # 綠色（優秀）
    elif score >= 70:
        color = (0, 255, 255)  # 黃色（良好）
    else:
        color = (0, 0, 255)  # 紅色（需改進）
    
    # 繪製半透明背景框
    overlay = annotated_frame.copy()
    cv2.rectangle(overlay, (10, 10), (width - 10, 150), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.6, annotated_frame, 0.4, 0, annotated_frame)
    
    # 顯示姿勢名稱
    cv2.putText(
        annotated_frame,
        f"Pose: {pose_name}",
        (20, 50),
        font,
        1.2,
        (255, 255, 255),
        2,
        cv2.LINE_AA
    )
    
    # 顯示分數
    cv2.putText(
        annotated_frame,
        f"Score: {score}",
        (20, 90),
        font,
        1.0,
        color,
        2,
        cv2.LINE_AA
    )
    
    # 顯示回饋（支援中文需要使用 PIL，這裡簡化處理）
    # 註：OpenCV 對中文支援不佳，實際應用中可使用 PIL 或自訂字體
    cv2.putText(
        annotated_frame,
        feedback[:50],  # 限制長度
        (20, 130),
        font,
        0.6,
        (255, 255, 255),
        1,
        cv2.LINE_AA
    )
    
    return annotated_frame


def draw_pose_landmarks(frame: np.ndarray, landmarks: List[Dict]) -> np.ndarray:
    """
    在影格上繪製姿勢骨架
    
    Args:
        frame: 原始影格
        landmarks: 33 個關鍵點
    
    Returns:
        np.ndarray: 繪製骨架後的影格
    """
    if not landmarks or len(landmarks) != 33:
        return frame
    
    annotated_frame = frame.copy()
    height, width = frame.shape[:2]
    
    # MediaPipe 連接線定義
    connections = [
        # 臉部
        (0, 1), (1, 2), (2, 3), (3, 7),
        (0, 4), (4, 5), (5, 6), (6, 8),
        (9, 10),
        # 上半身
        (11, 12),  # 肩膀
        (11, 13), (13, 15),  # 左手臂
        (12, 14), (14, 16),  # 右手臂
        (11, 23), (12, 24),  # 軀幹
        (23, 24),  # 臀部
        # 下半身
        (23, 25), (25, 27),  # 左腿
        (24, 26), (26, 28),  # 右腿
        (27, 29), (29, 31),  # 左腳
        (28, 30), (30, 32),  # 右腳
    ]
    
    # 繪製連接線
    for connection in connections:
        start_idx, end_idx = connection
        if start_idx < len(landmarks) and end_idx < len(landmarks):
            start_point = landmarks[start_idx]
            end_point = landmarks[end_idx]
            
            # 檢查可見度
            if start_point['visibility'] > 0.5 and end_point['visibility'] > 0.5:
                start_pos = (int(start_point['x'] * width), int(start_point['y'] * height))
                end_pos = (int(end_point['x'] * width), int(end_point['y'] * height))
                
                cv2.line(annotated_frame, start_pos, end_pos, (0, 255, 0), 2)
    
    # 繪製關鍵點
    for landmark in landmarks:
        if landmark['visibility'] > 0.5:
            pos = (int(landmark['x'] * width), int(landmark['y'] * height))
            cv2.circle(annotated_frame, pos, 4, (255, 0, 0), -1)
    
    return annotated_frame


def merge_segments_to_final(segment_paths: List[Path], output_path: Path, 
                            pose_info: List[Dict]) -> bool:
    """
    合併多個影片片段為最終影片，並加上標註
    
    Args:
        segment_paths: 片段影片路徑列表
        output_path: 輸出影片路徑
        pose_info: 每個片段的姿勢資訊 [{pose_name, score, feedback}, ...]
    
    Returns:
        bool: 是否成功合併
    """
    try:
        if not segment_paths:
            logger.warning("沒有影片片段可合併")
            return False
        
        # 讀取第一個片段以取得影片參數
        first_cap = cv2.VideoCapture(str(segment_paths[0]))
        if not first_cap.isOpened():
            logger.error(f"無法開啟第一個片段：{segment_paths[0]}")
            return False
        
        width = int(first_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(first_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(first_cap.get(cv2.CAP_PROP_FPS))
        first_cap.release()
        
        # 建立輸出寫入器
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
        
        if not writer.isOpened():
            logger.error(f"無法建立輸出影片：{output_path}")
            return False
        
        # 逐一處理每個片段
        for idx, segment_path in enumerate(segment_paths):
            logger.info(f"處理片段 {idx + 1}/{len(segment_paths)}: {segment_path}")
            
            cap = cv2.VideoCapture(str(segment_path))
            if not cap.isOpened():
                logger.warning(f"無法開啟片段：{segment_path}，跳過")
                continue
            
            # 取得該片段的姿勢資訊
            info = pose_info[idx] if idx < len(pose_info) else {
                'pose_name': 'Unknown',
                'score': 0,
                'feedback': ''
            }
            
            # 讀取並標註每一幀
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # 加上標註
                annotated_frame = add_annotations(
                    frame,
                    info.get('pose_name', 'Unknown'),
                    info.get('score', 0),
                    info.get('feedback', '')
                )
                
                writer.write(annotated_frame)
            
            cap.release()
        
        writer.release()
        logger.info(f"影片合併完成：{output_path}")
        return True
        
    except Exception as e:
        logger.error(f"影片合併失敗：{e}")
        return False


class VideoProcessor:
    """影片處理管理器"""
    
    def __init__(self, session_id: str):
        """
        初始化
        
        Args:
            session_id: Session ID
        """
        self.session_id = session_id
        self.camera = None
        self.current_recorder = None
        self.segment_paths = []
        self.segment_info = []
        self.segment_count = 0
        
    def start_camera(self) -> bool:
        """啟動相機"""
        self.camera = CameraCapture()
        return self.camera.start()
    
    def stop_camera(self):
        """停止相機"""
        if self.camera:
            self.camera.stop()
    
    def start_segment_recording(self) -> bool:
        """開始錄製新片段"""
        self.segment_count += 1
        segment_path = VIDEO_SEGMENTS_DIR / f"{self.session_id}_segment_{self.segment_count}.mp4"
        
        self.current_recorder = VideoRecorder(
            segment_path,
            CAMERA_WIDTH,
            CAMERA_HEIGHT
        )
        
        if self.current_recorder.start():
            self.segment_paths.append(segment_path)
            return True
        return False
    
    def record_frame(self, frame: np.ndarray):
        """錄製一幀"""
        if self.current_recorder:
            self.current_recorder.write_frame(frame)
    
    def stop_segment_recording(self, pose_name: str, score: int, feedback: str):
        """停止當前片段錄製"""
        if self.current_recorder:
            self.current_recorder.stop()
            self.segment_info.append({
                'pose_name': pose_name,
                'score': score,
                'feedback': feedback
            })
            self.current_recorder = None
    
    def merge_final_video(self) -> Path:
        """合併最終影片"""
        output_path = VIDEO_SESSIONS_DIR / f"{self.session_id}.mp4"
        
        success = merge_segments_to_final(
            self.segment_paths,
            output_path,
            self.segment_info
        )
        
        if success:
            return output_path
        return None


if __name__ == "__main__":
    # 測試相機
    logging.basicConfig(level=logging.INFO)
    
    camera = CameraCapture()
    if camera.start():
        print("相機測試成功")
        
        # 讀取 10 幀
        for i in range(10):
            frame = camera.read_frame()
            if frame is not None:
                print(f"讀取第 {i+1} 幀，大小：{frame.shape}")
        
        camera.stop()
    else:
        print("相機測試失敗")
