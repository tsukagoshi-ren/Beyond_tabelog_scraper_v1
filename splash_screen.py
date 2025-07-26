import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import sys
import os

class SplashScreen:
    """詳細なスプラッシュスクリーンクラス"""
    
    def __init__(self):
        self.splash = tk.Tk()
        self.splash.title("食べログスクレイピングツール")
        self.splash.geometry("400x300")
        self.splash.resizable(False, False)
        
        # ウィンドウを中央に配置
        self.splash.eval('tk::PlaceWindow . center')
        
        # ウィンドウの装飾を削除してスプラッシュスクリーンらしく
        self.splash.overrideredirect(True)
        
        # フレームの作成
        main_frame = tk.Frame(self.splash, bg='#f0f0f0', relief='ridge', bd=2)
        main_frame.pack(fill='both', expand=True)
        
        # アプリケーション名
        title_label = tk.Label(
            main_frame, 
            text="食べログスクレイピングツール", 
            font=("Helvetica", 18, "bold"),
            bg='#f0f0f0',
            fg='#333333'
        )
        title_label.pack(pady=30)
        
        # バージョン情報
        version_label = tk.Label(
            main_frame, 
            text="Version 2.0", 
            font=("Helvetica", 10),
            bg='#f0f0f0',
            fg='#666666'
        )
        version_label.pack()
        
        # 説明文
        desc_label = tk.Label(
            main_frame, 
            text="食べログから店舗情報を効率的に収集", 
            font=("Helvetica", 12),
            bg='#f0f0f0',
            fg='#555555'
        )
        desc_label.pack(pady=10)
        
        # 進捗バー
        self.progress = ttk.Progressbar(
            main_frame, 
            mode='indeterminate',
            length=250
        )
        self.progress.pack(pady=20)
        
        # ステータスラベル
        self.status_label = tk.Label(
            main_frame, 
            text="初期化中...", 
            font=("Helvetica", 10),
            bg='#f0f0f0',
            fg='#666666'
        )
        self.status_label.pack(pady=5)
        
        # コピーライト
        # copyright_label = tk.Label(
        #     main_frame, 
        #     text="© 2024 TabelogScraper", 
        #     font=("Helvetica", 8),
        #     bg='#f0f0f0',
        #     fg='#999999'
        # )
        # copyright_label.pack(side='bottom', pady=10)
        
        # 進捗バーをアニメーション開始
        self.progress.start(10)
        
        # ESCキーで強制終了
        self.splash.bind('<Escape>', lambda e: self.close())
        
        # 初期化処理を別スレッドで実行
        self.init_thread = threading.Thread(target=self.initialize_app, daemon=True)
        self.init_thread.start()
        
        # ウィンドウを最前面に表示
        self.splash.lift()
        self.splash.attributes('-topmost', True)
        
    def update_status(self, message):
        """ステータスメッセージを更新"""
        if self.splash.winfo_exists():
            self.status_label.config(text=message)
            self.splash.update()
    
    def initialize_app(self):
        """アプリケーションの初期化処理"""
        try:
            # 各モジュールを段階的にインポート
            self.update_status("パッケージを読み込み中...")
            time.sleep(0.5)
            
            self.update_status("Pandasを読み込み中...")
            import pandas as pd
            time.sleep(0.3)
            
            self.update_status("日時ライブラリを読み込み中...")
            from datetime import datetime
            time.sleep(0.2)
            
            self.update_status("リクエストライブラリを読み込み中...")
            import requests_cache
            import requests
            import requests.exceptions
            time.sleep(0.3)
            
            self.update_status("HTMLパーサーを読み込み中...")
            from bs4 import BeautifulSoup
            time.sleep(0.3)
            
            self.update_status("設定ファイルを読み込み中...")
            os.environ['TK_SILENCE_DEPRECATION'] = '1'
            from cat import prefectures
            time.sleep(0.3)
            
            self.update_status("キャッシュを初期化中...")
            requests_cache.install_cache('tabelog_cache', expire_after=3600)
            time.sleep(0.2)
            
            self.update_status("アプリケーションを起動中...")
            time.sleep(0.5)
            
            # モジュールをグローバルに設定
            import __main__
            __main__.pd = pd
            __main__.datetime = datetime
            __main__.requests_cache = requests_cache
            __main__.requests = requests
            __main__.requests_exceptions = requests.exceptions
            __main__.BeautifulSoup = BeautifulSoup
            __main__.prefectures = prefectures
            __main__._imports_loaded = True
            
            # メインウィンドウを作成
            self.splash.after(500, self.launch_main_app)
            
        except ImportError as e:
            self.update_status(f"モジュールの読み込みに失敗: {e}")
            time.sleep(2)
            self.close()
        except Exception as e:
            self.update_status(f"初期化エラー: {e}")
            time.sleep(2)
            self.close()
    
    def launch_main_app(self):
        """メインアプリケーションを起動"""
        try:
            self.close()
            # メイン関数を呼び出し（外部から設定される）
            if hasattr(self, 'main_app_function'):
                self.main_app_function()
        except Exception as e:
            messagebox.showerror("エラー", f"アプリケーションの起動に失敗しました: {e}")
            sys.exit(1)
    
    def set_main_app_function(self, func):
        """メインアプリケーション関数を設定"""
        self.main_app_function = func
    
    def close(self):
        """スプラッシュスクリーンを閉じる"""
        if self.splash.winfo_exists():
            self.progress.stop()
            self.splash.destroy()
    
    def show(self):
        """スプラッシュスクリーンを表示"""
        self.splash.mainloop()


class SimpleSplash:
    """シンプルなスプラッシュスクリーンクラス"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("食べログスクレイピングツール")
        self.root.geometry("300x150")
        self.root.resizable(False, False)
        self.root.eval('tk::PlaceWindow . center')
        self.root.overrideredirect(True)
        
        # シンプルなデザイン
        frame = tk.Frame(self.root, bg='white', relief='ridge', bd=1)
        frame.pack(fill='both', expand=True)
        
        title = tk.Label(frame, text="食べログスクレイピングツール", 
                        font=("Arial", 12, "bold"), bg='white')
        title.pack(pady=20)
        
        self.status = tk.Label(frame, text="起動中...", 
                              font=("Arial", 9), bg='white', fg='gray')
        self.status.pack()
        
        # 進捗バー
        self.progress = ttk.Progressbar(frame, mode='indeterminate', length=200)
        self.progress.pack(pady=15)
        self.progress.start()
        
        # ESCキーで終了
        self.root.bind('<Escape>', lambda e: self.close())
        
        # バックグラウンドで初期化
        threading.Thread(target=self.init_app, daemon=True).start()
    
    def update_status(self, text):
        """ステータスを更新"""
        if self.root.winfo_exists():
            self.status.config(text=text)
            self.root.update()
    
    def init_app(self):
        """アプリケーション初期化"""
        self.update_status("モジュールを読み込み中...")
        time.sleep(0.5)
        
        try:
            # 必要なモジュールを一括読み込み
            import pandas as pd
            from datetime import datetime
            import requests_cache
            import requests
            import requests.exceptions
            from bs4 import BeautifulSoup
            
            os.environ['TK_SILENCE_DEPRECATION'] = '1'
            from cat import prefectures
            
            requests_cache.install_cache('tabelog_cache', expire_after=3600)
            
            # モジュールをグローバルに設定
            import __main__
            __main__.pd = pd
            __main__.datetime = datetime
            __main__.requests_cache = requests_cache
            __main__.requests = requests
            __main__.requests_exceptions = requests.exceptions
            __main__.BeautifulSoup = BeautifulSoup
            __main__.prefectures = prefectures
            __main__._imports_loaded = True
            
        except Exception as e:
            self.update_status(f"エラー: {e}")
            time.sleep(2)
            self.close()
            return
        
        self.update_status("準備完了")
        time.sleep(0.3)
        
        # メインアプリを起動
        self.root.after(100, self.launch_main)
    
    def launch_main(self):
        """メインアプリを起動"""
        self.close()
        if hasattr(self, 'main_app_function'):
            self.main_app_function()
    
    def set_main_app_function(self, func):
        """メインアプリケーション関数を設定"""
        self.main_app_function = func
    
    def close(self):
        """スプラッシュスクリーンを閉じる"""
        if self.root.winfo_exists():
            self.progress.stop()
            self.root.destroy()
    
    def show(self):
        """スプラッシュスクリーンを表示"""
        self.root.mainloop()
