@echo off
REM 文件名: build_windows.bat
REM 创建日期: 2026-06-01
REM 功能描述: 本地 Nuitka 打包脚本，生成单文件 EXE。

setlocal

set /p VERSION="请输入版本号 (默认 test_0.1.0): "
if "%VERSION%"=="" set VERSION=test_0.1.0

echo.
echo [1/2] 构建前端...
cd frontend
call pnpm build
if errorlevel 1 (
    echo 前端构建失败！
    exit /b 1
)
cd ..

echo.
echo [2/2] Nuitka 打包...
uv run nuitka ^
    --mingw64 ^
    --standalone ^
    --onefile ^
    --windows-console-mode=disable ^
    --remove-output ^
    --include-package=nfc_writer ^
    --include-data-dir=frontend/dist=frontend/dist ^
    --windows-file-version=0.1.0.0 ^
    --windows-product-name="NFC Writer" ^
    --windows-company-name="NFC Writer" ^
    --windows-product-version=0.1.0.0 ^
    --output-filename=NFC-Writer_%VERSION%.exe ^
    --output-dir=dist ^
    --show-progress ^
    --show-memory ^
    src/nfc_writer/main.py

if errorlevel 1 (
    echo Nuitka 打包失败！
    exit /b 1
)

echo.
echo 打包完成: dist\NFC-Writer_%VERSION%.exe
endlocal
