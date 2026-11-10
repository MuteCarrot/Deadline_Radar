import React, { useState } from 'react';
import { Calendar as CalendarIcon, Search, Filter } from 'lucide-react';
import { EventItem } from '../types';
import { EventCard } from '../components/EventCard';

interface EventsViewProps {
  events: EventItem[];
  onEventClick: (event: EventItem) => void;
}

export const EventsView: React.FC<EventsViewProps> = ({ events, onEventClick }) => {
  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState<'all' | 'event' | 'schedule_change' | 'cancellation'>('all');

  const eventsList = events.filter((e) => e.category !== 'deadline');

  const filtered = eventsList.filter((e) => {
    const matchSearch =
      !search ||
      e.title.toLowerCase().includes(search.toLowerCase()) ||
      (e.course_or_subject && e.course_or_subject.toLowerCase().includes(search.toLowerCase()));

    const matchType = typeFilter === 'all' || e.category === typeFilter;
    return matchSearch && matchType;
  });

  return (
    <div className="space-y-6">
      {/* Filter Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-4 rounded-2xl border border-border shadow-card">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-secondaryText absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search events, quizzes, lectures, venues..."
            className="w-full pl-9 pr-4 py-2 bg-app border border-border rounded-xl text-[14px] text-primaryText focus:outline-accent"
          />
        </div>

        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-secondaryText shrink-0" />
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value as any)}
            className="bg-app border border-border rounded-xl px-3 py-2 text-[13px] font-medium text-primaryText focus:outline-accent"
          >
            <option value="all">All Types</option>
            <option value="event">Scheduled Events</option>
            <option value="schedule_change">Updated / Postponed</option>
            <option value="cancellation">Cancelled</option>
          </select>
        </div>
      </div>

      {/* Events List */}
      <div className="space-y-3">
        {filtered.map((ev) => (
          <EventCard key={ev.id} event={ev} onClick={onEventClick} />
        ))}

        {filtered.length === 0 && (
          <div className="bg-white rounded-2xl border border-border p-12 text-center">
            <CalendarIcon className="w-10 h-10 text-secondaryText/40 mx-auto mb-2" />
            <h3 className="font-bold text-[16px] text-primaryText">No events found</h3>
            <p className="text-[13px] text-secondaryText mt-1">Try adjusting your search criteria.</p>
          </div>
        )}
      </div>
    </div>
  );
};

