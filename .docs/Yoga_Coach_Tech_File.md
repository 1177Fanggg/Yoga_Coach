# AI 瑜珈教練系統技術文檔

**版本**：1.0（本地端 MVP 版）  
**更新日期**：2026-01-14  
**作者**：Yi（與 Grok 協作優化）  
**運行環境**：Windows 本機（純本地執行，無雲端依賴）  
**主要技術棧**：USB Camera + OpenCV + MediaPipe + FastAPI + React/Vite + MongoDB 或 PostgreSQL

---

## 一、系統概述

本系統為一套**純本地端** AI 瑜珈教練應用，透過 USB 攝影機即時捕捉使用者姿勢，利用 MediaPipe 進行骨架辨識，以規則為基礎判斷姿勢正確性，提供即時文字 + 分數 + 語音回饋，並在練習結束後合併生成帶標註的完整影片供回放檢視。

### 核心設計原則
- 後端集中所有重度運算（姿勢分析、影片合併、TTS），前端僅負責顯示與播放，降低瀏覽器負載
- 目前採用 rule-based 姿勢判斷，預留 ML 模型切換接口
- 支援 session 歷史紀錄儲存與查詢
- 前端以**即時回饋**為主，**回放影片**為輔（單開 modal 或分頁）
- 全部離線執行（TTS 使用 pyttsx3）

### 目前已實作 / 規劃重點
1. 1080p USB 相機即時影像擷取
2. MediaPipe Pose 關鍵點提取
3. 基於角度與相對位置的姿勢正確性判斷（目前 MVP：Warrior II、Tree Pose、Downward Dog）
4. 即時文字 + 分數 + 語音回饋
5. 後端片段錄製 → 合併標註影片
6. 使用者 session 與姿勢歷史儲存與查詢
7. 基本單元測試、整合測試與性能監控
8. 預留 TTS 語音接口及未來 ML 擴充架構

---

## 二、系統架構

### 2.1 資料流總覽
```
[USB Camera 1080p]
↓ (OpenCV VideoCapture)
[FastAPI Backend]
├─ MediaPipe Pose → 33 landmarks
├─ Rule-based Analysis → pose_name, score, feedback
├─ Real-time Feedback (WebSocket 或 polling)
├─ Segment Recording + Annotation
├─ Merge Segments → final mp4 with overlays
├─ TTS (pyttsx3) → audio file
└─ MongoDB / PostgreSQL → save session & history
↓ REST API / WebSocket
[React + Vite Frontend]
├─ Live camera view + real-time text/score/audio
└─ History list → Session detail → Replay modal/video
```

### 2.2 模組對照表

| 模組              | 技術                  | 主要職責                              | 目前狀態          | 擴充預留點                  |
|-------------------|-----------------------|---------------------------------------|-------------------|-----------------------------|
| 影像擷取          | OpenCV                | 1080p 串流                            | 已規劃            | 相機選擇、解析度/FPS 調整   |
| 姿勢估計          | MediaPipe Pose        | 33 landmarks                          | 已實作            | 其他 Pose 模型              |
| 姿勢判斷          | 自訂 rule-based       | 角度 + 相對位置檢查                   | MVP 3 姿勢        | ML 模式、更多姿勢規則       |
| 影片處理          | OpenCV (+ FFmpeg)     | 片段錄製、合併、文字/顏色標註         | 已規劃            | 畫骨架、熱圖、可視化        |
| 語音回饋          | pyttsx3               | 離線 TTS                              | 預留接口          | gTTS / Edge TTS             |
| 資料儲存          | MongoDB / PostgreSQL  | session、姿勢、影片路徑、歷史         | 已設計            | 使用者帳號、排行榜          |
| 後端伺服器        | FastAPI               | API + WebSocket                       | 核心接口          | 異步任務 (Celery)           |
| 前端介面          | React + Vite          | 即時回饋 + 單開回放 + 歷史            | 規劃中            | 骨架疊加、進度統計          |
| 測試與監控        | pytest + logging + psutil | 測試 + CPU/延遲記錄               | 基本框架          | CI/CD、錯誤追蹤             |

---

## 三、後端設計細節

### 3.1 主要 API 端點

| Endpoint                  | Method | 主要用途                              | 重要回傳欄位                          |
|---------------------------|--------|---------------------------------------|---------------------------------------|
| `/start_session`          | POST   | 開始新練習 session                    | `{session_id, start_time}`            |
| `/pose_analysis`          | POST   | 送 landmarks → 即時姿勢分析           | `{pose_name, correct, score, feedback}` |
| `/end_segment`            | POST   | 結束一段姿勢，儲存片段資訊            | `{segment_id, status}`                |
| `/merge_and_export`       | POST   | 合併所有片段並產生最終影片            | `{video_url, download_path}`          |
| `/user_history`           | GET    | 查詢歷史（支援 ?limit=20 &user_id=xxx）| `[{session_id, date, avg_score, duration}]` |
| `/session_detail`         | GET    | 取得單一 session 完整資料             | `{poses[], stats, video_url}`         |
| `/tts_feedback`           | POST   | 文字轉語音                            | `{audio_url}`                         |

### 3.2 姿勢判斷核心邏輯（角度計算）

```python
import math
import mediapipe as mp

mp_pose = mp.solutions.pose

def calculate_angle(a, b, c):
    """計算三點 a-b-c 夾角（度）"""
    a = [a.x, a.y]
    b = [b.x, b.y]
    c = [c.x, c.y]
    radians = math.atan2(c[1]-b[1], c[0]-b[0]) - math.atan2(a[1]-b[1], a[0]-b[0])
    angle = abs(math.degrees(radians))
    if angle > 180.0:
        angle = 360 - angle
    return angle
```

### 3.3 測試與監控建議
- 單元測試：pytest 測試 calculate_angle、check_warrior_ii 等
- 整合測試：錄製短影片 → 完整流程驗證 JSON 與 mp4 產出
- 監控：FPS、分析延遲、正確率，psutil 監控 CPU/記憶體，logging 寫入 logs/yoga_coach.log

---

## 四、前端設計重點

### 4.1 主要畫面建議布局
- **即時練習畫面**：左半部即時攝影機畫面，右半部回饋區（姿勢名稱 + 分數 + 建議文字 + TTS 播放）
- **回放區域**：練習結束後按鈕查看完整影片，使用 <video> 播放後端產生的 mp4
- **歷史紀錄頁**：表格或卡片列表，日期、平均分數、持續時間、觀看按鈕

### 4.2 資料更新策略
- 首選 WebSocket，備用 1–2 秒 polling

---

## 五、資料庫結構（MongoDB 範例）
```json
{
  "_id": ObjectId(...),
  "user_id": "default_user",
  "session_id": "20260114_165412",
  "start_time": "2026-01-14T16:54:12Z",
  "duration_seconds": 458,
  "avg_score": 84.7,
  "poses": [
    {
      "segment_id": 1,
      "pose_name": "Warrior II",
      "start_frame": 0,
      "end_frame": 320,
      "score": 88,
      "correct": true,
      "feedback": "很好！標準的Warrior II",
      "keypoints_sample": [...] 
    },
    ...
  ],
  "final_video_path": "videos/sessions/20260114_165412.mp4"
}
```

---

## 六、快速啟動指令
```bash
# 後端
python -m venv venv
venv\Scripts\activate
pip install fastapi uvicorn opencv-python mediapipe numpy pyttsx3 psutil pytest pymongo  # 或 psycopg2
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 前端
cd frontend
npm install
npm run dev

# 測試
pytest tests/
```

---

## 七、擴充設計與預留框架

### 7.1 語音回饋 (TTS)
- 目標：完成姿勢後即時回饋語音
- 後端 TTS 模組：pyttsx3 / gTTS / Edge TTS
- 前端播放音檔同步姿勢完成
- API `/tts_feedback` 預留接口

### 7.2 後續功能擴充框架
1. 姿勢分析模式切換：rule-based → ML 模型
2. 資料儲存擴充：使用者歷史、排行榜、分數量化
3. 前端回饋擴充：骨架疊加、進度條、動畫

### 7.3 設計原則
- 模組化、接口統一、低耦合、高擴充性
- 後端優先處理運算與影片合併

---

## 八、未來擴充方向
1. 增加更多瑜伽姿勢規則（Plank、Chair、Warrior I 等）
2. 前端骨架疊加（canvas / react-three-fiber）
3. 進階 ML 姿勢辨識（輔助 rule-based）
4. 使用者帳號與進度追蹤
5. 支援手機/平板 USB 相機
6. TTS 多引擎切換（pyttsx3 → gTTS / Edge TTS）
7. 日誌與監控自動化（CI/CD、性能報告、異常追蹤）