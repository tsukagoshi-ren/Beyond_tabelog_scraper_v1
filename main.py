import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
import sys
import os

# スプラッシュスクリーンをインポート
from splash_screen import SimpleSplash, SplashScreen

# グローバル変数
is_scraping = False
stop_scraping = False
_imports_loaded = False

# 遅延インポートされるモジュール（スプラッシュスクリーンで初期化される）
pd = None
datetime = None
requests_cache = None
requests = None
requests_exceptions = None
BeautifulSoup = None
prefectures = None

def check_imports():
    """必要なモジュールが読み込まれているかチェック"""
    global _imports_loaded
    if not _imports_loaded:
        messagebox.showerror("エラー", "アプリケーションが正しく初期化されていません。")
        return False
    return True

def generate_tabelog_url(prefecture_code, start_page, new_open_mode=False):
    """食べログのURLを正確に生成する関数"""
    base_url = "https://tabelog.com"
    
    if new_open_mode:
        if prefecture_code:
            if start_page > 1:
                url = f"{base_url}/{prefecture_code}/rstLst/cond16-00-00/{start_page}/"
            else:
                url = f"{base_url}/{prefecture_code}/rstLst/cond16-00-00/"
        else:
            if start_page > 1:
                url = f"{base_url}/rstLst/cond16-00-00/{start_page}/"
            else:
                url = f"{base_url}/rstLst/cond16-00-00/"
    else:
        if prefecture_code:
            if start_page > 1:
                url = f"{base_url}/{prefecture_code}/rstLst/{start_page}/"
            else:
                url = f"{base_url}/{prefecture_code}/rstLst/"
        else:
            if start_page > 1:
                url = f"{base_url}/rstLst/{start_page}/"
            else:
                url = f"{base_url}/rstLst/"
    
    return url

def scrape_shop_details(shop_url):
    """店舗詳細をスクレイピングする関数"""
    if not check_imports():
        return {}
    
    retry_count = 0
    max_retries = 3
    wait_time = 5
    
    while retry_count < max_retries:
        try:
            shop_response = requests.get(shop_url, timeout=10)
            shop_response.raise_for_status()
            shop_soup = BeautifulSoup(shop_response.text, 'html.parser')
            
            # 店舗情報の抽出
            name_element = shop_soup.find('h2', class_='display-name') or shop_soup.find('h2', class_='rstdtl-header__rst-name')
            name = name_element.text.strip() if name_element else '店舗名がありません'
            
            address_element = shop_soup.find('p', class_='rstinfo-table__address') or shop_soup.find('p', class_='rstinfo-table__address-text')
            address = address_element.text.strip() if address_element else '住所がありません'
            
            # 営業時間の取得
            opening_hours_element = None
            for heading in shop_soup.find_all(['th', 'dt']):
                if '営業時間' in heading.text:
                    opening_hours_element = heading.find_next(['td', 'dd'])
                    break
            opening_hours = opening_hours_element.text.strip() if opening_hours_element else '営業時間がありません'
            
            phone_element = shop_soup.find('p', class_='rstdtl-side-yoyaku__tel-number') or shop_soup.find('strong', class_='rstinfo-table__tel-num')
            phone_number = phone_element.text.strip() if phone_element else '電話番号がありません'
            
            opened_date_element = shop_soup.find('p', class_='rstinfo-opened-date')
            opened_dates = opened_date_element.text.strip() if opened_date_element else 'オープン日がありません'
            
            instagram_element = shop_soup.find('a', class_='rstinfo-sns-instagram')
            instagram = instagram_element['href'] if instagram_element and 'href' in instagram_element.attrs else 'Instagramがありません'
            
            # サービスとジャンルの取得
            service = 'サービスがありません'
            genre = 'ジャンルがありません'
            
            for th in shop_soup.find_all('th'):
                if 'サービス' in th.text:
                    next_td = th.find_next('td')
                    if next_td:
                        service = next_td.get_text(strip=True)
                elif 'ジャンル' in th.text:
                    next_td = th.find_next('td')
                    if next_td:
                        genre = next_td.get_text(strip=True)
            
            return {
                '店舗名': name,
                'ジャンル': genre,
                '住所': address,
                'オープン日': opened_dates,
                '電話番号': phone_number,
                'URL': shop_url,
                '営業時間/定休日': opening_hours,
                '公式アカウント': instagram,
                'サービス': service
            }
            
        except Exception as e:
            print(f'{shop_url}でエラーが発生しました: {e}')
            retry_count += 1
            time.sleep(wait_time)
            wait_time *= 2
            
    return {}

def update_progress(page_value, page_max, item_count=0):
    """進捗バーを更新する（ページ進捗と取得件数を表示）"""
    progress_var.set(page_value / page_max * 100)
    progress_label.config(text=f"ページ進捗: {page_value}/{page_max} ページ")
    item_count_label.config(text=f"取得件数: {item_count} 件")
    window.update()

def update_status(text):
    """ステータスラベルを更新する"""
    status_label.config(text=text)
    window.update()

def get_prefecture_code(prefecture):
    """都道府県名から都道府県コードを取得する"""
    if not check_imports():
        return ""
    
    if prefecture == "全国":
        return ""
    return prefectures.prefectures_values.get(prefecture, "")

def browse_save_path():
    """保存先フォルダを選択する"""
    folder_path = filedialog.askdirectory(title="保存先フォルダを選択してください")
    if folder_path:
        save_path_var.set(folder_path)

def generate_default_filename():
    """デフォルトのファイル名を生成する"""
    if not check_imports():
        return "default_filename.xlsx"
    
    prefecture = prefecture_combo.get()
    new_open_mode = new_open_var.get()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if prefecture != "全国":
        file_prefix = prefecture
    else:
        file_prefix = "全国"
        
    if new_open_mode:
        file_prefix += "_ニューオープン"
        
    return f"{file_prefix}_scraped_data_{timestamp}.xlsx"

def generate_auto_filename():
    """自動ボタン用のファイル名生成関数"""
    filename = generate_default_filename()
    # 拡張子を除去
    if filename.endswith('.xlsx'):
        filename = filename[:-5]
    return filename

def auto_generate_filename():
    """自動ボタンが押された時の処理"""
    filename_entry.delete(0, tk.END)
    filename_entry.insert(0, generate_auto_filename())

def stop_scraping_process():
    """スクレイピングを停止する"""
    global stop_scraping
    stop_scraping = True
    update_status("スクレイピングを停止しています...")

def scrape_data_thread():
    """別スレッドでスクレイピングを実行する"""
    thread = threading.Thread(target=scrape_data)
    thread.daemon = True
    thread.start()

def scrape_data():
    """スクレイピングを実行する"""
    if not check_imports():
        return
    
    global is_scraping, stop_scraping
    is_scraping = True
    stop_scraping = False
    
    # 検索中タブに切り替え
    notebook.select(search_tab)
    notebook.tab(condition_tab, state="disabled")
    
    update_status("スクレイピングの準備中...")
    
    prefecture = prefecture_combo.get()
    start_page = int(start_page_entry.get()) if start_page_entry.get() else 1
    end_page = int(end_page_entry.get()) if end_page_entry.get() else 60
    new_open_mode = new_open_var.get()
    
    # ページ範囲の検証
    if start_page < 1 or end_page < 1 or start_page > end_page:
        messagebox.showerror("エラー", "ページ範囲が正しくありません。")
        notebook.tab(condition_tab, state="normal")
        notebook.select(condition_tab)
        is_scraping = False
        return
    
    if end_page > 60:
        messagebox.showerror("エラー", "終了ページは60以下で入力してください。")
        notebook.tab(condition_tab, state="normal")
        notebook.select(condition_tab)
        is_scraping = False
        return
    
    # 検索予定ページ数を計算
    total_pages = end_page - start_page + 1
    
    # 保存先とファイル名の取得
    save_path = save_path_var.get()
    filename = filename_entry.get().strip()
    
    if not save_path:
        save_path = os.path.expanduser("~\\Downloads")
    
    if not filename:
        filename = generate_auto_filename()
    
    # 拡張子を自動で付与
    if not filename.endswith('.xlsx'):
        filename += '.xlsx'
    
    prefecture_code = get_prefecture_code(prefecture)
    current_url = generate_tabelog_url(prefecture_code, start_page, new_open_mode)
    
    update_status(f"スクレイピング開始: {current_url}")
    all_scraped_data = []
    page_count = start_page
    pages_scraped = 0
    total_items = 0  # 取得件数をカウント
    
    progress_var.set(0)
    
    while current_url and page_count <= end_page and not stop_scraping:
        update_status(f"スクレイピング中: ページ {page_count}/{end_page}")
        update_progress(pages_scraped + 1, total_pages, total_items)
        
        try:
            response = requests.get(current_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            shop_list = soup.find_all('div', class_='list-rst')
            
            shop_count = len(shop_list)
            if shop_count == 0:
                break
                
            for i, shop in enumerate(shop_list):
                if stop_scraping:
                    break
                    
                update_status(f"ページ {page_count}/{end_page} - 店舗 {i+1}/{shop_count} スクレイピング中")
                detail_url_element = shop.find('a', class_='list-rst__rst-name-target') or shop.find('a', class_='list-rst__title-target')
                if detail_url_element and 'href' in detail_url_element.attrs:
                    shop_url = detail_url_element['href']
                    shop_data = scrape_shop_details(shop_url)
                    if shop_data and shop_data.get('店舗名') != '店舗名がありません':
                        total_items += 1
                    all_scraped_data.append(shop_data)
                    update_progress(pages_scraped + 1, total_pages, total_items)
                else:
                    all_scraped_data.append({})
                
                time.sleep(0.5)
            
            if stop_scraping:
                break
            
            pages_scraped += 1
            
            if page_count >= end_page:
                break
            
            # 次のページを探す
            next_link = soup.find('a', class_='c-pagination__arrow c-pagination__arrow--next')
            if next_link and 'href' in next_link.attrs:
                next_url = next_link['href']
                if not next_url.startswith("https://tabelog.com"):
                    next_url = "https://tabelog.com" + next_url
                current_url = next_url
                page_count += 1
                time.sleep(2)
            else:
                break
                
        except Exception as e:
            update_status(f"エラーが発生しました: {e}")
            break
    
    # 結果の保存
    if all_scraped_data and not stop_scraping:
        update_status("データをExcelに保存中...")
        df = pd.DataFrame(all_scraped_data)
        df = df[df['店舗名'] != '店舗名がありません']
        
        file_path = os.path.join(save_path, filename)
        
        try:
            df.to_excel(file_path, index=False)
            update_status(f"スクレイピングが完了しました。")
            messagebox.showinfo("完了", f"スクレイピングが完了しました。\n{file_path}に結果が保存されました。")
        except Exception as e:
            update_status(f"ファイル保存中にエラーが発生しました: {e}")
            messagebox.showerror("エラー", f"ファイル保存中にエラーが発生しました: {e}")
    elif stop_scraping:
        update_status("スクレイピングが停止されました。")
        messagebox.showinfo("停止", "スクレイピングが停止されました。")
    else:
        update_status("スクレイピングに失敗しました。")
        messagebox.showerror("エラー", "スクレイピングに失敗しました。")
    
    # 検索条件タブを有効化
    notebook.tab(condition_tab, state="normal")
    notebook.select(condition_tab)
    
    is_scraping = False
    stop_scraping = False

def create_gui():
    """GUIを作成する"""
    global prefecture_combo, start_page_entry, end_page_entry, new_open_var, window
    global progress_var, progress_label, status_label, new_open_check, item_count_label
    global notebook, condition_tab, search_tab, save_path_var, filename_entry
    
    window = tk.Tk()
    window.title("食べログスクレイピングツール")
    window.geometry("600x650")
    
    # タイトルラベル
    title_label = ttk.Label(window, text="食べログスクレイピングツール", font=("Helvetica", 16))
    title_label.pack(pady=10)
    
    # ノートブック（タブ）の作成
    notebook = ttk.Notebook(window)
    notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
    # 検索条件タブ
    condition_tab = ttk.Frame(notebook)
    notebook.add(condition_tab, text="検索条件")
    
    # 検索中タブ
    search_tab = ttk.Frame(notebook)
    notebook.add(search_tab, text="検索中")
    
    # === 検索条件タブの内容 ===
    condition_frame = ttk.Frame(condition_tab)
    condition_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # 都道府県選択
    prefecture_frame = ttk.Frame(condition_frame)
    prefecture_frame.pack(fill=tk.X, pady=5)
    
    prefecture_label = ttk.Label(prefecture_frame, text="都道府県:", width=15)
    prefecture_label.pack(side=tk.LEFT)
    
    # 初期値として一時的なリストを設定
    prefecture_combo = ttk.Combobox(prefecture_frame, values=["全国"])
    prefecture_combo.set("全国")
    prefecture_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    # フォーカス時に都道府県リストを読み込み
    def on_prefecture_focus(event):
        if check_imports():
            prefecture_values = ["全国"] + list(prefectures.prefectures_values.keys())
            prefecture_combo['values'] = prefecture_values
    
    prefecture_combo.bind('<Button-1>', on_prefecture_focus)
    
    # ページ範囲指定フレーム
    page_range_frame = ttk.LabelFrame(condition_frame, text="ページ範囲設定")
    page_range_frame.pack(fill=tk.X, pady=10)
    
    start_page_frame = ttk.Frame(page_range_frame)
    start_page_frame.pack(fill=tk.X, pady=5)
    
    start_page_label = ttk.Label(start_page_frame, text="開始ページ:", width=15)
    start_page_label.pack(side=tk.LEFT)
    
    start_page_entry = ttk.Entry(start_page_frame, width=10)
    start_page_entry.insert(0, "1")
    start_page_entry.pack(side=tk.LEFT, padx=(5, 10))
    
    end_page_label = ttk.Label(start_page_frame, text="終了ページ:", width=15)
    end_page_label.pack(side=tk.LEFT)
    
    end_page_entry = ttk.Entry(start_page_frame, width=10)
    end_page_entry.insert(0, "60")
    end_page_entry.pack(side=tk.LEFT, padx=(5, 0))
    
    page_info_label = ttk.Label(page_range_frame, text="※ 1~60ページの範囲で指定してください（食べログの仕様により最大60ページまで）", font=("Helvetica", 8))
    page_info_label.pack(pady=2)
    
    # オプションフレーム
    options_frame = ttk.Frame(condition_frame)
    options_frame.pack(fill=tk.X, pady=10)
    
    new_open_var = tk.BooleanVar(value=False)
    new_open_check = ttk.Checkbutton(options_frame, text="ニューオープン", variable=new_open_var)
    new_open_check.pack(side=tk.LEFT)
    
    # 保存設定フレーム
    save_frame = ttk.LabelFrame(condition_frame, text="保存設定")
    save_frame.pack(fill=tk.X, pady=10)
    
    save_path_frame = ttk.Frame(save_frame)
    save_path_frame.pack(fill=tk.X, pady=5)
    
    save_path_label = ttk.Label(save_path_frame, text="保存先:")
    save_path_label.pack(side=tk.LEFT)
    
    save_path_var = tk.StringVar(value=os.path.expanduser("~\\Downloads"))
    save_path_entry = ttk.Entry(save_path_frame, textvariable=save_path_var, state="readonly")
    save_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
    
    browse_button = ttk.Button(save_path_frame, text="参照", command=browse_save_path)
    browse_button.pack(side=tk.RIGHT)
    
    filename_frame = ttk.Frame(save_frame)
    filename_frame.pack(fill=tk.X, pady=5)
    
    filename_label = ttk.Label(filename_frame, text="ファイル名:")
    filename_label.pack(side=tk.LEFT)
    
    filename_entry = ttk.Entry(filename_frame)
    filename_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
    
    # 自動ボタン
    auto_button = ttk.Button(filename_frame, text="自動", command=auto_generate_filename, width=6)
    auto_button.pack(side=tk.RIGHT, padx=(5, 0))
    
    # 拡張子表示
    extension_label = ttk.Label(filename_frame, text=".xlsx", font=("Helvetica", 9), foreground="gray")
    extension_label.pack(side=tk.RIGHT)
    
    # ファイル名の初期値設定（フォーカス時に生成）
    def on_filename_focus(event):
        if not filename_entry.get():
            filename_entry.insert(0, generate_auto_filename())
    
    filename_entry.bind('<FocusIn>', on_filename_focus)
    
    # スクレイピング実行ボタン
    button_frame = ttk.Frame(condition_frame)
    button_frame.pack(pady=20)
    
    start_button = ttk.Button(button_frame, text="スクレイピング開始", command=scrape_data_thread)
    start_button.pack(ipadx=20, ipady=10)
    
    # 説明テキスト
    help_text = """
    使用方法：
    1. 対象の都道府県を選択（「全国」でも可）
    2. ページ範囲を指定（1~60ページの範囲で指定）
    3. オプションを設定
      - ニューオープン：新規オープン店舗のみをスクレイピングします
    4. 保存先とファイル名を設定
    5. 「スクレイピング開始」ボタンをクリックしてください
    
    スクレイピング中は「検索中」タブで進捗を確認できます。
    """
    
    help_label = ttk.Label(condition_frame, text=help_text, justify=tk.LEFT, wraplength=560)
    help_label.pack(pady=10)
    
    # === 検索中タブの内容 ===
    search_frame = ttk.Frame(search_tab)
    search_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    progress_display_frame = ttk.LabelFrame(search_frame, text="進捗状況")
    progress_display_frame.pack(fill=tk.X, pady=10)
    
    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(progress_display_frame, orient=tk.HORIZONTAL, length=100, mode='determinate', variable=progress_var)
    progress_bar.pack(fill=tk.X, padx=10, pady=10)
    
    progress_label = ttk.Label(progress_display_frame, text="ページ進捗: 0/0 ページ")
    progress_label.pack(pady=2)
    
    item_count_label = ttk.Label(progress_display_frame, text="取得件数: 0 件")
    item_count_label.pack(pady=2)
    
    status_frame = ttk.LabelFrame(search_frame, text="ステータス")
    status_frame.pack(fill=tk.X, pady=10)
    
    status_label = ttk.Label(status_frame, text="準備完了", wraplength=560)
    status_label.pack(pady=10)
    
    stop_button_frame = ttk.Frame(search_frame)
    stop_button_frame.pack(pady=20)
    
    stop_button = ttk.Button(stop_button_frame, text="検索を停止", command=stop_scraping_process)
    stop_button.pack(ipadx=20, ipady=10)
    
    search_help_text = """
    検索の進行状況をこちらで確認できます。
    
    - 進捗バー：現在のページ処理状況を表示
    - ページ進捗：処理中のページ数を表示
    - 取得件数：実際に取得できた店舗数を表示
    - ステータス：詳細な処理状況を表示
    - 検索を停止：現在の検索を中断します
    
    検索が完了または停止されると、自動的に「検索条件」タブに戻ります。
    """
    
    search_help_label = ttk.Label(search_frame, text=search_help_text, justify=tk.LEFT, wraplength=560)
    search_help_label.pack(pady=10)
    
    window.mainloop()

if __name__ == "__main__":
    # スプラッシュスクリーンの選択（SimpleSplash または SplashScreen）
    USE_DETAILED_SPLASH = True  # Falseにすると高速なSimpleSplashを使用
    
    if USE_DETAILED_SPLASH:
        splash = SplashScreen()
    else:
        splash = SimpleSplash()
    
    # メインアプリケーション関数を設定
    splash.set_main_app_function(create_gui)
    
    # スプラッシュスクリーンを表示してアプリケーションを開始
    splash.show()