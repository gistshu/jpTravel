const MAX_VISIBLE_TITLE_LENGTH = 46;
const SAMURAI_TITLE_ICONS = ["浪", "鄉", "足", "侍", "頭", "將", "家", "宿", "小", "大", "霸", "天"];
const RECOMMENDATION_CATEGORY_LABELS = {
  attraction: "景點",
  food: "美食",
  shop: "商店",
  cafe: "咖啡",
  hotel: "住宿",
  transport: "交通",
  other: "其他",
};

const hero = document.querySelector("#castle-journal-hero");
const titleElement = document.querySelector("#castle-journal-title");
const subtitleElement = document.querySelector("#castle-journal-subtitle");
const listElement = document.querySelector("#castle-journal-list");
const emptyElement = document.querySelector("#castle-journal-empty");
const detailElement = document.querySelector("#castle-journal-detail");
const recommendationViewButton = document.querySelector("#toggle-recommendation-view");

let records = [];
let selectedIndex = 0;
let viewMode = "records";

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function getCastleIdFromPath() {
  const match = window.location.pathname.match(/\/castles\/(\d+)\/journals\/?$/);
  return match ? Number(match[1]) : null;
}

async function requestJson(url) {
  const response = await fetch(url, {
    headers: { Accept: "application/json" },
  });
  const payload = await response.json().catch(() => null);
  if (!response.ok || !payload?.success) {
    throw new Error(payload?.message || "資料載入失敗");
  }
  return payload;
}

function formatUpdatedAt(value) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return new Intl.DateTimeFormat("zh-Hant", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

function getJournalImageUrls(record) {
  return Array.isArray(record.image_urls) ? record.image_urls : [];
}

function getJournalRecommendations(record) {
  return Array.isArray(record.recommendations) ? record.recommendations : [];
}

function getRecommendationMapUrl(recommendation) {
  const latitude = Number(recommendation.latitude);
  const longitude = Number(recommendation.longitude);
  if (Number.isFinite(latitude) && Number.isFinite(longitude)) {
    return `https://www.google.com/maps/search/?api=1&query=${latitude},${longitude}`;
  }
  return recommendation.google_maps_url || recommendation.osm_url || "";
}

function getTabelogSearchUrl(recommendation) {
  if (!["food", "cafe"].includes(recommendation.category)) {
    return "";
  }
  const query = [recommendation.name, recommendation.address]
    .filter(Boolean)
    .join(" ");
  if (!query.trim()) {
    return "";
  }
  return `https://tabelog.com/tw/rstLst/?SrtT=trend&sw=${encodeURIComponent(query)}`;
}

function getRecordTitleLevel(record) {
  return Math.max(0, Math.min(
    SAMURAI_TITLE_ICONS.length - 1,
    Number(record.title_level) || 0,
  ));
}

function getAllRecommendations() {
  return records.flatMap((record) => (
    getJournalRecommendations(record).map((recommendation) => ({
      recommendation,
      record,
    }))
  ));
}

function renderRecommendationCard(recommendation, sourceRecord = null) {
  const categoryLabel = (
    RECOMMENDATION_CATEGORY_LABELS[recommendation.category] || "其他"
  );
  const mapUrl = getRecommendationMapUrl(recommendation);
  const tabelogUrl = getTabelogSearchUrl(recommendation);
  const mapLink = mapUrl
    ? `
      <a
        class="castle-journal-recommendation-map"
        href="${escapeHtml(mapUrl)}"
        target="_blank"
        rel="noopener noreferrer"
      >
        Google Maps
      </a>
    `
    : "";
  const tabelogLink = tabelogUrl
    ? `
      <a
        class="castle-journal-recommendation-map"
        href="${escapeHtml(tabelogUrl)}"
        target="_blank"
        rel="noopener noreferrer"
      >
        Tabelog
      </a>
    `
    : "";
  const rating = Number(recommendation.rating) || 0;
  const source = sourceRecord
    ? `
      <div class="castle-journal-recommendation-source">
        ${escapeHtml(sourceRecord.user_display_name)}
        ・${escapeHtml(sourceRecord.travel_date)}
      </div>
    `
    : "";
  return `
    <article class="castle-journal-recommendation-card">
      <div class="castle-journal-recommendation-meta">
        <span>${escapeHtml(categoryLabel)}</span>
        <span class="castle-journal-recommendation-links">
          ${mapLink}
          ${tabelogLink}
        </span>
      </div>
      <h3>${escapeHtml(recommendation.name || "未命名推薦")}</h3>
      ${source}
      ${rating ? `
        <div class="castle-journal-recommendation-rating">
          ${"★".repeat(rating)}${"☆".repeat(5 - rating)}
        </div>
      ` : ""}
      ${recommendation.address ? `
        <div class="castle-journal-recommendation-address">
          ${escapeHtml(recommendation.address)}
        </div>
      ` : ""}
      <p>${escapeHtml(recommendation.description || "尚未填寫推薦原因")}</p>
      ${renderRecommendationImages(getJournalImageUrls(recommendation))}
    </article>
  `;
}

function renderRecommendations(recommendations) {
  if (recommendations.length === 0) {
    return "";
  }

  const items = recommendations.map((recommendation) => (
    renderRecommendationCard(recommendation)
  )).join("");
  return `
    <section class="castle-journal-recommendations">
      <h2>本趟順遊推薦</h2>
      <div class="castle-journal-recommendation-grid">
        ${items}
      </div>
    </section>
  `;
}

function renderRecommendationImages(imageUrls) {
  if (imageUrls.length === 0) {
    return "";
  }
  const images = imageUrls.map((url, index) => `
    <img src="${escapeHtml(url)}" alt="推薦圖片 ${index + 1}">
  `).join("");
  return `<div class="castle-journal-recommendation-images">${images}</div>`;
}

function renderJournalImages(imageUrls) {
  if (imageUrls.length === 0) {
    return "";
  }

  const images = imageUrls.map((url, index) => `
    <figure class="castle-journal-image">
      <img src="${escapeHtml(url)}" alt="筆記圖片 ${index + 1}">
    </figure>
  `);
  return `<div class="castle-journal-images">${images.join("")}</div>`;
}

function renderHero(collection) {
  document.title = `${collection.castle_name} 所有紀錄`;
  titleElement.textContent = collection.castle_name;
  subtitleElement.innerHTML = [
    collection.prefecture
      ? `<span>${escapeHtml(collection.prefecture)}</span>`
      : "",
    `<span>${collection.records.length} 筆紀錄</span>`,
    collection.address
      ? `<span>${escapeHtml(collection.address)}</span>`
      : "",
  ].filter(Boolean).join("");

  if (collection.image_url) {
    hero.style.setProperty(
      "--castle-journal-hero-image",
      `url("${collection.image_url.replaceAll('"', "%22")}")`,
    );
    hero.classList.add("has-image");
  }
}

function renderList() {
  const isRecommendationMode = viewMode === "recommendations";
  listElement.hidden = isRecommendationMode;
  recommendationViewButton.classList.toggle("is-active", isRecommendationMode);
  recommendationViewButton.setAttribute("aria-pressed", String(isRecommendationMode));
  recommendationViewButton.textContent = isRecommendationMode ? "旅遊紀錄" : "順遊推薦";

  if (isRecommendationMode) {
    const recommendationCount = getAllRecommendations().length;
    emptyElement.hidden = false;
    emptyElement.textContent = recommendationCount > 0
      ? `共 ${recommendationCount} 筆順遊推薦`
      : "尚無順遊推薦";
    return;
  }

  listElement.innerHTML = "";
  emptyElement.hidden = records.length > 0;
  emptyElement.textContent = "尚無筆記紀錄";

  records.forEach((record, index) => {
    const summary = record.journal_text.trim() || "尚未填寫筆記內容";
    const titleLevel = getRecordTitleLevel(record);
    const imageCount = getJournalImageUrls(record).length;
    const recommendationCount = getJournalRecommendations(record).length;
    const isSelected = index === selectedIndex;
    const item = document.createElement("li");
    item.className = "castle-journal-list-item";
    item.innerHTML = `
      <button
        class="castle-journal-list-button ${isSelected ? "is-selected" : ""}"
        type="button"
        data-record-index="${index}"
      >
        <span class="castle-journal-list-date">
          ${escapeHtml(record.travel_date)}
        </span>
        <span class="castle-journal-list-user">
          <span
            class="samurai-badge title-level-${titleLevel}"
            title="${escapeHtml(record.title || "浪人")}"
            aria-label="${escapeHtml(record.title || "浪人")}"
          >
            ${escapeHtml(SAMURAI_TITLE_ICONS[titleLevel])}
          </span>
          <strong>${escapeHtml(record.user_display_name)}</strong>
          ${imageCount > 0 ? `<span class="journal-has-images" title="有圖片" aria-label="有圖片">${imageCount}</span>` : ""}
        </span>
        ${recommendationCount > 0 ? `
          <span class="castle-journal-list-recommendation">
            推薦 ${recommendationCount}
          </span>
        ` : ""}
        <small>${escapeHtml(summary.slice(0, MAX_VISIBLE_TITLE_LENGTH))}</small>
      </button>
    `;
    listElement.append(item);
  });
}

function renderDetail() {
  if (viewMode === "recommendations") {
    renderRecommendationOverview();
    return;
  }

  const record = records[selectedIndex];
  if (!record) {
    detailElement.innerHTML = '<div class="castle-journal-empty">尚無筆記紀錄</div>';
    return;
  }

  detailElement.innerHTML = `
    <div class="castle-journal-detail-kicker">
      <span>第 ${selectedIndex + 1} / ${records.length} 筆</span>
      <span>${getJournalImageUrls(record).length} 張圖片</span>
    </div>
    <div class="castle-journal-detail-header">
      <div>
        <h2>
          <span class="samurai-badge title-level-${getRecordTitleLevel(record)}">
            ${escapeHtml(SAMURAI_TITLE_ICONS[getRecordTitleLevel(record)])}
          </span>
          ${escapeHtml(record.user_display_name)}
        </h2>
        <p>
          ${escapeHtml(record.title || "浪人")}
          ・旅遊日期 ${escapeHtml(record.travel_date)}
        </p>
      </div>
      <time>${escapeHtml(formatUpdatedAt(record.updated_at))}</time>
    </div>
    <div class="castle-journal-detail-text">
      ${escapeHtml(record.journal_text || "尚未填寫筆記內容")}
    </div>
    ${renderRecommendations(getJournalRecommendations(record))}
    ${renderJournalImages(getJournalImageUrls(record))}
  `;
}

function renderRecommendationOverview() {
  const recommendations = getAllRecommendations();
  if (recommendations.length === 0) {
    detailElement.innerHTML = `
      <div class="castle-journal-empty castle-journal-overview-empty">
        目前還沒有順遊推薦
      </div>
    `;
    return;
  }

  const items = recommendations.map(({ recommendation, record }) => (
    renderRecommendationCard(recommendation, record)
  )).join("");
  detailElement.innerHTML = `
    <div class="castle-journal-detail-kicker">
      <span>周邊順遊推薦</span>
      <span>${recommendations.length} 筆</span>
    </div>
    <section class="castle-journal-recommendations castle-journal-recommendations-overview">
      <h2>此城堡周邊順遊景點</h2>
      <div class="castle-journal-recommendation-grid">
        ${items}
      </div>
    </section>
  `;
}

function selectRecord(index) {
  viewMode = "records";
  selectedIndex = index;
  renderList();
  renderDetail();
}

function toggleRecommendationView() {
  viewMode = viewMode === "recommendations" ? "records" : "recommendations";
  renderList();
  renderDetail();
}

async function loadCastleJournals() {
  const castleId = getCastleIdFromPath();
  if (!castleId) {
    throw new Error("城堡網址格式錯誤");
  }

  const payload = await requestJson(`/api/v1/journals/castles/${castleId}`);
  const collection = payload.data;
  records = collection.records ?? [];
  selectedIndex = 0;
  renderHero(collection);
  renderList();
  renderDetail();
}

listElement.addEventListener("click", (event) => {
  const button = event.target.closest(".castle-journal-list-button");
  if (!button) {
    return;
  }
  selectRecord(Number(button.dataset.recordIndex));
});

recommendationViewButton.addEventListener("click", toggleRecommendationView);

loadCastleJournals().catch((error) => {
  subtitleElement.textContent = error.message;
  detailElement.innerHTML = `<div class="castle-journal-empty">${escapeHtml(error.message)}</div>`;
});
