"use client";

import { formatLongDate, TYPE_SYMBOLS } from "@/app/lib/events";

export default function DayEventsModal({
  game,
  onClose,
  onEventSelect,
  selectedDate,
  selectedDayEvents,
}) {
  if (!selectedDate) {
    return null;
  }

  return (
    <div
      className="modal-backdrop fixed inset-0 z-50 flex items-center justify-center bg-black/75 p-5"
      onClick={onClose}
    >
      <div
        className="panel modal-panel day-events-sheet max-h-[90vh] w-full max-w-3xl overflow-y-auto rounded-[28px] border border-white/10 p-6"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="mb-5 flex flex-wrap items-start justify-between gap-4">
          <div className="min-w-0 flex-1 space-y-2">
            <p className="eyebrow">Eventos del dia</p>
            <h2 className="font-display break-words text-2xl uppercase tracking-[0.08em] text-white">
              {formatLongDate(selectedDate)}
            </h2>
            <p className="text-sm text-zinc-400">
              {selectedDayEvents.length} evento(s) programado(s)
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

        {selectedDayEvents.length ? (
          <div className="grid gap-3">
            {selectedDayEvents.map((event, index) => (
              <button
                key={`${event.start}-${index}`}
                type="button"
                className="day-event-card text-left"
                style={{ borderLeftColor: event.backgroundColor }}
                onClick={() => {
                  onEventSelect({
                    title: event.extendedProps.fullTitle || event.title,
                    time: event.extendedProps.time,
                    store: event.extendedProps.store,
                    type: event.extendedProps.type,
                    date: new Date(event.start),
                    address: event.extendedProps.address,
                    game: event.extendedProps.game,
                  });
                }}
              >
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div className="min-w-0 flex-1">
                    <p className="font-display break-words text-lg uppercase tracking-[0.08em] text-white">
                      {TYPE_SYMBOLS[event.extendedProps.type] ?? "•"}{" "}
                      {event.extendedProps.store}
                    </p>
                    <p className="mt-1 break-words text-sm text-zinc-300">
                      {event.extendedProps.time} · {event.extendedProps.type}
                    </p>
                  </div>
                  <span className="text-xs uppercase tracking-[0.24em] text-zinc-500">
                    {(event.extendedProps.game ?? game).toUpperCase()}
                  </span>
                </div>
              </button>
            ))}
          </div>
        ) : (
          <div className="rounded-[24px] border border-dashed border-white/10 bg-white/5 px-6 py-14 text-center text-zinc-400">
            No hay eventos para este dia.
          </div>
        )}
      </div>
    </div>
  );
}
