# AI 瑜珈教練系統 - 快速開始指南

## 三步驟啟動系統

### 1️⃣ 安裝依賴
```bash
install.bat
```
此腳本將：
- ✅ 檢查 Python 與 Node.js 環境
- ✅ 建立 Python 虛擬環境
- ✅ 安裝後端 Python 套件
- ✅ 安裝前端 npm 套件

### 2️⃣ 啟動 MongoDB
在新的命令提示字元執行：
```bash
mongod
```

### 3️⃣ 啟動系統
```bash
start.bat
```
此腳本將：
- 🚀 啟動後端 API 服務 (http://localhost:8000)
- 🚀 啟動前端網頁應用 (http://localhost:5173)

---

## 🔍 驗證系統

執行驗證腳本檢查系統狀態：
```bash
verify.bat
```

驗證項目：
- Python 是否已安裝
- Node.js 是否已安裝
- MongoDB 是否運行
- 虛擬環境是否建立
- 依賴套件是否安裝
- 後端/前端服務是否運行
- 專案結構是否完整

---

## 📋 系統需求

### 必要軟體
- **Python 3.8+** - [下載](https://www.python.org/downloads/)
- **Node.js 18+** - [下載](https://nodejs.org/)
- **MongoDB 4.0+** - [下載](https://www.mongodb.com/try/download/community)

### 硬體需求
- **RAM**: 4GB+ (建議 8GB)
- **USB 攝影機**: 建議 1080p

---

## 📡 服務網址

啟動後可訪問：

### 前端
- **主頁**: http://localhost:5173

### 後端
- **API 根路徑**: http://localhost:8000
- **Swagger 文檔**: http://localhost:8000/docs
- **ReDoc 文檔**: http://localhost:8000/redoc

---

## 🚨 常見問題

### Q: install.bat 報錯 "Python 未安裝"
**A**: 請先安裝 Python 3.8+ 並確認已加入系統 PATH

### Q: MongoDB 連接失敗
**A**: 確認 `mongod` 命令已在背景執行

### Q: 前端顯示 "無法連接後端"
**A**: 確認後端服務已啟動 (http://localhost:8000)

### Q: 相機無法啟動
**A**: 
1. 確認 USB 攝影機已連接
2. 瀏覽器允許相機權限
3. 檢查 `backend/config.py` 中的 `CAMERA_INDEX` 設定

---

## 📂 專案結構

```
Yoga_Coach/
├── install.bat          ← 安裝腳本
├── start.bat            ← 啟動腳本
├── verify.bat           ← 驗證腳本
├── backend/             ← 後端 Python 程式
├── frontend/            ← 前端 React 應用
├── tests/               ← 測試檔案
├── videos/              ← 影片輸出
├── logs/                ← 日誌檔案
└── .docs/               ← 技術文檔
```

---

## 🎯 使用流程

1. **執行 install.bat** - 首次使用時安裝依賴
2. **啟動 MongoDB** - `mongod`
3. **執行 start.bat** - 啟動系統
4. **開啟瀏覽器** - 訪問 http://localhost:5173
5. **開始練習** - 點擊「開始練習」按鈕
6. **執行瑜珈姿勢** - 面對攝影機執行動作
7. **查看即時回饋** - 右側顯示姿勢分析與分數
8. **結束練習** - 系統自動合併影片
9. **查看歷史** - 瀏覽練習記錄與回放影片

---

## 📖 詳細文檔

- **README.md** - 完整專案說明
- **.docs/Yoga_Coach_Tech_File.md** - 技術手冊
- **.docs/API_Documentation.md** - API 文檔
- **.docs/Frontend_Guide.md** - 前端開發指南
- **.docs/Frontend_UI_Design.md** - UI 設計規劃

---

## 🛠️ 開發模式

### 後端開發
```bash
cd backend
venv\Scripts\activate
python main.py
```

### 前端開發
```bash
cd frontend
npm run dev
```

### 執行測試
```bash
cd tests
python test_pose_analyzer.py
```

---

## 停止服務

關閉啟動的命令提示字元視窗即可停止服務

或按 `Ctrl + C` 中斷執行

---

**版本**: 1.0.0  
**最後更新**: 2026-01-14
