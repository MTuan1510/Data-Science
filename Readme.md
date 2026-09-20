# EX2.1 — Bộ dữ liệu ô nhiễm không khí từ VnExpress

Thu thập 523 bài báo về ô nhiễm không khí và chất lượng không khí từ [VnExpress](https://vnexpress.net/) (INFO3020 — Web scraping).

- **Tác giả:** Dương Minh Tuấn (BIT250370)
- **Ngày thu thập:** 19/09/2026
- **Từ khóa tìm kiếm:** `ô nhiễm không khí`, `chất lượng không khí`, `bụi mịn`, `AQI`

## Cấu trúc thư mục

```
.
├─ data/raw/
│   ├─ articles.json      # 523 bài: url, title, author, date, content
│   ├─ metadata.json      # mô tả dataset
│   ├─ dictionary.md      # từ điển dữ liệu (data dictionary)
│   ├─ urls.txt           # 572 URL ứng viên từ kết quả tìm kiếm
│   └─ rejected.json      # 49 URL bị loại kèm lý do
├─ source/
│   ├─ collect_url.py     # bước 1: thu thập URL
│   └─ collect_articles.py# bước 2: tải và trích xuất từng bài
└─ README.md
```

## Cách chạy lại

Chạy **từ thư mục gốc của project** (các script dùng đường dẫn tương đối `data/raw/...`):

```bash
pip install requests beautifulsoup4
python source/collect_url.py
python source/collect_articles.py --test   # thử 5 bài để kiểm tra selector
python source/collect_articles.py
```

> Lưu ý: `collect_articles.py` ghi đè `data/raw/articles.json`. Kết quả có thể khác giữa các lần chạy vì kết quả tìm kiếm và giao diện trang báo thay đổi theo thời gian.

## Tài liệu dữ liệu

- Mô tả từng trường: [`data/raw/dictionary.md`](data/raw/dictionary.md)
- Thông tin dataset: [`data/raw/metadata.json`](data/raw/metadata.json)