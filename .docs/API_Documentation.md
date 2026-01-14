# AI 瑜珈教練系統 API 文檔

**版本**：1.0  
**更新日期**：2026-01-14  
**基礎 URL**：`http://localhost:8000`

---

## API 端點總覽

| 端點 | 方法 | 功能 | 認證 |
|------|------|------|------|
| `/start_session` | POST | 開始新的練習 session | 否 |
| `/pose_analysis` | POST | 即時姿勢分析 | 否 |
| `/end_segment` | POST | 結束姿勢片段 | 否 |
| `/merge_and_export` | POST | 合併影片並匯出 | 否 |
| `/user_history` | GET | 查詢使用者歷史記錄 | 否 |
| `/session_detail` | GET | 取得 session 詳細資訊 | 否 |
| `/tts_feedback` | POST | 文字轉語音 | 否 |
| `/ws` | WebSocket | 即時回饋推送 | 否 |

---

## 詳細 API 規格

### 1. 開始新 Session

**端點**：`POST /start_session`

**描述**：開始一個新的瑜珈練習 session，系統將初始化相機與錄製服務。

**請求體**：
```json
{
  "user_id": "default_user"
}
```

**回應**：
```json
{
  "session_id": "20260114_163847",
  "start_time": "2026-01-14T16:38:47Z",
  "status": "started"
}
```

**狀態碼**：
- `200 OK`：成功建立 session
- `500 Internal Server Error`：相機初始化失敗

---

### 2. 即時姿勢分析

**端點**：`POST /pose_analysis`

**描述**：接收 MediaPipe 偵測到的 33 個關鍵點，分析姿勢正確性並回傳即時回饋。

**請求體**：
```json
{
  "session_id": "20260114_163847",
  "landmarks": [
    {"x": 0.5, "y": 0.3, "z": -0.1, "visibility": 0.99},
    ...
    // 共 33 個 landmark 點
  ],
  "timestamp": 1234567890
}
```

**回應**：
```json
{
  "pose_name": "Warrior II",
  "correct": true,
  "score": 88,
  "feedback": "很好！標準的 Warrior II 姿勢。保持手臂水平。",
  "details": {
    "left_arm_angle": 92,
    "right_arm_angle": 88,
    "hip_alignment": "good"
  }
}
```

**狀態碼**：
- `200 OK`：成功分析
- `400 Bad Request`：landmarks 格式錯誤
- `404 Not Found`：session_id 不存在

---

### 3. 結束姿勢片段

**端點**：`POST /end_segment`

**描述**：結束當前姿勢片段的錄製，儲存片段資訊到資料庫。

**請求體**：
```json
{
  "session_id": "20260114_163847",
  "pose_name": "Warrior II",
  "avg_score": 86,
  "duration_seconds": 15
}
```

**回應**：
```json
{
  "segment_id": 1,
  "status": "saved",
  "video_path": "videos/segments/20260114_163847_segment_1.mp4"
}
```

**狀態碼**：
- `200 OK`：成功儲存片段
- `404 Not Found`：session_id 不存在

---

### 4. 合併並匯出影片

**端點**：`POST /merge_and_export`

**描述**：合併所有片段影片，加上文字與分數標註，產生最終完整影片。

**請求體**：
```json
{
  "session_id": "20260114_163847"
}
```

**回應**：
```json
{
  "video_url": "/videos/sessions/20260114_163847.mp4",
  "download_path": "c:/Users/RAG/Desktop/Yoga_Coach/videos/sessions/20260114_163847.mp4",
  "duration_seconds": 458,
  "file_size_mb": 125.4,
  "status": "completed"
}
```

**狀態碼**：
- `200 OK`：成功合併
- `404 Not Found`：session_id 不存在
- `500 Internal Server Error`：影片合併失敗

---

### 5. 查詢使用者歷史

**端點**：`GET /user_history`

**描述**：查詢使用者的練習歷史記錄。

**查詢參數**：
- `user_id` (可選)：使用者 ID，預設 "default_user"
- `limit` (可選)：回傳筆數限制，預設 20

**範例**：`GET /user_history?user_id=default_user&limit=10`

**回應**：
```json
{
  "total": 45,
  "sessions": [
    {
      "session_id": "20260114_163847",
      "date": "2026-01-14T16:38:47Z",
      "duration_seconds": 458,
      "avg_score": 84.7,
      "poses_count": 3,
      "video_available": true
    },
    ...
  ]
}
```

**狀態碼**：
- `200 OK`：成功查詢

---

### 6. 取得 Session 詳情

**端點**：`GET /session_detail`

**描述**：取得單一 session 的完整資訊，包含所有姿勢資料與統計。

**查詢參數**：
- `session_id` (必填)：Session ID

**範例**：`GET /session_detail?session_id=20260114_163847`

**回應**：
```json
{
  "session_id": "20260114_163847",
  "user_id": "default_user",
  "start_time": "2026-01-14T16:38:47Z",
  "duration_seconds": 458,
  "avg_score": 84.7,
  "video_url": "/videos/sessions/20260114_163847.mp4",
  "poses": [
    {
      "segment_id": 1,
      "pose_name": "Warrior II",
      "start_frame": 0,
      "end_frame": 320,
      "score": 88,
      "correct": true,
      "feedback": "很好！標準的 Warrior II",
      "duration_seconds": 15
    },
    {
      "segment_id": 2,
      "pose_name": "Tree Pose",
      "start_frame": 321,
      "end_frame": 580,
      "score": 82,
      "correct": true,
      "feedback": "重心穩定，保持平衡",
      "duration_seconds": 12
    }
  ],
  "stats": {
    "total_poses": 3,
    "correct_poses": 3,
    "accuracy_rate": 100.0
  }
}
```

**狀態碼**：
- `200 OK`：成功取得資料
- `404 Not Found`：session_id 不存在

---

### 7. 文字轉語音

**端點**：`POST /tts_feedback`

**描述**：將文字回饋轉換為語音檔案。

**請求體**：
```json
{
  "text": "很好！標準的 Warrior II 姿勢。保持手臂水平。",
  "language": "zh-TW"
}
```

**回應**：
```json
{
  "audio_url": "/audio/feedback_1705224327.mp3",
  "audio_path": "c:/Users/RAG/Desktop/Yoga_Coach/audio/feedback_1705224327.mp3",
  "duration_seconds": 3.2
}
```

**狀態碼**：
- `200 OK`：成功生成語音
- `500 Internal Server Error`：TTS 服務失敗

---

### 8. WebSocket 即時回饋

**端點**：`WebSocket /ws`

**描述**：建立 WebSocket 連接以接收即時姿勢分析回饋。

**連接**：
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
```

**接收訊息格式**：
```json
{
  "type": "pose_feedback",
  "data": {
    "pose_name": "Warrior II",
    "correct": true,
    "score": 88,
    "feedback": "很好！標準的 Warrior II 姿勢。",
    "timestamp": 1705224327
  }
}
```

**訊息類型**：
- `pose_feedback`：姿勢分析回饋
- `session_started`：Session 開始通知
- `segment_ended`：片段結束通知
- `error`：錯誤訊息

---

## 錯誤處理

所有 API 錯誤回應格式統一如下：

```json
{
  "error": "Error message description",
  "detail": "Detailed error information",
  "timestamp": "2026-01-14T16:38:47Z"
}
```

**常見錯誤碼**：
- `400 Bad Request`：請求格式錯誤
- `404 Not Found`：資源不存在
- `500 Internal Server Error`：伺服器內部錯誤

---

## 資料模型

### Landmark 物件
```json
{
  "x": 0.5,        // 正規化 x 座標 (0-1)
  "y": 0.3,        // 正規化 y 座標 (0-1)
  "z": -0.1,       // 正規化 z 座標
  "visibility": 0.99  // 可見度 (0-1)
}
```

### Session 物件
```json
{
  "session_id": "string",
  "user_id": "string",
  "start_time": "ISO 8601 datetime",
  "duration_seconds": "integer",
  "avg_score": "float",
  "poses": "array of Pose objects",
  "video_url": "string"
}
```

### Pose 物件
```json
{
  "segment_id": "integer",
  "pose_name": "string",
  "start_frame": "integer",
  "end_frame": "integer",
  "score": "integer (0-100)",
  "correct": "boolean",
  "feedback": "string",
  "duration_seconds": "integer"
}
```

---

## 使用範例

### Python 範例
```python
import requests

# 開始新 session
response = requests.post('http://localhost:8000/start_session', json={
    'user_id': 'default_user'
})
session_data = response.json()
session_id = session_data['session_id']

# 姿勢分析
landmarks = [...]  # MediaPipe 產生的 33 個點
response = requests.post('http://localhost:8000/pose_analysis', json={
    'session_id': session_id,
    'landmarks': landmarks,
    'timestamp': int(time.time())
})
feedback = response.json()
print(f"姿勢：{feedback['pose_name']}, 分數：{feedback['score']}")
```

### JavaScript 範例
```javascript
// 開始新 session
const sessionResponse = await fetch('http://localhost:8000/start_session', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({user_id: 'default_user'})
});
const sessionData = await sessionResponse.json();

// WebSocket 連接
const ws = new WebSocket('ws://localhost:8000/ws');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'pose_feedback') {
    console.log(`姿勢：${data.data.pose_name}, 分數：${data.data.score}`);
  }
};
```

---

## 註解

1. 所有時間均使用 ISO 8601 格式 (UTC)
2. 座標值均為正規化值 (0-1)，基於影像寬高
3. 分數範圍為 0-100
4. 影片格式為 MP4 (H.264 編碼)
5. 音訊格式為 MP3
