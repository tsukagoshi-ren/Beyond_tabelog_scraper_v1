import sys
import os
from cx_Freeze import setup, Executable

# cx_Freezeのバージョンを確認
try:
    from cx_Freeze import __version__ as cx_freeze_version
    print(f"cx_Freeze バージョン: {cx_freeze_version}")
except ImportError:
    cx_freeze_version = "unknown"

# 基本的なパッケージのみ指定
packages = [
    "tkinter",
    "tkinter.ttk",
    "tkinter.filedialog",
    "tkinter.messagebox",
    "threading",
    "time",
    "pandas",
    "requests",
    "bs4",
    "urllib3",
    "certifi",
    "chardet",
    "idna",
    "splash_screen",  # splash_screen.pyをパッケージとして含める
]

# 含めるファイル
include_files = []

# catフォルダの存在を確認して含める
if os.path.exists("cat"):
    include_files.append(("cat/", "cat/"))
    print("✓ cat/ フォルダを含めます")
else:
    print("✗ 警告: cat/ フォルダが見つかりません")

# splash_screen.pyの存在確認
if os.path.exists("splash_screen.py"):
    print("✓ splash_screen.py が見つかりました")
else:
    print("✗ 警告: splash_screen.py が見つかりません")

# tcl/tkライブラリを手動で追加
import tkinter
print(f"tkinter パス: {tkinter.__file__}")

# Pythonのtcl/tkライブラリパスを探す
possible_tcl_paths = [
    os.path.join(sys.prefix, "tcl"),
    os.path.join(sys.prefix, "Library", "lib"),
    os.path.join(sys.exec_prefix, "tcl"),
    os.path.join(sys.exec_prefix, "Library", "lib"),
    os.path.join(os.path.dirname(sys.executable), "tcl"),
    os.path.join(os.path.dirname(sys.executable), "Library", "lib"),
]

tcl_found = False
for tcl_path in possible_tcl_paths:
    if os.path.exists(tcl_path):
        print(f"tcl/tkライブラリを検索: {tcl_path}")
        try:
            for item in os.listdir(tcl_path):
                if item.startswith(('tcl8', 'tk8')):
                    item_path = os.path.join(tcl_path, item)
                    if os.path.isdir(item_path):
                        include_files.append((item_path, f"lib/{item}"))
                        print(f"✓ {item} ライブラリを含めます")
                        tcl_found = True
        except Exception as e:
            print(f"⚠️ {tcl_path} の読み込み中にエラー: {e}")
            continue

if not tcl_found:
    print("⚠️ tcl/tkライブラリが見つかりませんでした")

# 除外するモジュール（最小限）
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

# 最小限のビルドオプション（互換性最優先）
build_exe_options = {
    "packages": packages,
    "excludes": excludes,
    "include_files": include_files,
}

# 出力フォルダ名を設定
output_dir = "食べログスクレイパー"
build_exe_options["build_exe"] = output_dir
print(f"✓ 出力フォルダ: {output_dir}")

# 実行ファイル設定
base = None
if sys.platform == "win32":
    base = "Win32GUI"
    print("✓ Windows GUI モードに設定")

executables = [
    Executable(
        "main.py",
        base=base,
        target_name="TabelogScraper.exe",
    )
]

# デバッグ情報表示
print("\n=== ビルド設定 ===")
print(f"パッケージ数: {len(packages)}")
print(f"除外モジュール数: {len(excludes)}")
print(f"含有ファイル数: {len(include_files)}")
print("==================\n")

# セットアップ実行
setup(
    name="TabelogScraper",
    version="2.1",
    description="食べログスクレイピングツール",
    options={"build_exe": build_exe_options},
    executables=executables
)