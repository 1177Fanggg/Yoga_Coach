@echo off
REM AI 瑜珈教練系統 - 啟動腳本
REM 此腳本將同時啟動後端與前端服務

echo ========================================
echo AI 瑜珈教練系統 - 啟動程式
echo ========================================
echo.

REM 檢查 MongoDB 是否運行
echo [檢查] MongoDB 服務...
tasklist /FI "IMAGENAME eq mongod.exe" 2>NUL | find /I /N "mongod.exe">NUL
if errorlevel 1 (
    echo [警告] MongoDB 未運行
    echo 請在新的命令提示字元執行: mongod
    echo.
    echo 是否繼續啟動系統？ (MongoDB 未運行可能導致錯誤)
    pause
)
echo.

REM 檢查虛擬環境是否存在
if not exist "backend\venv" (
    echo [錯誤] 後端虛擬環境不存在
    echo 請先執行 install.bat 安裝依賴
    pause
    exit /b 1
)

REM 檢查前端 node_modules 是否存在
if not exist "frontend\node_modules" (
    echo [錯誤] 前端依賴未安裝
    echo 請先執行 install.bat 安裝依賴
    pause
    exit /b 1
)

echo [啟動] 正在啟動後端服務...
echo 後端 API: http://localhost:8000
echo API 文檔: http://localhost:8000/docs
echo.

REM 在新視窗啟動後端
start "AI 瑜珈教練 - 後端服務" cmd /k "cd backend && venv\Scripts\activate && python main.py"

REM 等待 3 秒讓後端啟動
timeout /t 3 /nobreak >nul

echo [啟動] 正在啟動前端服務...
echo 前端網址: http://localhost:5173
echo.

REM 在新視窗啟動前端
start "AI 瑜珈教練 - 前端服務" cmd /k "cd frontend && npm run dev"

echo ========================================
echo 系統啟動完成！
echo ========================================
echo.
echo 服務網址：
echo - 前端: http://localhost:5173
echo - 後端: http://localhost:8000
echo - API 文檔: http://localhost:8000/docs
echo.
echo 已在新視窗中啟動服務
echo 關閉視窗即可停止服務
echo.
pause
