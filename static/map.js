const JAPAN_BOUNDS = L.latLngBounds(
  [23.0, 122.0],
  [46.5, 154.5],
);
const OSAKA_CASTLE_CENTER = [34.687315, 135.526201];
const DEFAULT_ZOOM = 6;
const POPULARITY_BUCKET_SIZE = 3;
const SAMURAI_TITLES = [
  "浪人",
  "鄉士",
  "足輕",
  "侍",
  "足輕頭",
  "侍大將",
  "家老",
  "宿老",
  "小大名",
  "大大名",
  "霸主",
  "天下人",
];
const SAMURAI_TITLE_ICONS = ["流", "鄉", "足", "侍", "頭", "將", "家", "宿", "小", "大", "霸", "天"];
const MAX_CASTLE_COUNT_FOR_TOP_TITLE = 100;
const POPULARITY_COLORS = [
  "#dfe8ef",
  "#bfe3ea",
  "#9edccf",
  "#a9d76f",
  "#f0d861",
  "#f4b85c",
  "#ef8f4f",
  "#e75f4f",
  "#c83f65",
  "#8f2f80",
];

const map = L.map("map", {
  attributionControl: true,
  zoomControl: true,
  maxBounds: JAPAN_BOUNDS.pad(0.12),
  maxBoundsViscosity: 0.9,
  minZoom: 4,
  preferCanvas: true,
  worldCopyJump: false,
}).setView(OSAKA_CASTLE_CENTER, DEFAULT_ZOOM);

const markerGroup = L.featureGroup().addTo(map);
const countElement = document.querySelector("#castle-count");
const authNameElement = document.querySelector("#auth-name");
const loginLink = document.querySelector("#login-link");
const logoutButton = document.querySelector("#logout-button");
const toggleCastleLabelsButton = document.querySelector("#toggle-castle-labels");
const toggleVisitedMarkersButton = document.querySelector("#toggle-visited-markers");
const toggleActivityPanelButton = document.querySelector("#toggle-activity-panel");
const togglePopularPanelButton = document.querySelector("#toggle-popular-panel");
const toggleMyRecordsPanelButton = document.querySelector("#toggle-my-records-panel");
const toggleAccountRankingPanelButton = document.querySelector(
  "#toggle-account-ranking-panel",
);
const activityPanel = document.querySelector("#activity-panel");
const activityList = document.querySelector("#activity-list");
const activityEmpty = document.querySelector("#activity-empty");
const refreshActivityButton = document.querySelector("#refresh-activity");
const popularityLegendList = document.querySelector("#popularity-legend-list");
const popularPanel = document.querySelector("#popular-panel");
const popularList = document.querySelector("#popular-list");
const myRecordsPanel = document.querySelector("#my-records-panel");
const myRecordsList = document.querySelector("#my-records-list");
const myRecordsEmpty = document.querySelector("#my-records-empty");
const accountRankingPanel = document.querySelector("#account-ranking-panel");
const accountRankingList = document.querySelector("#account-ranking-list");
const accountRankingEmpty = document.querySelector("#account-ranking-empty");
const closeAccountRankingButton = document.querySelector("#close-account-ranking");
const samuraiRankLegend = document.querySelector("#samurai-rank-legend");
const samuraiRankLegendList = document.querySelector("#samurai-rank-legend-list");
const accountViewBanner = document.querySelector("#account-view-banner");
const accountViewLabel = document.querySelector("#account-view-label");
const closeAccountViewButton = document.querySelector("#close-account-view");

const markerByCastleId = new Map();
const castleById = new Map();
const journalByCastleId = new Map();
const viewedAccountJournalByCastleId = new Map();
const mapViewState = {
  showCastleLabels: true,
  showUnvisitedMarkers: true,
  showActivityPanel: false,
  showPopularPanel: false,
  showMyRecordsPanel: false,
  showAccountRankingPanel: false,
};
let viewedAccount = null;
let currentAuth = {
  authenticated: false,
  user: null,
  google_login_enabled: false,
};

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function buildWikipediaUrl(castle) {
  return castle.wikipedia_url
    ?? `https://zh.wikipedia.org/wiki/${encodeURIComponent(castle.name)}`;
}

function getPopularityLevel(journalCount) {
  if (journalCount <= 0) {
    return 0;
  }
  return Math.min(
    POPULARITY_COLORS.length - 1,
    Math.floor((journalCount - 1) / POPULARITY_BUCKET_SIZE),
  );
}

function getPopularityRangeLabel(level) {
  const minCount = level * POPULARITY_BUCKET_SIZE + 1;
  const maxCount = (level + 1) * POPULARITY_BUCKET_SIZE;
  if (level === POPULARITY_COLORS.length - 1) {
    return `${minCount}+ 筆`;
  }
  return `${minCount}-${maxCount} 筆`;
}

function getSamuraiRankRangeLabel(level) {
  if (level === SAMURAI_TITLES.length - 1) {
    return `${MAX_CASTLE_COUNT_FOR_TOP_TITLE}+ 座`;
  }

  const minCount = Math.ceil(
    level * MAX_CASTLE_COUNT_FOR_TOP_TITLE / SAMURAI_TITLES.length,
  );
  const maxCount = Math.ceil(
    (level + 1) * MAX_CASTLE_COUNT_FOR_TOP_TITLE / SAMURAI_TITLES.length,
  ) - 1;
  return `${minCount}-${maxCount} 座`;
}

function renderPopularityLegend() {
  popularityLegendList.innerHTML = "";
  POPULARITY_COLORS.forEach((color, index) => {
    const item = document.createElement("li");
    item.className = "popularity-legend-item";
    item.innerHTML = `
      <span
        class="popularity-legend-swatch"
        style="
          --legend-color: ${color};
          --legend-bg: color-mix(in srgb, ${color} 22%, transparent);
        "
      ></span>
      <span>${escapeHtml(getPopularityRangeLabel(index))}</span>
    `;
    popularityLegendList.append(item);
  });
}

function renderSamuraiRankLegend() {
  samuraiRankLegendList.innerHTML = "";
  SAMURAI_TITLES.forEach((title, index) => {
    const item = document.createElement("li");
    item.className = "samurai-rank-legend-item";
    item.innerHTML = `
      <span class="samurai-badge title-level-${index}">
        ${escapeHtml(SAMURAI_TITLE_ICONS[index])}
      </span>
      <span>
        <strong>${escapeHtml(title)}</strong>
        ${escapeHtml(getSamuraiRankRangeLabel(index))}
      </span>
    `;
    samuraiRankLegendList.append(item);
  });
}

function createCastleIcon(isVisited, journalCount) {
  const popularityLevel = getPopularityLevel(journalCount);
  const ringSize = journalCount > 0 ? 40 + popularityLevel * 5 : 34;
  const ringOpacity = journalCount > 0 ? 0.32 + popularityLevel * 0.06 : 0.12;
  const ringColor = POPULARITY_COLORS[popularityLevel];

  return L.divIcon({
    className: "",
    html: `
      <div
        class="castle-marker-wrap"
        style="
          --popularity-ring-size: ${ringSize}px;
          --popularity-ring-color: ${ringColor};
          --popularity-ring-opacity: ${ringOpacity};
        "
      >
        <div class="castle-popularity-ring"></div>
        <div class="castle-marker ${isVisited ? "is-visited" : "is-unvisited"
      }">濟</div>
      </div>
    `,
    iconSize: [72, 72],
    iconAnchor: [36, 36],
    popupAnchor: [0, -34],
  });
}

function getEmptyJournal(castleId, travelDate = "") {
  return {
    castle_id: castleId,
    visited: false,
    travel_date: travelDate,
    journal_text: "",
  };
}

function getJournalsForCastle(castleId) {
  return journalByCastleId.get(castleId) ?? [];
}

function getViewedAccountJournalsForCastle(castleId) {
  return viewedAccountJournalByCastleId.get(castleId) ?? [];
}

function getActiveJournalsForCastle(castleId) {
  if (viewedAccount) {
    return getViewedAccountJournalsForCastle(castleId);
  }
  return getJournalsForCastle(castleId);
}

function getJournalForCastleDate(castleId, travelDate) {
  return getJournalsForCastle(castleId).find(
    (journal) => journal.travel_date === travelDate,
  ) ?? getEmptyJournal(castleId, travelDate);
}

function getDefaultJournal(castleId) {
  const journals = getJournalsForCastle(castleId);
  return journals[0] ?? getEmptyJournal(castleId);
}

function isCastleVisited(castleId) {
  return getActiveJournalsForCastle(castleId).some((journal) => journal.visited);
}

function upsertLocalJournal(journal) {
  const journals = getJournalsForCastle(journal.castle_id);
  const nextJournals = journals.filter(
    (item) => item.travel_date !== journal.travel_date,
  );
  nextJournals.push(journal);
  nextJournals.sort((left, right) => (
    String(right.travel_date).localeCompare(left.travel_date)
  ));
  journalByCastleId.set(journal.castle_id, nextJournals);
}

function buildJournalForm(castle, travelDate = null) {
  const journal = travelDate
    ? getJournalForCastleDate(castle.id, travelDate)
    : getDefaultJournal(castle.id);
  return `
    <form class="journal-form">
      <label class="journal-visited">
        <input
          type="checkbox"
          name="visited"
          ${journal.visited ? "checked" : ""}
        >
        已去過
      </label>
      <label class="journal-field">
        <span>旅遊日期</span>
        <div class="journal-date-row">
          <input
            class="journal-date"
            type="text"
            name="travel_date"
            value="${escapeHtml(journal.travel_date)}"
            inputmode="numeric"
            pattern="\\d{4}-\\d{2}-\\d{2}"
            placeholder="YYYY-MM-DD"
            required
          >
          <button
            class="journal-date-picker-button"
            type="button"
            aria-label="快速選擇旅遊日期"
            title="快速選擇旅遊日期"
          ></button>
          <input
            class="journal-date-picker"
            type="date"
            value="${escapeHtml(journal.travel_date)}"
            tabindex="-1"
            aria-hidden="true"
          >
        </div>
      </label>
      <textarea
        class="journal-text"
        name="journal_text"
        maxlength="5000"
        placeholder="寫下這座城的旅行手帳"
      >${escapeHtml(journal.journal_text)}</textarea>
      <button class="journal-save" type="submit">
        儲存手帳
      </button>
      <div class="journal-message"></div>
    </form>
  `;
}

function buildPopupShell(castle, content) {
  const wikipediaUrl = buildWikipediaUrl(castle);
  const imageMarkup = castle.image_url
    ? `
      <a
        class="castle-popup-image-link"
        href="${escapeHtml(wikipediaUrl)}"
        target="_blank"
        rel="noopener noreferrer"
        title="開啟 ${escapeHtml(castle.name)} 的維基百科文章"
      >
        <img class="castle-popup-image" src="${escapeHtml(castle.image_url)}" alt="${escapeHtml(castle.name)}">
      </a>
    `
    : "";
  return `
    <div class="castle-popup" data-castle-id="${castle.id}">
      ${imageMarkup}
      <strong>${escapeHtml(castle.name)}</strong>
      <span>${escapeHtml(castle.address)}</span>
      ${content}
    </div>
  `;
}

function buildPopupActions(castle) {
  return buildPopupShell(
    castle,
    `
      <div class="popup-actions">
        <button class="popup-action-button show-castle-records" type="button">
          顯示最新紀錄
        </button>
        <button class="popup-action-button show-journal-form" type="button">
          輸入手帳
        </button>
      </div>
    `,
  );
}

function buildPopupRecords(castle) {
  return buildPopupShell(
    castle,
    '<div class="popup-record-list">載入中</div>',
  );
}

function buildPopupForm(castle) {
  return buildPopupShell(castle, buildJournalForm(castle));
}

function buildPopupFormForDate(castle, travelDate) {
  return buildPopupShell(castle, buildJournalForm(castle, travelDate));
}

function buildPopup(castle) {
  if (viewedAccount) {
    return buildPopupShell(
      castle,
      renderCastleRecords(getViewedAccountJournalsForCastle(castle.id)),
    );
  }
  if (currentAuth.authenticated) {
    return buildPopupActions(castle);
  }
  return buildPopupRecords(castle);
}

function renderCastleRecords(records) {
  if (records.length === 0) {
    return '<div class="popup-record-list">尚無手帳紀錄</div>';
  }

  const items = records.map((record) => `
    <article class="popup-record">
      <div class="popup-record-meta">
        ${escapeHtml(record.user_display_name)}
        ・旅遊日期 ${escapeHtml(record.travel_date)}
        ・更新 ${escapeHtml(formatUpdatedAt(record.updated_at))}
      </div>
      <div class="popup-record-text">
        ${escapeHtml(record.journal_text)}
      </div>
    </article>
  `);
  return `<div class="popup-record-list">${items.join("")}</div>`;
}

async function showCastleRecords(castleId) {
  const marker = markerByCastleId.get(castleId);
  const castle = castleById.get(castleId);
  if (!marker || !castle) {
    return;
  }

  marker.setPopupContent(buildPopupRecords(castle));
  const payload = await requestJson(`/api/v1/journals/castles/${castleId}/latest`);
  marker.setPopupContent(
    buildPopupShell(castle, renderCastleRecords(payload.data ?? [])),
  );
}

function showJournalForm(castleId, travelDate = null) {
  const marker = markerByCastleId.get(castleId);
  const castle = castleById.get(castleId);
  if (!marker || !castle) {
    return;
  }
  marker.setPopupContent(
    travelDate
      ? buildPopupFormForDate(castle, travelDate)
      : buildPopupForm(castle),
  );
}

function refreshMarker(castleId) {
  const marker = markerByCastleId.get(castleId);
  const castle = castleById.get(castleId);
  if (!marker || !castle) {
    return;
  }

  marker.setIcon(createCastleIcon(isCastleVisited(castleId), castle.journal_count));
  marker.setPopupContent(buildPopup(castle));
}

function refreshAllMarkers() {
  castleById.forEach((castle) => {
    refreshMarker(castle.id);
  });
}

function setAccountViewBanner() {
  accountViewBanner.hidden = viewedAccount === null;
  accountViewLabel.textContent = viewedAccount
    ? `目前觀看：${viewedAccount.displayName} 的城堡紀錄`
    : "";
}

async function showAccountMap(userId, displayName) {
  viewedAccountJournalByCastleId.clear();
  viewedAccount = { userId, displayName };
  setAccountViewBanner();
  refreshAllMarkers();

  const payload = await requestJson(`/api/v1/journals/accounts/${userId}/journals`);
  (payload.data ?? []).forEach((journal) => {
    const journals = viewedAccountJournalByCastleId.get(journal.castle_id) ?? [];
    journals.push({
      castle_id: journal.castle_id,
      visited: true,
      travel_date: journal.travel_date,
      journal_text: journal.journal_text,
      user_display_name: journal.user_display_name,
      updated_at: journal.updated_at,
    });
    journals.sort((left, right) => (
      String(right.travel_date).localeCompare(left.travel_date)
    ));
    viewedAccountJournalByCastleId.set(journal.castle_id, journals);
  });
  refreshAllMarkers();
}

function closeAccountMap() {
  viewedAccount = null;
  viewedAccountJournalByCastleId.clear();
  setAccountViewBanner();
  refreshAllMarkers();
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

function renderActivityList(activities) {
  activityList.innerHTML = "";
  activityEmpty.hidden = activities.length > 0;

  activities.forEach((activity, index) => {
    const item = document.createElement("li");
    item.className = "activity-item";
    item.innerHTML = `
      <button
        class="activity-button"
        type="button"
        data-activity-index="${index}"
        data-castle-id="${activity.castle_id}"
      >
        <div class="activity-main">
          <strong>${escapeHtml(activity.user_display_name)}</strong>
          更新了
          <strong>${escapeHtml(activity.castle_name)}</strong>
          的手帳
        </div>
        <div class="activity-trip-date">
          旅遊日期：${escapeHtml(activity.travel_date)}
        </div>
        <time class="activity-time">${escapeHtml(
    formatUpdatedAt(activity.updated_at),
  )}</time>
      </button>
      <article class="activity-journal" hidden>
        ${escapeHtml(activity.journal_text || "尚無手帳內容")}
      </article>
    `;
    activityList.append(item);
  });
}

function renderPopularCastles() {
  const castles = Array.from(castleById.values())
    .sort((left, right) => {
      if (right.journal_count !== left.journal_count) {
        return right.journal_count - left.journal_count;
      }
      return left.id - right.id;
    })
    .slice(0, 20);

  popularList.innerHTML = "";
  castles.forEach((castle, index) => {
    const rank = index + 1;
    const crown = rank <= 3
      ? `<span class="popular-crown rank-${rank}">♛</span>`
      : "";
    const item = document.createElement("li");
    item.className = "popular-item";
    item.innerHTML = `
      <button
        class="popular-button"
        type="button"
        data-castle-id="${castle.id}"
      >
        <div class="popular-main">
          <span class="popular-rank">${crown}${rank}.</span>
          <strong>${escapeHtml(castle.name)}</strong>
        </div>
        <div class="popular-count">
          ${escapeHtml(castle.prefecture || "縣市未明")}
          ・${castle.journal_count} 筆手帳
        </div>
      </button>
    `;
    popularList.append(item);
  });
}

function renderMyRecords() {
  const journals = Array.from(journalByCastleId.values())
    .flat()
    .filter((journal) => journal.visited || journal.journal_text.trim())
    .sort((left, right) => (
      String(right.travel_date).localeCompare(left.travel_date)
    ));

  myRecordsList.innerHTML = "";
  myRecordsEmpty.hidden = journals.length > 0;

  journals.forEach((journal) => {
    const castle = castleById.get(journal.castle_id);
    if (!castle) {
      return;
    }

    const item = document.createElement("li");
    item.className = "popular-item";
    item.innerHTML = `
      <button
        class="popular-button my-record-button"
        type="button"
        data-castle-id="${castle.id}"
        data-travel-date="${escapeHtml(journal.travel_date)}"
      >
        <div class="popular-main">
          <strong>${escapeHtml(castle.name)}</strong>
        </div>
        <div class="popular-count">
          ${escapeHtml(castle.prefecture || "縣市未明")}
          ・旅遊日期 ${escapeHtml(journal.travel_date)}
        </div>
      </button>
    `;
    myRecordsList.append(item);
  });
}

function renderAccountRankings(rankings) {
  accountRankingList.innerHTML = "";
  accountRankingEmpty.hidden = rankings.length > 0;

  rankings.forEach((ranking) => {
    const titleLevel = Math.max(0, Math.min(
      SAMURAI_TITLES.length - 1,
      Number(ranking.title_level) || 0,
    ));
    const item = document.createElement("li");
    item.className = "account-ranking-item";
    item.innerHTML = `
      <button
        class="account-ranking-button"
        type="button"
        data-user-id="${ranking.user_id}"
        data-display-name="${escapeHtml(ranking.user_display_name)}"
      >
        <div class="account-ranking-rank">${ranking.rank}</div>
        <span class="samurai-badge title-level-${titleLevel}">
          ${escapeHtml(SAMURAI_TITLE_ICONS[titleLevel])}
        </span>
        <div class="account-ranking-main">
          <strong>${escapeHtml(ranking.user_display_name)}</strong>
          <span>${escapeHtml(ranking.title)}</span>
        </div>
        <div class="account-ranking-count">
          ${ranking.visited_castle_count} 座
        </div>
      </button>
    `;
    accountRankingList.append(item);
  });
}

async function loadAccountRankings() {
  accountRankingList.innerHTML = "";
  accountRankingEmpty.hidden = false;
  accountRankingEmpty.textContent = "載入中";

  try {
    const payload = await requestJson("/api/v1/journals/accounts/rankings?limit=30");
    accountRankingEmpty.textContent = "尚無排名資料";
    renderAccountRankings(payload.data ?? []);
  } catch (error) {
    accountRankingEmpty.textContent = error.message || "排名資料載入失敗";
  }
}

function syncMapViewControls() {
  document.body.classList.toggle(
    "is-castle-labels-hidden",
    !mapViewState.showCastleLabels,
  );
  document.body.classList.toggle(
    "is-visited-markers-hidden",
    !mapViewState.showUnvisitedMarkers,
  );
  popularPanel.hidden = !mapViewState.showPopularPanel;
  myRecordsPanel.hidden = !mapViewState.showMyRecordsPanel;
  activityPanel.hidden = !mapViewState.showActivityPanel;
  accountRankingPanel.hidden = !mapViewState.showAccountRankingPanel;
  toggleCastleLabelsButton.classList.toggle(
    "is-active",
    mapViewState.showCastleLabels,
  );
  toggleVisitedMarkersButton.classList.toggle(
    "is-active",
    mapViewState.showUnvisitedMarkers,
  );
  toggleActivityPanelButton.classList.toggle(
    "is-active",
    mapViewState.showActivityPanel,
  );
  togglePopularPanelButton.classList.toggle(
    "is-active",
    mapViewState.showPopularPanel,
  );
  toggleMyRecordsPanelButton.classList.toggle(
    "is-active",
    mapViewState.showMyRecordsPanel,
  );
  toggleAccountRankingPanelButton.classList.toggle(
    "is-active",
    mapViewState.showAccountRankingPanel,
  );
}

async function requestJson(url, options = {}) {
  const response = await fetch(url, {
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
      ...(options.headers ?? {}),
    },
    ...options,
  });

  const payload = await response.json();
  if (!response.ok || payload.success === false) {
    throw new Error(payload.message ?? "Request failed.");
  }
  return payload;
}

async function loadAuth() {
  const payload = await requestJson("/api/v1/auth/me");
  currentAuth = payload.data;

  if (currentAuth.authenticated) {
    authNameElement.textContent = currentAuth.user.display_name;
    loginLink.hidden = true;
    logoutButton.hidden = false;
    return;
  }

  authNameElement.textContent = currentAuth.google_login_enabled
    ? "尚未登入"
    : "尚未設定 Google 登入";
  loginLink.hidden = !currentAuth.google_login_enabled;
  logoutButton.hidden = true;
}

async function loadJournals() {
  journalByCastleId.clear();
  if (!currentAuth.authenticated) {
    return;
  }

  const payload = await requestJson("/api/v1/me/journals");
  payload.data.forEach((journal) => {
    upsertLocalJournal(journal);
  });
}

async function loadCastles() {
  const payload = await requestJson("/api/v1/castles");
  const castles = payload.data ?? [];

  castles.forEach((castle) => {
    castleById.set(castle.id, castle);
    const marker = L.marker([castle.latitude, castle.longitude], {
      icon: createCastleIcon(
        isCastleVisited(castle.id),
        castle.journal_count,
      ),
    });
    marker.bindPopup(buildPopup(castle));
    marker.on("popupopen", () => {
      if (!viewedAccount && !currentAuth.authenticated) {
        showCastleRecords(castle.id).catch(() => {
          marker.setPopupContent(
            buildPopupShell(castle, '<div class="popup-record-list">載入失敗</div>'),
          );
        });
      }
    });
    marker.on("popupclose", () => {
      marker.setPopupContent(buildPopup(castle));
    });
    marker.bindTooltip(escapeHtml(castle.name), {
      className: "castle-label",
      direction: "right",
      offset: [12, 0],
      opacity: 0.9,
      permanent: true,
    });
    marker.addTo(markerGroup);
    markerByCastleId.set(castle.id, marker);
  });

  countElement.textContent = `${castles.length} 座城堡`;
  renderPopularCastles();
  map.setView(OSAKA_CASTLE_CENTER, DEFAULT_ZOOM);
}

async function loadLatestActivities() {
  const payload = await requestJson("/api/v1/journals/latest?limit=20");
  renderActivityList(payload.data ?? []);
}

async function loadAdministrativeAreas() {
  const response = await fetch("/static/data/japan_prefectures.geojson", {
    headers: { Accept: "application/geo+json, application/json" },
  });
  if (!response.ok) {
    throw new Error("Failed to load administrative map.");
  }

  const geojson = await response.json();
  L.geoJSON(geojson, {
    style: {
      color: "#8a969d",
      fillColor: "#e9efe3",
      fillOpacity: 1,
      opacity: 1,
      weight: 0.9,
    },
    onEachFeature: (feature, layer) => {
      const prefectureName = feature.properties?.nam_ja;
      if (prefectureName) {
        layer.bindTooltip(prefectureName, {
          className: "prefecture-label",
          direction: "center",
          sticky: true,
        });
      }
    },
  }).addTo(map);

  map.attributionControl.addAttribution(
    '行政區資料: <a href="https://github.com/amay077/JapanPrefGeoJson">JapanPrefGeoJson</a>',
  );
}

async function saveJournal(form) {
  const popupElement = form.closest(".castle-popup");
  const messageElement = form.querySelector(".journal-message");
  const castleId = Number(popupElement.dataset.castleId);
  const payload = await requestJson(`/api/v1/me/journals/${castleId}`, {
    method: "PUT",
    body: JSON.stringify({
      visited: form.elements.visited.checked,
      travel_date: form.elements.travel_date.value,
      journal_text: form.elements.journal_text.value,
    }),
  });

  upsertLocalJournal(payload.data);
  refreshMarker(castleId);
  renderMyRecords();
  await loadLatestActivities();
  messageElement.textContent = "已儲存";
}

document.addEventListener("submit", (event) => {
  if (!event.target.classList.contains("journal-form")) {
    return;
  }

  event.preventDefault();
  const form = event.target;
  const messageElement = form.querySelector(".journal-message");
  messageElement.textContent = "儲存中";
  saveJournal(form).catch((error) => {
    messageElement.textContent = error.message;
  });
});

document.addEventListener("click", (event) => {
  const imageLink = event.target.closest(".castle-popup-image-link");
  if (!imageLink) {
    return;
  }

  event.preventDefault();
  event.stopPropagation();
  window.open(imageLink.href, "_blank", "noopener,noreferrer");
}, true);

document.addEventListener("click", (event) => {
  const recordsButton = event.target.closest(".show-castle-records");
  if (recordsButton) {
    const popupElement = recordsButton.closest(".castle-popup");
    showCastleRecords(Number(popupElement.dataset.castleId)).catch(() => {});
    return;
  }

  const formButton = event.target.closest(".show-journal-form");
  if (formButton) {
    const popupElement = formButton.closest(".castle-popup");
    showJournalForm(Number(popupElement.dataset.castleId));
  }
});

document.addEventListener("click", (event) => {
  const pickerButton = event.target.closest(".journal-date-picker-button");
  if (!pickerButton) {
    return;
  }

  const datePicker = pickerButton
    .closest(".journal-date-row")
    .querySelector(".journal-date-picker");
  if (!datePicker) {
    return;
  }

  if (typeof datePicker.showPicker === "function") {
    datePicker.showPicker();
    return;
  }

  datePicker.focus();
  datePicker.click();
});

activityList.addEventListener("click", (event) => {
  const button = event.target.closest(".activity-button");
  if (!button) {
    return;
  }

  const item = button.closest(".activity-item");
  const journal = item.querySelector(".activity-journal");
  const isExpanded = !journal.hidden;
  activityList.querySelectorAll(".activity-journal").forEach((element) => {
    element.hidden = true;
  });
  journal.hidden = isExpanded;
  if (!isExpanded) {
    openCastlePopup(Number(button.dataset.castleId));
  }
});

document.addEventListener("change", (event) => {
  if (event.target.classList.contains("journal-date-picker")) {
    const form = event.target.closest(".journal-form");
    form.elements.travel_date.value = event.target.value;
    form.elements.travel_date.dispatchEvent(new Event("change", { bubbles: true }));
    return;
  }

  if (!event.target.classList.contains("journal-date")) {
    return;
  }

  const popupElement = event.target.closest(".castle-popup");
  const form = event.target.closest(".journal-form");
  const castleId = Number(popupElement.dataset.castleId);
  const datePicker = form.querySelector(".journal-date-picker");
  if (datePicker) {
    datePicker.value = event.target.value;
  }
  const journal = getJournalForCastleDate(castleId, event.target.value);
  form.elements.visited.checked = journal.visited;
  form.elements.journal_text.value = journal.journal_text;
});

accountRankingList.addEventListener("click", (event) => {
  const button = event.target.closest(".account-ranking-button");
  if (!button) {
    return;
  }

  accountRankingEmpty.hidden = false;
  accountRankingEmpty.textContent = "載入帳號紀錄中";
  showAccountMap(Number(button.dataset.userId), button.dataset.displayName)
    .then(() => {
      accountRankingEmpty.hidden = true;
      mapViewState.showAccountRankingPanel = false;
      syncMapViewControls();
    })
    .catch((error) => {
      closeAccountMap();
      accountRankingEmpty.hidden = false;
      accountRankingEmpty.textContent = error.message || "帳號紀錄載入失敗";
    });
});

closeAccountViewButton.addEventListener("click", () => {
  closeAccountMap();
});

logoutButton.addEventListener("click", async () => {
  await requestJson("/api/v1/auth/logout", { method: "POST" });
  window.location.reload();
});

toggleCastleLabelsButton.addEventListener("click", () => {
  mapViewState.showCastleLabels = !mapViewState.showCastleLabels;
  syncMapViewControls();
});

toggleVisitedMarkersButton.addEventListener("click", () => {
  mapViewState.showUnvisitedMarkers = !mapViewState.showUnvisitedMarkers;
  syncMapViewControls();
});

toggleActivityPanelButton.addEventListener("click", async () => {
  mapViewState.showActivityPanel = !mapViewState.showActivityPanel;
  if (mapViewState.showActivityPanel) {
    mapViewState.showPopularPanel = false;
    mapViewState.showMyRecordsPanel = false;
    mapViewState.showAccountRankingPanel = false;
  }
  syncMapViewControls();
  if (mapViewState.showActivityPanel) {
    await loadLatestActivities();
  }
});

togglePopularPanelButton.addEventListener("click", () => {
  mapViewState.showPopularPanel = !mapViewState.showPopularPanel;
  if (mapViewState.showPopularPanel) {
    mapViewState.showActivityPanel = false;
    mapViewState.showMyRecordsPanel = false;
    mapViewState.showAccountRankingPanel = false;
    renderPopularCastles();
  }
  syncMapViewControls();
});

toggleMyRecordsPanelButton.addEventListener("click", () => {
  mapViewState.showMyRecordsPanel = !mapViewState.showMyRecordsPanel;
  if (mapViewState.showMyRecordsPanel) {
    mapViewState.showActivityPanel = false;
    mapViewState.showPopularPanel = false;
    mapViewState.showAccountRankingPanel = false;
    renderMyRecords();
  }
  syncMapViewControls();
});

toggleAccountRankingPanelButton.addEventListener("click", async () => {
  mapViewState.showAccountRankingPanel = !mapViewState.showAccountRankingPanel;
  if (mapViewState.showAccountRankingPanel) {
    mapViewState.showActivityPanel = false;
    mapViewState.showPopularPanel = false;
    mapViewState.showMyRecordsPanel = false;
  }
  syncMapViewControls();
  if (mapViewState.showAccountRankingPanel) {
    await loadAccountRankings();
  }
});

closeAccountRankingButton.addEventListener("click", () => {
  mapViewState.showAccountRankingPanel = false;
  syncMapViewControls();
});

function openCastlePopup(castleId, mode = "default", travelDate = null) {
  const castle = castleById.get(castleId);
  const marker = markerByCastleId.get(castleId);
  if (!castle || !marker) {
    return;
  }

  map.setView([castle.latitude, castle.longitude], Math.max(map.getZoom(), 7));
  marker.openPopup();
  if (mode === "edit") {
    showJournalForm(castleId, travelDate);
  }
}

popularList.addEventListener("click", (event) => {
  const button = event.target.closest(".popular-button");
  if (!button) {
    return;
  }

  openCastlePopup(Number(button.dataset.castleId));
});

myRecordsList.addEventListener("click", (event) => {
  const button = event.target.closest(".my-record-button");
  if (!button) {
    return;
  }
  openCastlePopup(
    Number(button.dataset.castleId),
    "edit",
    button.dataset.travelDate,
  );
});

refreshActivityButton.addEventListener("click", () => {
  loadLatestActivities().catch(() => {
    activityEmpty.hidden = false;
    activityEmpty.textContent = "更新紀錄載入失敗";
  });
});

async function initialize() {
  syncMapViewControls();
  renderPopularityLegend();
  renderSamuraiRankLegend();
  await loadAuth();
  await loadJournals();
  await loadAdministrativeAreas();
  await loadCastles();
  renderMyRecords();
  await loadLatestActivities();
}

initialize().catch(() => {
  countElement.textContent = "載入失敗";
});
