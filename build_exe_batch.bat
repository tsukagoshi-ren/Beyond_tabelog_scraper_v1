@echo off
echo =====================================
echo 食べログスクレイピングツール EXE化
echo =====================================
echo.

echo 必要なパッケージをインストール中...
pip install cx_Freeze
pip install pandas openpyxl requests beautifulsoup4 requests-cache lxml html5lib xlsxwriter

echo.
echo EXE化を開始します...
python setup.py build

echo.
echo EXE化が完了しました。
echo build/exe フォルダを確認してください。
echo.
pause
