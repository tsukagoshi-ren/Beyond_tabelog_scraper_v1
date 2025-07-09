import tkinter as tk
from tkinter import ttk
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

def disable_controls():
    """スクレイピング中のコントロールを無効化する"""
    prefecture_combo.configure(state="disabled")
    start_page_entry.configure(state="disabled")
    fifty_page_check.configure(state="disabled")
    new_open_check.configure(state="disabled")
    area_scrape_button.configure(state="disabled")

def enable_controls():
    """スクレイピング終了後にコントロールを有効化する"""
    prefecture_combo.configure(state="normal")
    start_page_entry.configure(state="normal")
    fifty_page_check.configure(state="normal")
    new_open_check.configure(state="normal")
    area_scrape_button.configure(state="normal")

def get_prefecture_code(prefecture):
    """都道府県名から都道府県コードを取得する"""
    if prefecture == "全国":
        return ""
    return prefectures.prefectures_values.get(prefecture, "")

def scrape_data_thread():
    """別スレッドでスクレイピングを実行する（UIのフリーズを防ぐ）"""
    thread = threading.Thread(target=scrape_data)
    thread.daemon = True
    thread.start()

def scrape_data():
    """スクレイピングを実行する"""
    disable_controls()
    update_status("スクレイピングの準備中...")
    
    prefecture = prefecture_combo.get()
    start_page = int(start_page_entry.get()) if start_page_entry.get() else 1
    fifty_page_mode = fifty_page_var.get()
    new_open_mode = new_open_var.get()
    max_pages = 50 if fifty_page_mode else 999
    
    # スクレイピングする最大ページ数を計算
    end_page = start_page + max_pages - 1
    
    prefecture_code = get_prefecture_code(prefecture)
    
    # 新しいURL生成関数を使用
    current_url = generate_tabelog_url(prefecture_code, start_page, new_open_mode)
    
    update_status(f"スクレイピング開始: {current_url}")
    all_scraped_data = []
    page_count = start_page  # start_pageから開始
    pages_scraped = 0  # 実際にスクレイピングしたページ数
    
    # 進捗バーの初期化
    progress_var.set(0)
    
    while current_url and page_count <= end_page:
        update_status(f"スクレイピング中: ページ {page_count}/{end_page}")
        update_progress(pages_scraped + 1, max_pages)
        
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
            
            # このページのスクレイピングが完了
            pages_scraped += 1
            
            # 最大ページ数に達したかチェック
            if pages_scraped >= max_pages:
                print(f"最大ページ数({max_pages}ページ)に達しました。スクレイピングを終了します。")
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
    if all_scraped_data:
        update_status("データをExcelに保存中...")
        df = pd.DataFrame(all_scraped_data)
        
        # 不要な空のデータを除外
        df = df[df['店舗名'] != '店舗名がありません']
        
        download_dir = os.path.expanduser("~\\Downloads")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if prefecture != "全国":
            file_prefix = prefecture
        else:
            file_prefix = "全国"
            
        if new_open_mode:
            file_prefix += "_ニューオープン"
            
        file_name = f"{file_prefix}_scraped_data_{timestamp}.xlsx"
        file_path = os.path.join(download_dir, file_name)
        
        df.to_excel(file_path, index=False)
        update_status(f"スクレイピングが完了しました。{file_name}に結果が保存されました。")
        print(f'スクレイピングが完了しました。{file_name}に結果が保存されました。')
    else:
        update_status("スクレイピングに失敗しました。データが取得できませんでした。")
        print('スクレイピングに失敗しました。')
    
    enable_controls()

def create_gui():
    """GUIを作成する"""
    global prefecture_combo, start_page_entry, fifty_page_var, area_scrape_button, new_open_var, window
    global progress_var, progress_label, status_label, fifty_page_check, new_open_check
    
    window = tk.Tk()
    window.title("食べログスクレイピングツール")
    window.geometry("500x520")
    
    # タイトルラベル
    title_label = ttk.Label(window, text="食べログスクレイピングツール", font=("Helvetica", 16))
    title_label.pack(pady=10)
    
    # メインフレーム
    main_frame = ttk.Frame(window)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
    # 都道府県選択
    prefecture_frame = ttk.Frame(main_frame)
    prefecture_frame.pack(fill=tk.X, pady=5)
    
    prefecture_label = ttk.Label(prefecture_frame, text="都道府県:", width=15)
    prefecture_label.pack(side=tk.LEFT)
    
    prefecture_values = ["全国"] + list(prefectures.prefectures_values.keys())
    prefecture_combo = ttk.Combobox(prefecture_frame, values=prefecture_values)
    prefecture_combo.set(prefecture_values[0])
    prefecture_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    # 開始ページ指定
    page_frame = ttk.Frame(main_frame)
    page_frame.pack(fill=tk.X, pady=5)
    
    start_page_label = ttk.Label(page_frame, text="開始ページ:", width=15)
    start_page_label.pack(side=tk.LEFT)
    
    start_page_entry = ttk.Entry(page_frame)
    start_page_entry.insert(0, "1")
    start_page_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    # オプションフレーム
    options_frame = ttk.Frame(main_frame)
    options_frame.pack(fill=tk.X, pady=10)
    
    # 50ページ区切り
    fifty_page_var = tk.BooleanVar(value=True)
    fifty_page_check = ttk.Checkbutton(options_frame, text="50ページ区切り", variable=fifty_page_var)
    fifty_page_check.pack(side=tk.LEFT, padx=(0, 20))
    
    # ニューオープン
    new_open_var = tk.BooleanVar(value=False)
    new_open_check = ttk.Checkbutton(options_frame, text="ニューオープン", variable=new_open_var)
    new_open_check.pack(side=tk.LEFT)
    
    # 進捗バー
    progress_frame = ttk.Frame(main_frame)
    progress_frame.pack(fill=tk.X, pady=10)
    
    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(progress_frame, orient=tk.HORIZONTAL, length=100, mode='determinate', variable=progress_var)
    progress_bar.pack(fill=tk.X)
    
    progress_label = ttk.Label(progress_frame, text="進捗: 0/0 ページ")
    progress_label.pack(pady=5)
    
    # ステータスラベル
    status_label = ttk.Label(main_frame, text="準備完了")
    status_label.pack(pady=5)
    
    # スクレイピング実行ボタン
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(pady=10)
    
    area_scrape_button = ttk.Button(button_frame, text="スクレイピング開始", command=scrape_data_thread)
    area_scrape_button.pack(ipadx=10, ipady=5)
    
    # 説明テキスト
    help_text = """
    使用方法：
    1. 対象の都道府県を選択（「全国」でも可）
    2. 開始ページを指定（省略時は1）
    3. オプションを設定
      - 50ページ区切り：ONにすると最大50ページまでスクレイピングします
      - ニューオープン：新規オープン店舗のみをスクレイピングします
    4. 「スクレイピング開始」ボタンをクリックしてください
    
    結果はDownloadsフォルダに保存されます。
    """
    
    help_label = ttk.Label(main_frame, text=help_text, justify=tk.LEFT, wraplength=460)
    help_label.pack(pady=10)
    
    window.mainloop()

if __name__ == "__main__":
    requests_cache.install_cache('tabelog_cache', expire_after=3600)
    create_gui()