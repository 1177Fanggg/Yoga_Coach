@echo off
REM AI 瑜珈教練系統 - 安裝腳本
REM 此腳本將安裝所有必要的依賴

echo ========================================
echo AI 瑜珈教練系統 - 安裝程式
echo ========================================
echo.

REM 檢查 Python 是否安裝
echo [1/5] 檢查 Python 環境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [錯誤] 未偵測到 Python，請先安裝 Python 3.8+
    echo 下載連結: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [成功] Python 已安裝
echo.

REM 檢查 Node.js 是否安裝
echo [2/5] 檢查 Node.js 環境...
node --version >nul 2>&1
if errorlevel 1 (
    echo [錯誤] 未偵測到 Node.js，請先安裝 Node.js 18+
    echo 下載連結: https://nodejs.org/
    pause
    exit /b 1
)
echo [成功] Node.js 已安裝
echo.

REM 安裝後端依賴
echo [3/5] 安裝後端 Python 依賴...
cd backend

REM 建立虛擬環境（如果不存在）
if not exist "venv" (
    echo 建立 Python 虛擬環境...
    python -m venv venv
)

REM 啟動虛擬環境並安裝依賴
echo 安裝 Python 套件...
call venv\Scripts\activate.bat
pip install -r requirements.txt
if errorlevel 1 (
    echo [錯誤] 後端依賴安裝失敗
    pause
    exit /b 1
)
deactivate
echo [成功] 後端依賴安裝完成
echo.

cd ..

REM 安裝前端依賴
echo [4/5] 安裝前端 npm 依賴...
cd frontend

REM 檢查是否已安裝 node_modules
if not exist "node_modules" (
    echo 安裝 npm 套件...
    call npm install
    if errorlevel 1 (
        echo [錯誤] 前端依賴安裝失敗
        pause
        exit /b 1
    )
) else (
    echo node_modules 已存在，跳過安裝
)
echo [成功] 前端依賴安裝完成
echo.

cd ..

REM 檢查 MongoDB
echo [5/5] 檢查 MongoDB...
echo.
echo 請確認 MongoDB 已安裝並啟動：
echo - 下載: https://www.mongodb.com/try/download/community
echo - 啟動: 執行 mongod 命令
echo.

echo ========================================
echo 安裝完成！
echo ========================================
echo.
echo 下一步：
echo 1. 啟動 MongoDB (在新的命令提示字元執行: mongod)
echo 2. 執行 start.bat 啟動系統
echo 3. 執行 verify.bat 驗證系統
echo.
pause
