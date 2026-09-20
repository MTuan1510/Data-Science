import json
import re
import sys
import time

import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0"}
URL_FILE = "data/raw/urls.txt"
OUT_FILE = "data/raw/articles.json"
REJECT_FILE = "data/raw/rejected.json"
MIN_CONTENT = 300       
TEST_N = 5


def fetch(url, retries=3):
    for _ in range(retries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            r.raise_for_status()
            return r.text
        except Exception as e:
            print(f"  Lỗi {e}")
            time.sleep(1.5)
    return None


def first_text(soup, selectors):
    """Thử lần lượt các selector, trả về giá trị đầu tiên không rỗng."""
    for sel in selectors:
        el = soup.select_one(sel)
        if not el:
            continue
        val = el.get("content") if el.name == "meta" else el.get_text(" ", strip=True)
        if val and val.strip():
            return val.strip()
    return None


def looks_like_author(p):
    text = p.get_text(" ", strip=True)
    styled = p.find("strong") or "right" in (p.get("style") or "").replace(" ", "")
    return bool(text) and len(text) <= 60 and not text.endswith(".") and bool(styled)


def parse(html):
    soup = BeautifulSoup(html, "html.parser")

    title = first_text(soup, ["h1.title-detail", "h1.title_gallery",
                              'meta[property="og:title"]', "h1"])
    if title:
        title = re.sub(r"\s*[-|]\s*VnExpress.*$", "", title).strip() or None

    date = first_text(soup, ["span.date", 'meta[property="article:published_time"]',
                             'meta[name="pubdate"]', 'meta[itemprop="datePublished"]'])

    author = first_text(soup, ["p.author_mail"])
    content = None

    body = soup.select_one("article.fck_detail") or soup.select_one("article")
    if body:
        paras = body.select("p.Normal")
        if paras:
            if not author and looks_like_author(paras[-1]):
                author = paras[-1].get_text(" ", strip=True)
                paras = paras[:-1]
            texts = [p.get_text(" ", strip=True) for p in paras]
            lede = soup.select_one("p.description")
            if lede:
                texts.insert(0, lede.get_text(" ", strip=True))
            content = " ".join(t for t in texts if t)
        else:
            content = body.get_text(" ", strip=True)

    if not author:
        author = first_text(soup, ['a[href*="/tac-gia/"]'])

    return {"title": title, "author": author or None,
            "date": date, "content": content or None}


def problems(a):
    p = []
    if not a["title"]:
        p.append("no_title")
    if not a["date"]:
        p.append("no_date")
    if not a["content"] or len(a["content"]) < MIN_CONTENT:
        p.append("short_or_no_content")
    return p


def main():
    with open(URL_FILE, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]

    test = "--test" in sys.argv
    if test:
        urls = urls[:TEST_N]

    valid, rejected = [], []
    for i, url in enumerate(urls, start=1):
        print(f"[{i}/{len(urls)}] {url[:90]}")
        html = fetch(url)
        if html is None:
            rejected.append({"url": url, "reasons": ["fetch_failed"]})
            continue

        art = {"url": url, **parse(html)}
        issues = problems(art)

        if test:
            print("  title  :", art["title"])
            print("  author :", art["author"])
            print("  date   :", art["date"])
            print("  content:", len(art["content"] or 0), "ký tự |", (art["content"] or "")[:120])
            print("  issues :", issues or "OK")
        elif issues:
            rejected.append({"url": url, "reasons": issues})
        else:
            valid.append(art)
        time.sleep(0.5)

    if test:
        return

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(valid, f, ensure_ascii=False, indent=2)
    with open(REJECT_FILE, "w", encoding="utf-8") as f:
        json.dump(rejected, f, ensure_ascii=False, indent=2)

    n = len(valid)
    no_author = sum(1 for a in valid if not a["author"])
    print("\n=== KẾT QUẢ ===")
    print(f"Bài hợp lệ (đủ title/date/content): {n}")
    print(f"Bài bị loại: {len(rejected)} (xem {REJECT_FILE})")
    print(f"Author null: {no_author}/{n} ({100 * no_author / max(n, 1):.0f}%)")
    if n < 500:
        print(f"!! Mới {n}/500 bài -> chạy lại collect_url.py với thêm từ khóa rồi thu tiếp")
    if n and no_author / n > 0.3:
        print("!! Author null > 30% -> selector tác giả có thể sai, kiểm tra bằng --test")


if __name__ == "__main__":
    main()