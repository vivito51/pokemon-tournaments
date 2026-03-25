"use client";

import { useEffect, useState } from "react";

import DayEventsModal from "@/app/components/DayEventsModal";
import EventModal from "@/app/components/EventModal";
import EventsCalendar from "@/app/components/EventsCalendar";
import FiltersPanel from "@/app/components/FiltersPanel";
import HeroPanel from "@/app/components/HeroPanel";
import WeeklyLeagueScheduleModal from "@/app/components/WeeklyLeagueScheduleModal";
import {
  API_BASE_URL,
  GAME_OPTIONS,
  INITIAL_FILTERS,
  buildStoreColorMap,
  deriveStores,
  filterRawEvents,
  formatCalendarEvent,
  getHistoryModalState,
  getDataMode,
  parseEventsPayload,
  STATIC_EVENTS_PATH,
} from "@/app/lib/events";

export default function Home() {
  const dataMode = getDataMode();
  const [rawEvents, setRawEvents] = useState([]);
  const [events, setEvents] = useState([]);
  const [stores, setStores] = useState([]);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [selectedDate, setSelectedDate] = useState(null);
  const [game, setGame] = useState("tcg");
  const [store, setStore] = useState("");
  const [filters, setFilters] = useState(INITIAL_FILTERS);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [updatedAt, setUpdatedAt] = useState(null);
  const [isWeeklyScheduleOpen, setIsWeeklyScheduleOpen] = useState(false);

  useEffect(() => {
    const handlePopState = () => {
      const modalState = getHistoryModalState();

      setIsWeeklyScheduleOpen(modalState === "weekly-schedule");

      if (modalState === "day-events") {
        setSelectedEvent(null);
        return;
      }

      setSelectedEvent(null);
      setSelectedDate(null);
    };

    window.addEventListener("popstate", handlePopState);

    return () => window.removeEventListener("popstate", handlePopState);
  }, []);

  useEffect(() => {
    const controller = new AbortController();

    async function loadInitialData() {
      setLoading(true);
      setError("");

      try {
        const targetUrl =
          dataMode === "api" ? `${API_BASE_URL}/events` : STATIC_EVENTS_PATH;

        const response = await fetch(targetUrl, {
          signal: controller.signal,
        });

        if (!response.ok) {
          throw new Error("No se pudieron cargar los eventos.");
        }

        const payload = parseEventsPayload(await response.json());
        setRawEvents(payload.events);
        setStores(deriveStores(payload.events));
        setUpdatedAt(payload.updatedAt);
      } catch (fetchError) {
        if (fetchError.name !== "AbortError") {
          setError(
            dataMode === "api"
              ? "No se pudieron cargar los eventos. Comprueba que el backend este activo."
              : "No se pudieron cargar los datos publicados del calendario.",
          );
          setRawEvents([]);
          setEvents([]);
          setStores([]);
          setUpdatedAt(null);
        }
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    }

    loadInitialData();

    return () => controller.abort();
  }, [dataMode]);

  useEffect(() => {
    const filteredEvents = filterRawEvents(rawEvents, { game, filters, store });
    const colorMap = buildStoreColorMap(filteredEvents);
    setEvents(filteredEvents.map((event) => formatCalendarEvent(event, colorMap)));
  }, [filters, game, rawEvents, store]);

  const updateModalHistory = (modal, { stack = false } = {}) => {
    const currentState = getHistoryModalState();

    if (!currentState || stack) {
      window.history.pushState({ modal }, "");
      return;
    }

    window.history.replaceState({ modal }, "");
  };

  const openSelectedDate = (date) => {
    setIsWeeklyScheduleOpen(false);
    setSelectedEvent(null);
    setSelectedDate(date);
    updateModalHistory("day-events");
  };

  const openSelectedEvent = (event, { preserveDay = false } = {}) => {
    setIsWeeklyScheduleOpen(false);
    const isDayModalOpen = getHistoryModalState() === "day-events" && selectedDate;

    setSelectedEvent(event);

    if (!preserveDay) {
      setSelectedDate(null);
    }

    updateModalHistory("event", { stack: Boolean(preserveDay && isDayModalOpen) });
  };

  const closeSelectedDate = () => {
    if (getHistoryModalState() === "day-events") {
      window.history.back();
      return;
    }

    setSelectedDate(null);
  };

  const closeSelectedEvent = () => {
    if (getHistoryModalState() === "event") {
      window.history.back();
      return;
    }

    setSelectedEvent(null);
  };

  const openWeeklySchedule = () => {
    setSelectedEvent(null);
    setSelectedDate(null);
    setIsWeeklyScheduleOpen(true);
    updateModalHistory("weekly-schedule");
  };

  const closeWeeklySchedule = () => {
    if (getHistoryModalState() === "weekly-schedule") {
      window.history.back();
      return;
    }

    setIsWeeklyScheduleOpen(false);
  };

  const selectedDayEvents = selectedDate
    ? events
        .filter((event) => event.start.startsWith(selectedDate))
        .sort((a, b) => new Date(a.start) - new Date(b.start))
    : [];

  return (
    <main className="app-shell min-h-screen px-4 py-5 text-white sm:px-6 lg:px-8">
      <div className="mx-auto flex max-w-7xl flex-col gap-4 lg:gap-5">
        <HeroPanel />

        <section className="panel calendar-panel rounded-[30px] border border-white/10 p-4 sm:p-5 lg:p-6">
          <FiltersPanel
            error={error}
            filters={filters}
            game={game}
            gameOptions={GAME_OPTIONS}
            loading={loading}
            onOpenWeeklySchedule={openWeeklySchedule}
            updatedAt={updatedAt}
            setFilters={setFilters}
            setGame={setGame}
            setStore={setStore}
            store={store}
            stores={stores}
          />

          <EventsCalendar
            events={events}
            onDateSelect={openSelectedDate}
            onEventSelect={openSelectedEvent}
          />
        </section>

        <footer className="site-credit px-1 pb-2 text-center">
          <p className="site-credit-text">
            Developed by <span className="site-credit-brand">Get Vicented</span>
          </p>
        </footer>
      </div>

      <EventModal
        game={game}
        onClose={closeSelectedEvent}
        selectedEvent={selectedEvent}
      />

      <DayEventsModal
        game={game}
        onClose={closeSelectedDate}
        onEventSelect={(event) => openSelectedEvent(event, { preserveDay: true })}
        selectedDate={selectedEvent ? null : selectedDate}
        selectedDayEvents={selectedDayEvents}
      />

      <WeeklyLeagueScheduleModal
        onClose={closeWeeklySchedule}
        open={isWeeklyScheduleOpen}
      />
    </main>
  );
}
