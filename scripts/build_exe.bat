@echo off
rem 一键打包为单文件 exe（需要先: pip install pyinstaller tkinterdnd2）
cd /d "%~dp0.."
python -m PyInstaller --onefile --windowed --name "全能TXT文本处理器" --collect-all tkinterdnd2 "全能TXT文本处理器.py"
echo.
echo 打包完成，输出位于 dist\全能TXT文本处理器.exe
pause
