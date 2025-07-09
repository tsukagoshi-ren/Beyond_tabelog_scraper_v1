import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os
from datetime import datetime
import requests_cache
import requests
from bs4 import BeautifulSoup
import requests.exceptions
import time
import threading

os.environ['TK_SILENCE_DEPRECATION'] = '1'
from cat import prefectures

# グローバル変数
is_scraping = False
stop_scraping = False

def generate_tabelog_url(prefecture_code, start_page, new_open_mode=False):
    """
    食べログのURLを正確に生成する関数
    
    Args:
        prefecture_code (str): 都道府県コード
        start_page (int): 開始ページ
        new_open_mode (bool): ニューオープンモードかどうか
    
    Returns:
        str: 生成されたURL
    """
    base_url = "https://tabelog.com"
    
    # ニューオープンモードの場合
    if new_open_mode:
        if prefecture_code:
            # ニューオープンモードでページ指定がある場合の処理
            if start_page > 1:
                url = f"{base_url}/{prefecture_code}/rstLst/cond16-00-00/{start_page}/"
            else:
                url = f"{base_url}/{prefecture_code}/rstLst/cond16-00-00/"
        else:
            # 全国のニューオープンモード
            if start_page > 1:
                url = f"{base_url}/rstLst/cond16-00-00/{start_page}/"
            else:
                url = f"{base_url}/rstLst/cond16-00-00/"
    else:
        # 通常のスクレイピングモード
        if prefecture_code:
            # ページ番号を正確に計算
            if start_page > 1:
                url = f"{base_url}/{prefecture_code}/rstLst/{start_page}/"
            else:
                url = f"{base_url}/{prefecture_code}/rstLst/"
        else:
            # 全国の場合
            if start_page > 1:
                url = f"{base_url}/rstLst/{start_page}/"
            else:
                url = f"{base_url}/rstLst/"
    
    return url

def scrape_shop_details(shop_url):
    retry_count = 0
    max_retries = 3
    wait_time = 5
    while retry_count < max_retries:
        try:
            shop_response = requests.get(shop_url, timeout=10)
            shop_response.raise_for_status()
            shop_soup = BeautifulSoup(shop_response.text, 'html.parser')
            
            # より柔軟なセレクタを使用
            name_element = shop_soup.find('h2', class_='display-name') or shop_soup.find('h2', class_='rstdtl-header__rst-name')
            name = name_element.text.strip() if name_element else '店舗名がありません'
            
            address_element = shop_soup.find('p', class_='rstinfo-table__address') or shop_soup.find('p', class_='rstinfo-table__address-text')
            address = address_element.text.strip() if address_element else '住所がありません'
            
            # より汎用的な方法で営業時間を取得
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
            
            # よりロバストな方法でサービスとジャンルを取得
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
        except requests.exceptions.RequestException as e:
            print(f'{shop_url}でエラーが発生しました: {e}')
            retry_count += 1
            time.sleep(wait_time)
            wait_time *= 2  # エクスポネンシャルバックオフ
        except AttributeError as e:
            print(f'{shop_url}で要素の取得に失敗しました: {e}')
            retry_count += 1
            time.sleep(wait_time)
        except Exception as e:
            print(f'{shop_url}で予期しないエラーが発生しました: {e}')
            return {}
    return {}

def update_progress(value, max_value):
    """進捗バーを更新する"""
    progress_var.set(value / max_value * 100)
    progress_label.config(text=f"進捗: {value}/{max_value} ページ")
    window.update()

def update_status(text):
    """ステータスラベルを更新する"""
    status_label.config(text=text)
    window.update()

def get_prefecture_code(prefecture):
    """都道府県名から都道府県コードを取得する"""
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

def stop_scraping_process():
    """スクレイピングを停止する"""
    global stop_scraping
    stop_scraping = True
    update_status("スクレイピングを停止しています...")

def scrape_data_thread():
    """別スレッドでスクレイピングを実行する（UIのフリーズを防ぐ）"""
    thread = threading.Thread(target=scrape_data)
    thread.daemon = True
    thread.start()

def scrape_data():
    """スクレイピングを実行する"""
    global is_scraping, stop_scraping
    is_scraping = True
    stop_scraping = False
    
    # 検索中タブに切り替え
    notebook.select(search_tab)
    
    # 検索条件タブを無効化
    notebook.tab(condition_tab, state="disabled")
    
    update_status("スクレイピングの準備中...")
    
    prefecture = prefecture_combo.get()
    start_page = int(start_page_entry.get()) if start_page_entry.get() else 1
    end_page = int(end_page_entry.get()) if end_page_entry.get() else 60
    new_open_mode = new_open_var.get()
    
    # ページ範囲の検証
    if start_page < 1 or end_page < 1 or start_page > end_page:
        messagebox.showerror("エラー", "ページ範囲が正しくありません。開始ページと終了ページを正しく入力してください。")
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
    filename = filename_entry.get()
    
    if not save_path:
        save_path = os.path.expanduser("~\\Downloads")
    
    if not filename:
        filename = generate_default_filename()
    
    # 拡張子の確認
    if not filename.endswith('.xlsx'):
        filename += '.xlsx'
    
    prefecture_code = get_prefecture_code(prefecture)
    
    # 新しいURL生成関数を使用
    current_url = generate_tabelog_url(prefecture_code, start_page, new_open_mode)
    
    update_status(f"スクレイピング開始: {current_url}")
    all_scraped_data = []
    page_count = start_page  # start_pageから開始
    pages_scraped = 0  # 実際にスクレイピングしたページ数
    
    # 進捗バーの初期化
    progress_var.set(0)
    
    while current_url and page_count <= end_page and not stop_scraping:
        update_status(f"スクレイピング中: ページ {page_count}/{end_page}")
        update_progress(pages_scraped + 1, total_pages)
        
        print(f"スクレイピング中: {current_url}, ページ数: {page_count}")
        try:
            response = requests.get(current_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            shop_list = soup.find_all('div', class_='list-rst')
            
            shop_count = len(shop_list)
            if shop_count == 0:
                print("このページには店舗がありません。")
                break
                
            for i, shop in enumerate(shop_list):
                if stop_scraping:
                    break
                    
                update_status(f"ページ {page_count}/{end_page} - 店舗 {i+1}/{shop_count} スクレイピング中")
                detail_url_element = shop.find('a', class_='list-rst__rst-name-target') or shop.find('a', class_='list-rst__title-target')
                if detail_url_element and 'href' in detail_url_element.attrs:
                    shop_url = detail_url_element['href']
                    shop_data = scrape_shop_details(shop_url)
                    all_scraped_data.append(shop_data)
                else:
                    print("店舗詳細URLが見つかりませんでした。")
                    all_scraped_data.append({})
                
                # 負荷軽減のための待機
                time.sleep(0.5)
            
            if stop_scraping:
                break
            
            # このページのスクレイピングが完了
            pages_scraped += 1
            
            # 指定された終了ページに達したかチェック
            if page_count >= end_page:
                print(f"指定された終了ページ({end_page}ページ)に達しました。スクレイピングを終了します。")
                break
            
            # 次のページを探す
            next_link = soup.find('a', class_='c-pagination__arrow c-pagination__arrow--next')
            if next_link and 'href' in next_link.attrs:
                next_url = next_link['href']
                if not next_url.startswith("https://tabelog.com"):
                    next_url = "https://tabelog.com" + next_url
                current_url = next_url
                page_count += 1
                # ページ間の待機時間を長めに設定
                time.sleep(2)
            else:
                print("次のページはありません。")
                break
                
        except requests.exceptions.RequestException as e:
            print(f'{current_url}でエラーが発生しました: {e}')
            update_status(f"エラーが発生しました: {e}")
            time.sleep(5)  # エラーが発生した場合、少し長めに待機
            break
        except Exception as e:  # 一般的な例外処理を追加
            print(f'予期しないエラーが発生しました: {e}')
            update_status(f"予期しないエラーが発生しました: {e}")
            break
    
    # 結果の保存
    if all_scraped_data and not stop_scraping:
        update_status("データをExcelに保存中...")
        df = pd.DataFrame(all_scraped_data)
        
        # 不要な空のデータを除外
        df = df[df['店舗名'] != '店舗名がありません']
        
        file_path = os.path.join(save_path, filename)
        
        try:
            df.to_excel(file_path, index=False)
            update_status(f"スクレイピングが完了しました。{filename}に結果が保存されました。")
            print(f'スクレイピングが完了しました。{filename}に結果が保存されました。')
            messagebox.showinfo("完了", f"スクレイピングが完了しました。\n{file_path}に結果が保存されました。")
        except Exception as e:
            update_status(f"ファイル保存中にエラーが発生しました: {e}")
            messagebox.showerror("エラー", f"ファイル保存中にエラーが発生しました: {e}")
    elif stop_scraping:
        update_status("スクレイピングが停止されました。")
        messagebox.showinfo("停止", "スクレイピングが停止されました。")
    else:
        update_status("スクレイピングに失敗しました。データが取得できませんでした。")
        messagebox.showerror("エラー", "スクレイピングに失敗しました。データが取得できませんでした。")
        print('スクレイピングに失敗しました。')
    
    # 検索条件タブを有効化
    notebook.tab(condition_tab, state="normal")
    
    # 検索条件タブに切り替え
    notebook.select(condition_tab)
    
    is_scraping = False
    stop_scraping = False

def on_filename_change(*args):
    """ファイル名が変更されたときの処理"""
    if not filename_entry.get():
        filename_entry.insert(0, generate_default_filename())

def create_gui():
    """GUIを作成する"""
    global prefecture_combo, start_page_entry, end_page_entry, new_open_var, window
    global progress_var, progress_label, status_label, new_open_check
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
    
    prefecture_values = ["全国"] + list(prefectures.prefectures_values.keys())
    prefecture_combo = ttk.Combobox(prefecture_frame, values=prefecture_values)
    prefecture_combo.set(prefecture_values[0])
    prefecture_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    # ページ範囲指定フレーム
    page_range_frame = ttk.LabelFrame(condition_frame, text="ページ範囲設定")
    page_range_frame.pack(fill=tk.X, pady=10)
    
    # 開始ページ指定
    start_page_frame = ttk.Frame(page_range_frame)
    start_page_frame.pack(fill=tk.X, pady=5)
    
    start_page_label = ttk.Label(start_page_frame, text="開始ページ:", width=15)
    start_page_label.pack(side=tk.LEFT)
    
    start_page_entry = ttk.Entry(start_page_frame, width=10)
    start_page_entry.insert(0, "1")
    start_page_entry.pack(side=tk.LEFT, padx=(5, 10))
    
    # 終了ページ指定
    end_page_label = ttk.Label(start_page_frame, text="終了ページ:", width=15)
    end_page_label.pack(side=tk.LEFT)
    
    end_page_entry = ttk.Entry(start_page_frame, width=10)
    end_page_entry.insert(0, "60")
    end_page_entry.pack(side=tk.LEFT, padx=(5, 0))
    
    # ページ範囲の説明
    page_info_label = ttk.Label(page_range_frame, text="※ 1~60ページの範囲で指定してください", font=("Helvetica", 8))
    page_info_label.pack(pady=2)
    
    # オプションフレーム
    options_frame = ttk.Frame(condition_frame)
    options_frame.pack(fill=tk.X, pady=10)
    
    # ニューオープン
    new_open_var = tk.BooleanVar(value=False)
    new_open_check = ttk.Checkbutton(options_frame, text="ニューオープン", variable=new_open_var)
    new_open_check.pack(side=tk.LEFT)
    
    # 保存設定フレーム
    save_frame = ttk.LabelFrame(condition_frame, text="保存設定")
    save_frame.pack(fill=tk.X, pady=10)
    
    # 保存先フォルダ
    save_path_frame = ttk.Frame(save_frame)
    save_path_frame.pack(fill=tk.X, pady=5)
    
    save_path_label = ttk.Label(save_path_frame, text="保存先:")
    save_path_label.pack(side=tk.LEFT)
    
    save_path_var = tk.StringVar(value=os.path.expanduser("~\\Downloads"))
    save_path_entry = ttk.Entry(save_path_frame, textvariable=save_path_var, state="readonly")
    save_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
    
    browse_button = ttk.Button(save_path_frame, text="参照", command=browse_save_path)
    browse_button.pack(side=tk.RIGHT)
    
    # ファイル名
    filename_frame = ttk.Frame(save_frame)
    filename_frame.pack(fill=tk.X, pady=5)
    
    filename_label = ttk.Label(filename_frame, text="ファイル名:")
    filename_label.pack(side=tk.LEFT)
    
    filename_entry = ttk.Entry(filename_frame)
    filename_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
    filename_entry.insert(0, generate_default_filename())
    
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
    
    # 進捗表示フレーム
    progress_display_frame = ttk.LabelFrame(search_frame, text="進捗状況")
    progress_display_frame.pack(fill=tk.X, pady=10)
    
    # 進捗バー
    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(progress_display_frame, orient=tk.HORIZONTAL, length=100, mode='determinate', variable=progress_var)
    progress_bar.pack(fill=tk.X, padx=10, pady=10)
    
    progress_label = ttk.Label(progress_display_frame, text="進捗: 0/0 ページ")
    progress_label.pack(pady=5)
    
    # ステータス表示
    status_frame = ttk.LabelFrame(search_frame, text="ステータス")
    status_frame.pack(fill=tk.X, pady=10)
    
    status_label = ttk.Label(status_frame, text="準備完了", wraplength=560)
    status_label.pack(pady=10)
    
    # 停止ボタン
    stop_button_frame = ttk.Frame(search_frame)
    stop_button_frame.pack(pady=20)
    
    stop_button = ttk.Button(stop_button_frame, text="検索を停止", command=stop_scraping_process)
    stop_button.pack(ipadx=20, ipady=10)
    
    # 検索中タブの説明
    search_help_text = """
    検索の進行状況をこちらで確認できます。
    
    - 進捗バー：現在の処理状況を表示
    - ステータス：詳細な処理状況を表示
    - 検索を停止：現在の検索を中断します
    
    検索が完了または停止されると、自動的に「検索条件」タブに戻ります。
    
    ※ 食べログの仕様により、最大60ページまでの検索が可能です。
    """
    
    search_help_label = ttk.Label(search_frame, text=search_help_text, justify=tk.LEFT, wraplength=560)
    search_help_label.pack(pady=10)
    
    window.mainloop()

if __name__ == "__main__":
    requests_cache.install_cache('tabelog_cache', expire_after=3600)
    create_gui()