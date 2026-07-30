# JP Travel

日本城堡旅遊紀錄網站。首頁以日本行政區地圖呈現城堡位置，使用者可透過 Google 登入標記去過的城堡、依旅遊日期撰寫手帳，並瀏覽熱門城堡與最新手帳紀錄。

## 技術選型

- Python 3.12 目標版本
- FastAPI
- SQLAlchemy
- SQLite
- RESTful JSON API
- pytest
- Leaflet
- OpenStreetMap / JapanPrefGeoJson 行政區資料

## 目前功能

- 首頁顯示日本區域地圖，預設以大阪城為中心。
- 地圖限制在日本周邊區域拖曳。
- 城堡座標、地址、縣市來自 ToCoo 城堡頁面。
- 可用維基百科「日本100名城」頁面可對應圖片置換城堡圖片。
- 地圖 marker 使用白底紅色 `濟` 字。
- 已去過的城堡 marker 正常顯示，未去過的 `濟` 字淡化，可用左側按鈕隱藏。
- 依各城堡手帳數量顯示熱門外圈，使用 10 個顏色區間。
- 左側固定顯示熱門程度圖例。
- 右側固定顯示武士階級區間圖例。
- Google OAuth 登入。
- 登入後可為同一城堡建立多筆手帳，不同旅遊日期可多筆，同一天只會有一筆。
- 手帳日期可手動輸入 `YYYY-MM-DD`，也可用日曆 icon 快速選擇日期。
- 點城堡時：
  - 未登入：顯示該城最新 10 筆手帳紀錄。
  - 已登入：可選擇顯示最新紀錄或輸入手帳。
  - 觀看其他帳號紀錄時：只顯示該帳號手帳，不顯示輸入手帳。
- 點城堡 popup 圖片會開啟對應城堡的中文維基百科文章。
- 左側按鈕：
  - `城堡名稱`：切換城堡名稱標籤。
  - `隱藏未去過`：只隱藏未去過城堡的 `濟` 字，不隱藏熱門外圈。
  - `最新更新`：顯示最新 20 筆手帳更新，可點選展開手帳內容並定位城堡。
  - `熱門城堡`：依手帳數排序顯示前 20 座，含縣市資訊，前三名顯示皇冠。
  - `我的紀錄`：顯示目前登入使用者的手帳清單，可點選編輯。
  - `最強大名`：依各帳號不重複去過城堡數排序顯示前 30 位帳號。
- 最強大名可點選帳號進入觀看模式：
  - 地圖上的 `濟` 改為該帳號去過的城堡。
  - 畫面浮現目前觀看帳號名稱。
  - 關閉觀看提示後回到目前登入帳號的地圖狀態。
- 武士階級由低到高：
  - 浪人、鄉士、足輕、侍、足輕頭、侍大將、家老、宿老、小大名、大大名、霸主、天下人。

## 資料庫

使用 SQLite：

```text
jp_travel.sqlite3
```

主要資料表：

- `castles`：城堡名稱、縣市、地址、座標、圖片 URL、來源資料。
- `users`：Google 登入使用者。
- `castle_journals`：使用者手帳紀錄。

`castle_journals` 的唯一限制：

```text
user_id + castle_id + travel_date
```

也就是同一使用者同一城堡，同一天只能一筆；不同旅遊日期可以多筆。

## 安裝

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

## 執行

```bash
uvicorn app.main:app --reload
```

如果 `--reload` 在本機環境被擋，可以改用：

```bash
uvicorn app.main:app --port 8000
```

首頁：

```text
http://127.0.0.1:8000
```

健康檢查：

```bash
curl http://127.0.0.1:8000/api/v1/health
```

## 測試

```bash
pytest
```

前端 JS 語法檢查：

```bash
node --check static/map.js
```

Python lint：

```bash
ruff check .
```

## Google 登入設定

建立 `.env` 並填入 Google OAuth 設定：

```bash
cp .env.example .env
```

```env
SECRET_KEY="請換成隨機長字串"
GOOGLE_CLIENT_ID="你的 Google OAuth Client ID"
GOOGLE_CLIENT_SECRET="你的 Google OAuth Client Secret"
GOOGLE_REDIRECT_URI="http://127.0.0.1:8000/api/v1/auth/google/callback"
```

Google Cloud Console 的 OAuth redirect URI 也要填同一個：

```text
http://127.0.0.1:8000/api/v1/auth/google/callback
```

如果出現 `redirect_uri_mismatch`，請確認 Google Cloud Console 裡的 Authorized redirect URI 與 `.env` 完全一致，包含：

- `http` / `https`
- `127.0.0.1` / `localhost`
- port `8000`
- 路徑 `/api/v1/auth/google/callback`

## 資料匯入與維護腳本

建立資料表：

```bash
python3 scripts/create_db.py
```

從 ToCoo 匯入城堡資料：

```bash
python3 scripts/import_tocoo_castles.py
```

若已有下載好的 HTML：

```bash
python3 scripts/import_tocoo_castles.py --html /tmp/tocoo_castles.html
```

從維基百科「日本100名城」頁面更新可對應城堡圖片：

```bash
python3 scripts/update_wikipedia_castle_images.py
```

預設只會 dry-run 顯示可更新數量與無法對應清單。確認後套用：

```bash
python3 scripts/update_wikipedia_castle_images.py --apply
```

若已有下載好的 HTML：

```bash
python3 scripts/update_wikipedia_castle_images.py --html /tmp/jp100.html --apply
```

資料庫 migration：

```bash
python3 scripts/migrate_add_travel_date.py
python3 scripts/migrate_add_castle_metadata.py
python3 scripts/migrate_castle_journal_unique_date.py
```

產生虛擬手帳資料：

```bash
python3 scripts/seed_demo_journals.py --count 1100
```

目前已建立約 20 個 demo 使用者與 1100 筆 demo 手帳。

## API 摘要

```text
GET  /api/v1/health
GET  /api/v1/castles
GET  /api/v1/auth/me
GET  /api/v1/auth/google/login
GET  /api/v1/auth/google/callback
POST /api/v1/auth/logout
GET  /api/v1/me/journals
PUT  /api/v1/me/journals/{castle_id}
GET  /api/v1/journals/latest
GET  /api/v1/journals/castles/{castle_id}/latest
GET  /api/v1/journals/accounts/rankings
GET  /api/v1/journals/accounts/{user_id}/journals
```

`GET /api/v1/castles` 回傳包含：

- 城堡名稱
- 縣市
- 地址
- 緯度、經度
- 圖片 URL
- 維基百科 URL `wikipedia_url`
- 手帳數量 `journal_count`

## 資料來源

- 城堡名稱、地址、座標、圖片：ToCoo  
  https://www2.tocoo.jp/must-visit/fine-castles.php?cc=cn
- 日本行政區 GeoJSON：JapanPrefGeoJson  
  https://github.com/amay077/JapanPrefGeoJson

## 今日完成摘要

- 建立 FastAPI + SQLAlchemy + SQLite 專案骨架。
- 建立日本城堡地圖首頁。
- 匯入 100 座城堡資料與圖片。
- 建立 Google 登入與 session。
- 建立手帳資料模型與 API。
- 加入旅遊日期必填。
- 支援同帳號同城堡多日期手帳，同一天只更新同一筆。
- 加入熱門程度外圈、熱門圖例、熱門城堡排行。
- 加入最新更新清單與單一城堡最新手帳紀錄。
- 加入我的紀錄清單與編輯入口。
- 產生 600 筆 demo 手帳資料供地圖測試。

## 20260730 完成摘要

- 讀取 README 與補齊專案脈絡。
- 新增維基百科「日本100名城」圖片更新腳本：
  - `scripts/update_wikipedia_castle_images.py`
  - 支援 dry-run、`--apply`、本機 HTML。
  - 已將本機 SQLite 中 54 座可安全對應城堡圖片換成 Wikimedia 圖片。
- 城堡 popup 圖片可點擊，開啟對應中文維基百科文章。
- 補 500 筆 demo 手帳，demo 手帳總數由 600 筆增至 1100 筆。
- 最新更新清單可點選展開手帳內容，並定位到該城堡。
- 新增最強大名排行榜：
  - 依帳號不重複去過城堡數排名。
  - 顯示前 30 位帳號、去過城堡數、武士階級與小圖示。
  - 支援點選帳號切換成該帳號地圖觀看模式。
- 新增武士階級圖例並常駐右側。
- 調整左側按鈕文案：
  - `未去過濟字` 改為 `隱藏未去過`。
  - `帳號排名` 改為 `最強大名`。
- 調整左上標題區塊位置，避開地圖縮放按鈕。
- 手帳日期輸入優化：
  - 支援手動輸入 `YYYY-MM-DD`。
  - 快速日期選擇改為日曆 icon。
  - 移除 `今天`、`去年今日` 快捷按鈕。
- 新增帳號公開手帳 API：
  - `GET /api/v1/journals/accounts/rankings`
  - `GET /api/v1/journals/accounts/{user_id}/journals`
- 測試更新至 11 個案例並通過。
