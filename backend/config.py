"""
AI 瑜珈教練系統 - 設定檔
包含系統所有設定參數
"""

import os
from pathlib import Path

# 專案根目錄
BASE_DIR = Path(__file__).parent.parent

# MongoDB 設定
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = "yoga_coach"
COLLECTION_SESSIONS = "sessions"

# 影片設定
VIDEO_DIR = BASE_DIR / "videos"
VIDEO_SESSIONS_DIR = VIDEO_DIR / "sessions"
VIDEO_SEGMENTS_DIR = VIDEO_DIR / "segments"
AUDIO_DIR = BASE_DIR / "audio"

# 確保目錄存在
VIDEO_SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
VIDEO_SEGMENTS_DIR.mkdir(parents=True, exist_ok=True)
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

# 相機設定
CAMERA_INDEX = 0  # 預設使用第一個 USB 相機
CAMERA_WIDTH = 1920  # 1080p
CAMERA_HEIGHT = 1080
CAMERA_FPS = 30

# MediaPipe 設定
MP_MIN_DETECTION_CONFIDENCE = 0.5
MP_MIN_TRACKING_CONFIDENCE = 0.5

# 姿勢分析設定
POSE_SCORE_THRESHOLD = 70  # 分數門檻，高於此值視為正確姿勢
ANGLE_TOLERANCE = 15  # 角度容許誤差（度）

# 支援的姿勢清單
SUPPORTED_POSES = [
    "Warrior II",
    "Tree Pose",
    "Downward Dog"
]

# TTS 設定
TTS_LANGUAGE = "zh-TW"
TTS_RATE = 150  # 語速
TTS_VOLUME = 0.9  # 音量

# 日誌設定
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "yoga_coach.log"
LOG_LEVEL = "INFO"

# API 設定
API_HOST = "0.0.0.0"
API_PORT = 8000
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",  # Vite 預設 port
]

# 預設使用者 ID
DEFAULT_USER_ID = "default_user"
