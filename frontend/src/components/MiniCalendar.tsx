import React, { useState } from 'react';
import { AlertTriangle, ChevronLeft, ChevronRight } from 'lucide-react';

interface MiniCalendarProps {
  selectedDate?: string;
  onSelectDate?: (dateStr: string) => void;
  eventDates?: Record<string, 'deadline' | 'event' | 'updated'>;
}

export const MiniCalendar: React.FC<MiniCalendarProps> = ({
  selectedDate = '2026-11-11',
  onSelectDate,
  eventDates = {
    '2026-11-11': 'deadline',
    '2026-11-14': 'deadline',
    '2026-11-17': 'updated',
    '2026-11-19': 'event',
    '2026-11-21': 'event',
  },
}) => {
  const [currentMonth, setCurrentMonth] = useState('November 2026');

  // Days matrix for November 2026 (Nov 1 is Sunday)
  // Calendar grid starting Monday:
  // Oct 27, 28, 29, 30, 31 (prev month) | Nov 1 (Sunday)
  // Nov 2..8
  // Nov 9..15
  // Nov 16..22
  // Nov 23..29
  // Nov 30
  const days = [
    { day: 27, inMonth: false },
    { day: 28, inMonth: false },
    { day: 29, inMonth: false },
    { day: 30, inMonth: false },
    { day: 31, inMonth: false },
    { day: 1, inMonth: true },
    { day: 2, inMonth: true },
    { day: 3, inMonth: true },
    { day: 4, inMonth: true },
    { day: 5, inMonth: true },
    { day: 6, inMonth: true },
    { day: 7, inMonth: true },
    { day: 8, inMonth: true },
    { day: 9, inMonth: true },
    { day: 10, inMonth: true },
    { day: 11, inMonth: true, fullDate: '2026-11-11' },
    { day: 12, inMonth: true },
    { day: 13, inMonth: true },
    { day: 14, inMonth: true, fullDate: '2026-11-14' },
    { day: 15, inMonth: true },
    { day: 16, inMonth: true },
    { day: 17, inMonth: true, fullDate: '2026-11-17' },
    { day: 18, inMonth: true },
    { day: 19, inMonth: true, fullDate: '2026-11-19' },
    { day: 20, inMonth: true },
    { day: 21, inMonth: true, fullDate: '2026-11-21' },
    { day: 22, inMonth: true },
    { day: 23, inMonth: true },
  ];

  return (
    <div className="bg-white rounded-2xl border border-border p-4 shadow-card">
      {/* Calendar Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="w-8 h-8 rounded-lg bg-amber-50 border border-amber-200 flex items-center justify-center text-amber-600">
          <AlertTriangle className="w-4 h-4" />
        </div>
        <div className="font-bold text-[14px] text-primaryText">{currentMonth}</div>
        <div className="flex items-center gap-1">
          <button className="w-6 h-6 rounded-md hover:bg-app flex items-center justify-center text-secondaryText">
            <ChevronLeft className="w-3.5 h-3.5" />
          </button>
          <button className="w-6 h-6 rounded-md hover:bg-app flex items-center justify-center text-secondaryText">
            <ChevronRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Weekdays */}
      <div className="grid grid-cols-7 text-center text-[11px] font-semibold text-secondaryText mb-1">
        <span>Mon</span>
        <span>Tue</span>
        <span>Wed</span>
        <span>Thu</span>
        <span>Fri</span>
        <span>Sat</span>
        <span>Sun</span>
      </div>

      {/* Day Cells */}
      <div className="grid grid-cols-7 text-center gap-y-1">
        {days.map((item, idx) => {
          const isSelected = item.fullDate === selectedDate;
          const dotType = item.fullDate ? eventDates[item.fullDate] : undefined;

          return (
            <div
              key={idx}
              onClick={() => item.fullDate && onSelectDate?.(item.fullDate)}
              className={`h-8 flex flex-col items-center justify-center rounded-lg text-[12px] font-medium cursor-pointer transition-colors relative ${
                isSelected
                  ? 'bg-accent text-white font-bold shadow-xs'
                  : item.inMonth
                  ? 'text-primaryText hover:bg-app'
                  : 'text-secondaryText/40'
              }`}
            >
              <span>{item.day}</span>
              {dotType && !isSelected && (
                <span
                  className={`w-1.5 h-1.5 rounded-full absolute bottom-1 ${
                    dotType === 'deadline'
                      ? 'bg-red-500'
                      : dotType === 'updated'
                      ? 'bg-green-500'
                      : 'bg-accent'
                  }`}
                />
              )}
            </div>
          );
        })}
      </div>

      {/* Legend */}
      <div className="flex items-center justify-center gap-4 mt-3 pt-3 border-t border-border text-[11px] text-secondaryText font-medium">
        <div className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-red-500" />
          <span>Deadline</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-accent" />
          <span>Event</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-green-500" />
          <span>Updated</span>
        </div>
      </div>
    </div>
  );
};

