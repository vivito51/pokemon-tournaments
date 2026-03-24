export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";
export const STATIC_EVENTS_PATH = "/data/events_clean.json";

export const COLOR_PALETTE = [
  "#ef4444",
  "#f87171",
  "#dc2626",
  "#f97316",
  "#fb7185",
  "#b91c1c",
  "#e11d48",
  "#f59e0b",
  "#991b1b",
  "#be123c",
  "#7f1d1d",
  "#ea580c",
  "#fecaca",
];

export const TYPE_SYMBOLS = {
  Cup: "🏆",
  Challenge: "⚡",
  League: "🏅",
  Prerelease: "🎯",
};

export const TYPE_LABELS = {
  Cup: "Cups",
  Challenge: "Challenges",
  League: "Leagues",
  Prerelease: "Prereleases",
};

export const GAME_OPTIONS = [
  { value: "tcg", label: "TCG" },
  { value: "vg", label: "VG" },
];

export const INITIAL_FILTERS = {
  Cup: true,
  Challenge: true,
  League: false,
  Prerelease: false,
};

export function getDataMode() {
  return API_BASE_URL ? "api" : "static";
}

export function normalizeStoreName(storeName) {
  return storeName ? storeName.replace(/\s+S\.L\.?$/i, "").trim() : "";
}

export function getStoreAbbr(storeName) {
  const words = normalizeStoreName(storeName)
    .toUpperCase()
    .split(/\s+/)
    .filter(Boolean);

  if (!words.length) {
    return "EVT";
  }

  if (words.length === 1) {
    return words[0].slice(0, 3);
  }

  return words.map((word) => word[0]).join("").slice(0, 3);
}

export function buildStoreColorMap(rawEvents) {
  const uniqueStores = Array.from(
    new Set(rawEvents.map((event) => normalizeStoreName(event.store)).filter(Boolean)),
  ).sort();

  return Object.fromEntries(
    uniqueStores.map((store, index) => [
      store,
      COLOR_PALETTE[index % COLOR_PALETTE.length],
    ]),
  );
}

export function deriveStores(rawEvents) {
  return Array.from(
    new Set(rawEvents.map((event) => normalizeStoreName(event.store)).filter(Boolean)),
  ).sort();
}

export function filterRawEvents(rawEvents, { game, filters, store }) {
  const activeTypes = Object.keys(filters).filter((type) => filters[type]);

  return rawEvents.filter((event) => {
    if (game && event.game !== game) {
      return false;
    }

    if (activeTypes.length && !activeTypes.includes(event.type)) {
      return false;
    }

    if (store && normalizeStoreName(event.store) !== store) {
      return false;
    }

    return true;
  });
}

export function formatCalendarEvent(event, colorMap) {
  const storeName = normalizeStoreName(event.store);
  const start = event.date?.replace(/Z$/, "") ?? "";
  const date = start ? new Date(start) : null;
  const time = date
    ? `${String(date.getHours()).padStart(2, "0")}:${String(
        date.getMinutes(),
      ).padStart(2, "0")}`
    : "--:--";
  const accentColor = colorMap[storeName] ?? "#ef4444";

  return {
    title: `[${getStoreAbbr(storeName)}] ${TYPE_SYMBOLS[event.type] ?? "•"} ${event.type}`,
    start,
    backgroundColor: accentColor,
    borderColor: accentColor,
    extendedProps: {
      accentColor,
      fullTitle: event.name || `${event.game?.toUpperCase() ?? "POKEMON"} ${event.type}`,
      store: storeName,
      type: event.type,
      time,
      address: event.address,
      game: event.game,
    },
  };
}

export function formatLongDate(value) {
  if (!value) {
    return "";
  }

  return new Date(value).toLocaleDateString("es-ES", {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

export function getHistoryModalState() {
  if (typeof window === "undefined") {
    return null;
  }

  return window.history.state?.modal ?? null;
}
