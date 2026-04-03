export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";
export const STATIC_EVENTS_PATH = "/data/events_clean.json";
export const MADRID_TIME_ZONE = "Europe/Madrid";
const LOCAL_MADRID_TYPES = new Set(["Cup", "Challenge"]);

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

export function parseEventsPayload(payload) {
  if (Array.isArray(payload)) {
    return {
      events: payload,
      updatedAt: null,
    };
  }

  return {
    events: payload?.events ?? [],
    updatedAt: payload?.updatedAt ?? null,
  };
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

function parseIsoParts(value) {
  const match = value?.match(
    /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})(?::(\d{2}))?Z?$/,
  );

  if (!match) {
    return null;
  }

  return {
    year: Number(match[1]),
    month: Number(match[2]),
    day: Number(match[3]),
    hour: Number(match[4]),
    minute: Number(match[5]),
    second: Number(match[6] ?? "0"),
  };
}

function getTimeZoneOffsetMinutes(date, timeZone) {
  const timeZoneName = new Intl.DateTimeFormat("en-US", {
    timeZone,
    timeZoneName: "shortOffset",
  })
    .formatToParts(date)
    .find((part) => part.type === "timeZoneName")?.value;

  const match = timeZoneName?.match(/^GMT([+-])(\d{1,2})(?::?(\d{2}))?$/);

  if (!match) {
    return 0;
  }

  const sign = match[1] === "-" ? -1 : 1;
  const hours = Number(match[2]);
  const minutes = Number(match[3] ?? "0");

  return sign * (hours * 60 + minutes);
}

function getMadridDateKey(date) {
  const parts = new Intl.DateTimeFormat("en-CA", {
    timeZone: MADRID_TIME_ZONE,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).formatToParts(date);

  const year = parts.find((part) => part.type === "year")?.value;
  const month = parts.find((part) => part.type === "month")?.value;
  const day = parts.find((part) => part.type === "day")?.value;

  return `${year}-${month}-${day}`;
}

function normalizeEventStart(rawDate, type) {
  if (!rawDate) {
    return "";
  }

  if (!LOCAL_MADRID_TYPES.has(type)) {
    return rawDate;
  }

  const parts = parseIsoParts(rawDate);

  if (!parts) {
    return rawDate;
  }

  const utcGuess = new Date(
    Date.UTC(parts.year, parts.month - 1, parts.day, parts.hour, parts.minute, parts.second),
  );
  const offsetMinutes = getTimeZoneOffsetMinutes(utcGuess, MADRID_TIME_ZONE);
  const correctedDate = new Date(utcGuess.getTime() - offsetMinutes * 60_000);

  return correctedDate.toISOString();
}

export function formatCalendarEvent(event, colorMap) {
  const storeName = normalizeStoreName(event.store);
  const start = normalizeEventStart(event.date, event.type);
  const date = start ? new Date(start) : null;
  const time = date
    ? new Intl.DateTimeFormat("es-ES", {
        timeZone: MADRID_TIME_ZONE,
        hour: "2-digit",
        minute: "2-digit",
        hour12: false,
      }).format(date)
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
      localDateKey: date ? getMadridDateKey(date) : "",
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
    timeZone: MADRID_TIME_ZONE,
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

export function formatLastSync(updatedAt) {
  if (!updatedAt) {
    return "Sincronizado";
  }

  return `Sincronizado por ultima vez a las ${new Date(updatedAt).toLocaleString("es-ES", {
    timeZone: MADRID_TIME_ZONE,
    hour: "2-digit",
    minute: "2-digit",
    day: "numeric",
    month: "long",
    year: "numeric",
  })}`;
}
