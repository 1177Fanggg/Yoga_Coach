# 前端建置指南

本文檔說明如何建置 AI 瑜珈教練系統的前端介面。

## 環境需求

- Node.js 18.0+
- npm 或 yarn

## 建立專案

### 1. 使用 Vite 建立 React 專案

```bash
cd c:\Users\RAG\Desktop\Yoga_Coach
npm create vite@latest frontend -- --template react
cd frontend
npm install
```

### 2. 安裝必要依賴

```bash
npm install axios                    # HTTP 請求
npm install @mediapipe/pose          # MediaPipe Pose (前端版)
npm install @mediapipe/camera_utils  # 相機工具
npm install @mediapipe/drawing_utils # 繪圖工具
```

## 專案結構

建議的前端專案結構：

```
frontend/
├── src/
│   ├── components/          # React 元件
│   │   ├── Camera.jsx       # 相機元件
│   │   ├── FeedbackPanel.jsx # 回饋面板
│   │   ├── SessionCard.jsx  # Session 卡片
│   │   └── VideoPlayer.jsx  # 影片播放器
│   ├── pages/               # 頁面
│   │   ├── LivePracticePage.jsx  # 即時練習頁面
│   │   ├── HistoryPage.jsx       # 歷史記錄頁面
│   │   └── SessionDetailModal.jsx # Session 詳情 Modal
│   ├── services/            # API 服務
│   │   ├── apiService.js    # REST API 呼叫
│   │   └── websocketService.js # WebSocket 連接
│   ├── styles/              # CSS 樣式
│   │   └── main.css         # 主要樣式
│   ├── App.jsx              # 主應用元件
│   └── main.jsx             # 入口檔案
├── public/                  # 靜態資源
└── package.json
```

## 核心功能實作

### 1. API 服務層 (`services/apiService.js`)

```javascript
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export const apiService = {
  // 開始 session
  async startSession(userId = 'default_user') {
    const response = await axios.post(`${API_BASE_URL}/start_session`, {
      user_id: userId
    });
    return response.data;
  },

  // 姿勢分析
  async analyzePose(sessionId, landmarks, poseHint = null) {
    const response = await axios.post(`${API_BASE_URL}/pose_analysis`, {
      session_id: sessionId,
      landmarks: landmarks,
      timestamp: Math.floor(Date.time() / 1000),
      pose_hint: poseHint
    });
    return response.data;
  },

  // 結束片段
  async endSegment(sessionId, poseName, avgScore, duration) {
    const response = await axios.post(`${API_BASE_URL}/end_segment`, {
      session_id: sessionId,
      pose_name: poseName,
      avg_score: avgScore,
      duration_seconds: duration
    });
    return response.data;
  },

  // 合併影片
  async mergeAndExport(sessionId) {
    const response = await axios.post(`${API_BASE_URL}/merge_and_export`, {
      session_id: sessionId
    });
    return response.data;
  },

  // 取得歷史
  async getUserHistory(userId = 'default_user', limit = 20) {
    const response = await axios.get(`${API_BASE_URL}/user_history`, {
      params: { user_id: userId, limit }
    });
    return response.data;
  },

  // 取得 session 詳情
  async getSessionDetail(sessionId) {
    const response = await axios.get(`${API_BASE_URL}/session_detail`, {
      params: { session_id: sessionId }
    });
    return response.data;
  },

  // TTS
  async generateTTS(text) {
    const response = await axios.post(`${API_BASE_URL}/tts_feedback`, {
      text: text,
      language: 'zh-TW'
    });
    return response.data;
  }
};
```

### 2. WebSocket 服務層 (`services/websocketService.js`)

```javascript
class WebSocketService {
  constructor() {
    this.ws = null;
    this.sessionId = null;
    this.listeners = [];
  }

  connect(sessionId) {
    this.sessionId = sessionId;
    this.ws = new WebSocket('ws://localhost:8000/ws');

    this.ws.onopen = () => {
      console.log('WebSocket 已連接');
      // 發送 session_id
      this.ws.send(JSON.stringify({ session_id: sessionId }));
    };

    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.notifyListeners(data);
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket 錯誤：', error);
    };

    this.ws.onclose = () => {
      console.log('WebSocket 已斷開');
    };
  }

  addListener(callback) {
    this.listeners.push(callback);
  }

  notifyListeners(data) {
    this.listeners.forEach(listener => listener(data));
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
    }
  }
}

export const websocketService = new WebSocketService();
```

### 3. 相機元件 (`components/Camera.jsx`)

```jsx
import React, { useRef, useEffect } from 'react';
import { Pose } from '@mediapipe/pose';
import { Camera as MediaPipeCamera } from '@mediapipe/camera_utils';

function Camera({ onResults }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  useEffect(() => {
    const pose = new Pose({
      locateFile: (file) => {
        return `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`;
      }
    });

    pose.setOptions({
      modelComplexity: 1,
      smoothLandmarks: true,
      minDetectionConfidence: 0.5,
      minTrackingConfidence: 0.5
    });

    pose.onResults(onResults);

    if (videoRef.current) {
      const camera = new MediaPipeCamera(videoRef.current, {
        onFrame: async () => {
          await pose.send({ image: videoRef.current });
        },
        width: 1280,
        height: 720
      });
      camera.start();
    }
  }, []);

  return (
    <div className="camera-container">
      <video ref={videoRef} style={{ display: 'none' }}></video>
      <canvas ref={canvasRef} width={1280} height={720}></canvas>
    </div>
  );
}

export default Camera;
```

### 4. 即時練習頁面 (`pages/LivePracticePage.jsx`)

```jsx
import React, { useState, useEffect } from 'react';
import Camera from '../components/Camera';
import FeedbackPanel from '../components/FeedbackPanel';
import { apiService } from '../services/apiService';
import { websocketService } from '../services/websocketService';

function LivePracticePage() {
  const [sessionId, setSessionId] = useState(null);
  const [feedback, setFeedback] = useState(null);
  const [isRecording, setIsRecording] = useState(false);

  const startSession = async () => {
    try {
      const data = await apiService.startSession();
      setSessionId(data.session_id);
      
      // 連接 WebSocket
      websocketService.connect(data.session_id);
      websocketService.addListener((data) => {
        if (data.type === 'pose_feedback') {
          setFeedback(data.data);
        }
      });
      
      setIsRecording(true);
    } catch (error) {
      console.error('啟動 session 失敗：', error);
    }
  };

  const endSession = async () => {
    try {
      await apiService.mergeAndExport(sessionId);
      websocketService.disconnect();
      setIsRecording(false);
      alert('練習結束！影片已儲存。');
    } catch (error) {
      console.error('結束 session 失敗：', error);
    }
  };

  const handlePoseResults = async (results) => {
    if (!sessionId || !results.poseLandmarks) return;

    // 轉換 landmarks 格式
    const landmarks = results.poseLandmarks.map(lm => ({
      x: lm.x,
      y: lm.y,
      z: lm.z,
      visibility: lm.visibility
    }));

    // 發送到後端分析
    try {
      const analysis = await apiService.analyzePose(sessionId, landmarks);
      setFeedback(analysis);
    } catch (error) {
      console.error('姿勢分析失敗：', error);
    }
  };

  return (
    <div className="live-practice-page">
      <div className="camera-section">
        <Camera onResults={handlePoseResults} />
      </div>
      <div className="feedback-section">
        {!isRecording ? (
          <button onClick={startSession}>開始練習</button>
        ) : (
          <>
            <FeedbackPanel feedback={feedback} />
            <button onClick={endSession}>結束練習</button>
          </>
        )}
      </div>
    </div>
  );
}

export default LivePracticePage;
```

## 設計風格指南

### CSS 主題

```css
:root {
  --primary-color: #6366f1;
  --secondary-color: #8b5cf6;
  --success-color: #10b981;
  --warning-color: #f59e0b;
  --error-color: #ef4444;
  --bg-dark: #1a1a2e;
  --bg-light: #16213e;
  --text-primary: #ffffff;
  --text-secondary: #94a3b8;
}

/* 漸層背景 */
body {
  background: linear-gradient(135deg, var(--bg-dark) 0%, var(--bg-light) 100%);
  color: var(--text-primary);
  font-family: 'Inter', sans-serif;
}

/* 玻璃態效果 */
.glass {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}
```

## 啟動開發伺服器

```bash
cd frontend
npm run dev
```

前端將在 `http://localhost:5173` 啟動。

## 建置生產版本

```bash
npm run build
```

建置檔案將輸出到 `dist/` 目錄。

## 整合測試

確保後端服務已啟動：

```bash
cd backend
python main.py
```

然後啟動前端並測試完整流程。

---

**注意事項**：
1. 確保瀏覽器允許存取相機權限
2. HTTPS 環境下相機存取更穩定
3. MediaPipe 需要穩定的網路連接來載入模型檔案（可改用本地版本）
