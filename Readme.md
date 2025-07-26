# 食べログスクレイピングツール

食べログのおすすめページやニューオープンページから店舗情報を効率的に収集するGUIアプリケーションです。

## 機能

- 都道府県別の店舗情報取得
- ページ範囲指定（1～60ページ）
- ニューオープン店舗の絞り込み
- 保存先とファイル名の自由設定
- 検索進捗の可視化
- 検索の中断機能
- Excel形式での結果出力

## 取得できる情報

- 店舗名
- ジャンル
- 住所
- オープン日
- 電話番号
- URL
- 営業時間/定休日
- 公式アカウント（Instagram等）
- サービス情報

## 必要な環境

- Python 3.8以上
- Windows 10/11（推奨）

## セットアップ手順

### 1. リポジトリのクローンまたはダウンロード

```bash
git clone https://github.com/your-username/tabelog-scraper.git
cd tabelog-scraper
```

### 2. 必要なパッケージのインストール

#### 基本パッケージ（実行に必要）
```bash
pip install pandas requests beautifulsoup4 openpyxl requests-cache lxml html5lib xlsxwriter
```

#### EXE化に必要な追加パッケージ
```bash
pip install cx_Freeze defusedxml et_xmlfile
```

#### 一括インストール（推奨）
```bash
pip install -r requirements.txt
```

### 3. requirements.txtの内容
```
pandas>=1.5.0
requests>=2.28.0
beautifulsoup4>=4.11.0
openpyxl>=3.0.0
requests-cache>=1.0.0
lxml>=4.9.0
html5lib>=1.1
xlsxwriter>=3.0.0
cx_Freeze>=6.15.0
defusedxml>=0.7.0
et_xmlfile>=1.1.0
certifi>=2022.0.0
chardet>=5.0.0
idna>=3.4
soupsieve>=2.3.0
urllib3>=1.26.0
```

## 起動について

### 起動時間の改善

アプリケーションには起動時間を改善するための仕組みが組み込まれています：

1. **スプラッシュスクリーン**
   - 起動中であることをユーザーに明確に表示
   - 各モジュールの読み込み状況をリアルタイム表示
   - 進捗バーによる視覚的フィードバック

2. **遅延読み込み**
   - 重いモジュール（pandas、requests等）は必要時まで読み込まない
   - UIの基本部分を先に表示してユーザビリティを向上

3. **バックグラウンド初期化**
   - モジュールの読み込みを別スレッドで実行
   - UIがフリーズしない設計

### 初回起動時の注意

- 初回起動時は各種モジュールの初期化のため、通常より時間がかかる場合があります
- スプラッシュスクリーンが表示されている間はアプリケーションの準備中です
- ESCキーで起動を中断できます

## 使用方法

### Python直接実行

```bash
python main.py
```

### 使用手順

1. **検索条件タブ**で条件を設定
   - 都道府県を選択（「全国」も可能）
   - ページ範囲を指定（1～60ページ）
   - ニューオープン店舗のみの場合はチェック

2. **保存設定**
   - 保存先フォルダを選択
   - ファイル名を入力（自動生成も可能）

3. **スクレイピング開始**をクリック

4. **検索中タブ**で進捗を確認
   - 必要に応じて「検索を停止」で中断可能

5. 完了後、指定した場所にExcelファイルが保存されます

## EXE化（配布用実行ファイル作成）

### 前提条件の確認

EXE化には以下のパッケージが必要です：

```bash
pip install cx_Freeze defusedxml et_xmlfile
```

### 方法1: バッチファイルを使用（Windows）

1. **build_exe.bat** をダブルクリック
   - 自動的に必要なパッケージをチェック・インストール
   - EXE化を実行

2. **出力確認**
   - `build/exe/` フォルダに実行ファイルが生成されます

### 方法2: 手動でEXE化

#### ステップ1: 必要なパッケージのインストール確認
```bash
pip install --upgrade pip
pip install cx_Freeze pandas requests beautifulsoup4 openpyxl requests-cache lxml html5lib xlsxwriter defusedxml et_xmlfile
```

#### ステップ2: EXE化の実行
```bash
python setup.py build
```

#### ステップ3: 出力ファイルの確認
- `build/exe/` フォルダに `TabelogScraper.exe` が生成されます
- このフォルダ全体を配布用として使用できます

### EXE化のトラブルシューティング

#### よくあるエラーと解決方法

1. **ImportError: No module named 'xxx'**
   ```bash
   pip install xxx
   ```

2. **catフォルダが見つからない**
   - プロジェクトフォルダに `cat/` フォルダがあることを確認
   - 必要なファイル: `prefectures.py`, `middle_categorys.py`, `small_categorys.py`

3. **ビルドが失敗する**
   - 最小限のsetup.pyを使用（シンプルなsetup.py）
   - 段階的にパッケージを追加

#### 代替案: PyInstaller

cx_Freezeで問題が発生する場合：

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --add-data "cat;cat" main.py
```

## バッチファイルの内容

### build_exe.bat
```batch
@echo off
echo =====================================
echo 食べログスクレイピングツール EXE化
echo =====================================
echo.

echo 必要なパッケージをインストール中...
pip install --upgrade pip
pip install cx_Freeze pandas requests beautifulsoup4 openpyxl requests-cache lxml html5lib xlsxwriter defusedxml et_xmlfile

echo.
echo EXE化を開始します...
python setup.py build

echo.
echo EXE化が完了しました。
echo build/exe フォルダを確認してください。
echo.
pause
```

## プロジェクト構造

```
tabelog-scraper/
├── main.py                    # メインアプリケーション
├── setup.py                   # EXE化設定ファイル
├── build_exe.bat             # EXE化用バッチファイル
├── requirements.txt          # 依存関係
├── README.md                 # このファイル
├── cat/                      # 都道府県・地域データ
│   ├── prefectures.py
│   ├── middle_categorys.py
│   └── small_categorys.py
├── scraping_functions.py     # スクレイピング関数（参考用）
└── build/                    # EXE化出力フォルダ
    └── exe/
        └── TabelogScraper.exe
```

## 配布方法

### 配布用パッケージの作成

1. **EXE化の完了確認**
   - `build/exe/` フォルダに `TabelogScraper.exe` が存在
   - 同じフォルダ内の必要なDLLやファイルも含まれている

2. **配布用フォルダの作成**
   - `build/exe/` フォルダ全体をZIPで圧縮
   - または、フォルダごとコピーして配布

3. **エンドユーザーでの使用**
   - 解凍したフォルダ内の `TabelogScraper.exe` を実行
   - Python環境は不要

## 使用上の注意

1. **利用規約の遵守**
   - 食べログの利用規約を必ず確認してください
   - 過度なアクセスは避け、適切な間隔でのスクレイピングを心がけてください

2. **レート制限**
   - アプリケーションには適切な待機時間が設定されています
   - 必要に応じて待機時間を調整してください

3. **データの取り扱い**
   - 取得したデータは個人利用の範囲で使用してください
   - 商用利用の際は適切な許可を取得してください

4. **技術的制約**
   - 食べログの仕様により、最大60ページまでの検索が可能です
   - サイトの構造変更により、動作しなくなる可能性があります

## トラブルシューティング

### よくある問題

1. **ModuleNotFoundError**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

2. **EXE化でエラーが発生**
   - Python環境の確認
   - 必要なパッケージの再インストール
   - catフォルダの存在確認

3. **スクレイピングが停止する**
   - ネットワーク接続の確認
   - 食べログサイトの状態確認
   - 待機時間の調整

4. **Excelファイルが保存されない**
   - 保存先フォルダの書き込み権限確認
   - ファイル名の有効性確認
   - 十分な空き容量の確認

### ログの確認

アプリケーションはコンソールにログを出力します。エラーが発生した場合は、コンソールの出力を確認してください。

## ライセンス

このプロジェクトは個人利用目的で作成されています。商用利用の際は適切な許可を取得してください。

## 貢献

バグレポートや機能提案は、GitHubのIssuesでお知らせください。

## 免責事項

このツールの使用によって生じた問題について、開発者は一切の責任を負いません。利用者の責任でご使用ください。