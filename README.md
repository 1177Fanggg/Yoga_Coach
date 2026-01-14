# AI 瑜珈教練系統

一套**純本地端** AI 瑜珈教練應用，透過 USB 攝影機即時捕捉使用者姿勢，利用 MediaPipe 進行骨架辨識，提供即時回饋與影片回放功能。

## 專案概述

### 核心功能
-  1080p USB 相機即時影像擷取
-  MediaPipe 姿勢分析（支援 Warrior II、Tree Pose、Downward Dog）
-  即時文字 + 分數 + 語音回饋
-  自動錄製與合併標註影片
-  練習歷史記錄與查詢
-  離線 TTS 語音回饋 (pyttsx3)

### 技術棧
- **後端**: FastAPI + OpenCV + MediaPipe + MongoDB
- **前端**: React + Vite
- **語音**: pyttsx3（離線 TTS）
- **資料庫**: MongoDB
- **影片處理**: OpenCV + FFmpeg

## 專案結構

```
Yoga_Coach/
├── backend/                    # 後端 FastAPI 服務
│   ├── main.py                 # API 主程式
│   ├── config.py               # 設定檔
│   ├── pose_analyzer.py        # 姿勢分析模組
│   ├── video_processor.py      # 影片處理模組
│   ├── database.py             # 資料庫模組
│   ├── tts_service.py          # 語音回饋服務
│   └── requirements.txt        # Python 依賴
├── frontend/                   # 前端 React 專案（需手動建立）
├── tests/                      # 測試目錄
│   └── test_pose_analyzer.py   # 姿勢分析單元測試
├── videos/                     # 影片輸出目錄
│   ├── sessions/               # 最終合併影片
│   └── segments/               # 片段影片
├── audio/                      # 語音檔案目錄
├── logs/                       # 日誌目錄
├── models/                     # MediaPipe 權重
│   └── 0.05_svc.pkl
└── .docs/                      # 技術文檔
    ├── Yoga_Coach_Tech_File.md # 技術手冊
    └── API_Documentation.md    # API 文檔
```

## 安裝與設定

### 前置需求

1. **Python 3.8+**
2. **MongoDB** - 本地端服務
   - 下載：https://www.mongodb.com/try/download/community
   - 安裝後啟動服務：`mongod`
3. **USB 攝影機** - 建議 1080p
4. **Node.js 18+** - 用於前端開發
   - 下載：https://nodejs.org/

### 後端安裝

```bash
# 1. 建立 Python 虛擬環境
cd backend
python -m venv venv

# 2. 啟動虛擬環境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. 安裝依賴
pip install -r requirements.txt

# 4. 確認 MongoDB 服務運行
# 在另一個終端機執行：
mongod

# 5. 啟動後端服務
python main.py
# 或使用 uvicorn：
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

後端服務將在 `http://localhost:8000` 啟動。

API 文檔：`http://localhost:8000/docs`

### 前端安裝

```bash
# 1. 建立 React 專案（使用 Vite）
cd Yoga_Coach
npm create vite@latest frontend -- --template react

# 2. 安裝依賴
cd frontend
npm install

# 3. 安裝額外依賴（依需要）
npm install axios

# 4. 啟動開發伺服器
npm run dev
```

前端將在 `http://localhost:5173` 啟動。

> **注意**：前端程式碼需要根據 `.docs/Yoga_Coach_Tech_File.md` 技術手冊建置。目前僅完成後端實作。

## 使用方式

### 1. 啟動系統

1. 啟動 MongoDB 服務
2. 啟動後端服務（`python backend/main.py`）
3. 啟動前端服務（`cd frontend && npm run dev`）
4. 連接 USB 攝影機

### 2. 開始練習

1. 前端點擊「開始練習」
2. 系統建立新 session 並啟動相機
3. 執行瑜珈姿勢（Warrior II / Tree Pose / Downward Dog）
4. 查看即時回饋（姿勢名稱、分數、建議）
5. 結束練習，系統自動合併影片

### 3. 查看歷史

1. 進入「歷史記錄」頁面
2. 選擇 session 查看詳情
3. 播放回放影片

## API 端點

完整 API 文檔請參考：`.docs/API_Documentation.md`

主要端點：
- `POST /start_session` - 開始練習
- `POST /pose_analysis` - 姿勢分析
- `POST /end_segment` - 結束片段
- `POST /merge_and_export` - 合併影片
- `GET /user_history` - 查詢歷史
- `GET /session_detail` - Session 詳情
- `POST /tts_feedback` - 語音回饋
- `WebSocket /ws` - 即時回饋推送

## 測試

### 單元測試

```bash
cd tests
python test_pose_analyzer.py
```

### 使用 pytest

```bash
cd backend
pytest ../tests/ -v
```

## 支援的瑜珈姿勢

目前支援三種基礎瑜珈姿勢：

1. **Warrior II（戰士二式）**
   - 雙臂水平展開
   - 前腿彎曲 90 度
   - 後腿伸直

2. **Tree Pose（樹式）**
   - 單腿站立
   - 另一腿彎曲貼於支撐腿
   - 雙手合十

3. **Downward Dog（下犬式）**
   - 身體呈倒 V 字形
   - 雙手雙腳著地
   - 臀部抬高

## 設定調整

編輯 `backend/config.py` 可調整以下參數：

- 相機解析度與 FPS
- MediaPipe 偵測信心度
- 姿勢分數門檻
- TTS 語速與音量
- MongoDB 連接字串

## 日誌與監控

日誌檔案位置：`logs/yoga_coach.log`

包含：
- API 請求記錄
- 姿勢分析結果
- 影片處理狀態
- 錯誤訊息

## 常見問題

### Q: 相機無法啟動？
A: 檢查相機是否已連接，並確認 `config.py` 中的 `CAMERA_INDEX` 設定正確（預設為 0）。

### Q: MongoDB 連接失敗？
A: 確認 MongoDB 服務已啟動，預設連接字串為 `mongodb://localhost:27017`。

### Q: 中文語音無法播放？
A: pyttsx3 需要系統支援中文語音引擎，Windows 內建支援。Linux 可能需要安裝額外套件。

### Q: 姿勢分數一直很低？
A: 調整 `config.py` 中的 `ANGLE_TOLERANCE` 參數增加容錯範圍。

## 未來擴充

- ✨ 增加更多瑜珈姿勢（Plank、Chair、Warrior I 等）
- 🤖 導入 ML 模型輔助姿勢辨識
- 📱 支援手機/平板相機
- 👥 使用者帳號系統
- 📈 進度追蹤與統計圖表
- 🎨 前端骨架疊加視覺化
- 🌐 多語言 TTS 支援

## 技術文檔

- **技術手冊**：`.docs/Yoga_Coach_Tech_File.md`
- **API 文檔**：`.docs/API_Documentation.md`

## 授權

本專案為內部使用專案。

## 貢獻者

- Yi（技術開發）
- 與 Grok、Gemini 協作優化

---

**版本**: 1.0.0  
**最後更新**: 2026-01-14
