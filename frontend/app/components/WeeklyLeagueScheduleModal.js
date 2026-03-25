"use client";

import { WEEKLY_LEAGUE_SCHEDULE } from "@/app/lib/weeklyLeagueSchedule";

function sortEntriesByTime(entries) {
  return [...entries].sort((left, right) => left.time.localeCompare(right.time));
}

export default function WeeklyLeagueScheduleModal({ onClose, open }) {
  if (!open) {
    return null;
  }

  return (
    <div
      className="modal-backdrop fixed inset-0 z-50 flex items-center justify-center bg-black/75 p-5"
      onClick={onClose}
    >
      <div
        className="panel modal-panel weekly-schedule-sheet max-h-[90vh] w-full max-w-7xl overflow-y-auto rounded-[28px] border border-white/10 p-6"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="mb-5 flex flex-wrap items-start justify-between gap-4">
          <div className="min-w-0 flex-1 space-y-2">
            <p className="eyebrow">Ligas semanales</p>
            <h2 className="font-display break-words text-2xl uppercase tracking-[0.08em] text-white">
              Horario fijo de tiendas
            </h2>
            <p className="text-sm text-zinc-400">
              Referencia rapida para las ligas recurrentes que no siempre aparecen con antelacion
              en el calendario oficial.
            </p>
          </div>
          <button
            type="button"
            className="close-button"
            onClick={onClose}
          >
            ✕
          </button>
        </div>

        <div className="hidden md:block">
          <div className="weekly-schedule-columns-wrap">
            <div
              className="weekly-schedule-columns"
              style={{ gridTemplateColumns: "repeat(7, minmax(150px, 1fr))" }}
            >
            {WEEKLY_LEAGUE_SCHEDULE.map((day) => (
              <section
                key={day.day}
                className="weekly-schedule-day-column"
              >
                <div className="weekly-schedule-day-column-header">
                  <h3 className="font-display text-sm uppercase tracking-[0.08em] text-white">
                    {day.day}
                  </h3>
                </div>

                <div className="weekly-schedule-day-column-list">
                  {sortEntriesByTime(day.entries).map((entry) => (
                    <a
                      key={`${day.day}-${entry.store}-${entry.time}`}
                      className="weekly-schedule-column-pill"
                      href={entry.mapUrl}
                      target="_blank"
                      rel="noreferrer"
                    >
                      <span className="weekly-schedule-column-store">{entry.store}</span>
                      <span className="weekly-schedule-column-time">{entry.time}</span>
                    </a>
                  ))}
                </div>
              </section>
            ))}
            </div>
          </div>
        </div>

        <div className="md:hidden">
          <div className="weekly-schedule-grid">
            {WEEKLY_LEAGUE_SCHEDULE.map((day) => (
              <section
                key={day.day}
                className="weekly-schedule-card"
              >
                <div className="weekly-schedule-card-header">
                  <p className="eyebrow">Dia</p>
                  <h3 className="font-display text-lg uppercase tracking-[0.08em] text-white">
                    {day.day}
                  </h3>
                </div>

                <div className="weekly-schedule-list">
                  {sortEntriesByTime(day.entries).map((entry) => (
                    <a
                      key={`${day.day}-${entry.store}-${entry.time}`}
                      className="weekly-schedule-entry"
                      href={entry.mapUrl}
                      target="_blank"
                      rel="noreferrer"
                    >
                      <span className="weekly-schedule-time">{entry.time}</span>
                      <span className="weekly-schedule-store">{entry.store}</span>
                    </a>
                  ))}
                </div>
              </section>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
