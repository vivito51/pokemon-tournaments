"use client";

import { formatLongDate, TYPE_SYMBOLS } from "@/app/lib/events";

export default function EventModal({ game, selectedEvent, onClose }) {
  if (!selectedEvent) {
    return null;
  }

  return (
    <div
      className="modal-backdrop fixed inset-0 z-50 flex items-center justify-center bg-black/75 p-5"
      onClick={onClose}
    >
      <div
        className="panel modal-panel event-modal-sheet max-h-[90vh] w-full max-w-lg overflow-y-auto rounded-[28px] border border-white/10 p-6"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="min-w-0 flex-1 space-y-3">
            <p className="eyebrow">Detalle del evento</p>
            <h2 className="font-display break-words text-2xl uppercase tracking-[0.08em] text-white">
              {TYPE_SYMBOLS[selectedEvent.type] ?? "•"} {selectedEvent.store}
            </h2>
            <p className="break-words text-sm leading-6 text-zinc-300">{selectedEvent.title}</p>
          </div>
          <button
            type="button"
            className="close-button"
            onClick={onClose}
          >
            ✕
          </button>
        </div>

        <div className="mt-6 grid gap-3 sm:grid-cols-2">
          <div className="info-card">
            <span className="info-label">Hora</span>
            <strong className="info-value">{selectedEvent.time}</strong>
          </div>
          <div className="info-card">
            <span className="info-label">Formato</span>
            <strong className="info-value">
              {(selectedEvent.game ?? game).toUpperCase()} · {selectedEvent.type}
            </strong>
          </div>
        </div>

        <div className="event-modal-divider mt-6 space-y-4 border-t border-white/10 pt-5">
          <p className="text-sm capitalize text-zinc-300">
            {formatLongDate(selectedEvent.date)}
          </p>

          {selectedEvent.address ? (
            <button
              type="button"
              className="map-link break-words text-left"
              onClick={() => {
                const encodedAddress = encodeURIComponent(selectedEvent.address);
                window.open(
                  `https://www.google.com/maps/search/?api=1&query=${encodedAddress}`,
                  "_blank",
                );
              }}
            >
              {selectedEvent.address}
            </button>
          ) : null}
        </div>
      </div>
    </div>
  );
}
