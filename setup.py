import sys
import os
from cx_Freeze import setup, Executable

# 基本的なパッケージのみ指定（存在するもののみ）
packages = [
    "tkinter",
    "threading",  # スプラッシュスクリーン用
    "time",       # スプラッシュスクリーン用
    "pandas",
    "requests",
    "bs4",
    "urllib3",
    "certifi",
    "chardet",
    "idna",
]

# 含めるファイル
include_files = []
if os.path.exists("cat"):
    include_files.append(("cat/", "cat/"))
    print("cat/ フォルダを含めます")

# splash_screen.pyファイルを含める
if os.path.exists("splash_screen.py"):
    include_files.append(("splash_screen.py", "splash_screen.py"))
    print("splash_screen.py を含めます")
else:
    print("警告: splash_screen.py が見つかりません")

# 除外するモジュール
excludes = [
    "test",
    "unittest",
    "distutils",
    "setuptools",
    "pip",
    "wheel",
    "matplotlib",
    "scipy",
    "IPython",
    "jupyter",
    "PyQt5",
    "PyQt6",
    "PySide2",
    "PySide6",
    "sqlite3",
]

# ビルドオプション（最小限）
build_exe_options = {
    "packages": packages,
    "excludes": excludes,
    "include_files": include_files,
}

# 実行ファイル設定
base = None
if sys.platform == "win32":
    base = "Win32GUI"

executables = [
    Executable(
        "main.py",
        base=base,
        target_name="TabelogScraper.exe"
    )
]

# セットアップ
setup(
    name="TabelogScraper",
    version="2.1",  # バージョンアップ
    description="食べログスクレイピングツール（分離型スプラッシュスクリーン対応）",
    options={"build_exe": build_exe_options},
    executables=executables
)