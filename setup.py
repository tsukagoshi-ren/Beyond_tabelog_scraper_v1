import sys
import os
from cx_Freeze import setup, Executable

# アプリケーションの基本情報
app_name = "TabelogScraper"
version = "2.0"
description = "食べログスクレイピングツール"

# 必要なパッケージをリストアップ
packages = [
    "tkinter",
    "pandas", 
    "openpyxl",  # pandasのExcel読み書きに必要
    "requests",
    "bs4",
    "beautifulsoup4",
    "requests_cache",
    "urllib3",
    "chardet",
    "certifi",
    "idna",
    "soupsieve",
    "lxml",  # BeautifulSoupの高速パーサー
    "html5lib",  # HTMLパーサー
    "et_xmlfile",  # openpyxlの依存関係
    "defusedxml",  # openpyxlの依存関係
    "six",
    "python_dateutil",
    "pytz",
    "numpy",
    "xlsxwriter",  # pandasのExcel書き込み支援
]

# 含めるファイル
include_files = [
    ("cat/", "cat/"),  # catフォルダ全体をコピー
]

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
    "notebook",
    "PyQt5",
    "PyQt6",
    "PySide2",
    "PySide6",
    "tkinter.test",
    "sqlite3",
    "asyncio",
    "multiprocessing",
    "concurrent",
    "xml.etree.ElementTree",
]

# build_exeのオプション
build_exe_options = {
    "packages": packages,
    "excludes": excludes,
    "include_files": include_files,
    "optimize": 2,  # 最適化レベル
    "build_exe": "build/exe",  # 出力ディレクトリ
    "include_msvcrt": True,  # Microsoft Visual C++ runtimeを含める
    "zip_include_packages": ["encodings", "importlib"],  # zipに含めるパッケージ
}

# 実行可能ファイルの設定
if sys.platform == "win32":
    base = "Win32GUI"  # Windowsの場合、コンソールを非表示にする
else:
    base = None

executables = [
    Executable(
        script="main.py",
        base=base,
        target_name=f"{app_name}.exe",
        icon=None,  # アイコンファイルがある場合はパスを指定
        copyright="© 2024 TabelogScraper",
        shortcut_name=app_name,
        shortcut_dir="DesktopFolder",
    )
]

# セットアップ
setup(
    name=app_name,
    version=version,
    description=description,
    author="Your Name",
    author_email="your.email@example.com",
    options={"build_exe": build_exe_options},
    executables=executables,
)