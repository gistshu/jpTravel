const JAPAN_BOUNDS = L.latLngBounds(
  [23.0, 122.0],
  [46.5, 154.5],
);
const DEFAULT_MAP_CENTER = [35.014239, 135.748134];
const DEFAULT_ZOOM = 8;
const POPULARITY_BUCKET_SIZE = 20;
const MAX_JOURNAL_IMAGES = 5;
const MAX_RECOMMENDATION_IMAGES = 3;
const POPUP_ARROW_Y = 64;
const POPUP_LEFT_GAP = 15;
const DEFAULT_POI_SEARCH_RADIUS_METERS = 300;
const POI_SEARCH_RADIUS_OPTIONS = [100, 300, 800];
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
const SAMURAI_TITLE_ICONS = ["浪", "鄉", "足", "侍", "頭", "將", "家", "宿", "小", "大", "霸", "天"];
const MAX_CASTLE_COUNT_FOR_TOP_TITLE = 100;
const POPULARITY_COLORS = [
  "#8ca0b3",
  "#2f80ed",
  "#00a6c8",
  "#009b72",
  "#72a700",
  "#d8a000",
  "#f47c20",
  "#d93636",
  "#c0267a",
  "#6f35c4",
];
const PREFECTURE_REGION_COLORS = [
  { ids: [1], color: "#c9c3a4" },
  { ids: [2, 3, 4, 5, 6, 7], color: "#a9b886" },
  { ids: [8, 9, 10, 11, 12, 13, 14], color: "#d9a868" },
  { ids: [15, 16, 17, 18, 19, 20, 21, 22, 23], color: "#d4c07a" },
  { ids: [24, 25, 26, 27, 28, 29, 30], color: "#cf8f7c" },
  { ids: [31, 32, 33, 34, 35], color: "#9fb7a8" },
  { ids: [36, 37, 38, 39], color: "#e0bf8a" },
  { ids: [40, 41, 42, 43, 44, 45, 46, 47], color: "#b7a3c4" },
];
const ACCOUNT_PREFECTURE_COLORS = [
  "#f1ecf7",
  "#dfd0f0",
  "#c6a6df",
  "#a978cd",
  "#8951b5",
  "#68309a",
];
const NEUTRAL_PREFECTURE_COLOR = "#e4d6b0";
const CALENDAR_FIRST_YEAR = 1990;
const CALENDAR_WEEKDAYS = ["日", "一", "二", "三", "四", "五", "六"];
const GSI_ATTRIBUTION = (
  '<a href="https://maps.gsi.go.jp/development/ichiran.html" target="_blank" rel="noopener noreferrer">国土地理院</a>'
);
const POI_PICKER_BASE_LAYERS = [
  {
    name: "地理院 標準地図（含建物）",
    url: "https://cyberjapandata.gsi.go.jp/xyz/std/{z}/{x}/{y}.png",
    options: { attribution: GSI_ATTRIBUTION, maxNativeZoom: 18, maxZoom: 20 },
  },
  {
    name: "地理院 航空照片",
    url: "https://cyberjapandata.gsi.go.jp/xyz/seamlessphoto/{z}/{x}/{y}.jpg",
    options: { attribution: GSI_ATTRIBUTION, maxNativeZoom: 18, maxZoom: 20 },
  },
  {
    name: "OpenStreetMap",
    url: "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
    options: { attribution: "© OpenStreetMap contributors", maxZoom: 19 },
  },
];
const MAPLIBRE_ASSETS = {
  css: "https://cdnjs.cloudflare.com/ajax/libs/maplibre-gl/4.7.1/maplibre-gl.css",
  script: "https://cdnjs.cloudflare.com/ajax/libs/maplibre-gl/4.7.1/maplibre-gl.js",
  leafletBridge: "https://unpkg.com/@maplibre/maplibre-gl-leaflet@0.1.3/leaflet-maplibre-gl.js",
};
const GSI_VECTOR_TILE_URL = (
  "https://cyberjapandata.gsi.go.jp/xyz/optimal_bvmap-v1/{z}/{x}/{y}.pbf"
);
const BUILDING_SOURCE_LAYERS = new Set(["BldA", "BldL", "building"]);
const POI_PICKER_VECTOR_LAYERS = [
  {
    name: "地理院 簡潔地圖（無建物）",
    styleUrl: "https://gsi-cyberjapan.github.io/optimal_bvmap/style/std.json",
    attribution: GSI_ATTRIBUTION,
    useDirectGsiTiles: true,
  },
  {
    name: "OpenFreeMap 淡色（無建物）",
    styleUrl: "https://tiles.openfreemap.org/styles/positron",
    attribution: (
      '<a href="https://openfreemap.org" target="_blank" rel="noopener noreferrer">OpenFreeMap</a> © OpenMapTiles © OpenStreetMap contributors'
    ),
    useDirectGsiTiles: false,
  },
];
const RECOMMENDATION_CATEGORIES = [
  ["attraction", "景點"],
  ["food", "美食"],
  ["shop", "商店"],
  ["cafe", "咖啡"],
  ["hotel", "住宿"],
  ["transport", "交通"],
  ["other", "其他"],
];

const map = L.map("map", {
  attributionControl: true,
  zoomControl: true,
  maxBounds: JAPAN_BOUNDS.pad(0.12),
  maxBoundsViscosity: 0.9,
  minZoom: 4,
  preferCanvas: true,
  worldCopyJump: false,
}).setView(DEFAULT_MAP_CENTER, DEFAULT_ZOOM);

const markerGroup = L.featureGroup().addTo(map);
const countElement = document.querySelector("#castle-count");
const authRankBadgeElement = document.querySelector("#auth-rank-badge");
const authNameElement = document.querySelector("#auth-name");
const loginLink = document.querySelector("#login-link");
const logoutButton = document.querySelector("#logout-button");
const toggleCastleLabelsButton = document.querySelector("#toggle-castle-labels");
const toggleRegionColorsButton = document.querySelector("#toggle-region-colors");
const toggleVisitedMarkersButton = document.querySelector("#toggle-visited-markers");
const togglePopularityLegendButton = document.querySelector(
  "#toggle-popularity-legend",
);
const toggleActivityPanelButton = document.querySelector("#toggle-activity-panel");
const togglePopularPanelButton = document.querySelector("#toggle-popular-panel");
const toggleMyRecordsPanelButton = document.querySelector("#toggle-my-records-panel");
const toggleAccountRankingPanelButton = document.querySelector(
  "#toggle-account-ranking-panel",
);
const cycleCastleSeriesFilterButton = document.querySelector(
  "#cycle-castle-series-filter",
);
const activityPanel = document.querySelector("#activity-panel");
const activityList = document.querySelector("#activity-list");
const activityEmpty = document.querySelector("#activity-empty");
const refreshActivityButton = document.querySelector("#refresh-activity");
const closeActivityPanelButton = document.querySelector("#close-activity-panel");
const leftToolDrawer = document.querySelector("#left-tool-drawer");
const toggleLeftToolDrawerButton = document.querySelector("#toggle-left-tool-drawer");
const popularityLegend = document.querySelector("#popularity-legend");
const popularityLegendList = document.querySelector("#popularity-legend-list");
const popularPanel = document.querySelector("#popular-panel");
const popularList = document.querySelector("#popular-list");
const closePopularPanelButton = document.querySelector("#close-popular-panel");
const myRecordsPanel = document.querySelector("#my-records-panel");
const myRecordsList = document.querySelector("#my-records-list");
const myRecordsEmpty = document.querySelector("#my-records-empty");
const closeMyRecordsPanelButton = document.querySelector("#close-my-records-panel");
const journalSidePanel = document.querySelector("#journal-side-panel");
const journalSideTitle = document.querySelector("#journal-side-title");
const journalSideSubtitle = document.querySelector("#journal-side-subtitle");
const journalSideContent = document.querySelector("#journal-side-content");
const closeJournalSidePanelButton = document.querySelector(
  "#close-journal-side-panel",
);
const accountRankingPanel = document.querySelector("#account-ranking-panel");
const accountRankingList = document.querySelector("#account-ranking-list");
const accountRankingEmpty = document.querySelector("#account-ranking-empty");
const closeAccountRankingButton = document.querySelector("#close-account-ranking");
const rightRankDrawer = document.querySelector("#right-rank-drawer");
const toggleRightRankDrawerButton = document.querySelector("#toggle-right-rank-drawer");
const samuraiRankLegend = document.querySelector("#samurai-rank-legend");
const samuraiRankLegendList = document.querySelector("#samurai-rank-legend-list");
const accountViewBanner = document.querySelector("#account-view-banner");
const accountViewLabel = document.querySelector("#account-view-label");
const closeAccountViewButton = document.querySelector("#close-account-view");
const accountPrefectureLegend = document.querySelector("#account-prefecture-legend");
const accountPrefectureLegendList = document.querySelector(
  "#account-prefecture-legend-list",
);
const closeAccountPrefectureLegendButton = document.querySelector(
  "#close-account-prefecture-legend",
);
const siteInfoModal = document.querySelector("#site-info-modal");
const siteInfoTitle = document.querySelector("#site-info-title");
const siteInfoReferences = document.querySelector("#site-info-references");
const siteInfoPrivacy = document.querySelector("#site-info-privacy");
const journalStatsElement = document.querySelector("#journal-stats");

const markerByCastleId = new Map();
const castleById = new Map();
const journalByCastleId = new Map();
const viewedAccountJournalByCastleId = new Map();
let administrativeAreaLayer = null;
let latestActivities = [];
let selectedCastleLabelId = null;
const mapViewState = {
  showCastleLabels: false,
  showRegionColors: true,
  showUnvisitedMarkers: true,
  showPopularityLegend: false,
  showActivityPanel: false,
  showPopularPanel: false,
  showMyRecordsPanel: false,
  showAccountRankingPanel: false,
  showJournalSidePanel: false,
  showAccountPrefectureLegend: false,
  showLeftToolDrawer: false,
  showRightRankDrawer: false,
  castleSeriesFilter: "all",
};
const journalGalleryState = {
  imageUrls: [],
  currentIndex: 0,
};
const poiPickerState = {
  row: null,
  map: null,
  markerLayer: null,
  selectedMarker: null,
  clickedLatLng: null,
  searchRadiusMeters: DEFAULT_POI_SEARCH_RADIUS_METERS,
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

function buildCastleJournalPageUrl(castleId) {
  return `/castles/${encodeURIComponent(castleId)}/journals`;
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
    return `${minCount}+ 次`;
  }
  return `${minCount}-${maxCount} 次`;
}

function getPrefectureRegionColor(prefectureId) {
  const id = Number(prefectureId);
  const region = PREFECTURE_REGION_COLORS.find((item) => item.ids.includes(id));
  return region?.color ?? "#e4d6b0";
}

function normalizePrefectureName(value) {
  return String(value || "")
    .replace(/\s+/g, "")
    .replaceAll("縣", "県");
}

function getViewedAccountPrefectureCounts() {
  const visitedCastleIdsByPrefecture = new Map();
  viewedAccountJournalByCastleId.forEach((journals, castleId) => {
    if (!journals.some((journal) => journal.visited)) {
      return;
    }
    const prefecture = normalizePrefectureName(castleById.get(castleId)?.prefecture);
    if (!prefecture) {
      return;
    }
    const castleIds = visitedCastleIdsByPrefecture.get(prefecture) ?? new Set();
    castleIds.add(castleId);
    visitedCastleIdsByPrefecture.set(prefecture, castleIds);
  });

  return new Map(
    Array.from(visitedCastleIdsByPrefecture.entries()).map(
      ([prefecture, castleIds]) => [prefecture, castleIds.size],
    ),
  );
}

function getPrefectureCastleCounts() {
  const castleIdsByPrefecture = new Map();
  castleById.forEach((castle, castleId) => {
    if (!isOfficialCastle(castle)) {
      return;
    }
    const prefecture = normalizePrefectureName(castle.prefecture);
    if (!prefecture) {
      return;
    }
    const castleIds = castleIdsByPrefecture.get(prefecture) ?? new Set();
    castleIds.add(castleId);
    castleIdsByPrefecture.set(prefecture, castleIds);
  });

  return new Map(
    Array.from(castleIdsByPrefecture.entries()).map(
      ([prefecture, castleIds]) => [prefecture, castleIds.size],
    ),
  );
}

function getAccountPrefectureColor(visitedCount, totalCount) {
  if (visitedCount <= 0 || totalCount <= 0) {
    return NEUTRAL_PREFECTURE_COLOR;
  }
  const completionRate = Math.min(1, visitedCount / totalCount);
  const colorCount = ACCOUNT_PREFECTURE_COLORS.length;
  const colorIndex = Math.min(
    colorCount - 1,
    Math.ceil(completionRate * colorCount) - 1,
  );
  return ACCOUNT_PREFECTURE_COLORS[colorIndex];
}

function getAdministrativeAreaStyle(feature) {
  const prefectureName = normalizePrefectureName(feature.properties?.nam_ja);
  if (viewedAccount) {
    const prefectureCounts = getViewedAccountPrefectureCounts();
    const totalCastleCounts = getPrefectureCastleCounts();
    const visitedCount = prefectureCounts.get(prefectureName) ?? 0;
    const totalCount = totalCastleCounts.get(prefectureName) ?? 0;
    return {
      color: "#5a4526",
      fillColor: getAccountPrefectureColor(visitedCount, totalCount),
      fillOpacity: visitedCount > 0 ? 0.92 : 0.9,
      opacity: 1,
      weight: visitedCount > 0 ? 1.2 : 0.75,
    };
  }

  return {
    color: "#5a4526",
    fillColor: mapViewState.showRegionColors
      ? getPrefectureRegionColor(feature.properties?.id)
      : NEUTRAL_PREFECTURE_COLOR,
    fillOpacity: mapViewState.showRegionColors ? 0.95 : 0.9,
    opacity: 1,
    weight: 0.9,
  };
}

function refreshAdministrativeAreaStyles() {
  if (administrativeAreaLayer) {
    administrativeAreaLayer.setStyle(getAdministrativeAreaStyle);
  }
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
  [...SAMURAI_TITLES].reverse().forEach((title) => {
    const index = SAMURAI_TITLES.indexOf(title);
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

function renderAccountPrefectureLegend() {
  accountPrefectureLegendList.innerHTML = "";
  const ranges = ACCOUNT_PREFECTURE_COLORS.map((color, index) => {
    const minRate = Math.floor(index / ACCOUNT_PREFECTURE_COLORS.length * 100) + 1;
    const maxRate = Math.floor((index + 1) / ACCOUNT_PREFECTURE_COLORS.length * 100);
    return { color, label: `${minRate}-${maxRate}%` };
  });
  [
    { color: NEUTRAL_PREFECTURE_COLOR, label: "0%" },
    ...ranges,
  ].forEach((item) => {
    const element = document.createElement("li");
    element.className = "account-prefecture-legend-item";
    element.innerHTML = `
      <span
        class="account-prefecture-legend-swatch"
        style="--legend-color: ${item.color};"
      ></span>
      <span>${escapeHtml(item.label)}</span>
    `;
    accountPrefectureLegendList.append(element);
  });
}

function getSamuraiTitleLevel(visitedCastleCount) {
  if (visitedCastleCount >= MAX_CASTLE_COUNT_FOR_TOP_TITLE) {
    return SAMURAI_TITLES.length - 1;
  }

  const castlesPerLevel = MAX_CASTLE_COUNT_FOR_TOP_TITLE / SAMURAI_TITLES.length;
  return Math.min(
    SAMURAI_TITLES.length - 1,
    Math.floor(Math.max(visitedCastleCount, 0) / castlesPerLevel),
  );
}

function syncAuthRankBadge() {
  if (!currentAuth.authenticated) {
    authRankBadgeElement.hidden = true;
    authRankBadgeElement.textContent = "";
    authRankBadgeElement.removeAttribute("title");
    authRankBadgeElement.className = "auth-rank-badge";
    return;
  }

  const visitedCastleIds = new Set();
  journalByCastleId.forEach((journals, castleId) => {
    if (journals.some((journal) => journal.visited)) {
      visitedCastleIds.add(castleId);
    }
  });
  const titleLevel = getSamuraiTitleLevel(visitedCastleIds.size);
  authRankBadgeElement.hidden = false;
  authRankBadgeElement.className = `auth-rank-badge title-level-${titleLevel}`;
  authRankBadgeElement.textContent = SAMURAI_TITLE_ICONS[titleLevel];
  authRankBadgeElement.title = (
    `${SAMURAI_TITLES[titleLevel]}・${visitedCastleIds.size} 座`
  );
}

function getCastleDisplayName(castle) {
  const numberPrefix = castle.castle_number ? `#${castle.castle_number} ` : "";
  const seriesSuffix = castle.castle_series === "continued" ? " (續)" : "";
  return `${numberPrefix}${castle.name}${seriesSuffix}`;
}

function isOfficialCastle(castle) {
  return castle.castle_series === "original" || castle.castle_series === "continued";
}

function hasMyRecord(castleId) {
  return getJournalsForCastle(castleId).some((journal) => (
    journal.visited
    || journal.journal_text.trim()
    || getJournalImageUrls(journal).length > 0
  ));
}

function isCastleVisible(castle) {
  if (viewedAccount) {
    return (
      isOfficialCastle(castle)
      && getViewedAccountJournalsForCastle(castle.id).length > 0
    );
  }

  if (mapViewState.showMyRecordsPanel) {
    return isOfficialCastle(castle) && hasMyRecord(castle.id);
  }

  if (mapViewState.castleSeriesFilter === "all") {
    return isOfficialCastle(castle);
  }

  return castle.castle_series === mapViewState.castleSeriesFilter;
}

function createCastleIcon(isVisited, journalCount, castleSeries) {
  const popularityLevel = getPopularityLevel(journalCount);
  const ringSize = journalCount > 0 ? 30 + popularityLevel * 4 : 0;
  const ringOpacity = journalCount > 0 ? 0.32 + popularityLevel * 0.06 : 0;
  const ringColor = POPULARITY_COLORS[popularityLevel];

  return L.divIcon({
    className: "",
    html: `
      <div
        class="castle-marker-wrap ${isVisited ? "is-visited" : "is-unvisited"}"
        style="
          --popularity-ring-size: ${ringSize}px;
          --popularity-ring-color: ${ringColor};
          --popularity-ring-opacity: ${ringOpacity};
        "
      >
        <div class="castle-popularity-ring"></div>
        <div class="castle-marker series-${castleSeries} ${isVisited ? "is-visited" : "is-unvisited"
      }">濟</div>
      </div>
    `,
    iconSize: [72, 72],
    iconAnchor: [36, 36],
    popupAnchor: [252, -18],
  });
}

function getEmptyJournal(castleId, travelDate = "") {
  return {
    castle_id: castleId,
    visited: false,
    travel_date: travelDate,
    journal_text: "",
    image_urls: [],
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

function getJournalImageUrls(journal) {
  return Array.isArray(journal.image_urls) ? journal.image_urls : [];
}

function getJournalRecommendations(journal) {
  return Array.isArray(journal.recommendations) ? journal.recommendations : [];
}

function getGoogleMapsUrl(latitude, longitude) {
  const lat = Number(latitude);
  const lon = Number(longitude);
  if (!Number.isFinite(lat) || !Number.isFinite(lon)) {
    return "";
  }
  return `https://www.google.com/maps/search/?api=1&query=${lat},${lon}`;
}

function getRecommendationMapUrl(recommendation) {
  return (
    getGoogleMapsUrl(recommendation.latitude, recommendation.longitude)
    || recommendation.google_maps_url
    || recommendation.osm_url
    || ""
  );
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

function renderJournalImages(imageUrls, className = "journal-image-grid") {
  if (!imageUrls.length) {
    return "";
  }

  const images = imageUrls.map((imageUrl) => `
    <button
      class="journal-gallery-button"
      type="button"
      data-image-url="${escapeHtml(imageUrl)}"
      aria-label="開啟筆記圖片"
    >
      <img src="${escapeHtml(imageUrl)}" alt="筆記圖片">
    </button>
  `);
  return `<div class="${className}">${images.join("")}</div>`;
}

function ensureJournalGallery() {
  let gallery = document.querySelector("#journal-gallery");
  if (gallery) {
    return gallery;
  }

  gallery = document.createElement("div");
  gallery.id = "journal-gallery";
  gallery.className = "journal-gallery";
  gallery.hidden = true;
  gallery.innerHTML = `
    <div class="journal-gallery-backdrop" data-gallery-close></div>
    <div class="journal-gallery-dialog" role="dialog" aria-modal="true">
      <button class="journal-gallery-close" type="button" data-gallery-close aria-label="關閉圖片">×</button>
      <button class="journal-gallery-nav journal-gallery-prev" type="button" data-gallery-prev aria-label="上一張">‹</button>
      <img class="journal-gallery-image" alt="筆記圖片">
      <button class="journal-gallery-nav journal-gallery-next" type="button" data-gallery-next aria-label="下一張">›</button>
      <div class="journal-gallery-count"></div>
    </div>
  `;
  document.body.append(gallery);
  return gallery;
}

function renderJournalGallery() {
  const gallery = ensureJournalGallery();
  const image = gallery.querySelector(".journal-gallery-image");
  const count = gallery.querySelector(".journal-gallery-count");
  const total = journalGalleryState.imageUrls.length;
  const currentUrl = journalGalleryState.imageUrls[journalGalleryState.currentIndex];
  image.src = currentUrl;
  count.textContent = `${journalGalleryState.currentIndex + 1} / ${total}`;
  gallery.hidden = false;
}

function openJournalGallery(imageUrls, currentIndex) {
  journalGalleryState.imageUrls = imageUrls;
  journalGalleryState.currentIndex = currentIndex;
  renderJournalGallery();
}

function closeJournalGallery() {
  const gallery = ensureJournalGallery();
  gallery.hidden = true;
  gallery.querySelector(".journal-gallery-image").removeAttribute("src");
}

function openSiteInfoModal(type) {
  const isPrivacy = type === "privacy";
  siteInfoReferences.hidden = isPrivacy;
  siteInfoPrivacy.hidden = !isPrivacy;
  siteInfoTitle.textContent = isPrivacy ? "隱私條款" : "參考網站";
  siteInfoModal.hidden = false;
}

function closeSiteInfoModal() {
  siteInfoModal.hidden = true;
}

function moveJournalGallery(step) {
  const total = journalGalleryState.imageUrls.length;
  if (!total) {
    return;
  }
  journalGalleryState.currentIndex = (
    journalGalleryState.currentIndex + step + total
  ) % total;
  renderJournalGallery();
}

function renderRecommendationEditor(journal) {
  const recommendations = getJournalRecommendations(journal);
  const rows = recommendations.map(renderRecommendationEditorRow).join("");
  return `
    <section class="journal-recommendation-editor">
      <div class="journal-recommendation-header">
        <h3>順遊推薦</h3>
        <button class="journal-add-recommendation" type="button">
          新增推薦
        </button>
      </div>
      <div class="journal-recommendation-list">
        ${rows}
      </div>
    </section>
  `;
}

function renderRecommendationEditorRow(recommendation = {}) {
  const category = recommendation.category || "other";
  const selectedRating = Number(recommendation.rating) || 0;
  const categoryOptions = RECOMMENDATION_CATEGORIES.map(([value, label]) => `
    <option value="${escapeHtml(value)}" ${value === category ? "selected" : ""}>
      ${escapeHtml(label)}
    </option>
  `).join("");
  return `
    <div class="journal-recommendation-row">
      <div class="journal-recommendation-grid">
        <input
          class="journal-recommendation-name"
          type="text"
          maxlength="120"
          placeholder="店家或景點名稱"
          value="${escapeHtml(recommendation.name || "")}"
        >
        <select class="journal-recommendation-category">
          ${categoryOptions}
        </select>
      </div>
      <div class="journal-recommendation-place">
        <button class="journal-pick-place" type="button">
          地圖選取店家/景點
        </button>
        <span class="journal-picked-place">
          ${recommendation.latitude && recommendation.longitude
            ? `${escapeHtml(recommendation.latitude)}, ${escapeHtml(recommendation.longitude)}`
            : "尚未選取地點"}
        </span>
      </div>
      <input
        class="journal-recommendation-address"
        type="hidden"
        value="${escapeHtml(recommendation.address || "")}"
      >
      <input
        class="journal-recommendation-latitude"
        type="hidden"
        value="${escapeHtml(recommendation.latitude || "")}"
      >
      <input
        class="journal-recommendation-longitude"
        type="hidden"
        value="${escapeHtml(recommendation.longitude || "")}"
      >
      <input
        class="journal-recommendation-osm-type"
        type="hidden"
        value="${escapeHtml(recommendation.osm_type || "")}"
      >
      <input
        class="journal-recommendation-osm-id"
        type="hidden"
        value="${escapeHtml(recommendation.osm_id || "")}"
      >
      <input
        class="journal-recommendation-osm-url"
        type="hidden"
        value="${escapeHtml(recommendation.osm_url || "")}"
      >
      <div class="journal-recommendation-rating">
        <span>星號</span>
        <input
          class="journal-recommendation-rating-input"
          type="hidden"
          value="${selectedRating || ""}"
        >
        <div class="journal-star-rating" aria-label="星號等級">
          ${[1, 2, 3, 4, 5].map((rating) => `
            <button
              class="journal-star-button ${rating <= selectedRating ? "is-active" : ""}"
              type="button"
              data-rating="${rating}"
              aria-label="${rating} 星"
            >
              ★
            </button>
          `).join("")}
        </div>
      </div>
      <textarea
        class="journal-recommendation-description"
        maxlength="1000"
        placeholder="推薦原因"
      >${escapeHtml(recommendation.description || "")}</textarea>
      <div class="journal-recommendation-images">
        <input
          class="journal-recommendation-existing-images"
          type="hidden"
          value="${escapeHtml(JSON.stringify(getJournalImageUrls(recommendation)))}"
        >
        <div class="journal-recommendation-image-preview">
          ${renderRecommendationImagePreview(getJournalImageUrls(recommendation))}
        </div>
        <label class="journal-recommendation-image-upload">
          <input
            class="journal-recommendation-image-input"
            type="file"
            accept="image/*"
            multiple
          >
          <span>加入推薦照片</span>
          <small>最多 ${MAX_RECOMMENDATION_IMAGES} 張</small>
        </label>
      </div>
      <div class="journal-recommendation-grid">
        <input
          class="journal-recommendation-map-url"
          type="url"
          maxlength="500"
          placeholder="Google Maps 連結"
          value="${escapeHtml(getRecommendationMapUrl(recommendation))}"
        >
        <button class="journal-remove-recommendation" type="button">
          刪除
        </button>
      </div>
    </div>
  `;
}

function renderRecommendationImagePreview(imageUrls) {
  return imageUrls.map((imageUrl, index) => `
    <figure class="journal-recommendation-image-item">
      <img src="${escapeHtml(imageUrl)}" alt="推薦圖片 ${index + 1}">
      <button
        class="journal-recommendation-image-remove"
        type="button"
        data-image-kind="existing"
        data-image-index="${index}"
        aria-label="移除推薦圖片"
      >
        ×
      </button>
    </figure>
  `).join("");
}

function renderJournalImageEditor(journal) {
  const imageUrls = getJournalImageUrls(journal);
  return `
    <div class="journal-image-editor">
      <input
        class="journal-existing-images"
        type="hidden"
        name="existing_image_urls"
        value="${escapeHtml(JSON.stringify(imageUrls))}"
      >
      <div class="journal-image-preview"></div>
      <label class="journal-image-upload">
        <input
          class="journal-image-input"
          type="file"
          name="images"
          accept="image/*"
          multiple
        >
        <span>加入照片</span>
        <small>最多 ${MAX_JOURNAL_IMAGES} 張，儲存時會自動壓縮</small>
      </label>
    </div>
  `;
}

function buildJournalForm(castle, travelDate = null) {
  const journal = travelDate
    ? getJournalForCastleDate(castle.id, travelDate)
    : getDefaultJournal(castle.id);
  return `
    <form class="journal-form" data-loaded-travel-date="${escapeHtml(journal.travel_date)}">
      <label class="journal-visited">
        <input
          type="checkbox"
          name="visited"
          ${journal.visited ? "checked" : ""}
        >
        已去過
      </label>
      <div class="journal-field">
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
            aria-expanded="false"
            title="快速選擇旅遊日期"
          ></button>
          <button class="journal-new-date-button" type="button">
            新日期
          </button>
          <button class="journal-save" type="submit">
            儲存筆記
          </button>
        </div>
        <div class="journal-calendar" hidden></div>
      </div>
      <div class="journal-composer">
        <textarea
          class="journal-text"
          name="journal_text"
          maxlength="5000"
          placeholder="這趟攻城有什麼值得記下來？"
        >${escapeHtml(journal.journal_text)}</textarea>
        ${renderJournalImageEditor(journal)}
      </div>
      ${renderRecommendationEditor(journal)}
      <div class="journal-message"></div>
    </form>
  `;
}

function buildPopupShell(castle, content) {
  return `
    <div class="castle-popup" data-castle-id="${castle.id}">
      ${buildCastlePanelHeader(castle)}
      ${content}
    </div>
  `;
}

function buildCastlePanelHeader(castle, options = {}) {
  const showTitle = options.showTitle ?? true;
  const wikipediaUrl = buildWikipediaUrl(castle);
  const displayName = escapeHtml(getCastleDisplayName(castle));
  const castleNameMarkup = castle.official_url
    ? `
      <a
        class="castle-popup-title"
        href="${escapeHtml(castle.official_url)}"
        target="_blank"
        rel="noopener noreferrer"
        title="開啟 ${escapeHtml(castle.name)} 的官方介紹頁"
      >
        ${displayName}
      </a>
    `
    : `<strong class="castle-popup-title">${displayName}</strong>`;
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
    ${imageMarkup}
    ${showTitle ? castleNameMarkup : ""}
    <span>${escapeHtml(castle.address)}</span>
  `;
}

function renderJournalSideTitle(castle) {
  const displayName = escapeHtml(getCastleDisplayName(castle));
  if (!castle.official_url) {
    return displayName;
  }
  return `
    <a
      class="journal-side-title-link"
      href="${escapeHtml(castle.official_url)}"
      target="_blank"
      rel="noopener noreferrer"
      title="開啟 ${escapeHtml(castle.name)} 的官方介紹頁"
    >
      ${displayName}
    </a>
  `;
}

function renderPopupActions(castle, options = {}) {
  const showRecordsButton = options.showRecordsButton ?? true;
  const showJournalButton = (
    (options.showJournalButton ?? true)
    && currentAuth.authenticated
  );
  return `
    <div class="popup-actions">
      ${showRecordsButton ? `
        <button class="popup-action-button show-castle-records" type="button">
          顯示最新紀錄
        </button>
      ` : ""}
      ${showJournalButton ? `
        <button class="popup-action-button show-journal-form" type="button">
          輸入筆記
        </button>
      ` : ""}
      <a
        class="popup-action-button"
        href="${escapeHtml(buildCastleJournalPageUrl(castle.id))}"
        target="_blank"
        rel="noopener noreferrer"
      >
        觀看所有紀錄
      </a>
    </div>
  `;
}

function buildPopupActions(castle) {
  return buildPopupShell(castle, renderPopupActions(castle));
}

function buildPopupRecords(castle) {
  return buildPopupShell(
    castle,
    '<div class="popup-record-list">載入中</div>',
  );
}

function buildPopupForm(castle) {
  return buildPopupShell(
    castle,
    `${renderPopupActions(castle, { showJournalButton: false })}${buildJournalForm(castle)}`,
  );
}

function buildPopupFormForDate(castle, travelDate) {
  return buildPopupShell(
    castle,
    `${renderPopupActions(castle, { showJournalButton: false })}${buildJournalForm(castle, travelDate)}`,
  );
}

function buildPopup(castle) {
  if (viewedAccount) {
    return buildPopupShell(
      castle,
      renderCastleRecords(getViewedAccountJournalsForCastle(castle.id)),
    );
  }
  if (currentAuth.authenticated) {
    return buildPopupForm(castle);
  }
  return buildPopupRecords(castle);
}

function renderCastleRecords(records) {
  if (records.length === 0) {
    return '<div class="popup-record-list">尚無筆記紀錄</div>';
  }

  const items = records.map((record, index) => `
    <article class="popup-record is-collapsible">
      <button
        class="popup-record-summary"
        type="button"
        aria-expanded="false"
        data-record-index="${index}"
      >
        <span class="popup-record-meta">
          ${escapeHtml(record.user_display_name)}
          ・旅遊日期 ${escapeHtml(record.travel_date)}
        </span>
        <span class="popup-record-summary-text">
          ${escapeHtml(record.journal_text || "尚未填寫筆記內容")}
        </span>
      </button>
      <div class="popup-record-details" hidden>
        <div class="popup-record-meta">
          更新 ${escapeHtml(formatUpdatedAt(record.updated_at))}
        </div>
        <div class="popup-record-text">
          ${escapeHtml(record.journal_text || "尚未填寫筆記內容")}
        </div>
        ${renderJournalImages(getJournalImageUrls(record), "popup-record-images")}
      </div>
    </article>
  `);
  return `<div class="popup-record-list is-single-column">${items.join("")}</div>`;
}

function renderJournalSideRecords(records) {
  if (records.length === 0) {
    return '<div class="activity-empty">尚無筆記紀錄</div>';
  }

  return records.map((record) => `
    <article class="popup-record is-expanded">
      <div class="popup-record-meta">
        ${escapeHtml(record.user_display_name || currentAuth.user?.display_name || "旅人")}
        ・旅遊日期 ${escapeHtml(record.travel_date || "")}
      </div>
      <div class="popup-record-meta">
        ${record.updated_at ? `更新 ${escapeHtml(formatUpdatedAt(record.updated_at))}` : ""}
      </div>
      <div class="popup-record-text">
        ${escapeHtml(record.journal_text || "尚未填寫筆記內容")}
      </div>
      ${renderJournalImages(getJournalImageUrls(record), "popup-record-images")}
    </article>
  `).join("");
}

function centerCastleOnMap(castleId) {
  const castle = castleById.get(castleId);
  if (!castle) {
    return;
  }
  ensureCastleMarkerVisible(castleId);
  showSelectedCastleLabel(castleId);
  map.closePopup();
  map.setView(
    [castle.latitude, castle.longitude],
    Math.max(map.getZoom(), 7),
    { animate: true },
  );
}

function openJournalSidePanel(castle, records, subtitle = "") {
  journalSideTitle.innerHTML = renderJournalSideTitle(castle);
  journalSideSubtitle.textContent = subtitle;
  journalSideContent.innerHTML = `
    <div class="castle-popup" data-castle-id="${castle.id}">
      ${buildCastlePanelHeader(castle, { showTitle: false })}
      ${renderPopupActions(castle, { showRecordsButton: false })}
      ${renderJournalSideRecords(records)}
    </div>
  `;
  mapViewState.showJournalSidePanel = true;
  syncMapViewControls();
}

function openJournalFormSidePanel(castleId) {
  const castle = castleById.get(castleId);
  if (!castle) {
    return;
  }

  centerCastleOnMap(castleId);
  journalSideTitle.innerHTML = renderJournalSideTitle(castle);
  journalSideSubtitle.textContent = "輸入筆記";
  journalSideContent.innerHTML = `
    <div class="castle-popup" data-castle-id="${castle.id}">
      ${buildCastlePanelHeader(castle, { showTitle: false })}
      ${renderPopupActions(castle, { showJournalButton: false })}
      ${buildJournalForm(castle)}
    </div>
  `;
  mapViewState.showJournalSidePanel = true;
  syncMapViewControls();
  const form = journalSideContent.querySelector(".journal-form");
  if (form) {
    syncJournalImagePreview(form);
  }
}

async function openCastleJournalsSidePanel(castleId, travelDate = null) {
  const castle = castleById.get(castleId);
  if (!castle) {
    return;
  }

  centerCastleOnMap(castleId);
  journalSideTitle.innerHTML = renderJournalSideTitle(castle);
  journalSideSubtitle.textContent = travelDate
    ? `旅遊日期 ${travelDate}`
    : "";
  journalSideContent.innerHTML = '<div class="activity-empty">載入中</div>';
  mapViewState.showJournalSidePanel = true;
  syncMapViewControls();

  const payload = await requestJson(`/api/v1/journals/castles/${castleId}`);
  let records = payload.data?.records ?? [];
  if (travelDate) {
    records = records.filter((record) => record.travel_date === travelDate);
  } else {
    records = records.slice(0, 3);
  }
  openJournalSidePanel(
    castle,
    records,
    travelDate ? `旅遊日期 ${travelDate}` : "",
  );
}

function openMyJournalSidePanel(castleId, travelDate) {
  const castle = castleById.get(castleId);
  if (!castle) {
    return;
  }

  const records = getJournalsForCastle(castleId)
    .filter((journal) => journal.travel_date === travelDate)
    .map((journal) => ({
      ...journal,
      user_display_name: currentAuth.user?.display_name || "我",
    }));
  centerCastleOnMap(castleId);
  openJournalSidePanel(castle, records, `旅遊日期 ${travelDate}`);
}

function positionCastlePopupBesideMarker(castleId) {
  const castle = castleById.get(castleId);
  const marker = markerByCastleId.get(castleId);
  if (!castle || !marker) {
    return;
  }

  const nextZoom = Math.max(map.getZoom(), 7);
  const markerPoint = map.project([castle.latitude, castle.longitude], nextZoom);
  const mapSize = map.getSize();
  const desiredPoint = L.point(mapSize.x * 0.43, mapSize.y * 0.3);
  const centerPoint = markerPoint
    .subtract(desiredPoint)
    .add(mapSize.divideBy(2));
  map.setView(map.unproject(centerPoint, nextZoom), nextZoom, { animate: false });
}

function updateOpenPopupArrow(castleId) {
  const marker = markerByCastleId.get(castleId);
  const popupElement = marker?.getPopup()?.getElement();
  const popupWrapper = popupElement?.querySelector(".leaflet-popup-content-wrapper");
  if (!marker || !popupWrapper) {
    return;
  }

  popupWrapper.style.setProperty("--popup-arrow-y", `${POPUP_ARROW_Y}px`);
}

function alignOpenPopupToRight(castleId) {
  const marker = markerByCastleId.get(castleId);
  const popupElement = marker?.getPopup()?.getElement();
  const popupWrapper = popupElement?.querySelector(".leaflet-popup-content-wrapper");
  if (!marker || !popupElement || !popupWrapper) {
    return;
  }

  popupElement.style.translate = "0 0";
  popupWrapper.style.setProperty("--popup-arrow-y", `${POPUP_ARROW_Y}px`);

  const markerPoint = map.latLngToContainerPoint(marker.getLatLng());
  const mapRect = map.getContainer().getBoundingClientRect();
  const wrapperRect = popupWrapper.getBoundingClientRect();
  const markerViewportX = mapRect.left + markerPoint.x;
  const markerViewportY = mapRect.top + markerPoint.y;
  const targetLeft = markerViewportX + POPUP_LEFT_GAP;
  const targetTop = markerViewportY - POPUP_ARROW_Y;
  const horizontalDelta = targetLeft - wrapperRect.left;
  const verticalDelta = targetTop - wrapperRect.top;

  popupElement.style.translate = `${horizontalDelta}px ${verticalDelta}px`;
  updateOpenPopupArrow(castleId);
}

function openMarkerPopupOnRight(castleId) {
  const marker = markerByCastleId.get(castleId);
  if (!marker) {
    return;
  }

  ensureCastleMarkerVisible(castleId);
  positionCastlePopupBesideMarker(castleId);
  marker.openPopup();
  requestAnimationFrame(() => alignOpenPopupToRight(castleId));
  requestAnimationFrame(() => requestAnimationFrame(() => alignOpenPopupToRight(castleId)));
}

function syncPopupRecordOverflow(root = document) {
  root.querySelectorAll(".popup-record").forEach((recordElement) => {
    const textElement = recordElement.querySelector(".popup-record-text");
    const expandButton = recordElement.querySelector(".popup-record-expand");
    if (!textElement || !expandButton) {
      return;
    }

    if (recordElement.classList.contains("is-expanded")) {
      expandButton.hidden = true;
      return;
    }

    expandButton.hidden = textElement.scrollHeight <= textElement.clientHeight + 1;
  });
}

async function showCastleRecords(castleId) {
  const castle = castleById.get(castleId);
  const marker = markerByCastleId.get(castleId);
  if (!castle || !marker) {
    return;
  }

  mapViewState.showJournalSidePanel = false;
  syncMapViewControls();
  ensureCastleMarkerVisible(castleId);
  marker.setPopupContent(buildPopupShell(
    castle,
    `
      ${currentAuth.authenticated ? renderPopupActions(castle) : ""}
      <div class="popup-record-list is-single-column">載入中</div>
    `,
  ));
  openMarkerPopupOnRight(castleId);

  const payload = await requestJson(`/api/v1/journals/castles/${castleId}/latest?limit=1`);
  marker.setPopupContent(buildPopupShell(
    castle,
    `
      ${currentAuth.authenticated ? renderPopupActions(castle) : ""}
      ${renderCastleRecords(payload.data ?? [])}
    `,
  ));
  requestAnimationFrame(() => alignOpenPopupToRight(castleId));
  requestAnimationFrame(() => requestAnimationFrame(() => alignOpenPopupToRight(castleId)));
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
  const form = marker.getPopup().getElement()?.querySelector(".journal-form");
  if (form) {
    syncJournalImagePreview(form);
  }
  requestAnimationFrame(() => alignOpenPopupToRight(castleId));
}

function refreshMarker(castleId) {
  const marker = markerByCastleId.get(castleId);
  const castle = castleById.get(castleId);
  if (!marker || !castle) {
    return;
  }

  marker.setIcon(createCastleIcon(
    isCastleVisited(castleId),
    castle.journal_count,
    castle.castle_series,
  ));
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
  mapViewState.showAccountPrefectureLegend = true;
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
      image_urls: getJournalImageUrls(journal),
      user_display_name: journal.user_display_name,
      updated_at: journal.updated_at,
    });
    journals.sort((left, right) => (
      String(right.travel_date).localeCompare(left.travel_date)
    ));
    viewedAccountJournalByCastleId.set(journal.castle_id, journals);
  });
  refreshAllMarkers();
  syncCastleSeriesFilter();
  refreshAdministrativeAreaStyles();
  syncMapViewControls();
}

function closeAccountMap() {
  viewedAccount = null;
  viewedAccountJournalByCastleId.clear();
  mapViewState.showAccountPrefectureLegend = false;
  setAccountViewBanner();
  refreshAllMarkers();
  syncCastleSeriesFilter();
  refreshAdministrativeAreaStyles();
  syncMapViewControls();
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
          的筆記
        </div>
        <div class="activity-trip-date">
          旅遊日期：${escapeHtml(activity.travel_date)}
        </div>
      <time class="activity-time">${escapeHtml(
    formatUpdatedAt(activity.updated_at),
  )}</time>
      </button>
    `;
    activityList.append(item);
  });
}

function renderPopularCastles() {
  const castles = Array.from(castleById.values())
    .filter(isCastleVisible)
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
          <strong>${escapeHtml(getCastleDisplayName(castle))}</strong>
        </div>
        <div class="popular-count">
          ${escapeHtml(castle.prefecture || "縣市未明")}
          ・${castle.journal_count} 筆筆記
        </div>
      </button>
    `;
    popularList.append(item);
  });
}

function renderMyRecords() {
  const journals = Array.from(journalByCastleId.values())
    .flat()
    .filter((journal) => (
      journal.visited
      || journal.journal_text.trim()
      || getJournalImageUrls(journal).length > 0
    ))
    .sort((left, right) => (
      String(right.travel_date).localeCompare(left.travel_date)
    ));

  myRecordsList.innerHTML = "";
  myRecordsEmpty.hidden = journals.length > 0;

  journals.forEach((journal) => {
    const castle = castleById.get(journal.castle_id);
    if (!castle || !isCastleVisible(castle)) {
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
          <strong>${escapeHtml(getCastleDisplayName(castle))}</strong>
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
  if (!currentAuth.authenticated) {
    mapViewState.showUnvisitedMarkers = true;
  }
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
  journalSidePanel.hidden = !mapViewState.showJournalSidePanel;
  accountPrefectureLegend.hidden = !(
    viewedAccount && mapViewState.showAccountPrefectureLegend
  );
  popularityLegend.hidden = !mapViewState.showPopularityLegend;
  leftToolDrawer.classList.toggle(
    "is-collapsed",
    !mapViewState.showLeftToolDrawer,
  );
  rightRankDrawer.classList.toggle(
    "is-collapsed",
    !mapViewState.showRightRankDrawer,
  );
  toggleLeftToolDrawerButton.setAttribute(
    "aria-expanded",
    String(mapViewState.showLeftToolDrawer),
  );
  toggleRightRankDrawerButton.setAttribute(
    "aria-expanded",
    String(mapViewState.showRightRankDrawer),
  );
  toggleLeftToolDrawerButton.classList.toggle(
    "is-active",
    mapViewState.showLeftToolDrawer,
  );
  toggleRightRankDrawerButton.classList.toggle(
    "is-active",
    mapViewState.showRightRankDrawer,
  );
  toggleCastleLabelsButton.classList.toggle(
    "is-active",
    mapViewState.showCastleLabels,
  );
  toggleRegionColorsButton.classList.toggle(
    "is-active",
    mapViewState.showRegionColors,
  );
  toggleVisitedMarkersButton.classList.toggle(
    "is-active",
    !mapViewState.showUnvisitedMarkers,
  );
  toggleVisitedMarkersButton.disabled = !currentAuth.authenticated;
  toggleVisitedMarkersButton.setAttribute(
    "aria-disabled",
    String(!currentAuth.authenticated),
  );
  togglePopularityLegendButton.classList.toggle(
    "is-active",
    mapViewState.showPopularityLegend,
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
  cycleCastleSeriesFilterButton.classList.toggle(
    "is-active",
    mapViewState.castleSeriesFilter !== "all",
  );
  cycleCastleSeriesFilterButton.textContent = (
    `顯示城堡：${getCastleSeriesFilterLabel()}`
  );
  refreshAdministrativeAreaStyles();
  syncCastleSeriesFilter();
}

function getCastleSeriesFilterLabel() {
  if (mapViewState.castleSeriesFilter === "original") {
    return "100城";
  }
  if (mapViewState.castleSeriesFilter === "continued") {
    return "續100城";
  }
  return "全部";
}

function syncCastleSeriesFilter() {
  castleById.forEach((castle) => {
    const marker = markerByCastleId.get(castle.id);
    if (!marker) {
      return;
    }
    if (isCastleVisible(castle)) {
      if (!markerGroup.hasLayer(marker)) {
        marker.addTo(markerGroup);
      }
    } else if (markerGroup.hasLayer(marker)) {
      markerGroup.removeLayer(marker);
    }
  });
  renderPopularCastles();
  renderMyRecords();
}

function ensureCastleMarkerVisible(castleId) {
  const marker = markerByCastleId.get(castleId);
  if (marker && !markerGroup.hasLayer(marker)) {
    marker.addTo(markerGroup);
  }
}

function showSelectedCastleLabel(castleId) {
  if (selectedCastleLabelId !== null && selectedCastleLabelId !== castleId) {
    markerByCastleId
      .get(selectedCastleLabelId)
      ?.getTooltip()
      ?.getElement()
      ?.classList.remove("is-selected-castle-label");
  }

  selectedCastleLabelId = castleId;
  const marker = markerByCastleId.get(castleId);
  marker?.openTooltip();
  marker
    ?.getTooltip()
    ?.getElement()
    ?.classList.add("is-selected-castle-label");
}

function closeFloatingPanels() {
  mapViewState.showActivityPanel = false;
  mapViewState.showPopularPanel = false;
  mapViewState.showMyRecordsPanel = false;
  mapViewState.showAccountRankingPanel = false;
  mapViewState.showJournalSidePanel = false;
  mapViewState.showPopularityLegend = false;
}

function closeSideListPanels() {
  mapViewState.showActivityPanel = false;
  mapViewState.showPopularPanel = false;
  mapViewState.showMyRecordsPanel = false;
  mapViewState.showAccountRankingPanel = false;
}

function closeSideListPanelsExcept(panelName) {
  if (panelName !== "activity") {
    mapViewState.showActivityPanel = false;
  }
  if (panelName !== "popular") {
    mapViewState.showPopularPanel = false;
  }
  if (panelName !== "myRecords") {
    mapViewState.showMyRecordsPanel = false;
  }
  if (panelName !== "accountRanking") {
    mapViewState.showAccountRankingPanel = false;
  }
}

function alignSideListPanelToButton(buttonElement) {
  const buttonRect = buttonElement.getBoundingClientRect();
  const topAnchorRect = toggleCastleLabelsButton.getBoundingClientRect();
  const panelLeft = window.innerWidth <= 640
    ? 10
    : Math.min(buttonRect.right + 8, window.innerWidth - 376);
  document.documentElement.style.setProperty(
    "--side-panel-top",
    `${Math.round(topAnchorRect.top)}px`,
  );
  document.documentElement.style.setProperty(
    "--side-panel-left",
    `${Math.max(10, Math.round(panelLeft))}px`,
  );
}

async function requestJson(url, options = {}) {
  const isFormData = options.body instanceof FormData;
  const response = await fetch(url, {
    headers: {
      Accept: "application/json",
      ...(!isFormData ? { "Content-Type": "application/json" } : {}),
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
    syncAuthRankBadge();
    syncMapViewControls();
    return;
  }

  authNameElement.textContent = currentAuth.google_login_enabled
    ? "尚未登入"
    : "尚未設定 Google 登入";
  loginLink.hidden = !currentAuth.google_login_enabled;
  logoutButton.hidden = true;
  syncAuthRankBadge();
  syncMapViewControls();
}

async function loadJournals() {
  journalByCastleId.clear();
  if (!currentAuth.authenticated) {
    syncAuthRankBadge();
    syncMapViewControls();
    return;
  }

  const payload = await requestJson("/api/v1/me/journals");
  payload.data.forEach((journal) => {
    upsertLocalJournal(journal);
  });
  syncAuthRankBadge();
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
        castle.castle_series,
      ),
    });
    marker.bindPopup(buildPopup(castle), {
      className: "castle-leaflet-popup",
      maxWidth: 980,
      minWidth: 360,
      autoPan: false,
    });
    marker.off("click", marker._openPopup, marker);
    marker.on("click", (event) => {
      L.DomEvent.stop(event);
      openCastleJournalsSidePanel(castle.id).catch(() => {
        journalSideTitle.textContent = getCastleDisplayName(castle);
        journalSideSubtitle.textContent = "";
        journalSideContent.innerHTML = '<div class="activity-empty">筆記載入失敗</div>';
        mapViewState.showJournalSidePanel = true;
        syncMapViewControls();
      });
    });
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
    marker.bindTooltip(escapeHtml(getCastleDisplayName(castle)), {
      className: "castle-label",
      direction: "right",
      offset: [12, 0],
      opacity: 0.9,
      permanent: true,
    });
    if (isCastleVisible(castle)) {
      marker.addTo(markerGroup);
    }
    markerByCastleId.set(castle.id, marker);
  });

  syncCastleSeriesFilter();
  map.setView(DEFAULT_MAP_CENTER, DEFAULT_ZOOM);
}

async function loadLatestActivities() {
  const payload = await requestJson("/api/v1/journals/latest?limit=20");
  latestActivities = payload.data ?? [];
  renderActivityList(latestActivities);
}

async function loadJournalStats() {
  try {
    const payload = await requestJsonWithRetry("/api/v1/journals/stats");
    const stats = payload.data;
    journalStatsElement.textContent = (
      `筆記人數 ${stats.journal_user_count} 人・筆記 ${stats.journal_count} 筆`
    );
  } catch {
    const fallbackJournalCount = Array.from(castleById.values()).reduce(
      (total, castle) => total + Number(castle.journal_count || 0),
      0,
    );
    let fallbackUserLabel = "--";
    try {
      const rankingsPayload = await requestJson(
        "/api/v1/journals/accounts/rankings?limit=30",
      );
      const rankings = rankingsPayload.data ?? [];
      fallbackUserLabel = rankings.length >= 30
        ? `${rankings.length}+`
        : String(rankings.length);
    } catch {
      fallbackUserLabel = "--";
    }
    journalStatsElement.textContent = (
      fallbackJournalCount > 0
        ? `筆記人數 ${fallbackUserLabel} 人・筆記 ${fallbackJournalCount} 筆`
        : "筆記統計暫無資料"
    );
  }
}

async function requestJsonWithRetry(url, options = {}, retryCount = 1) {
  try {
    return await requestJson(url, options);
  } catch (error) {
    if (retryCount <= 0) {
      throw error;
    }
    await new Promise((resolve) => {
      window.setTimeout(resolve, 450);
    });
    return requestJsonWithRetry(url, options, retryCount - 1);
  }
}

async function loadAdministrativeAreas() {
  const response = await fetch("/static/data/japan_prefectures.geojson", {
    headers: { Accept: "application/geo+json, application/json" },
  });
  if (!response.ok) {
    throw new Error("Failed to load administrative map.");
  }

  const geojson = await response.json();
  administrativeAreaLayer = L.geoJSON(geojson, {
    style: getAdministrativeAreaStyle,
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
  const formData = new FormData();
  formData.append("visited", String(form.elements.visited.checked));
  formData.append("travel_date", form.elements.travel_date.value);
  formData.append("journal_text", form.elements.journal_text.value);
  formData.append(
    "existing_image_urls",
    form.elements.existing_image_urls.value || "[]",
  );
  const recommendationEntries = readJournalRecommendationEntries(form);
  formData.append(
    "recommendations_json",
    JSON.stringify(recommendationEntries.map((entry) => entry.data)),
  );
  Array.from(form.elements.images.files).forEach((file) => {
    formData.append("images", file);
  });
  recommendationEntries.forEach((entry, index) => {
    Array.from(entry.row.querySelector(".journal-recommendation-image-input").files)
      .forEach((file) => {
        formData.append("recommendation_image_indexes", String(index));
        formData.append("recommendation_images", file);
      });
  });

  const payload = await requestJson(`/api/v1/me/journals/${castleId}`, {
    method: "PUT",
    body: formData,
  });

  upsertLocalJournal(payload.data);
  syncAuthRankBadge();
  refreshMarker(castleId);
  renderMyRecords();
  await loadLatestActivities();
  messageElement.textContent = "已儲存";
  markerByCastleId.get(castleId)?.closePopup();
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

function readExistingImageUrls(form) {
  try {
    const value = JSON.parse(form.elements.existing_image_urls.value || "[]");
    return Array.isArray(value) ? value.filter((item) => typeof item === "string") : [];
  } catch {
    return [];
  }
}

function readJournalRecommendationEntries(form) {
  return Array.from(form.querySelectorAll(".journal-recommendation-row"))
    .map((row) => ({
      row,
      data: {
        name: row.querySelector(".journal-recommendation-name")?.value.trim() || "",
        category: (
          row.querySelector(".journal-recommendation-category")?.value || "other"
        ),
        description: (
          row.querySelector(".journal-recommendation-description")?.value.trim() || ""
        ),
        google_maps_url: (
          row.querySelector(".journal-recommendation-map-url")?.value.trim() || ""
        ),
        existing_image_urls: readRecommendationExistingImageUrls(row),
        address: row.querySelector(".journal-recommendation-address")?.value.trim() || "",
        latitude: row.querySelector(".journal-recommendation-latitude")?.value || "",
        longitude: row.querySelector(".journal-recommendation-longitude")?.value || "",
        osm_type: row.querySelector(".journal-recommendation-osm-type")?.value || "",
        osm_id: row.querySelector(".journal-recommendation-osm-id")?.value || "",
        osm_url: row.querySelector(".journal-recommendation-osm-url")?.value.trim() || "",
        rating: row.querySelector(".journal-recommendation-rating-input")?.value || "",
      },
    }))
    .filter((entry) => (
      entry.data.name
      || entry.data.description
      || entry.data.google_maps_url
      || entry.data.osm_url
      || entry.data.existing_image_urls.length > 0
      || entry.row.querySelector(".journal-recommendation-image-input").files.length > 0
    ));
}

function readRecommendationExistingImageUrls(row) {
  try {
    const value = JSON.parse(
      row.querySelector(".journal-recommendation-existing-images")?.value || "[]",
    );
    return Array.isArray(value) ? value.filter((item) => typeof item === "string") : [];
  } catch {
    return [];
  }
}

function isJournalFormDirty(form, castleId) {
  const loadedTravelDate = form.dataset.loadedTravelDate || form.elements.travel_date.value;
  const loadedJournal = getJournalForCastleDate(castleId, loadedTravelDate);
  const currentRecommendations = readJournalRecommendationEntries(form).map(
    (entry) => entry.data,
  );

  return (
    form.elements.visited.checked !== Boolean(loadedJournal.visited)
    || form.elements.journal_text.value !== loadedJournal.journal_text
    || JSON.stringify(readExistingImageUrls(form)) !== JSON.stringify(
      getJournalImageUrls(loadedJournal),
    )
    || form.elements.images.files.length > 0
    || JSON.stringify(currentRecommendations) !== JSON.stringify(
      getJournalRecommendations(loadedJournal).map((recommendation) => ({
        name: recommendation.name || "",
        category: recommendation.category || "other",
        description: recommendation.description || "",
        google_maps_url: getRecommendationMapUrl(recommendation),
        existing_image_urls: getJournalImageUrls(recommendation),
        address: recommendation.address || "",
        latitude: recommendation.latitude || "",
        longitude: recommendation.longitude || "",
        osm_type: recommendation.osm_type || "",
        osm_id: recommendation.osm_id || "",
        osm_url: recommendation.osm_url || "",
        rating: recommendation.rating ? String(recommendation.rating) : "",
      })),
    )
  );
}

function loadJournalIntoForm(form, journal) {
  form.dataset.loadedTravelDate = journal.travel_date;
  form.elements.travel_date.value = journal.travel_date;
  form.elements.visited.checked = journal.visited;
  form.elements.journal_text.value = journal.journal_text;
  setExistingImageUrls(form, getJournalImageUrls(journal));
  syncRecommendationEditor(form, getJournalRecommendations(journal));
  form.elements.images.value = "";
  syncJournalImagePreview(form);
}

function resetJournalFormForNewDate(form, castleId) {
  loadJournalIntoForm(form, getEmptyJournal(castleId));
  form.querySelector(".journal-message").textContent = "已清空，請選擇新的旅遊日期";
}

function syncJournalDate(form, castleId, travelDate) {
  if (isJournalFormDirty(form, castleId)) {
    return;
  }
  loadJournalIntoForm(form, getJournalForCastleDate(castleId, travelDate));
}

function markJournalVisited(form) {
  if (form?.elements.visited) {
    form.elements.visited.checked = true;
  }
}

function formatCalendarDate(year, monthIndex, day) {
  const month = String(monthIndex + 1).padStart(2, "0");
  return `${year}-${month}-${String(day).padStart(2, "0")}`;
}

function parseCalendarDate(value) {
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(value || "");
  if (!match) {
    return null;
  }
  const date = new Date(Number(match[1]), Number(match[2]) - 1, Number(match[3]));
  return Number.isNaN(date.getTime()) ? null : date;
}

function renderJournalCalendar(calendar, year, monthIndex) {
  const form = calendar.closest(".journal-form");
  const selectedValue = form.elements.travel_date.value;
  const today = new Date();
  const todayValue = formatCalendarDate(
    today.getFullYear(),
    today.getMonth(),
    today.getDate(),
  );
  const firstWeekday = new Date(year, monthIndex, 1).getDay();
  const dayCount = new Date(year, monthIndex + 1, 0).getDate();
  const lastYear = today.getFullYear() + 1;
  const yearOptions = [];
  for (let optionYear = lastYear; optionYear >= CALENDAR_FIRST_YEAR; optionYear -= 1) {
    yearOptions.push(
      `<option value="${optionYear}" ${optionYear === year ? "selected" : ""}>${optionYear} 年</option>`,
    );
  }
  const monthOptions = Array.from({ length: 12 }, (_, index) => (
    `<option value="${index}" ${index === monthIndex ? "selected" : ""}>${index + 1} 月</option>`
  ));
  const dayCells = [];
  for (let blank = 0; blank < firstWeekday; blank += 1) {
    dayCells.push('<span class="journal-calendar-blank"></span>');
  }
  for (let day = 1; day <= dayCount; day += 1) {
    const value = formatCalendarDate(year, monthIndex, day);
    const classNames = ["journal-calendar-day"];
    if (value === selectedValue) {
      classNames.push("is-selected");
    }
    if (value === todayValue) {
      classNames.push("is-today");
    }
    dayCells.push(
      `<button class="${classNames.join(" ")}" type="button" data-calendar-date="${value}">${day}</button>`,
    );
  }

  calendar.dataset.year = String(year);
  calendar.dataset.month = String(monthIndex);
  calendar.innerHTML = `
    <div class="journal-calendar-header">
      <button class="journal-calendar-nav" type="button" data-calendar-step="-1" aria-label="上個月">‹</button>
      <select class="journal-calendar-year" aria-label="年">${yearOptions.join("")}</select>
      <select class="journal-calendar-month" aria-label="月">${monthOptions.join("")}</select>
      <button class="journal-calendar-nav" type="button" data-calendar-step="1" aria-label="下個月">›</button>
    </div>
    <div class="journal-calendar-weekdays">
      ${CALENDAR_WEEKDAYS.map((weekday) => `<span>${weekday}</span>`).join("")}
    </div>
    <div class="journal-calendar-days">${dayCells.join("")}</div>
  `;
}

function openJournalCalendar(form) {
  const calendar = form.querySelector(".journal-calendar");
  const selectedDate = parseCalendarDate(form.elements.travel_date.value) ?? new Date();
  renderJournalCalendar(calendar, selectedDate.getFullYear(), selectedDate.getMonth());
  calendar.hidden = false;
  form.querySelector(".journal-date-picker-button").setAttribute("aria-expanded", "true");
}

function closeJournalCalendars(exceptCalendar = null) {
  document.querySelectorAll(".journal-calendar:not([hidden])").forEach((calendar) => {
    if (calendar === exceptCalendar) {
      return;
    }
    calendar.hidden = true;
    calendar
      .closest(".journal-form")
      ?.querySelector(".journal-date-picker-button")
      ?.setAttribute("aria-expanded", "false");
  });
}

function handleJournalCalendarClick(event, calendar) {
  const stepButton = event.target.closest("[data-calendar-step]");
  if (stepButton) {
    const shifted = new Date(
      Number(calendar.dataset.year),
      Number(calendar.dataset.month) + Number(stepButton.dataset.calendarStep),
      1,
    );
    renderJournalCalendar(calendar, shifted.getFullYear(), shifted.getMonth());
    return;
  }

  const dayButton = event.target.closest("[data-calendar-date]");
  if (!dayButton) {
    return;
  }
  const form = calendar.closest(".journal-form");
  const castleId = Number(calendar.closest(".castle-popup").dataset.castleId);
  form.elements.travel_date.value = dayButton.dataset.calendarDate;
  closeJournalCalendars();
  syncJournalDate(form, castleId, dayButton.dataset.calendarDate);
}

function syncRecommendationEditor(form, recommendations) {
  const list = form.querySelector(".journal-recommendation-list");
  if (!list) {
    return;
  }
  list.innerHTML = recommendations.map(renderRecommendationEditorRow).join("");
}

function setRecommendationExistingImageUrls(row, imageUrls) {
  row.querySelector(".journal-recommendation-existing-images").value = (
    JSON.stringify(imageUrls)
  );
}

function syncRecommendationImagePreview(row) {
  const preview = row.querySelector(".journal-recommendation-image-preview");
  const input = row.querySelector(".journal-recommendation-image-input");
  const existingImageUrls = readRecommendationExistingImageUrls(row);
  const selectedFiles = Array.from(input.files);
  const existingItems = renderRecommendationImagePreview(existingImageUrls);
  const newItems = selectedFiles.map((file, index) => `
    <figure class="journal-recommendation-image-item">
      <img src="${escapeHtml(URL.createObjectURL(file))}" alt="新推薦圖片 ${index + 1}">
      <button
        class="journal-recommendation-image-remove"
        type="button"
        data-image-kind="new"
        data-image-index="${index}"
        aria-label="移除推薦圖片"
      >
        ×
      </button>
    </figure>
  `).join("");
  preview.innerHTML = `${existingItems}${newItems}`;
}

function getRecommendationCategoryLabel(category) {
  const match = RECOMMENDATION_CATEGORIES.find(([value]) => value === category);
  return match ? match[1] : "其他";
}

function ensurePoiPicker() {
  let picker = document.querySelector("#poi-picker");
  if (picker) {
    return picker;
  }

  picker = document.createElement("section");
  picker.id = "poi-picker";
  picker.className = "poi-picker";
  picker.hidden = true;
  picker.innerHTML = `
    <div class="poi-picker-backdrop" data-poi-picker-close></div>
    <div class="poi-picker-dialog" role="dialog" aria-modal="true">
      <div class="poi-picker-header">
        <div>
          <h2>選取店家/景點</h2>
          <p class="poi-picker-status">在地圖上點選店家、景點或任一位置</p>
          <div class="poi-picker-radius" aria-label="搜尋半徑">
            ${POI_SEARCH_RADIUS_OPTIONS.map((radius) => `
              <button
                class="poi-radius-button ${radius === DEFAULT_POI_SEARCH_RADIUS_METERS ? "is-active" : ""}"
                type="button"
                data-poi-radius="${radius}"
              >
                ${radius}m
              </button>
            `).join("")}
          </div>
        </div>
        <button
          class="poi-picker-close"
          type="button"
          data-poi-picker-close
          aria-label="關閉選取地點"
        >
          ×
        </button>
      </div>
      <div id="poi-picker-map" class="poi-picker-map"></div>
      <div class="poi-picker-results" hidden>
        <div class="poi-picker-results-list"></div>
      </div>
    </div>
  `;
  document.body.append(picker);
  return picker;
}

function setPoiPickerStatus(message) {
  ensurePoiPicker().querySelector(".poi-picker-status").textContent = message;
}

function loadExternalScript(url) {
  return new Promise((resolve, reject) => {
    const script = document.createElement("script");
    script.src = url;
    script.onload = resolve;
    script.onerror = () => reject(new Error(`無法載入 ${url}`));
    document.head.append(script);
  });
}

let mapLibrePromise = null;

function loadMapLibre() {
  if (!mapLibrePromise) {
    const stylesheet = document.createElement("link");
    stylesheet.rel = "stylesheet";
    stylesheet.href = MAPLIBRE_ASSETS.css;
    document.head.append(stylesheet);
    mapLibrePromise = loadExternalScript(MAPLIBRE_ASSETS.script)
      .then(() => loadExternalScript(MAPLIBRE_ASSETS.leafletBridge));
  }
  return mapLibrePromise;
}

async function fetchStyleWithoutBuildings(layerConfig) {
  const response = await fetch(layerConfig.styleUrl);
  if (!response.ok) {
    throw new Error("無法載入地圖樣式");
  }
  const style = await response.json();
  style.layers = style.layers.filter(
    (layer) => !BUILDING_SOURCE_LAYERS.has(layer["source-layer"]),
  );
  if (layerConfig.useDirectGsiTiles) {
    Object.values(style.sources).forEach((source) => {
      if (source.type === "vector") {
        source.tiles = [GSI_VECTOR_TILE_URL];
      }
    });
  }
  return style;
}

async function createPoiPickerVectorLayers() {
  await loadMapLibre();
  const results = await Promise.allSettled(
    POI_PICKER_VECTOR_LAYERS.map(async (layerConfig) => [
      layerConfig.name,
      L.maplibreGL({
        style: await fetchStyleWithoutBuildings(layerConfig),
        attribution: layerConfig.attribution,
      }),
    ]),
  );
  return results
    .filter((result) => result.status === "fulfilled")
    .map((result) => result.value);
}

async function openPoiPicker(row) {
  const form = row.closest(".journal-form");
  const popupElement = form.closest(".castle-popup");
  const castleId = Number(popupElement.dataset.castleId);
  const castle = castleById.get(castleId);
  if (!castle) {
    return;
  }

  poiPickerState.row = row;
  poiPickerState.searchRadiusMeters = DEFAULT_POI_SEARCH_RADIUS_METERS;
  const picker = ensurePoiPicker();
  picker.hidden = false;
  setPoiPickerStatus("在地圖上點選店家、景點或任一位置");
  syncPoiRadiusButtons();
  renderPoiChoices([]);

  if (!poiPickerState.map) {
    poiPickerState.map = L.map("poi-picker-map", {
      attributionControl: true,
      zoomControl: true,
    });
    poiPickerState.markerLayer = L.layerGroup().addTo(poiPickerState.map);
    poiPickerState.map.on("click", (event) => selectPoiFromMapClick(event.latlng));
    setPoiPickerStatus("地圖載入中");
    const vectorLayers = await createPoiPickerVectorLayers().catch(() => []);
    setPoiPickerStatus("在地圖上點選店家、景點或任一位置");
    const baseLayers = Object.fromEntries([
      ...vectorLayers,
      ...POI_PICKER_BASE_LAYERS.map((layer) => [
        layer.name,
        L.tileLayer(layer.url, layer.options),
      ]),
    ]);
    Object.values(baseLayers)[0].addTo(poiPickerState.map);
    L.control.layers(baseLayers, null, { collapsed: false }).addTo(poiPickerState.map);
  }

  poiPickerState.map.setView([castle.latitude, castle.longitude], 15);
  poiPickerState.markerLayer.clearLayers();
  L.marker([castle.latitude, castle.longitude])
    .bindTooltip(getCastleDisplayName(castle), { permanent: false })
    .addTo(poiPickerState.markerLayer);
  requestAnimationFrame(() => poiPickerState.map.invalidateSize());
}

async function selectPoiFromMapClick(latlng) {
  poiPickerState.clickedLatLng = latlng;
  if (poiPickerState.selectedMarker) {
    poiPickerState.markerLayer.removeLayer(poiPickerState.selectedMarker);
  }
  poiPickerState.selectedMarker = L.marker([latlng.lat, latlng.lng]).addTo(
    poiPickerState.markerLayer,
  );
  searchPoiPlacesAtLatLng(latlng).catch(() => {});
}

async function searchPoiPlacesAtLatLng(latlng) {
  const radius = poiPickerState.searchRadiusMeters;
  setPoiPickerStatus(`搜尋點選位置 ${radius}m 內的 POI`);
  renderPoiChoices([]);

  try {
    const payload = await requestJson(
      `/api/v1/castles/nearby-pois?lat=${encodeURIComponent(latlng.lat)}&lon=${encodeURIComponent(latlng.lng)}&radius_m=${radius}`,
    );
    renderPoiChoices(payload.data ?? []);
    setPoiPickerStatus(
      (payload.data ?? []).length > 0
        ? `找到 ${(payload.data ?? []).length} 個附近地點，依距離排序`
        : `${radius}m 內找不到 POI，可放大半徑或直接使用此座標`,
    );
  } catch (error) {
    renderPoiChoices([]);
    setPoiPickerStatus(error.message || "附近地點載入失敗，可直接使用此座標");
  }
}

function setPoiSearchRadius(radiusMeters) {
  if (!POI_SEARCH_RADIUS_OPTIONS.includes(radiusMeters)) {
    return;
  }
  poiPickerState.searchRadiusMeters = radiusMeters;
  syncPoiRadiusButtons();
  if (poiPickerState.clickedLatLng) {
    searchPoiPlacesAtLatLng(poiPickerState.clickedLatLng).catch(() => {});
    return;
  }
  setPoiPickerStatus("在地圖上點選店家、景點或任一位置");
}

function syncPoiRadiusButtons() {
  const picker = ensurePoiPicker();
  picker.querySelectorAll(".poi-radius-button").forEach((button) => {
    button.classList.toggle(
      "is-active",
      Number(button.dataset.poiRadius) === poiPickerState.searchRadiusMeters,
    );
  });
}

function renderPoiChoices(places) {
  const picker = ensurePoiPicker();
  const results = picker.querySelector(".poi-picker-results");
  const list = picker.querySelector(".poi-picker-results-list");
  if (!poiPickerState.clickedLatLng && places.length === 0) {
    results.hidden = true;
    list.innerHTML = "";
    return;
  }

  const coordinateChoice = poiPickerState.clickedLatLng
    ? `
      <button class="poi-choice-button" type="button" data-poi-choice-index="-1">
        <strong>只使用此座標</strong>
        <span>
          ${poiPickerState.clickedLatLng.lat.toFixed(6)},
          ${poiPickerState.clickedLatLng.lng.toFixed(6)}
        </span>
      </button>
    `
    : "";
  const placeChoices = places.map((place, index) => `
    <button class="poi-choice-button" type="button" data-poi-choice-index="${index}">
      <strong>${escapeHtml(place.name)}</strong>
      <span>
        ${escapeHtml(getRecommendationCategoryLabel(place.category))}
        ・約 ${escapeHtml(place.distance_meters)}m
      </span>
      ${place.address ? `<small>${escapeHtml(place.address)}</small>` : ""}
    </button>
  `).join("");

  results.hidden = false;
  list.dataset.places = JSON.stringify(places);
  list.innerHTML = `${placeChoices}${coordinateChoice}`;
}

function selectPoiChoice(choiceButton) {
  const index = Number(choiceButton.dataset.poiChoiceIndex);
  const places = JSON.parse(
    choiceButton.closest(".poi-picker-results-list").dataset.places || "[]",
  );
  if (index >= 0) {
    selectPoiPlace(places[index], places[index].distance_meters);
    return;
  }

  const latlng = poiPickerState.clickedLatLng;
  if (!latlng) {
    return;
  }
  selectPoiPlace({
    name: "自選地點",
    category: "other",
    latitude: latlng.lat,
    longitude: latlng.lng,
    distance_meters: 0,
    address: "",
    osm_type: "",
    osm_id: "",
    osm_url: `https://www.openstreetmap.org/?mlat=${latlng.lat}&mlon=${latlng.lng}#map=18/${latlng.lat}/${latlng.lng}`,
  });
}

function selectPoiPlace(place, matchDistanceMeters = null) {
  const row = poiPickerState.row;
  if (!row) {
    return;
  }
  row.querySelector(".journal-recommendation-name").value = place.name;
  row.querySelector(".journal-recommendation-category").value = place.category;
  row.querySelector(".journal-recommendation-map-url").value = (
    getGoogleMapsUrl(place.latitude, place.longitude) || place.osm_url
  );
  row.querySelector(".journal-recommendation-address").value = place.address || "";
  row.querySelector(".journal-recommendation-latitude").value = place.latitude;
  row.querySelector(".journal-recommendation-longitude").value = place.longitude;
  row.querySelector(".journal-recommendation-osm-type").value = place.osm_type;
  row.querySelector(".journal-recommendation-osm-id").value = place.osm_id;
  row.querySelector(".journal-recommendation-osm-url").value = place.osm_url;
  row.querySelector(".journal-picked-place").textContent = (
    matchDistanceMeters === null
      ? `${Number(place.latitude).toFixed(6)}, ${Number(place.longitude).toFixed(6)}`
      : `${place.name}・點位旁約 ${Math.round(matchDistanceMeters)}m`
  );
  closePoiPicker();
}

function closePoiPicker() {
  const picker = document.querySelector("#poi-picker");
  if (!picker) {
    return;
  }
  picker.hidden = true;
  poiPickerState.row = null;
  poiPickerState.clickedLatLng = null;
  poiPickerState.searchRadiusMeters = DEFAULT_POI_SEARCH_RADIUS_METERS;
  renderPoiChoices([]);
}

function setExistingImageUrls(form, imageUrls) {
  form.elements.existing_image_urls.value = JSON.stringify(imageUrls);
}

function setSelectedFiles(input, files) {
  const transfer = new DataTransfer();
  files.forEach((file) => transfer.items.add(file));
  input.files = transfer.files;
}

function syncJournalImagePreview(form) {
  const preview = form.querySelector(".journal-image-preview");
  const input = form.elements.images;
  const existingImageUrls = readExistingImageUrls(form);
  const selectedFiles = Array.from(input.files);
  const totalCount = existingImageUrls.length + selectedFiles.length;

  if (totalCount > MAX_JOURNAL_IMAGES) {
    setSelectedFiles(
      input,
      selectedFiles.slice(0, MAX_JOURNAL_IMAGES - existingImageUrls.length),
    );
  }

  const nextFiles = Array.from(input.files);
  const existingItems = existingImageUrls.map((imageUrl, index) => `
    <figure class="journal-image-preview-item">
      <img src="${escapeHtml(imageUrl)}" alt="已上傳筆記圖片">
      <button
        class="journal-image-remove"
        type="button"
        data-image-kind="existing"
        data-image-index="${index}"
        aria-label="移除圖片"
      >×</button>
    </figure>
  `);
  const newItems = nextFiles.map((file, index) => `
    <figure class="journal-image-preview-item">
      <img src="${escapeHtml(URL.createObjectURL(file))}" alt="新筆記圖片預覽">
      <button
        class="journal-image-remove"
        type="button"
        data-image-kind="new"
        data-image-index="${index}"
        aria-label="移除圖片"
      >×</button>
    </figure>
  `);

  preview.innerHTML = [...existingItems, ...newItems].join("");
}

document.addEventListener("click", (event) => {
  const summaryButton = event.target.closest(".popup-record-summary");
  if (!summaryButton) {
    return;
  }

  const recordElement = summaryButton.closest(".popup-record");
  const detailElement = recordElement.querySelector(".popup-record-details");
  const isExpanded = !recordElement.classList.contains("is-expanded");
  recordElement.classList.toggle("is-expanded", isExpanded);
  summaryButton.setAttribute("aria-expanded", String(isExpanded));
  detailElement.hidden = !isExpanded;
  const popupElement = recordElement.closest(".leaflet-popup");
  const castleId = Number(recordElement.closest(".castle-popup")?.dataset.castleId);
  if (popupElement && castleId) {
    requestAnimationFrame(() => alignOpenPopupToRight(castleId));
  }
});

document.addEventListener("click", (event) => {
  const galleryButton = event.target.closest(".journal-gallery-button");
  if (!galleryButton) {
    return;
  }

  const galleryScope = galleryButton.closest(
    ".popup-record-list, .activity-journal, .castle-journal-reader",
  ) ?? document;
  const galleryButtons = Array.from(
    galleryScope.querySelectorAll(".journal-gallery-button"),
  );
  const imageUrls = galleryButtons.map((button) => button.dataset.imageUrl);
  openJournalGallery(imageUrls, galleryButtons.indexOf(galleryButton));
});

document.addEventListener("click", (event) => {
  const infoModalButton = event.target.closest("[data-info-modal]");
  if (infoModalButton) {
    openSiteInfoModal(infoModalButton.dataset.infoModal);
    return;
  }

  if (event.target.closest("[data-info-modal-close]")) {
    closeSiteInfoModal();
    return;
  }

  if (event.target.closest("[data-gallery-close]")) {
    closeJournalGallery();
    return;
  }

  if (event.target.closest("[data-gallery-prev]")) {
    moveJournalGallery(-1);
    return;
  }

  if (event.target.closest("[data-gallery-next]")) {
    moveJournalGallery(1);
  }
});

document.addEventListener("input", (event) => {
  if (
    event.target.classList.contains("journal-text")
    && event.target.value.trim()
  ) {
    markJournalVisited(event.target.closest(".journal-form"));
  }
});

document.addEventListener("keydown", (event) => {
  if (
    event.key === "Escape"
    && document.querySelector(".journal-calendar:not([hidden])")
  ) {
    closeJournalCalendars();
    return;
  }

  const poiPicker = document.querySelector("#poi-picker");
  if (poiPicker && !poiPicker.hidden && event.key === "Escape") {
    closePoiPicker();
    return;
  }

  if (!siteInfoModal.hidden && event.key === "Escape") {
    closeSiteInfoModal();
    return;
  }

  const gallery = document.querySelector("#journal-gallery");
  if (!gallery || gallery.hidden) {
    return;
  }

  if (event.key === "Escape") {
    closeJournalGallery();
  } else if (event.key === "ArrowLeft") {
    moveJournalGallery(-1);
  } else if (event.key === "ArrowRight") {
    moveJournalGallery(1);
  }
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
  const recommendationImageRemove = event.target.closest(
    ".journal-recommendation-image-remove",
  );
  if (recommendationImageRemove) {
    const row = recommendationImageRemove.closest(".journal-recommendation-row");
    const imageIndex = Number(recommendationImageRemove.dataset.imageIndex);
    if (recommendationImageRemove.dataset.imageKind === "existing") {
      const imageUrls = readRecommendationExistingImageUrls(row);
      imageUrls.splice(imageIndex, 1);
      setRecommendationExistingImageUrls(row, imageUrls);
    } else {
      const input = row.querySelector(".journal-recommendation-image-input");
      const files = Array.from(input.files);
      files.splice(imageIndex, 1);
      setSelectedFiles(input, files);
    }
    syncRecommendationImagePreview(row);
    return;
  }

  const removeButton = event.target.closest(".journal-image-remove");
  if (!removeButton) {
    return;
  }

  const form = removeButton.closest(".journal-form");
  const imageIndex = Number(removeButton.dataset.imageIndex);
  if (removeButton.dataset.imageKind === "existing") {
    const imageUrls = readExistingImageUrls(form);
    imageUrls.splice(imageIndex, 1);
    setExistingImageUrls(form, imageUrls);
  } else {
    const input = form.elements.images;
    const files = Array.from(input.files);
    files.splice(imageIndex, 1);
    setSelectedFiles(input, files);
  }
  syncJournalImagePreview(form);
});

document.addEventListener("click", (event) => {
  const addButton = event.target.closest(".journal-add-recommendation");
  if (addButton) {
    const form = addButton.closest(".journal-form");
    const list = form.querySelector(".journal-recommendation-list");
    list.insertAdjacentHTML("beforeend", renderRecommendationEditorRow());
    return;
  }

  const removeButton = event.target.closest(".journal-remove-recommendation");
  if (!removeButton) {
    return;
  }
  removeButton.closest(".journal-recommendation-row")?.remove();
});

document.addEventListener("click", (event) => {
  const starButton = event.target.closest(".journal-star-button");
  if (!starButton) {
    return;
  }

  const rating = Number(starButton.dataset.rating);
  const row = starButton.closest(".journal-recommendation-row");
  row.querySelector(".journal-recommendation-rating-input").value = rating;
  row.querySelectorAll(".journal-star-button").forEach((button) => {
    button.classList.toggle("is-active", Number(button.dataset.rating) <= rating);
  });
});

document.addEventListener("click", (event) => {
  const poiRadiusButton = event.target.closest(".poi-radius-button");
  if (poiRadiusButton) {
    setPoiSearchRadius(Number(poiRadiusButton.dataset.poiRadius));
    return;
  }

  const poiChoiceButton = event.target.closest(".poi-choice-button");
  if (poiChoiceButton) {
    selectPoiChoice(poiChoiceButton);
    return;
  }

  const pickPlaceButton = event.target.closest(".journal-pick-place");
  if (pickPlaceButton) {
    openPoiPicker(pickPlaceButton.closest(".journal-recommendation-row"));
    return;
  }

  if (event.target.closest("[data-poi-picker-close]")) {
    closePoiPicker();
  }
});

document.addEventListener("click", (event) => {
  const recordsButton = event.target.closest(".show-castle-records");
  if (recordsButton) {
    const popupElement = recordsButton.closest(".castle-popup");
    const castleId = Number(popupElement.dataset.castleId);
    if (recordsButton.closest("#journal-side-panel")) {
      openCastleJournalsSidePanel(castleId).catch(() => {
        journalSideContent.innerHTML = '<div class="activity-empty">筆記載入失敗</div>';
      });
      return;
    }
    showCastleRecords(castleId).catch(() => {});
    return;
  }

  const formButton = event.target.closest(".show-journal-form");
  if (formButton) {
    const popupElement = formButton.closest(".castle-popup");
    const castleId = Number(popupElement.dataset.castleId);
    if (formButton.closest("#journal-side-panel")) {
      openJournalFormSidePanel(castleId);
      return;
    }
    showJournalForm(castleId);
  }
});

document.addEventListener("click", (event) => {
  const calendar = event.target.closest(".journal-calendar");
  if (calendar) {
    handleJournalCalendarClick(event, calendar);
    return;
  }

  const pickerButton = event.target.closest(".journal-date-picker-button");
  if (pickerButton) {
    const form = pickerButton.closest(".journal-form");
    const formCalendar = form.querySelector(".journal-calendar");
    closeJournalCalendars(formCalendar);
    if (formCalendar.hidden) {
      openJournalCalendar(form);
    } else {
      closeJournalCalendars();
    }
    return;
  }

  closeJournalCalendars();

  const newDateButton = event.target.closest(".journal-new-date-button");
  if (!newDateButton) {
    return;
  }

  const popupElement = newDateButton.closest(".castle-popup");
  const form = newDateButton.closest(".journal-form");
  resetJournalFormForNewDate(form, Number(popupElement.dataset.castleId));
});

activityList.addEventListener("click", (event) => {
  const button = event.target.closest(".activity-button");
  if (!button) {
    return;
  }

  const castleId = Number(button.dataset.castleId);
  const castle = castleById.get(castleId);
  const activity = latestActivities[Number(button.dataset.activityIndex)];
  if (!castle || !activity) {
    return;
  }
  centerCastleOnMap(castleId);
  openJournalSidePanel(
    castle,
    [activity],
    `旅遊日期 ${activity.travel_date}`,
  );
});

document.addEventListener("change", (event) => {
  if (event.target.classList.contains("journal-recommendation-image-input")) {
    const row = event.target.closest(".journal-recommendation-row");
    const existingImageCount = readRecommendationExistingImageUrls(row).length;
    const selectedFiles = Array.from(event.target.files);
    const availableSlots = MAX_RECOMMENDATION_IMAGES - existingImageCount;
    if (selectedFiles.length > availableSlots) {
      setSelectedFiles(event.target, selectedFiles.slice(0, availableSlots));
      row.closest(".journal-form").querySelector(".journal-message").textContent = (
        `推薦圖片最多 ${MAX_RECOMMENDATION_IMAGES} 張`
      );
    }
    syncRecommendationImagePreview(row);
    return;
  }

  if (event.target.classList.contains("journal-image-input")) {
    const form = event.target.closest(".journal-form");
    const existingImageCount = readExistingImageUrls(form).length;
    const selectedFiles = Array.from(event.target.files);
    const availableSlots = MAX_JOURNAL_IMAGES - existingImageCount;
    if (selectedFiles.length > availableSlots) {
      setSelectedFiles(event.target, selectedFiles.slice(0, availableSlots));
      form.querySelector(".journal-message").textContent = (
        `筆記圖片最多 ${MAX_JOURNAL_IMAGES} 張`
      );
    }
    if (form.elements.images.files.length > 0) {
      markJournalVisited(form);
    }
    syncJournalImagePreview(form);
    return;
  }

  if (
    event.target.classList.contains("journal-calendar-year")
    || event.target.classList.contains("journal-calendar-month")
  ) {
    const calendar = event.target.closest(".journal-calendar");
    renderJournalCalendar(
      calendar,
      Number(calendar.querySelector(".journal-calendar-year").value),
      Number(calendar.querySelector(".journal-calendar-month").value),
    );
    return;
  }

  if (!event.target.classList.contains("journal-date")) {
    return;
  }

  const popupElement = event.target.closest(".castle-popup");
  const form = event.target.closest(".journal-form");
  const castleId = Number(popupElement.dataset.castleId);
  syncJournalDate(form, castleId, event.target.value);
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

closeAccountPrefectureLegendButton.addEventListener("click", () => {
  mapViewState.showAccountPrefectureLegend = false;
  syncMapViewControls();
});

toggleLeftToolDrawerButton.addEventListener("click", () => {
  const willCollapse = mapViewState.showLeftToolDrawer;
  mapViewState.showLeftToolDrawer = !mapViewState.showLeftToolDrawer;
  if (willCollapse) {
    closeFloatingPanels();
  }
  syncMapViewControls();
});

toggleRightRankDrawerButton.addEventListener("click", () => {
  mapViewState.showRightRankDrawer = !mapViewState.showRightRankDrawer;
  syncMapViewControls();
});

cycleCastleSeriesFilterButton.addEventListener("click", () => {
  const nextFilterByCurrent = {
    all: "original",
    original: "continued",
    continued: "all",
  };
  mapViewState.castleSeriesFilter = (
    nextFilterByCurrent[mapViewState.castleSeriesFilter] ?? "all"
  );
  mapViewState.showMyRecordsPanel = false;
  closeAccountMap();
  syncMapViewControls();
});

logoutButton.addEventListener("click", async () => {
  await requestJson("/api/v1/auth/logout", { method: "POST" });
  window.location.reload();
});

toggleCastleLabelsButton.addEventListener("click", () => {
  mapViewState.showCastleLabels = !mapViewState.showCastleLabels;
  syncMapViewControls();
});

toggleRegionColorsButton.addEventListener("click", () => {
  mapViewState.showRegionColors = !mapViewState.showRegionColors;
  syncMapViewControls();
});

toggleVisitedMarkersButton.addEventListener("click", () => {
  if (!currentAuth.authenticated) {
    return;
  }
  mapViewState.showUnvisitedMarkers = !mapViewState.showUnvisitedMarkers;
  syncMapViewControls();
});

togglePopularityLegendButton.addEventListener("click", () => {
  mapViewState.showPopularityLegend = !mapViewState.showPopularityLegend;
  syncMapViewControls();
});

toggleActivityPanelButton.addEventListener("click", async () => {
  mapViewState.showActivityPanel = !mapViewState.showActivityPanel;
  if (mapViewState.showActivityPanel) {
    alignSideListPanelToButton(toggleActivityPanelButton);
    closeSideListPanelsExcept("activity");
    mapViewState.showJournalSidePanel = false;
  }
  syncMapViewControls();
  if (mapViewState.showActivityPanel) {
    await loadLatestActivities();
  }
});

togglePopularPanelButton.addEventListener("click", () => {
  mapViewState.showPopularPanel = !mapViewState.showPopularPanel;
  if (mapViewState.showPopularPanel) {
    alignSideListPanelToButton(togglePopularPanelButton);
    closeSideListPanelsExcept("popular");
    mapViewState.showJournalSidePanel = false;
    renderPopularCastles();
  }
  syncMapViewControls();
});

toggleMyRecordsPanelButton.addEventListener("click", () => {
  mapViewState.showMyRecordsPanel = !mapViewState.showMyRecordsPanel;
  if (mapViewState.showMyRecordsPanel) {
    alignSideListPanelToButton(toggleMyRecordsPanelButton);
    closeSideListPanelsExcept("myRecords");
    mapViewState.showJournalSidePanel = false;
    renderMyRecords();
  }
  syncMapViewControls();
});

toggleAccountRankingPanelButton.addEventListener("click", async () => {
  mapViewState.showAccountRankingPanel = !mapViewState.showAccountRankingPanel;
  if (mapViewState.showAccountRankingPanel) {
    closeSideListPanelsExcept("accountRanking");
    mapViewState.showJournalSidePanel = false;
  }
  syncMapViewControls();
  if (mapViewState.showAccountRankingPanel) {
    await loadAccountRankings();
  }
});

closeActivityPanelButton.addEventListener("click", () => {
  mapViewState.showActivityPanel = false;
  syncMapViewControls();
});

closePopularPanelButton.addEventListener("click", () => {
  mapViewState.showPopularPanel = false;
  syncMapViewControls();
});

closeMyRecordsPanelButton.addEventListener("click", () => {
  mapViewState.showMyRecordsPanel = false;
  syncMapViewControls();
});

closeAccountRankingButton.addEventListener("click", () => {
  mapViewState.showAccountRankingPanel = false;
  syncMapViewControls();
});

closeJournalSidePanelButton.addEventListener("click", () => {
  mapViewState.showJournalSidePanel = false;
  syncMapViewControls();
});

function openCastlePopup(
  castleId,
  mode = "default",
  travelDate = null,
  alignRight = false,
) {
  const castle = castleById.get(castleId);
  const marker = markerByCastleId.get(castleId);
  if (!castle || !marker) {
    return;
  }

  if (alignRight) {
    if (mode === "default") {
      marker.setPopupContent(buildPopup(castle));
    }
    openMarkerPopupOnRight(castleId);
  } else {
    if (mode === "default") {
      marker.setPopupContent(buildPopup(castle));
    }
    map.setView([castle.latitude, castle.longitude], Math.max(map.getZoom(), 7));
    marker.openPopup();
  }
  if (mode === "edit") {
    showJournalForm(castleId, travelDate);
  }
}

popularList.addEventListener("click", (event) => {
  const button = event.target.closest(".popular-button");
  if (!button) {
    return;
  }

  openCastleJournalsSidePanel(Number(button.dataset.castleId)).catch(() => {
    journalSideContent.innerHTML = '<div class="activity-empty">筆記載入失敗</div>';
  });
});

myRecordsList.addEventListener("click", (event) => {
  const button = event.target.closest(".my-record-button");
  if (!button) {
    return;
  }
  openMyJournalSidePanel(
    Number(button.dataset.castleId),
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
  renderAccountPrefectureLegend();
  await loadAuth();
  await loadJournals();
  await loadAdministrativeAreas();
  await loadCastles();
  await loadJournalStats();
  renderMyRecords();
  await loadLatestActivities();
}

initialize().catch(() => {
  countElement.hidden = false;
  countElement.textContent = "載入失敗";
});
