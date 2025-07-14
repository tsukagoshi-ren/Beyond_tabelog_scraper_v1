import sys
import os
from cx_Freeze import setup, Executable

# パッケージの存在確認関数
def check_package_exists(package_name):
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False

# 確実に存在するパッケージのみを追加
base_packages = ["tkinter", "pandas", "requests", "bs4"]
optional_packages = [
    "openpyxl", "requests_cache", "urllib3", "certifi", "chardet", 
    "idna", "soupsieve", "lxml", "html5lib", "et_xmlfile", 
    "defusedxml", "xlsxwriter", "numpy", "dateutil", "pytz"
]

packages = base_packages.copy()
for pkg in optional_packages:
    if check_package_exists(pkg):
        packages.append(pkg)
        print(f"✓ {pkg} を含めます")
    else:
        print(f"✗ {pkg} が見つかりません（スキップ）")

# 含めるファイル
include_files = []
if os.path.exists("cat"):
    include_files.append(("cat/", "cat/"))
    print("✓ cat/ フォルダを含めます")
else:
    print("✗ cat/ フォルダが見つかりません")

# 除外するモジュール
excludes = [
    "test", "unittest", "distutils", "setuptools", "pip", "wheel",
    "matplotlib", "scipy", "IPython", "jupyter", "notebook",
    "PyQt5", "PyQt6", "PySide2", "PySide6", "tkinter.test",
    "sqlite3", "asyncio", "multiprocessing", "concurrent"
]

# ビルドオプション
build_exe_options = {
    "packages": packages,
    "excludes": excludes,
    "include_files": include_files,
    "optimize": 2,
    "silent_level": 1,
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

print(f"最終的なパッケージリスト: {packages}")

# セットアップ
setup(
    name="TabelogScraper",
    version="2.0",
    description="食べログスクレイピングツール",
    options={"build_exe": build_exe_options},
    executables=executables
)