import sys
from cx_Freeze import setup, Executable
# 必要なパッケージをリストアップ
packages = ["tkinter", "pandas", "urllib.parse", "os", "tkcalendar", "datetime", "requests", "bs4", "requests_cache", "cat", "scraping_functions"]
# 除外するモジュールをリストアップ（必要に応じて）
excludes = []
# GUIアプリの場合はbase="Win32GUI"を指定
if sys.platform == "win32":
    base = "Win32GUI"
else:
    base = None
setup(
    name="TabelogScraper",  # アプリケーション名
    version="1.0",
    description="食べログスクレイピングツール",
    options={"build_exe": {"packages": packages, "excludes": excludes}},
    executables=[Executable("main.py", base=base)]
)