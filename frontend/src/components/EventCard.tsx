import React from 'react';
import { Clock, MapPin, ChevronDown, AlertCircle } from 'lucide-react';
import { EventItem } from '../types';

interface EventCardProps {
  event: EventItem;
  onClick: (event: EventItem) => void;
}

export const EventCard: React.FC<EventCardProps> = ({ event, onClick }) => {
  // Parse date for display
  let dayName = 'TBA';
  let dateText = 'Date TBA';

  if (event.date) {
    try {
      const d = new Date(event.date + 'T00:00:00');
      dayName = d.toLocaleDateString('en-US', { weekday: 'short' });
      dateText = d.toLocaleDateString('en-US', { day: 'numeric', month: 'short' });
    } catch {
      dateText = event.date;
    }
  }

  // Left accent color and badge styles
  const isDeadline = event.category === 'deadline';
  const isUpdated = event.status === 'Updated';
  const isCancelled = event.status === 'Cancelled';
  const isNeedsReview = event.needs_review || event.has_conflict;

  let accentBorder = 'border-l-accent';
  let badgeClass = 'bg-accent-light text-accent border border-accent/20';
  let badgeLabel = 'Event';

  if (isCancelled) {
    accentBorder = 'border-l-danger';
    badgeClass = 'bg-danger-bg text-danger border border-danger-border';
    badgeLabel = 'Cancelled';
  } else if (isNeedsReview) {
    accentBorder = 'border-l-warning';
    badgeClass = 'bg-warning-bg text-warning border border-warning-border';
    badgeLabel = 'Needs Review';
  } else if (isUpdated) {
    accentBorder = 'border-l-success';
    badgeClass = 'bg-success-bg text-success border border-success-border';
    badgeLabel = 'Updated';
  } else if (isDeadline) {
    accentBorder = 'border-l-red-500';
    badgeClass = 'bg-red-50 text-red-600 border border-red-200';
    badgeLabel = 'Deadline';
  }

  // Relative time string
  const relativeText = event.time
    ? `${dateText} • ${event.time}`
    : `${dateText} • 11:59 PM`;

  return (
    <div
      onClick={() => onClick(event)}
      className={`bg-white rounded-xl border border-border border-l-4 ${accentBorder} p-3.5 hover:shadow-card hover:border-slate-300 transition-all cursor-pointer flex items-center justify-between group`}
    >
      <div className="flex items-center gap-4">
        {/* Date Box */}
        <div className="w-16 text-center shrink-0 border-r border-border pr-3">
          <div className="text-[11px] font-semibold text-secondaryText uppercase tracking-wider">
            {dayName}
          </div>
          <div className="text-[14px] font-bold text-primaryText leading-tight mt-0.5">
            {dateText}
          </div>
        </div>

        {/* Info */}
        <div>
          <div className="flex items-center gap-2">
            <h4 className="font-semibold text-[15px] text-primaryText group-hover:text-accent transition-colors leading-tight">
              {event.title}
            </h4>
            {event.has_conflict && (
              <AlertCircle className="w-4 h-4 text-warning shrink-0" />
            )}
          </div>

          <div className="text-[13px] text-secondaryText flex items-center gap-3 mt-1">
            <span>{event.course_or_subject || 'General'}</span>
            <span>•</span>
            <span className="flex items-center gap-1">
              <MapPin className="w-3.5 h-3.5 text-secondaryText/70" />
              {event.venue || 'Campus / Online'}
            </span>
          </div>

          <div className="text-[12px] text-secondaryText/80 flex items-center gap-1.5 mt-1 font-medium">
            <Clock className="w-3 h-3 text-secondaryText/70" />
            <span>{relativeText}</span>
            {event.sources.length > 1 && (
              <span className="text-[11px] text-accent bg-accent-light px-1.5 py-0.2 rounded font-semibold ml-2">
                {event.sources.length} notices merged
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Right Badge & Action */}
      <div className="flex items-center gap-3 shrink-0">
        <span className={`text-[12px] font-semibold px-2.5 py-1 rounded-full ${badgeClass}`}>
          {badgeLabel}
        </span>
        <ChevronDown className="w-4 h-4 text-secondaryText/60 group-hover:text-accent transition-colors" />
      </div>
    </div>
  );
};

