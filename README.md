# JP Travel

日本城堡旅遊紀錄網站。首頁以日本行政區地圖呈現城堡位置，使用者可透過 Google 登入標記去過的城堡、依旅遊日期撰寫筆記，並瀏覽熱門城堡與最新筆記紀錄。

## 技術選型

- Python 3.12 目標版本
- FastAPI
- SQLAlchemy
- SQLite
- RESTful JSON API
- pytest
- Leaflet（選點地圖另以 MapLibre GL 顯示向量底圖，開啟時才載入）
- OpenStreetMap / 国土地理院 / JapanPrefGeoJson 行政區資料

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
- 依各城堡筆記數量顯示熱門外圈，使用 10 個顏色區間。
- 左側工具按鈕與熱門程度圖例可收合展開。
- 右側武士階級圖例可收合展開。
- Google OAuth 登入。
- 登入帳號名稱左側顯示目前武士等級圓形徽章。
- 登入後可為同一城堡建立多筆筆記，不同旅遊日期可多筆，同一天只會有一筆。
- 整站採用《信長之野望・天翔記》風格主題：深藍視窗、金色雙框、明朝體、立體指令鈕、和紙筆記卡（`static/theme-tenshouki.css`）。
- 筆記日期可手動輸入 `YYYY-MM-DD`，也可用日曆 icon 開啟自製日曆（顯示在旅遊日期下方，可切換年、月）。
- 輸入筆記文字或加入照片時，自動勾選 `已去過`。
- 筆記編輯區支援最多 5 張圖片，上傳時會壓縮到 1MB 以下儲存。
- 筆記編輯區可新增順遊推薦，每筆推薦可填名稱、類型、推薦原因、5 星評分與最多 3 張圖片。
- 新增順遊推薦地點選取：
  - 選點地圖可切換：地理院 簡潔地圖（無建物，預設）、OpenFreeMap 淡色（無建物）、地理院 標準地図、地理院 航空照片、OpenStreetMap。
  - 不預先載入 POI，避免大量流量。
  - 使用者點選地圖位置後，才以預設 300m 半徑查詢附近 POI 清單，可切換 100m、300m、800m。
  - 可從附近 POI 選擇店家/景點；若沒有合適地點，可直接使用點選座標。
- 點城堡時：
  - 未登入：顯示該城最新 10 筆筆記紀錄。
  - 已登入：預設顯示自己上一筆筆記，可切換顯示最新紀錄或觀看所有紀錄。
  - 筆記表單可點 `新日期` 清空內容，再輸入同城堡的新旅遊日期紀錄。
  - 顯示最新紀錄預設只顯示最新一筆，並可縮合/展開。
  - 觀看其他帳號紀錄時：只顯示該帳號筆記，不顯示輸入筆記。
- 城堡單頁紀錄：
  - 由 `觀看所有紀錄` 以新分頁開啟。
  - 上方顯示城堡圖片。
  - 左側為旅遊紀錄清單，含帳號武士等級圖示與有圖片提示。
  - 右側顯示選取紀錄的筆記內容、完整圖片與順遊推薦。
  - 可切換為順遊推薦模式，只顯示此城堡周邊推薦景點清單。
  - 順遊推薦地點連結會以經緯度開啟 Google Maps。
  - 美食與咖啡類順遊推薦會提供 Tabelog 搜尋連結。
- 點城堡 popup 圖片會開啟對應城堡的中文維基百科文章。
- 點城堡 popup 內的城堡名稱會開啟 100finecastles 對應城堡介紹頁。
- 左側按鈕：
  - `城堡名稱`：切換城堡名稱標籤。
  - `隱藏未去過`：只隱藏未去過城堡的 `濟` 字，不隱藏熱門外圈。
  - `最新更新`：顯示最新 20 筆筆記更新，可點選定位城堡並在城堡右側 popup 顯示筆記。
  - `熱門城堡`：依筆記數排序顯示前 20 座，含縣市資訊，前三名顯示皇冠。
  - `我的紀錄`：顯示目前登入使用者的筆記清單，可點選編輯。
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
- `castle_journals`：使用者筆記紀錄與圖片 URL 清單。
- `journal_recommendations`：筆記順遊推薦、評分、座標、OSM 來源與圖片 URL 清單。

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

產生虛擬筆記資料：

```bash
python3 scripts/seed_demo_journals.py --count 1100
```

為目前 50 筆筆記產生 demo 圖片資料：

```bash
python3 scripts/seed_demo_journal_images.py
```

目前已建立約 20 個 demo 使用者與 1100 筆 demo 筆記。

清除目前所有筆記紀錄並重建大量 demo 資料：

```bash
python3 scripts/seed_large_demo_journals_with_recommendations.py --count 2000 --image-pool-size 48
```

此腳本會：

- 清除 `castle_journals` 與 `journal_recommendations`。
- 建立或更新 40 個 demo 使用者。
- 產生 2000 筆筆記，每筆 2 張示意圖片。
- 為每筆筆記產生 2 筆順遊推薦，每筆 1 張示意圖片。
- 優先從 Pexels 日本街景搜尋結果下載示意圖片；若搜尋頁被擋，改用 Pexels 圖片直連備援。

建立擬真 demo 資料（目前使用中）：

```bash
python3 scripts/seed_realistic_demo_data.py            # 抓取資料 + 產生紀錄
python3 scripts/seed_realistic_demo_data.py --fetch-only  # 只抓取（可中斷續傳）
python3 scripts/seed_realistic_demo_data.py --seed-only   # 只用快取重建紀錄
```

此腳本會：

- 從 Wikimedia Commons 依城堡座標下載實拍照片（每城最多 5 張），從 OpenStreetMap / Overpass 抓城堡周邊真實景點、餐廳、咖啡廳與伴手禮店，景點再配 Commons 附近實拍照片。
- 照片壓縮後存於 `static/uploads/journals/demo_real/`，快取為 `places_cache.json`，作者與授權記錄於 `CREDITS.json`（Commons 照片多為 CC BY / CC BY-SA，公開時需標示）。
- 只刪除 `demo-user-*` 帳號的筆記與推薦，真實帳號資料保留。
- 建立 50 個 demo 使用者，產生 3000 筆筆記：使用者活躍度呈長尾分布（前段帳號接近制霸）、以「連續數天走訪鄰近城堡」的旅程規劃、旅遊日期集中於賞櫻與紅葉季。
- 筆記文字依季節、天守類型（現存 / 重建 / 城跡）、百名城或續百名城印章組合產生；約 35% 筆記附 1–3 筆真實周邊地點的順遊推薦。

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
GET  /api/v1/journals/castles/{castle_id}
GET  /api/v1/journals/accounts/rankings
GET  /api/v1/journals/accounts/{user_id}/journals
GET  /api/v1/castles/nearby-pois
```

`GET /api/v1/castles` 回傳包含：

- 城堡名稱
- 縣市
- 地址
- 緯度、經度
- 圖片 URL
- 維基百科 URL `wikipedia_url`
- 100finecastles 官方城堡介紹 URL `official_url`
- 筆記數量 `journal_count`
- 官方編號 `castle_number`
- 城堡系列 `castle_series`

## 資料來源

- 城堡名稱、地址、座標、圖片：ToCoo<br>
  https://www2.tocoo.jp/must-visit/fine-castles.php?cc=cn
- 日本 100 名城官方清單與城堡介紹頁：日本100名城ガイド<br>
  https://www.100finecastles.com/castles-list/
- 續日本 100 名城官方清單、城堡介紹頁與部分圖片：日本100名城ガイド<br>
  https://www.100finecastles.com/castles-list2/
- 部分城堡圖片與延伸閱讀：Wikipedia<br>
  https://www.wikipedia.org/
- 地圖底圖：OpenStreetMap<br>
  https://www.openstreetmap.org/
- 順遊推薦選點地圖：国土地理院 地理院タイル<br>
  https://maps.gsi.go.jp/development/ichiran.html
- 順遊推薦選點淡色地圖：OpenFreeMap<br>
  https://openfreemap.org/
- 附近 POI 查詢：Overpass API / OpenStreetMap 資料<br>
  https://overpass-api.de/
- 日本行政區 GeoJSON：JapanPrefGeoJson<br>
  https://github.com/amay077/JapanPrefGeoJson
- Demo 筆記與順遊推薦示意圖片：Pexels<br>
  https://www.pexels.com/zh-tw/search/日本街景/
- 擬真 demo 筆記與順遊推薦照片：Wikimedia Commons（各照片作者與授權見 `static/uploads/journals/demo_real/CREDITS.json`）<br>
  https://commons.wikimedia.org/
- 擬真 demo 順遊推薦地點：OpenStreetMap / Overpass API<br>
  https://overpass-api.de/

## 今日完成摘要

- 建立 FastAPI + SQLAlchemy + SQLite 專案骨架。
- 建立日本城堡地圖首頁。
- 匯入 100 座城堡資料與圖片。
- 建立 Google 登入與 session。
- 建立筆記資料模型與 API。
- 加入旅遊日期必填。
- 支援同帳號同城堡多日期筆記，同一天只更新同一筆。
- 加入熱門程度外圈、熱門圖例、熱門城堡排行。
- 加入最新更新清單與單一城堡最新筆記紀錄。
- 加入我的紀錄清單與編輯入口。
- 產生 600 筆 demo 筆記資料供地圖測試。

## 20260730 完成摘要

- 讀取 README 與補齊專案脈絡。
- 新增維基百科「日本100名城」圖片更新腳本：
  - `scripts/update_wikipedia_castle_images.py`
  - 支援 dry-run、`--apply`、本機 HTML。
  - 已將本機 SQLite 中 54 座可安全對應城堡圖片換成 Wikimedia 圖片。
- 城堡 popup 圖片可點擊，開啟對應中文維基百科文章。
- 補 500 筆 demo 筆記，demo 筆記總數由 600 筆增至 1100 筆。
- 最新更新清單可點選展開筆記內容，並定位到該城堡。
- 新增最強大名排行榜：
  - 依帳號不重複去過城堡數排名。
  - 顯示前 30 位帳號、去過城堡數、武士階級與小圖示。
  - 支援點選帳號切換成該帳號地圖觀看模式。
- 新增武士階級圖例並常駐右側。
- 調整左側按鈕文案：
  - `未去過濟字` 改為 `隱藏未去過`。
  - `帳號排名` 改為 `最強大名`。
- 調整左上標題區塊位置，避開地圖縮放按鈕。
- 筆記日期輸入優化：
  - 支援手動輸入 `YYYY-MM-DD`。
  - 快速日期選擇改為日曆 icon。
  - 移除 `今天`、`去年今日` 快捷按鈕。
- 新增帳號公開筆記 API：
  - `GET /api/v1/journals/accounts/rankings`
  - `GET /api/v1/journals/accounts/{user_id}/journals`
- 測試更新至 11 個案例並通過。

## 20260803 完成摘要

- 筆記編輯與圖片：
  - 將輸入筆記編輯區改為較接近 Facebook 發文的編輯方式。
  - 支援每筆筆記最多上傳 5 張圖片。
  - 上傳圖片會壓縮至 1MB 以下後儲存。
  - 筆記圖片可在紀錄中顯示，點選後以圖片瀏覽器上一張/下一張切換。
  - 新增 `castle_journals.image_urls_json` 與圖片處理服務。
- Demo 資料：
  - 新增 `scripts/seed_demo_journal_images.py`，可替目前筆記資料隨機產生示意圖片。
  - 已為 50 筆筆記產生圖片資料作為上傳檔案示例。
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
  - 最新更新列表改為只顯示清單，不再在列表內展開筆記內容。
  - 點選最新更新後，筆記紀錄顯示於城堡右側 popup。
  - 最新紀錄顯示改為每列一筆。
  - 筆記紀錄卡固定高度；文字過長時以 `.....` 展開完整內容。
  - 熱門城堡與我的紀錄面板寬度依內容收斂，避免過多留白。
  - 修正左側工具按鈕遮住熱門城堡與我的紀錄面板的問題。
- 地圖 UI 與圖例：
  - 左側工具按鈕群與熱門程度圖例可收合展開。
  - 右側武士階級圖例可收合展開。
  - 收合工具按鈕群時會關閉仍開啟的最新更新、熱門城堡、我的紀錄、最強大名與筆記視窗。
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
  - `隱私條款` 條文說明 Google 登入、帳號基本資料、筆記、圖片、公開顯示與資料使用目的。
- 驗證：
  - `node --check static/map.js` 通過。
  - `ruff check .` 通過。
  - `pytest` 維持 11 個案例通過。

## 20260804 完成摘要

- 城堡 popup 筆記操作：
  - `顯示最新紀錄` 改為預設縮合，只顯示最新一筆。
  - 點選最新紀錄可展開完整內容。
  - 修正展開最新紀錄後 `顯示最新紀錄`、`輸入筆記`、`觀看所有紀錄` 按鈕消失的問題。
  - `輸入筆記` 右側新增 `觀看所有紀錄`，以新分頁開啟該城堡完整紀錄頁。
- 城堡完整紀錄頁：
  - 上方顯示較低高度的城堡圖片，降低版面占用。
  - 左側顯示旅遊紀錄清單。
  - 帳號名稱前顯示該帳號武士等級圖示。
  - 有圖片的紀錄在左側清單顯示圖片提示。
  - 右側顯示選取紀錄的筆記文字、完整圖片與順遊推薦，不再只顯示縮圖。
  - 調整版面、卡片、色彩與狀態樣式，讓單頁紀錄閱讀更完整。
- 筆記 modal：
  - `儲存筆記` 按鈕移到旅遊日期右方，避免被畫面下方遮住。
  - 儲存成功後自動關閉 modal 視窗。
- 順遊推薦設計與實作：
  - 新增每筆筆記的順遊推薦資料模型與 API 儲存流程。
  - 每筆推薦可填名稱、分類、推薦原因、5 星點選評分、座標、OSM 連結與圖片。
  - 推薦圖片支援上傳，最多 3 張；demo 資料每筆推薦放 1 張。
  - 地點選取使用目前 Leaflet / OpenStreetMap 地圖，不使用 Google Maps。
  - 不預先載入 POI；使用者點選地圖後，才用 Overpass 查詢該座標附近 POI 清單，半徑可切換 100m、300m、800m。
  - 若附近沒有 POI 或沒有合適店家/景點，可直接使用點選座標。
  - 討論並確認目前使用 OpenStreetMap tile 不需要個別授權，但需遵守 OSM/服務供應者署名、使用政策與流量限制。
- 大量 demo 資料：
  - 新增 `scripts/seed_large_demo_journals_with_recommendations.py`。
  - 已清除原本筆記與順遊推薦紀錄。
  - 已重新建立 2000 筆筆記與 4000 筆順遊推薦。
  - 每筆筆記含 2 張圖片，每筆順遊推薦含 1 張圖片。
  - 資料涵蓋 40 個 demo 帳號與 226 座城堡。
  - Pexels 搜尋頁回傳 403 時，腳本改用 Pexels 圖片直連備援，實際下載 6 張示意圖片並隨機套用。
- 驗證：
  - `node --check static/map.js` 通過。
  - `node --check static/castle_journals.js` 通過。
  - `ruff check .` 通過。
  - `pytest` 維持 12 個案例通過。
  - 大量 demo 資料驗證：2000 筆筆記皆有 2 張圖片，4000 筆順遊推薦皆有 1 張圖片。
  - API 驗證最新紀錄與城堡完整紀錄頁資料可正常回傳。

## 20260817 完成摘要

- 啟動與開發環境：
  - 修正 `.venv` 缺少 `Pillow`、`python-multipart` 導致 `uvicorn app.main:app` 無法啟動的問題。
  - `pyproject.toml` 明確指定 setuptools 只 discovery `app*`，避免 editable install 因 `app`、`static` 多個 top-level 目錄失敗。
  - `app/schemas/common.py` 改用 Python 3.12 泛型語法，讓 `ruff check .` 通過。
  - 確認本機服務可在 `http://127.0.0.1:8000` 啟動，健康檢查正常。
- 文案與武士階級：
  - 將浪人徽章 icon 由 `流` 修正為 `浪`。
  - 全站畫面與 README/readme 文案將 `手帳` 改為 `筆記`。
- 順遊推薦地點選取：
  - 保留 Leaflet + Overpass / OpenStreetMap，但將點選位置 POI 搜尋由 20m 改為預設 300m。
  - 地點選取器新增 100m、300m、800m 半徑切換，切換半徑會以同一座標重新查詢。
  - 修正 POI 結果清單第一筆被地圖蓋住的版面問題。
  - 討論 Geoapify、Mapbox Search、Google Places、Foursquare、OpenTripMap、GeoNames 等免費或低成本 POI 選項。
- 順遊推薦外部連結：
  - 順遊推薦地點連結改為優先以經緯度開啟 Google Maps。
  - 美食與咖啡類推薦新增 Tabelog 繁中站搜尋連結，以店名與地址組合搜尋。
- 城堡完整紀錄頁：
  - `/castles/{castle_id}/journals` 新增 `順遊推薦` 切換按鈕。
  - 可只顯示該城堡所有筆記中的周邊順遊推薦清單。
  - 推薦卡顯示分類、Google Maps、Tabelog、推薦人、旅遊日期、星等、地址、推薦原因與圖片。
- 筆記輸入流程：
  - 修正先輸入順遊推薦後再點日曆日期，表單被既有日期資料覆蓋、未儲存內容清空的問題。
  - 登入後點選城堡預設顯示自己的上一筆筆記。
  - 筆記表單新增 `新日期` 按鈕，可清空目前內容後輸入同城堡的新旅遊日期紀錄。
- 地圖視覺與圖層：
  - 熱門程度 10 階顏色改為較高辨識度的色彩序列。
  - 討論 Mapbox 與 Google Maps 成本差異：Mapbox 通常較便宜，Google Places 資料較完整但成本較高。
  - 主地圖新增 `鐵道圖層` 開關，使用 OpenRailwayMap standard layer，預設關閉、需要時才載入。
  - 參考網站 modal 與 README 補充 OpenRailwayMap 來源。
- 今日後續調整：
  - 頁首登入區右方新增 `選單` 與 `階級` 按鈕，左側選單改為直排工具列。
  - `選單` 內新增 `地方區域` 按鈕，可切換主地圖日本地方區塊上色。
  - 主地圖預設中心改為二條城，預設 zoom 由 6 調整為 8。
  - 熱門程度改為每 20 次一級、共 10 層；熱門圈改為無邊框填滿圓，筆記數越多越大。
  - `隱藏未去過` 未登入時反灰不可按，並會連同未去過城堡熱門圈一起隱藏。
  - `最新更新`、`熱門城堡`、`我的紀錄` 清單從左側展開，並貼齊左側選單最上方按鈕位置。
  - 點選清單筆記或直接點選城堡 marker 時，城堡移到畫面中央、顯示城堡名稱，筆記改由右側面板滑出。
  - 右側筆記面板顯示城堡圖片、城堡名稱官方連結、地址、`輸入筆記` 與 `觀看所有紀錄`；未登入時不顯示 `輸入筆記`。
  - 美化右側筆記卡片，縮小留白、移除多餘裝飾圓點，改善文字與圖片排版。
  - 新增公開統計 API `GET /api/v1/journals/stats`，頁首階級按鈕右方顯示已登錄筆記人數與筆記數量。
  - `最強大名` 清單顯示於畫面中央；點選帳號後，依該帳號在各縣去過城堡數 / 該縣總城堡數的完成率，以紫色系為縣區域分級上色。
  - 最強大名縣別完成率色階圖例顯示於畫面右下方，可用 X 關閉。
- Demo 資料：
  - `scripts/seed_large_demo_journals_with_recommendations.py` 新增 `--append` 模式，可保留既有資料並追加 demo 筆記。
  - 已追加 5000 筆 demo 筆記與 10000 筆順遊推薦；目前本機資料約 7005 筆筆記、14005 筆順遊推薦。
- 驗證：
  - `node --check static/map.js` 通過。
  - `node --check static/castle_journals.js` 通過。
  - `ruff check .` 通過。
  - `pytest` 維持 12 個案例通過。
  - `ruff check scripts/seed_large_demo_journals_with_recommendations.py` 通過。

## 20261005 完成摘要

- 天翔記風格 UI：
  - 新增 `static/theme-tenshouki.css`，疊在 `styles.css` 之後，只覆蓋色彩、字型與邊框，不改版面；移除該 link 即可還原原風格。
  - 視窗、面板、彈窗改為深藍漸層與金色雙框，標題金字；按鈕為立體指令鈕，選取中為朱漆色。
  - 筆記卡、輸入框改為和紙底墨字；武士階級徽章改為家紋風圓章（木、藍、金、朱四段）。
  - 城堡 marker 改為和紙方印；地圖海面改深藍，八地方改為大名勢力風色塊、縣界深褐色。
  - 首頁與城堡紀錄頁載入 Google Fonts「Noto Serif TC」明朝體。
- 筆記輸入：
  - 輸入筆記文字或加入照片時自動勾選 `已去過`（開啟表單時不預先勾選，避免切換日期時無法載入既有筆記）。
  - 瀏覽器原生日期選擇器改為自製日曆元件，顯示於旅遊日期下方，可用年、月下拉與左右箭頭切換，Esc 或點外部關閉。
  - 修正右側筆記面板出現水平捲軸：表單寬度改為跟隨面板。
- 主畫面選單移除 `鐵道圖層` 按鈕與 OpenRailwayMap 圖層程式。
- 順遊推薦選點地圖：
  - 新增圖層切換，加入国土地理院 標準地図、航空照片。
  - 地理院 raster 圖磚無法移除建物，改用地理院最適化向量圖磚（optimal_bvmap）並濾掉建物圖層，作為預設「地理院 簡潔地圖（無建物）」；另加 OpenFreeMap positron 淡色（無建物）。
  - 向量底圖透過 MapLibre GL + maplibre-gl-leaflet，開啟選點地圖時才動態載入，不影響主畫面速度。
  - 評估 CARTO Voyager：目前需 API key，未採用。
  - 討論 Google Maps 選點：須用官方 Maps JavaScript API 與帳單帳戶；Places 資料依條款只能長期保存 `place_id`，與目前永久保存名稱、地址、座標的設計衝突，暫不採用；現行以經緯度開啟 Google Maps 連結則無授權問題。
  - 參考網站 modal 補上国土地理院與 OpenFreeMap 來源。
- 擬真 demo 資料：
  - 新增 `scripts/seed_realistic_demo_data.py`（抓取可續傳、Wikimedia 全域限速、Overpass 每台伺服器一次一個請求）。
  - 200 座 100 名城與續 100 名城：Commons 城堡實拍照片每城最多 5 張，OSM 周邊真實景點、餐廳、咖啡廳與伴手禮店，景點配 Commons 附近照片；照片約 250MB 存於 `static/uploads/journals/demo_real/`，授權記錄於 `CREDITS.json`。
  - 刪除 demo 帳號舊紀錄，重建 50 位 demo 使用者、3000 筆筆記（2288 筆附照片）與 1466 筆順遊推薦（396 筆附照片）；真實帳號 8 筆筆記保留。
  - 原資料庫備份為 `jp_travel.backup-20261005.sqlite3`。
- 驗證：
  - `node --check static/map.js` 通過。
  - `ruff check .` 通過。
  - `pytest` 維持 12 個案例通過。
  - 以 headless Chrome / Playwright 截圖確認主題、日曆、選點地圖與 demo 資料頁面。
