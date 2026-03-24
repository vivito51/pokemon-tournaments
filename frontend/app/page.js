"use client";

import { useEffect, useState } from "react";

import DayEventsModal from "@/app/components/DayEventsModal";
import EventModal from "@/app/components/EventModal";
import EventsCalendar from "@/app/components/EventsCalendar";
import FiltersPanel from "@/app/components/FiltersPanel";
import HeroPanel from "@/app/components/HeroPanel";
import {
  API_BASE_URL,
  GAME_OPTIONS,
  INITIAL_FILTERS,
  buildStoreColorMap,
  deriveStores,
  filterRawEvents,
  formatCalendarEvent,
  getDataMode,
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

        const data = await response.json();
        setRawEvents(data);
        setStores(deriveStores(data));
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
            setFilters={setFilters}
            setGame={setGame}
            setStore={setStore}
            store={store}
            stores={stores}
          />

          <EventsCalendar
            events={events}
            onDateSelect={setSelectedDate}
            onEventSelect={setSelectedEvent}
          />
        </section>
      </div>

      <EventModal
        game={game}
        selectedEvent={selectedEvent}
        setSelectedEvent={setSelectedEvent}
      />

      <DayEventsModal
        game={game}
        selectedDate={selectedDate}
        selectedDayEvents={selectedDayEvents}
        setSelectedDate={setSelectedDate}
        setSelectedEvent={setSelectedEvent}
      />
    </main>
  );
}
