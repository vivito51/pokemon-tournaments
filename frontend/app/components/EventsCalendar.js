"use client";

import { useEffect, useState } from "react";

import FullCalendar from "@fullcalendar/react";
import dayGridPlugin from "@fullcalendar/daygrid";
import esLocale from "@fullcalendar/core/locales/es";

import { TYPE_SYMBOLS } from "@/app/lib/events";

function toDateKey(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function startOfWeekMonday(date) {
  const copy = new Date(date);
  copy.setHours(0, 0, 0, 0);
  const day = copy.getDay();
  const diff = day === 0 ? -6 : 1 - day;
  copy.setDate(copy.getDate() + diff);
  return copy;
}

function addDays(date, days) {
  const copy = new Date(date);
  copy.setDate(copy.getDate() + days);
  return copy;
}

function getWeekLabel(weekStart) {
  const weekEnd = addDays(weekStart, 6);
  const formatter = new Intl.DateTimeFormat("es-ES", {
    day: "numeric",
    month: "short",
  });

  return `${formatter.format(weekStart)} - ${formatter.format(weekEnd)}`;
}

function getWeekDays(weekStart) {
  return Array.from({ length: 7 }, (_, index) => {
    const date = addDays(weekStart, index);
    return {
      date,
      dateKey: toDateKey(date),
      label: date.toLocaleDateString("es-ES", {
        weekday: "short",
      }),
      dayNumber: date.getDate(),
    };
  });
}

function getEventsForDate(events, dateKey) {
  return events
    .filter((event) => event.extendedProps.localDateKey === dateKey)
    .sort((a, b) => new Date(a.start) - new Date(b.start));
}

function MobileWeekList({ events, onDateSelect, onEventSelect }) {
  const currentWeekStart = startOfWeekMonday(new Date());
  const [weekStart, setWeekStart] = useState(currentWeekStart);
  const weekDays = getWeekDays(weekStart);
  const isCurrentWeek = toDateKey(weekStart) === toDateKey(currentWeekStart);

  return (
    <div className="mobile-week-board">
      <div className="mobile-week-header">
        <div className="mobile-week-controls">
          <button
            type="button"
            className={`mobile-nav-button ${isCurrentWeek ? "mobile-nav-button-disabled" : ""}`}
            onClick={() => {
              if (!isCurrentWeek) {
                setWeekStart((current) => addDays(current, -7));
              }
            }}
            disabled={isCurrentWeek}
          >
            Anterior
          </button>
          <button
            type="button"
            className="mobile-nav-button mobile-nav-button-current"
            onClick={() => setWeekStart(startOfWeekMonday(new Date()))}
          >
            Hoy
          </button>
          <button
            type="button"
            className="mobile-nav-button"
            onClick={() => setWeekStart((current) => addDays(current, 7))}
          >
            Siguiente
          </button>
        </div>
      </div>

      <div className="mobile-week-label font-display">{getWeekLabel(weekStart)}</div>

      <div className="mobile-week-list">
        {weekDays.map((day) => {
          const dayEvents = getEventsForDate(events, day.dateKey);

          return (
            <button
              key={day.dateKey}
              type="button"
              className="mobile-week-row"
              onClick={() => onDateSelect(day.dateKey)}
            >
              <div className="mobile-week-day">
                <span className="mobile-week-day-label">{day.label}</span>
                <strong className="mobile-week-day-number">{day.dayNumber}</strong>
              </div>

              <div className="mobile-week-events">
                {dayEvents.length ? (
                  dayEvents.map((event, index) => (
                    <button
                      key={`${day.dateKey}-${index}`}
                      type="button"
                      className="mobile-week-event"
                      style={{ borderLeftColor: event.backgroundColor }}
                      onClick={(clickEvent) => {
                        clickEvent.stopPropagation();
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
                      <span className="mobile-week-event-time">
                        {event.extendedProps.time}
                      </span>
                      <span className="mobile-week-event-title">
                        {TYPE_SYMBOLS[event.extendedProps.type] ?? "•"}{" "}
                        {event.extendedProps.store}
                      </span>
                    </button>
                  ))
                ) : (
                  <span className="mobile-week-empty">Sin eventos</span>
                )}
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}

export default function EventsCalendar({ events, onDateSelect, onEventSelect }) {
  const [isMobile, setIsMobile] = useState(false);
  const [mobileView, setMobileView] = useState("weekList");

  useEffect(() => {
    const mediaQuery = window.matchMedia("(max-width: 768px)");

    const syncViewport = (event) => {
      const matches = event.matches ?? mediaQuery.matches;
      setIsMobile(matches);
      setMobileView(matches ? "weekList" : "dayGridMonth");
    };

    syncViewport(mediaQuery);
    mediaQuery.addEventListener("change", syncViewport);

    return () => mediaQuery.removeEventListener("change", syncViewport);
  }, []);

  const activeView = isMobile ? mobileView : "dayGridMonth";

  return (
    <section className="calendar-shell rounded-[26px] border border-white/10 p-3 sm:p-4 lg:p-5">
      {isMobile ? (
        <div className="mobile-calendar-topbar mb-3 flex items-center justify-between gap-3">
          <div className="mobile-view-switcher">
            <button
              type="button"
              className={`mobile-view-button ${
                mobileView === "weekList" ? "mobile-view-button-active" : ""
              }`}
              onClick={() => setMobileView("weekList")}
            >
              Semana
            </button>
            <button
              type="button"
              className={`mobile-view-button ${
                mobileView === "dayGridMonth" ? "mobile-view-button-active" : ""
              }`}
              onClick={() => setMobileView("dayGridMonth")}
            >
              Mes
            </button>
          </div>
        </div>
      ) : null}

      {isMobile && activeView === "weekList" ? (
        <MobileWeekList
          events={events}
          onDateSelect={onDateSelect}
          onEventSelect={onEventSelect}
        />
      ) : (
        <FullCalendar
          key={activeView}
          locale={esLocale}
          plugins={[dayGridPlugin]}
          initialView={activeView}
          events={events}
          headerToolbar={{
            left: "prev,next today",
            center: "title",
            right: "",
          }}
          eventTimeFormat={{ hour: "2-digit", minute: "2-digit", hour12: false }}
          height="auto"
          validRange={{ start: new Date() }}
          dayMaxEventRows={isMobile ? 2 : 3}
          dayCellDidMount={(info) => {
            const today = new Date();
            today.setHours(0, 0, 0, 0);

            info.el.style.cursor = "pointer";
            info.el.onclick = (event) => {
              if (event.target.closest(".fc-event")) {
                return;
              }

              const clickedDate =
                info.el.getAttribute("data-date") ?? info.date.toISOString().slice(0, 10);
              onDateSelect(clickedDate);
            };

            if (info.date < today) {
              info.el.classList.add("past-day");
            }

            if (info.date.toDateString() === today.toDateString()) {
              info.el.classList.add("today-cell");
            }

            if (isMobile) {
              info.el.classList.add("mobile-day-cell");
            }
          }}
          eventDidMount={(info) => {
            info.el.setAttribute("title", info.event.extendedProps.fullTitle || info.event.title);

            const accentColor = info.event.extendedProps.accentColor;
            info.el.style.backgroundColor = accentColor;
            info.el.style.borderColor = accentColor;
          }}
          eventClick={(info) => {
            info.jsEvent.preventDefault();
            info.jsEvent.stopPropagation();

            onEventSelect({
              title: info.event.extendedProps.fullTitle || info.event.title,
              time: info.event.extendedProps.time,
              store: info.event.extendedProps.store,
              type: info.event.extendedProps.type,
              date: info.event.start,
              address: info.event.extendedProps.address,
              game: info.event.extendedProps.game,
            });
          }}
        />
      )}
    </section>
  );
}
