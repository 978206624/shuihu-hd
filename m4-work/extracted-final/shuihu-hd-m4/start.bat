@echo off
cd /d "%~dp0"
echo 正在启动水浒神兽高清版...
where py >nul 2>nul && (start "" http://127.0.0.1:8765 & py -3 -m http.server 8765 --bind 127.0.0.1 & goto :eof)
where python >nul 2>nul && (start "" http://127.0.0.1:8765 & python -m http.server 8765 --bind 127.0.0.1 & goto :eof)
echo 没有找到 Python，请先从 https://www.python.org/downloads/ 安装 Python 3（安装时勾选 Add Python to PATH）。
pause
