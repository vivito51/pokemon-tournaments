"use client";

import { formatLastSync, TYPE_LABELS, TYPE_SYMBOLS } from "@/app/lib/events";

export default function FiltersPanel({
  error,
  filters,
  game,
  gameOptions,
  loading,
  updatedAt,
  setFilters,
  setGame,
  setStore,
  store,
  stores,
}) {
  return (
    <section className="filters-toolbar mb-4 rounded-[24px] border border-white/10 p-4">
      <div className="mb-4 flex flex-col gap-3 xl:flex-row xl:items-end xl:justify-between">
        <div>
          <p className="eyebrow">Panel de filtros</p>
          <h3 className="font-display text-xl uppercase tracking-[0.08em] text-white">
            Ajusta tu vista competitiva
          </h3>
        </div>

        <div className="flex flex-wrap items-center gap-2 text-sm">
          <span
            className={`status-pill ${loading ? "status-pill-live" : "status-pill-idle"}`}
          >
            {loading ? "Actualizando eventos" : formatLastSync(updatedAt)}
          </span>
          {error ? <span className="status-pill status-pill-error">{error}</span> : null}
        </div>
      </div>

      <div className="grid gap-4 min-w-0 xl:grid-cols-[0.40fr_1.35fr_0.95fr] xl:items-start">
        <div className="min-w-0 space-y-3 xl:pr-1">
          <p className="filter-label">Juego</p>
          <div className="filter-chip-row">
            {gameOptions.map((option) => (
              <button
                key={option.value}
                type="button"
                onClick={() => setGame(option.value)}
                className={`filter-chip ${game === option.value ? "filter-chip-active" : ""}`}
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>

        <div className="min-w-0 space-y-3 xl:-ml-0">
          <p className="filter-label">Tipos de evento</p>
          <div className="filter-chip-row">
            {Object.keys(filters).map((type) => (
              <button
                key={type}
                type="button"
                onClick={() =>
                  setFilters((currentFilters) => ({
                    ...currentFilters,
                    [type]: !currentFilters[type],
                  }))
                }
                className={`filter-chip ${filters[type] ? "filter-chip-active" : ""}`}
              >
                <span>{TYPE_SYMBOLS[type] ?? "•"}</span>
                <span>{TYPE_LABELS[type] ?? type}</span>
              </button>
            ))}
          </div>
        </div>

        <label className="min-w-0 space-y-3">
          <span className="filter-label">Tienda</span>
          <select
            value={store}
            onChange={(event) => setStore(event.target.value)}
            className="select-field"
          >
            <option value="">Todas las tiendas</option>
            {stores.map((storeName) => (
              <option key={storeName} value={storeName}>
                {storeName}
              </option>
            ))}
          </select>
        </label>
      </div>
    </section>
  );
}
