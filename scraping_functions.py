import requests
from bs4 import BeautifulSoup
import time
import requests.exceptions
def scrape_shop_details(shop_url):
    retry_count = 0
    max_retries = 3
    wait_time = 5
    while retry_count < max_retries:
        try:
            shop_response = requests.get(shop_url, timeout=10)
            shop_response.raise_for_status()
            shop_soup = BeautifulSoup(shop_response.text, 'html.parser')
            # 店舗の詳細情報を抽出する処理
            name_element = shop_soup.find('h2', class_='display-name')
            name = name_element.text.strip() if name_element else '店舗名がありません'
            address_element = shop_soup.find('p', class_='rstinfo-table__address')
            address = address_element.text.strip() if address_element else '住所がありません'
            opening_hours_element = shop_soup.find('p', class_='rstinfo-table__subject-text')
            opening_hours = opening_hours_element.text.strip() if opening_hours_element else '営業時間がありません'
            phone_element = shop_soup.find('p', class_='rstdtl-side-yoyaku__tel-number')
            phone_number = phone_element.text.strip() if phone_element else '電話番号がありません'
            opened_date_element = shop_soup.find('p', class_='rstinfo-opened-date')
            opened_dates = opened_date_element.text.strip() if opened_date_element else 'オープン日がありません'
            instagram_element = shop_soup.find('a', class_='rstinfo-sns-instagram')
            instagram = instagram_element['href'] if instagram_element and 'href' in instagram_element.attrs else 'Instagramがありません'
            service_element = shop_soup.find('th', string='サービス')
            service = service_element.find_next('td').get_text(strip=True) if service_element and service_element.find_next('td') else 'サービスがありません'
            genre_element = shop_soup.find('th', string='ジャンル')
            genre = genre_element.find_next('td').get_text(strip=True) if genre_element and genre_element.find_next('td') else 'ジャンルがありません'
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
            return {}
    return {}
def scrape_shops_by_prefecture(url, page_count=1, max_pages=50):
    """都道府県別の店舗リストページをスクレイピングする"""
    print(f"スクレイピング中: {url}, ページ数: {page_count}")
    all_shop_data = []
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        shop_list = soup.find_all('div', class_='list-rst')
        for shop in shop_list:
            detail_url_element = shop.find('a', class_='list-rst__rst-name-target')
            if detail_url_element and 'href' in detail_url_element.attrs:
                shop_url = detail_url_element['href']
                shop_data = scrape_shop_details(shop_url)
                all_shop_data.append(shop_data)
            else:
                print("店舗詳細URLが見つかりませんでした。")
                all_shop_data.append({})
        next_link = soup.find('a', class_='c-pagination__arrow c-pagination__arrow--next')
        if next_link and 'href' in next_link.attrs and page_count < max_pages:
            next_url = next_link['href']
            if not next_url.startswith("https://tabelog.com"):
                next_url = "https://tabelog.com" + next_url
            time.sleep(1)
            all_shop_data.extend(scrape_shops_by_prefecture(next_url, page_count + 1, max_pages))
        else:
            print("次のページはありません。")
    except requests.exceptions.RequestException as e:
        print(f'{url}でエラーが発生しました: {e}')
    return all_shop_data