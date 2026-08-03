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
- 城堡座標、地址、縣市目前整合 ToCoo 與 100finecastles 官方 100/續 100 名城資料。
- 支援原日本 100 名城與續日本 100 名城，標題顯示為 `日本城堡地圖 (100+續)`。
- 原 100 城 marker 使用紅色 `濟` 字，續 100 城 marker 使用藍色 `濟` 字。
- 城堡名稱顯示包含官方編號，續 100 城會加上 `(續)` 標示。
- 可用維基百科「日本100名城」頁面與 100finecastles 續 100 城詳細頁更新城堡圖片。
- 地圖 marker 使用白底 `濟` 字，依城堡系列使用紅色或藍色。
- 已去過的城堡 marker 正常顯示，未去過的 `濟` 字淡化，可用左側按鈕隱藏。
- 依各城堡手帳數量顯示熱門外圈，使用 10 個顏色區間。
- 左側工具按鈕與熱門程度圖例可收合展開。
- 右側武士階級圖例可收合展開。
- Google OAuth 登入。
- 登入帳號名稱左側顯示目前武士等級圓形徽章。
- 登入後可為同一城堡建立多筆手帳，不同旅遊日期可多筆，同一天只會有一筆。
- 手帳日期可手動輸入 `YYYY-MM-DD`，也可用日曆 icon 快速選擇日期。
- 手帳編輯區支援最多 5 張圖片，上傳時會壓縮到 1MB 以下儲存。
- 點城堡時：
  - 未登入：顯示該城最新 10 筆手帳紀錄。
  - 已登入：可選擇顯示最新紀錄或輸入手帳。
  - 觀看其他帳號紀錄時：只顯示該帳號手帳，不顯示輸入手帳。
- 點城堡 popup 圖片會開啟對應城堡的中文維基百科文章。
- 點城堡 popup 內的城堡名稱會開啟 100finecastles 對應城堡介紹頁。
- 左側按鈕：
  - `城堡名稱`：切換城堡名稱標籤。
  - `隱藏未去過`：只隱藏未去過城堡的 `濟` 字，不隱藏熱門外圈。
  - `最新更新`：顯示最新 20 筆手帳更新，可點選定位城堡並在城堡右側 popup 顯示手帳。
  - `熱門城堡`：依手帳數排序顯示前 20 座，含縣市資訊，前三名顯示皇冠。
  - `我的紀錄`：顯示目前登入使用者的手帳清單，可點選編輯。
  - `最強大名`：依各帳號不重複去過城堡數排序顯示前 30 位帳號。
  - `顯示城堡`：循環切換顯示全部、100 城、續 100 城。
- 最強大名可點選帳號進入觀看模式：
  - 地圖上的 `濟` 改為該帳號去過的城堡。
  - 畫面浮現目前觀看帳號名稱。
  - 關閉觀看提示後回到目前登入帳號的地圖狀態。
- 武士階級由低到高：
  - 浪人、鄉士、足輕、侍、足輕頭、侍大將、家老、宿老、小大名、大大名、霸主、天下人。
- 畫面下方提供 `參考網站` 與 `隱私條款` 連結，點選後以置中 modal 顯示外部資料來源、免費非營利聲明與 Google 登入相關隱私說明。

## 資料庫

使用 SQLite：

```text
jp_travel.sqlite3
```

主要資料表：

- `castles`：城堡名稱、縣市、地址、座標、圖片 URL、來源資料。
- `users`：Google 登入使用者。
- `castle_journals`：使用者手帳紀錄與圖片 URL 清單。

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
python3 scripts/migrate_add_journal_images.py
python3 scripts/migrate_add_castle_official_series.py
```

匯入 100finecastles 原 100 城與續 100 城官方資料：

```bash
python3 scripts/import_100finecastles.py
```

更新續 100 城圖片：

```bash
python3 scripts/update_continued_castle_images.py --apply
```

產生虛擬手帳資料：

```bash
python3 scripts/seed_demo_journals.py --count 1100
```

為目前 50 筆手帳產生 demo 圖片資料：

```bash
python3 scripts/seed_demo_journal_images.py
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
- 100finecastles 官方城堡介紹 URL `official_url`
- 手帳數量 `journal_count`
- 官方編號 `castle_number`
- 城堡系列 `castle_series`

## 資料來源

- 城堡名稱、地址、座標、圖片：ToCoo  
  https://www2.tocoo.jp/must-visit/fine-castles.php?cc=cn
- 日本 100 名城官方清單與城堡介紹頁：日本100名城ガイド  
  https://www.100finecastles.com/castles-list/
- 續日本 100 名城官方清單、城堡介紹頁與部分圖片：日本100名城ガイド  
  https://www.100finecastles.com/castles-list2/
- 部分城堡圖片與延伸閱讀：Wikipedia  
  https://www.wikipedia.org/
- 地圖底圖：OpenStreetMap  
  https://www.openstreetmap.org/
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

## 20260803 完成摘要

- 手帳編輯與圖片：
  - 將輸入手帳編輯區改為較接近 Facebook 發文的編輯方式。
  - 支援每筆手帳最多上傳 5 張圖片。
  - 上傳圖片會壓縮至 1MB 以下後儲存。
  - 手帳圖片可在紀錄中顯示，點選後以圖片瀏覽器上一張/下一張切換。
  - 新增 `castle_journals.image_urls_json` 與圖片處理服務。
- Demo 資料：
  - 新增 `scripts/seed_demo_journal_images.py`，可替目前手帳資料隨機產生示意圖片。
  - 已為 50 筆手帳產生圖片資料作為上傳檔案示例。
- 日本 100 名城與續 100 名城：
  - 匯入 `https://www.100finecastles.com/castles-list/` 原日本 100 名城。
  - 匯入 `https://www.100finecastles.com/castles-list2/` 續日本 100 名城。
  - 新增 `castles.castle_number`、`castles.castle_series`。
  - 原 100 城與續 100 城皆加上官方編號；續 100 城顯示 `(續)`。
  - 地圖 marker 以紅色區分原 100 城、藍色區分續 100 城。
  - 左側按鈕整合為 `顯示城堡`，可循環切換全部、100 城、續 100 城。
  - 地圖初始不顯示城堡名稱，避免畫面過度擁擠。
  - 續 100 城圖片可由 100finecastles 詳細頁更新。
- 城堡 popup 與外部連結：
  - popup 內城堡圖片維持連到中文維基百科。
  - popup 內城堡名稱改為連到 100finecastles 對應城堡介紹頁。
  - `/api/v1/castles` 新增 `official_url`。
  - 修正直接點選遠方城堡時，popup 與左側箭頭對齊城堡 marker 的定位問題。
  - 最新更新、熱門城堡、我的紀錄點選後，會將城堡移到畫面中間偏上，並在城堡右側顯示 popup。
- 最新更新、熱門城堡、我的紀錄：
  - 最新更新列表改為只顯示清單，不再在列表內展開手帳內容。
  - 點選最新更新後，手帳紀錄顯示於城堡右側 popup。
  - 最新紀錄顯示改為每列一筆。
  - 手帳紀錄卡固定高度；文字過長時以 `.....` 展開完整內容。
  - 熱門城堡與我的紀錄面板寬度依內容收斂，避免過多留白。
  - 修正左側工具按鈕遮住熱門城堡與我的紀錄面板的問題。
- 地圖 UI 與圖例：
  - 左側工具按鈕群與熱門程度圖例可收合展開。
  - 右側武士階級圖例可收合展開。
  - 收合工具按鈕群時會關閉仍開啟的最新更新、熱門城堡、我的紀錄、最強大名與手帳視窗。
  - 武士階級排序改為 `天下人` 在最上方。
  - 登入帳號名稱左側新增圓形武士等級徽章。
  - 頁首標題改為 `日本城堡地圖 (100+續)`，不再顯示動態 `N 座城堡` 文字。
- 帳號觀看模式：
  - 點選我的紀錄或任一最強大名帳號時，會顯示該帳號有紀錄的 100 城與續 100 城。
  - 最強大名帳號觀看模式維持可關閉並回到自己的地圖狀態。
- 參考網站與隱私條款：
  - 畫面下方新增 `參考網站` 與 `隱私條款` 連結。
  - 點選後以畫面中央 modal 顯示內容，可用關閉鈕、背景遮罩或 Escape 關閉。
  - `參考網站` 條文列出 100finecastles、Wikipedia、OpenStreetMap、JapanPrefGeoJson、Google OAuth 等外部來源與使用內容。
  - 條文註明本站無盈利模式，免費開放使用。
  - `隱私條款` 條文說明 Google 登入、帳號基本資料、手帳、圖片、公開顯示與資料使用目的。
- 驗證：
  - `node --check static/map.js` 通過。
  - `ruff check .` 通過。
  - `pytest` 維持 11 個案例通過。
