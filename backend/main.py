"""
AI 瑜珈教練系統 - FastAPI 主程式
提供 RESTful API 與 WebSocket 服務
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
import logging
import asyncio
import uvicorn
from pathlib import Path

# 匯入自訂模組
from config import (
    API_HOST, API_PORT, CORS_ORIGINS, DEFAULT_USER_ID,
    VIDEO_SESSIONS_DIR, VIDEO_SEGMENTS_DIR, AUDIO_DIR, LOG_FILE, LOG_LEVEL
)
from pose_analyzer import analyze_pose
from video_processor import VideoProcessor
from database import get_database
from tts_service import get_tts_service

# 設定日誌
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 建立 FastAPI 應用
app = FastAPI(
    title="AI 瑜珈教練系統 API",
    description="提供姿勢分析、影片處理與歷史記錄服務",
    version="1.0.0"
)

# 設定 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 掛載靜態檔案目錄
app.mount("/videos", StaticFiles(directory=str(VIDEO_SESSIONS_DIR.parent)), name="videos")
app.mount("/audio", StaticFiles(directory=str(AUDIO_DIR)), name="audio")

# 全域變數
active_sessions: Dict[str, VideoProcessor] = {}
websocket_connections: Dict[str, WebSocket] = {}


# ==================== Pydantic 模型 ====================

class StartSessionRequest(BaseModel):
    user_id: str = DEFAULT_USER_ID


class PoseAnalysisRequest(BaseModel):
    session_id: str
    landmarks: List[Dict]
    timestamp: int
    pose_hint: Optional[str] = None


class EndSegmentRequest(BaseModel):
    session_id: str
    pose_name: str
    avg_score: int
    duration_seconds: int


class MergeExportRequest(BaseModel):
    session_id: str


class TTSRequest(BaseModel):
    text: str
    language: str = "zh-TW"


# ==================== API 端點 ====================

@app.get("/")
async def root():
    """根路徑"""
    return {
        "message": "AI 瑜珈教練系統 API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.post("/start_session")
async def start_session(request: StartSessionRequest):
    """
    開始新的練習 session
    """
    try:
        # 生成 session_id（格式：YYYYMMDD_HHMMSS）
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 建立 VideoProcessor
        video_processor = VideoProcessor(session_id)
        
        # 啟動相機
        if not video_processor.start_camera():
            raise HTTPException(status_code=500, detail="相機啟動失敗")
        
        # 儲存到 active_sessions
        active_sessions[session_id] = video_processor
        
        # 建立初始 session 資料
        session_data = {
            'session_id': session_id,
            'user_id': request.user_id,
            'start_time': datetime.utcnow().isoformat(),
            'poses': [],
            'avg_score': 0,
            'duration_seconds': 0
        }
        
        # 儲存到資料庫
        db = get_database()
        db.save_session(session_data)
        
        logger.info(f"Session 已建立：{session_id}")
        
        return {
            "session_id": session_id,
            "start_time": session_data['start_time'],
            "status": "started"
        }
        
    except Exception as e:
        logger.error(f"建立 session 失敗：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/pose_analysis")
async def pose_analysis(request: PoseAnalysisRequest):
    """
    即時姿勢分析
    """
    try:
        # 檢查 session 是否存在
        if request.session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="Session 不存在")
        
        # 檢查 landmarks 數量
        if len(request.landmarks) != 33:
            raise HTTPException(status_code=400, detail="Landmarks 數量應為 33")
        
        # 分析姿勢
        result = analyze_pose(request.landmarks, request.pose_hint)
        
        # 透過 WebSocket 推送即時回饋（如果有連接）
        if request.session_id in websocket_connections:
            await websocket_connections[request.session_id].send_json({
                'type': 'pose_feedback',
                'data': result
            })
        
        logger.info(f"姿勢分析完成：{result['pose_name']}, 分數：{result['score']}")
        
        return result
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"姿勢分析失敗：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/end_segment")
async def end_segment(request: EndSegmentRequest):
    """
    結束姿勢片段
    """
    try:
        # 檢查 session 是否存在
        if request.session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="Session 不存在")
        
        video_processor = active_sessions[request.session_id]
        
        # 停止片段錄製
        video_processor.stop_segment_recording(
            request.pose_name,
            request.avg_score,
            "姿勢完成"
        )
        
        # 儲存姿勢資料到資料庫
        segment_id = video_processor.segment_count
        pose_data = {
            'segment_id': segment_id,
            'pose_name': request.pose_name,
            'score': request.avg_score,
            'correct': request.avg_score >= 70,
            'feedback': "姿勢完成",
            'duration_seconds': request.duration_seconds
        }
        
        db = get_database()
        db.update_session_poses(request.session_id, pose_data)
        
        logger.info(f"片段已結束：Session {request.session_id}, Segment {segment_id}")
        
        return {
            "segment_id": segment_id,
            "status": "saved",
            "video_path": str(video_processor.segment_paths[-1]) if video_processor.segment_paths else ""
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"結束片段失敗：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/merge_and_export")
async def merge_and_export(request: MergeExportRequest):
    """
    合併並匯出影片
    """
    try:
        # 檢查 session 是否存在
        if request.session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="Session 不存在")
        
        video_processor = active_sessions[request.session_id]
        
        # 停止相機
        video_processor.stop_camera()
        
        # 合併影片
        output_path = video_processor.merge_final_video()
        
        if not output_path or not output_path.exists():
            raise HTTPException(status_code=500, detail="影片合併失敗")
        
        # 計算總時長與平均分數
        db = get_database()
        session_data = db.get_session(request.session_id)
        
        if session_data:
            poses = session_data.get('poses', [])
            total_duration = sum(p.get('duration_seconds', 0) for p in poses)
            avg_score = sum(p.get('score', 0) for p in poses) / len(poses) if poses else 0
            
            # 更新最終資訊
            db.update_session_final_info(
                request.session_id,
                total_duration,
                round(avg_score, 1),
                str(output_path)
            )
        
        # 移除 active session
        del active_sessions[request.session_id]
        
        # 取得檔案大小
        file_size_mb = output_path.stat().st_size / (1024 * 1024)
        
        logger.info(f"影片已合併：{output_path}")
        
        return {
            "video_url": f"/videos/sessions/{output_path.name}",
            "download_path": str(output_path),
            "duration_seconds": total_duration if session_data else 0,
            "file_size_mb": round(file_size_mb, 2),
            "status": "completed"
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"合併影片失敗：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/user_history")
async def get_user_history(user_id: str = DEFAULT_USER_ID, limit: int = 20, skip: int = 0):
    """
    查詢使用者歷史記錄
    """
    try:
        db = get_database()
        
        # 取得歷史記錄
        sessions = db.get_user_history(user_id, limit, skip)
        
        # 取得總數
        total = db.get_total_sessions_count(user_id)
        
        # 格式化回應
        formatted_sessions = []
        for session in sessions:
            formatted_sessions.append({
                'session_id': session.get('session_id'),
                'date': session.get('start_time'),
                'duration_seconds': session.get('duration_seconds', 0),
                'avg_score': session.get('avg_score', 0),
                'poses_count': len(session.get('poses', [])),
                'video_available': 'final_video_path' in session
            })
        
        return {
            "total": total,
            "sessions": formatted_sessions
        }
        
    except Exception as e:
        logger.error(f"查詢歷史記錄失敗：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/session_detail")
async def get_session_detail(session_id: str):
    """
    取得 session 詳細資訊
    """
    try:
        db = get_database()
        session = db.get_session(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session 不存在")
        
        # 計算統計資訊
        poses = session.get('poses', [])
        correct_poses = sum(1 for p in poses if p.get('correct', False))
        
        stats = {
            'total_poses': len(poses),
            'correct_poses': correct_poses,
            'accuracy_rate': (correct_poses / len(poses) * 100) if poses else 0
        }
        
        # 格式化影片 URL
        video_url = None
        if 'final_video_path' in session:
            video_path = Path(session['final_video_path'])
            if video_path.exists():
                video_url = f"/videos/sessions/{video_path.name}"
        
        return {
            "session_id": session.get('session_id'),
            "user_id": session.get('user_id'),
            "start_time": session.get('start_time'),
            "duration_seconds": session.get('duration_seconds', 0),
            "avg_score": session.get('avg_score', 0),
            "video_url": video_url,
            "poses": poses,
            "stats": stats
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"取得 session 詳情失敗：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tts_feedback")
async def tts_feedback(request: TTSRequest):
    """
    文字轉語音
    """
    try:
        tts = get_tts_service()
        
        # 生成語音檔案
        audio_path = tts.generate_audio(request.text)
        
        if not audio_path or not audio_path.exists():
            raise HTTPException(status_code=500, detail="TTS 服務失敗")
        
        # 計算音訊長度（簡化估算：約 1 秒 3 個字）
        duration = len(request.text) / 3
        
        return {
            "audio_url": f"/audio/{audio_path.name}",
            "audio_path": str(audio_path),
            "duration_seconds": round(duration, 1)
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"TTS 服務失敗：{e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== WebSocket 端點 ====================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket 連接（即時回饋推送）
    """
    await websocket.accept()
    session_id = None
    
    try:
        # 接收 session_id
        data = await websocket.receive_json()
        session_id = data.get('session_id')
        
        if not session_id:
            await websocket.send_json({'error': 'session_id 為必填'})
            await websocket.close()
            return
        
        # 註冊連接
        websocket_connections[session_id] = websocket
        logger.info(f"WebSocket 已連接：Session {session_id}")
        
        # 保持連接
        while True:
            # 接收客戶端訊息（保持連線用）
            data = await websocket.receive_text()
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket 已斷開：Session {session_id}")
    except Exception as e:
        logger.error(f"WebSocket 錯誤：{e}")
    finally:
        # 移除連接
        if session_id and session_id in websocket_connections:
            del websocket_connections[session_id]


# ==================== 錯誤處理 ====================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全域錯誤處理"""
    logger.error(f"未處理的錯誤：{exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "內部伺服器錯誤",
            "detail": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# ==================== 啟動與關閉事件 ====================

@app.on_event("startup")
async def startup_event():
    """應用啟動事件"""
    logger.info("AI 瑜珈教練系統 API 已啟動")
    
    # 測試資料庫連接
    try:
        db = get_database()
        logger.info("資料庫連接成功")
    except Exception as e:
        logger.error(f"資料庫連接失敗：{e}")


@app.on_event("shutdown")
async def shutdown_event():
    """應用關閉事件"""
    logger.info("AI 瑜珈教練系統 API 正在關閉")
    
    # 停止所有 active sessions
    for session_id, video_processor in active_sessions.items():
        try:
            video_processor.stop_camera()
            logger.info(f"Session {session_id} 已停止")
        except Exception as e:
            logger.error(f"停止 Session {session_id} 失敗：{e}")
    
    active_sessions.clear()
    websocket_connections.clear()


# ==================== 主程式入口 ====================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=API_HOST,
        port=API_PORT,
        reload=True,
        log_level="info"
    )
