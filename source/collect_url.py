import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0"}
SEARCH_URL = "https://timkiem.vnexpress.net/"
KEYWORDS = ["ô nhiễm không khí", "chất lượng không khí", "bụi mịn", "AQI"]
MAX_PAGES = 40          
URL_FILE = "data/raw/urls.txt"


def load_old_urls():
    try:
        with open(URL_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []


def get_page(keyword, page):
    params = {
        "q": keyword, "media_type": "all", "fromdate": "0", "todate": "0",
        "latest": "", "cate_code": "", "search_f": "title,tag_list",
        "date_format": "all", "page": page,
    }
    for _ in range(3):
        try:
            r = requests.get(SEARCH_URL, params=params, headers=HEADERS, timeout=15)
            r.raise_for_status()
            return r.text
        except Exception as e:
            print(f"  Lỗi trang {page}: {e}")
            time.sleep(1.5)
    return None


urls = list(dict.fromkeys(load_old_urls()))  
seen = set(urls)
print("URL cũ:", len(urls))

for kw in KEYWORDS:
    print(f"\n== Từ khóa: {kw}")
    for page in range(1, MAX_PAGES + 1):
        html = get_page(kw, page)
        if html is None:
            break
        items = BeautifulSoup(html, "html.parser").select("#result_search article")
        if not items:
            print(f"  Trang {page} rỗng -> dừng")
            break

        added = 0
        for item in items:
            a = item.select_one("a[href]")
            if not a:
                continue
            href = urljoin("https://vnexpress.net", a["href"])
            if "video.vnexpress.net" in href:   
                continue
            if href not in seen:
                seen.add(href)
                urls.append(href)
                added += 1
        print(f"  Trang {page}: +{added} URL mới (tổng {len(urls)})")
        time.sleep(0.5)

with open(URL_FILE, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(urls) + "\n")

print("\nĐã lưu", len(urls), "URL vào", URL_FILE)