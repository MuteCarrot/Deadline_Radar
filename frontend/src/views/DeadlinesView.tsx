import React, { useState } from 'react';
import { Clock, Search, Filter, AlertCircle } from 'lucide-react';
import { EventItem } from '../types';
import { EventCard } from '../components/EventCard';

interface DeadlinesViewProps {
  events: EventItem[];
  onEventClick: (event: EventItem) => void;
}

export const DeadlinesView: React.FC<DeadlinesViewProps> = ({ events, onEventClick }) => {
  const [search, setSearch] = useState('');
  const [courseFilter, setCourseFilter] = useState('all');

  const deadlines = events.filter((e) => e.category === 'deadline');

  const courses = Array.from(
    new Set(deadlines.map((d) => d.course_or_subject).filter(Boolean))
  ) as string[];

  const filtered = deadlines.filter((d) => {
    const matchSearch =
      !search ||
      d.title.toLowerCase().includes(search.toLowerCase()) ||
      (d.course_or_subject && d.course_or_subject.toLowerCase().includes(search.toLowerCase()));

    const matchCourse = courseFilter === 'all' || d.course_or_subject === courseFilter;
    return matchSearch && matchCourse;
  });

  return (
    <div className="space-y-6">
      {/* Header & Filter Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-4 rounded-2xl border border-border shadow-card">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-secondaryText absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search deadlines by title, assignment, or portal..."
            className="w-full pl-9 pr-4 py-2 bg-app border border-border rounded-xl text-[14px] text-primaryText focus:outline-accent"
          />
        </div>

        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-secondaryText shrink-0" />
          <select
            value={courseFilter}
            onChange={(e) => setCourseFilter(e.target.value)}
            className="bg-app border border-border rounded-xl px-3 py-2 text-[13px] font-medium text-primaryText focus:outline-accent"
          >
            <option value="all">All Courses</option>
            {courses.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Deadlines List */}
      <div className="space-y-3">
        {filtered.map((d) => (
          <EventCard key={d.id} event={d} onClick={onEventClick} />
        ))}

        {filtered.length === 0 && (
          <div className="bg-white rounded-2xl border border-border p-12 text-center">
            <Clock className="w-10 h-10 text-secondaryText/40 mx-auto mb-2" />
            <h3 className="font-bold text-[16px] text-primaryText">No deadlines found</h3>
            <p className="text-[13px] text-secondaryText mt-1">Try adjusting your search query or filter.</p>
          </div>
        )}
      </div>
    </div>
  );
};

