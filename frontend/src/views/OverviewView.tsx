import React, { useState } from 'react';
import { Calendar, RefreshCw, Sparkles, BookOpen, ExternalLink } from 'lucide-react';
import { OverviewData, EventItem } from '../types';
import { EventCard } from '../components/EventCard';
import { MiniCalendar } from '../components/MiniCalendar';
import { ConnectedSourcesWidget } from '../components/ConnectedSourcesWidget';
import { QuickActionsWidget } from '../components/QuickActionsWidget';

interface OverviewViewProps {
  overviewData: OverviewData;
  onEventClick: (event: EventItem) => void;
  onOpenImport: () => void;
  onDownloadIcs: () => void;
  onNavigate: (view: string) => void;
}

export const OverviewView: React.FC<OverviewViewProps> = ({
  overviewData,
  onEventClick,
  onOpenImport,
  onDownloadIcs,
  onNavigate,
}) => {
  const [filterType, setFilterType] = useState<'all' | 'deadline' | 'event'>('all');
  const [selectedCalendarDate, setSelectedCalendarDate] = useState('2026-11-11');

  const { metrics, upcoming_agenda } = overviewData;

  const filteredAgenda = upcoming_agenda.filter((item) => {
    if (filterType === 'deadline') return item.category === 'deadline';
    if (filterType === 'event') return item.category === 'event' || item.category === 'schedule_change';
    return true;
  });

  const deadlineCount = upcoming_agenda.filter((i) => i.category === 'deadline').length;
  const eventCount = upcoming_agenda.filter((i) => i.category === 'event' || i.category === 'schedule_change').length;

  return (
    <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
      {/* Center 2 Columns: Metrics & Upcoming at a Glance */}
      <div className="xl:col-span-2 space-y-6">
        {/* Top 3 KPI Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {/* Card 1: Deadlines */}
          <div
            onClick={() => onNavigate('deadlines')}
            className="bg-white rounded-2xl border border-border p-4 shadow-card hover:shadow-subtle transition-all cursor-pointer flex items-center gap-3.5 group"
          >
            <div className="w-12 h-12 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center shrink-0 group-hover:scale-105 transition-transform">
              <Calendar className="w-6 h-6" />
            </div>
            <div>
              <div className="text-[24px] font-bold text-primaryText leading-none">
                {metrics.active_deadlines}
              </div>
              <div className="text-[13px] font-medium text-secondaryText mt-1">
                Active Deadlines
              </div>
              <div className="text-[11px] font-semibold text-emerald-600 mt-0.5 flex items-center gap-1">
                <span>↓ -1 from last week</span>
              </div>
            </div>
          </div>

          {/* Card 2: Upcoming Events */}
          <div
            onClick={() => onNavigate('events')}
            className="bg-white rounded-2xl border border-border p-4 shadow-card hover:shadow-subtle transition-all cursor-pointer flex items-center gap-3.5 group"
          >
            <div className="w-12 h-12 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center shrink-0 group-hover:scale-105 transition-transform">
              <BookOpen className="w-6 h-6" />
            </div>
            <div>
              <div className="text-[24px] font-bold text-primaryText leading-none">
                {metrics.upcoming_events}
              </div>
              <div className="text-[13px] font-medium text-secondaryText mt-1">
                Upcoming Events
              </div>
              <div className="text-[11px] font-semibold text-emerald-600 mt-0.5 flex items-center gap-1">
                <span>↑ +1 from last week</span>
              </div>
            </div>
          </div>

          {/* Card 3: Updated / Postponed */}
          <div
            onClick={() => onNavigate('needs_review')}
            className="bg-white rounded-2xl border border-border p-4 shadow-card hover:shadow-subtle transition-all cursor-pointer flex items-center gap-3.5 group"
          >
            <div className="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center shrink-0 group-hover:scale-105 transition-transform">
              <RefreshCw className="w-6 h-6" />
            </div>
            <div>
              <div className="text-[24px] font-bold text-primaryText leading-none">
                {metrics.updated_postponed}
              </div>
              <div className="text-[13px] font-medium text-secondaryText mt-1">
                Updated / Postponed
              </div>
              <div className="text-[11px] font-semibold text-secondaryText mt-0.5">
                Schedule changes detected
              </div>
            </div>
          </div>
        </div>

        {/* Upcoming at a Glance Section */}
        <div className="space-y-3.5">
          <div className="flex items-center justify-between">
            <h2 className="text-[18px] font-bold text-primaryText tracking-tight">
              Upcoming at a Glance
            </h2>

            {/* Filter Pills */}
            <div className="flex items-center gap-1.5 p-1 bg-slate-100 rounded-xl">
              <button
                onClick={() => setFilterType('all')}
                className={`px-3 py-1 rounded-lg text-[12px] font-semibold transition-all ${
                  filterType === 'all'
                    ? 'bg-accent text-white shadow-xs'
                    : 'text-secondaryText hover:text-primaryText'
                }`}
              >
                All ({upcoming_agenda.length})
              </button>
              <button
                onClick={() => setFilterType('deadline')}
                className={`px-3 py-1 rounded-lg text-[12px] font-semibold transition-all ${
                  filterType === 'deadline'
                    ? 'bg-accent text-white shadow-xs'
                    : 'text-secondaryText hover:text-primaryText'
                }`}
              >
                Deadlines ({deadlineCount})
              </button>
              <button
                onClick={() => setFilterType('event')}
                className={`px-3 py-1 rounded-lg text-[12px] font-semibold transition-all ${
                  filterType === 'event'
                    ? 'bg-accent text-white shadow-xs'
                    : 'text-secondaryText hover:text-primaryText'
                }`}
              >
                Events ({eventCount})
              </button>
            </div>
          </div>

          {/* Event Cards List */}
          <div className="space-y-2.5">
            {filteredAgenda.map((event) => (
              <EventCard key={event.id} event={event} onClick={onEventClick} />
            ))}

            {filteredAgenda.length === 0 && (
              <div className="bg-white rounded-2xl border border-border p-8 text-center text-secondaryText">
                No events in this view.
              </div>
            )}
          </div>
        </div>

        {/* AI Monitoring & Engine Banner */}
        <div className="p-4 rounded-2xl bg-gradient-to-r from-accent-light via-indigo-50 to-purple-50 border border-accent/20 flex items-center justify-between shadow-card">
          <div className="flex items-center gap-3.5">
            <div className="w-10 h-10 rounded-xl bg-accent text-white flex items-center justify-center shrink-0 shadow-sm shadow-accent/30">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <div className="text-[14px] font-bold text-primaryText flex items-center gap-2">
                <span>AI Engine: {overviewData.engine_used || 'Active'}</span>
                <span className="text-[11px] font-semibold text-accent bg-white px-2 py-0.5 rounded-full border border-accent/20">
                  {overviewData.active_dataset}
                </span>
              </div>
              <div className="text-[12px] text-secondaryText">
                {metrics.total_messages_parsed} messages parsed • Provenance and exact source notice mapped for all items.
              </div>
            </div>
          </div>

          <div className="hidden sm:flex items-center gap-2 pr-2">
            <button
              onClick={() => onNavigate('sources')}
              className="text-[12px] font-bold text-accent bg-white px-3 py-1.5 rounded-xl shadow-xs hover:bg-slate-50 transition-colors border border-accent/20 flex items-center gap-1"
            >
              <span>Inspect Chat Log</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Right Column: Mini Calendar, Connected Sources, Quick Actions */}
      <div className="space-y-6">
        <MiniCalendar
          selectedDate={selectedCalendarDate}
          onSelectDate={(d) => setSelectedCalendarDate(d)}
        />

        <ConnectedSourcesWidget onManage={() => onNavigate('sources')} />

        <QuickActionsWidget
          onImportClick={onOpenImport}
          onAddEventClick={() => onOpenImport()}
          onDownloadIcs={onDownloadIcs}
        />
      </div>
    </div>
  );
};

