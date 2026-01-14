# 啟動步驟指南

## 快速啟動（在虛擬環境中）

### Windows PowerShell

```powershell
# 1. 進入 backend 目錄
cd c:\Users\RAG\Desktop\Yoga_Coach\backend

# 2. 啟動虛擬環境
.\venv\Scripts\Activate.ps1
# 如果遇到執行政策錯誤，先執行：
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 3. 安裝依賴（如果尚未安裝）
pip install -r requirements.txt

# 4. 啟動 MongoDB（在另一個終端機）
mongod

# 5. 執行後端服務
python main.py
```

### 訪問 API 文檔
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 停止服務
- 按 `Ctrl + C` 停止後端服務
- 退出虛擬環境：`deactivate`

## 常見問題

### 虛擬環境執行政策錯誤
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### MongoDB 連接失敗
確保 MongoDB 服務已啟動：
```powershell
# 啟動 MongoDB
mongod
```

### 相機存取失敗
- 確認 USB 相機已連接
- 檢查 `config.py` 中的 `CAMERA_INDEX`（預設為 0）
