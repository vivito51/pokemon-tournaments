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
  formatCalendarEvent,
} from "@/app/lib/events";

export default function Home() {
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

    async function loadStores() {
      try {
        const response = await fetch(`${API_BASE_URL}/stores`, {
          signal: controller.signal,
        });

        if (!response.ok) {
          throw new Error("No se pudieron cargar las tiendas.");
        }

        const data = await response.json();
        setStores(data);
      } catch (fetchError) {
        if (fetchError.name !== "AbortError") {
          setError("No se pudieron cargar las tiendas.");
        }
      }
    }

    loadStores();

    return () => controller.abort();
  }, []);

  useEffect(() => {
    const controller = new AbortController();

    async function loadEvents() {
      setLoading(true);
      setError("");

      try {
        const activeTypes = Object.keys(filters).filter((type) => filters[type]);
        const params = new URLSearchParams({ game });

        if (activeTypes.length) {
          params.set("types", activeTypes.join(","));
        }

        if (store) {
          params.set("store", store);
        }

        const response = await fetch(`${API_BASE_URL}/events?${params.toString()}`, {
          signal: controller.signal,
        });

        if (!response.ok) {
          throw new Error("No se pudieron cargar los eventos.");
        }

        const data = await response.json();
        const colorMap = buildStoreColorMap(data);
        setEvents(data.map((event) => formatCalendarEvent(event, colorMap)));
      } catch (fetchError) {
        if (fetchError.name !== "AbortError") {
          setError(
            "No se pudieron cargar los eventos. Comprueba que el backend este activo.",
          );
          setEvents([]);
        }
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    }

    loadEvents();

    return () => controller.abort();
  }, [filters, game, store]);

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
