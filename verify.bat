@echo off
REM AI 瑜珈教練系統 - 驗證腳本
REM 此腳本將驗證系統是否正常運作

echo ========================================
echo AI 瑜珈教練系統 - 系統驗證
echo ========================================
echo.

set PASS_COUNT=0
set FAIL_COUNT=0

REM 1. 檢查 Python
echo [1/9] 檢查 Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [失敗] Python 未安裝
    set /a FAIL_COUNT+=1
) else (
    python --version
    echo [通過] Python 已安裝
    set /a PASS_COUNT+=1
)
echo.

REM 2. 檢查 Node.js
echo [2/9] 檢查 Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo [失敗] Node.js 未安裝
    set /a FAIL_COUNT+=1
) else (
    node --version
    echo [通過] Node.js 已安裝
    set /a PASS_COUNT+=1
)
echo.

REM 3. 檢查 MongoDB
echo [3/9] 檢查 MongoDB...
tasklist /FI "IMAGENAME eq mongod.exe" 2>NUL | find /I /N "mongod.exe">NUL
if errorlevel 1 (
    echo [失敗] MongoDB 服務未運行
    echo 提示: 執行 mongod 啟動 MongoDB
    set /a FAIL_COUNT+=1
) else (
    echo [通過] MongoDB 服務運行中
    set /a PASS_COUNT+=1
)
echo.

REM 4. 檢查後端虛擬環境
echo [4/9] 檢查後端虛擬環境...
if exist "backend\venv" (
    echo [通過] 虛擬環境已建立
    set /a PASS_COUNT+=1
) else (
    echo [失敗] 虛擬環境不存在
    echo 提示: 執行 install.bat
    set /a FAIL_COUNT+=1
)
echo.

REM 5. 檢查後端依賴
echo [5/9] 檢查後端 Python 套件...
if exist "backend\venv" (
    call backend\venv\Scripts\activate.bat
    pip show fastapi >nul 2>&1
    if errorlevel 1 (
        echo [失敗] FastAPI 未安裝
        set /a FAIL_COUNT+=1
    ) else (
        echo [通過] FastAPI 已安裝
        set /a PASS_COUNT+=1
    )
    deactivate
) else (
    echo [跳過] 虛擬環境不存在
    set /a FAIL_COUNT+=1
)
echo.

REM 6. 檢查前端依賴
echo [6/9] 檢查前端 npm 套件...
if exist "frontend\node_modules" (
    echo [通過] node_modules 已安裝
    set /a PASS_COUNT+=1
) else (
    echo [失敗] node_modules 不存在
    echo 提示: 執行 install.bat
    set /a FAIL_COUNT+=1
)
echo.

REM 7. 檢查後端 API (如果正在運行)
echo [7/9] 檢查後端 API...
curl -s http://localhost:8000/ >nul 2>&1
if errorlevel 1 (
    echo [警告] 後端 API 未運行或無法連接
    echo 提示: 執行 start.bat 啟動服務
    set /a FAIL_COUNT+=1
) else (
    echo [通過] 後端 API 運行中 (http://localhost:8000)
    set /a PASS_COUNT+=1
)
echo.

REM 8. 檢查前端服務 (如果正在運行)
echo [8/9] 檢查前端服務...
curl -s http://localhost:5173/ >nul 2>&1
if errorlevel 1 (
    echo [警告] 前端服務未運行或無法連接
    echo 提示: 執行 start.bat 啟動服務
    set /a FAIL_COUNT+=1
) else (
    echo [通過] 前端服務運行中 (http://localhost:5173)
    set /a PASS_COUNT+=1
)
echo.

REM 9. 檢查專案結構
echo [9/9] 檢查專案結構...
set STRUCTURE_OK=1

if not exist "backend\main.py" set STRUCTURE_OK=0
if not exist "backend\config.py" set STRUCTURE_OK=0
if not exist "backend\pose_analyzer.py" set STRUCTURE_OK=0
if not exist "frontend\src" set STRUCTURE_OK=0
if not exist "frontend\package.json" set STRUCTURE_OK=0

if %STRUCTURE_OK%==1 (
    echo [通過] 專案結構完整
    set /a PASS_COUNT+=1
) else (
    echo [失敗] 專案結構不完整
    set /a FAIL_COUNT+=1
)
echo.

REM 顯示結果
echo ========================================
echo 驗證結果
echo ========================================
echo 通過: %PASS_COUNT% 項
echo 失敗: %FAIL_COUNT% 項
echo.

if %FAIL_COUNT%==0 (
    echo [成功] 系統驗證通過！
    echo 您可以執行 start.bat 啟動系統
) else (
    echo [警告] 發現 %FAIL_COUNT% 個問題
    echo 請根據上述提示修復問題
    if %PASS_COUNT% LSS 6 (
        echo.
        echo 建議步驟：
        echo 1. 執行 install.bat 安裝依賴
        echo 2. 啟動 MongoDB (mongod)
        echo 3. 執行 start.bat 啟動系統
        echo 4. 重新執行 verify.bat 驗證
    )
)
echo.

REM 顯示系統資訊
echo ========================================
echo 系統資訊
echo ========================================
echo 專案路徑: %CD%
echo.
echo 後端設定:
if exist "backend\config.py" (
    echo - API: http://localhost:8000
    echo - 文檔: http://localhost:8000/docs
)
echo.
echo 前端設定:
if exist "frontend\package.json" (
    echo - URL: http://localhost:5173
)
echo.

pause
