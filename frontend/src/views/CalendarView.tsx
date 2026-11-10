import React, { useState } from 'react';
import { Calendar as CalendarIcon, Download, ChevronLeft, ChevronRight, MapPin, Clock } from 'lucide-react';
import { EventItem } from '../types';

interface CalendarViewProps {
  events: EventItem[];
  onDownloadIcs: () => void;
  onEventClick: (event: EventItem) => void;
}

export const CalendarView: React.FC<CalendarViewProps> = ({
  events,
  onDownloadIcs,
  onEventClick,
}) => {
  const [selectedDay, setSelectedDay] = useState<number>(11);

  const confirmedEvents = events.filter((e) => e.status !== 'Cancelled' && e.date);

  // Group events by day in November 2026
  const eventsByDay: Record<number, EventItem[]> = {};
  confirmedEvents.forEach((evt) => {
    if (evt.date) {
      const parts = evt.date.split('-');
      if (parts.length === 3) {
        const day = parseInt(parts[2], 10);
        if (!eventsByDay[day]) eventsByDay[day] = [];
        eventsByDay[day].push(evt);
      }
    }
  });

  const daysInNov = Array.from({ length: 30 }, (_, i) => i + 1);

  const activeDayEvents = eventsByDay[selectedDay] || [];

  return (
    <div className="space-y-6">
      {/* Calendar Header */}
      <div className="bg-white p-5 rounded-2xl border border-border shadow-card flex items-center justify-between">
        <div>
          <h2 className="text-[18px] font-bold text-primaryText flex items-center gap-2">
            <CalendarIcon className="w-5 h-5 text-accent" />
            <span>Academic Calendar & Export</span>
          </h2>
          <p className="text-[13px] text-secondaryText mt-0.5">
            Confirmed academic schedule anchored to Asia/Kolkata (IST).
          </p>
        </div>

        <button
          onClick={onDownloadIcs}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-accent text-white font-semibold text-[13px] hover:bg-accent-hover transition-colors shadow-xs"
        >
          <Download className="w-4 h-4" />
          <span>Export .ics Calendar ({confirmedEvents.length} Events)</span>
        </button>
      </div>

      {/* Main Grid: Calendar on Left, Selected Day Agenda on Right */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Month View Card */}
        <div className="lg:col-span-2 bg-white rounded-2xl border border-border p-5 shadow-card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-bold text-[16px] text-primaryText">November 2026</h3>
            <div className="flex items-center gap-2 text-secondaryText">
              <span className="text-[12px] font-medium">Asia/Kolkata Timezone</span>
            </div>
          </div>

          {/* Weekday Names */}
          <div className="grid grid-cols-7 text-center text-[12px] font-bold text-secondaryText mb-2 py-1 border-b border-border">
            <span>Sun</span>
            <span>Mon</span>
            <span>Tue</span>
            <span>Wed</span>
            <span>Thu</span>
            <span>Fri</span>
            <span>Sat</span>
          </div>

          {/* Month Days Grid (Nov 1 is Sunday) */}
          <div className="grid grid-cols-7 gap-1.5">
            {daysInNov.map((day) => {
              const dayEvts = eventsByDay[day] || [];
              const isSelected = selectedDay === day;

              return (
                <div
                  key={day}
                  onClick={() => setSelectedDay(day)}
                  className={`min-h-[76px] p-2 rounded-xl border transition-all cursor-pointer flex flex-col justify-between ${
                    isSelected
                      ? 'border-accent bg-accent-light/40 shadow-xs'
                      : 'border-border/70 hover:border-accent/40 bg-white'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span
                      className={`text-[12px] font-bold w-6 h-6 rounded-full flex items-center justify-center ${
                        isSelected ? 'bg-accent text-white' : 'text-primaryText'
                      }`}
                    >
                      {day}
                    </span>
                    {dayEvts.length > 0 && (
                      <span className="w-2 h-2 rounded-full bg-accent" />
                    )}
                  </div>

                  {/* Tiny Event Chips */}
                  <div className="space-y-1 mt-1">
                    {dayEvts.slice(0, 2).map((ev) => (
                      <div
                        key={ev.id}
                        className={`text-[10px] font-semibold truncate px-1.5 py-0.5 rounded ${
                          ev.category === 'deadline'
                            ? 'bg-red-50 text-red-700'
                            : ev.status === 'Updated'
                            ? 'bg-green-50 text-green-700'
                            : 'bg-accent-light text-accent'
                        }`}
                      >
                        {ev.title}
                      </div>
                    ))}
                    {dayEvts.length > 2 && (
                      <div className="text-[9px] text-secondaryText font-bold pl-1">
                        +{dayEvts.length - 2} more
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Selected Day Agenda Column */}
        <div className="bg-white rounded-2xl border border-border p-5 shadow-card space-y-4">
          <div className="border-b border-border pb-3">
            <span className="text-[11px] font-bold uppercase tracking-wider text-secondaryText">
              Schedule for
            </span>
            <h3 className="text-[18px] font-bold text-primaryText">
              {selectedDay} November 2026
            </h3>
          </div>

          <div className="space-y-3">
            {activeDayEvents.length > 0 ? (
              activeDayEvents.map((ev) => (
                <div
                  key={ev.id}
                  onClick={() => onEventClick(ev)}
                  className="p-3 rounded-xl border border-border hover:border-accent hover:shadow-xs transition-all cursor-pointer bg-app"
                >
                  <span
                    className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded ${
                      ev.category === 'deadline'
                        ? 'bg-red-100 text-red-700'
                        : 'bg-accent-light text-accent'
                    }`}
                  >
                    {ev.category}
                  </span>
                  <h4 className="font-bold text-[14px] text-primaryText mt-1.5">{ev.title}</h4>
                  <div className="text-[12px] text-secondaryText mt-1 flex items-center gap-1.5">
                    <Clock className="w-3.5 h-3.5" />
                    <span>{ev.time || '11:59 PM'}</span>
                    <span>•</span>
                    <MapPin className="w-3.5 h-3.5" />
                    <span>{ev.venue || 'Campus'}</span>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-10 text-secondaryText text-[13px]">
                No events scheduled for {selectedDay} November.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

