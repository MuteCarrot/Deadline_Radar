import React, { useState } from 'react';
import {
  X,
  Calendar,
  Clock,
  MapPin,
  Users,
  CheckCircle2,
  XCircle,
  Edit3,
  Save,
  MessageSquare,
  AlertTriangle,
  History,
  ExternalLink,
} from 'lucide-react';
import { EventItem } from '../types';

interface EventDetailDrawerProps {
  event: EventItem | null;
  onClose: () => void;
  onConfirm: (id: string) => void;
  onReject: (id: string) => void;
  onSave: (id: string, updated: Partial<EventItem>) => void;
  onLocateInChat?: (msgId: number) => void;
}

export const EventDetailDrawer: React.FC<EventDetailDrawerProps> = ({
  event,
  onClose,
  onConfirm,
  onReject,
  onSave,
  onLocateInChat,
}) => {
  if (!event) return null;

  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    title: event.title,
    course_or_subject: event.course_or_subject || '',
    date: event.date || '',
    time: event.time || '',
    venue: event.venue || '',
    audience: event.audience || 'All',
  });

  const handleSave = () => {
    onSave(event.id, formData);
    setIsEditing(false);
  };

  return (
    <div className="fixed inset-0 z-50 overflow-hidden flex justify-end">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-slate-900/30 backdrop-blur-xs transition-opacity"
        onClick={onClose}
      />

      {/* Slide-over Panel */}
      <div className="relative w-full max-w-lg bg-white h-full shadow-drawer flex flex-col z-10 animate-in slide-in-from-right duration-200">
        {/* Drawer Header */}
        <div className="p-5 border-b border-border flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[11px] font-bold uppercase tracking-wider text-secondaryText">
                {event.category}
              </span>
              <span
                className={`text-[11px] font-semibold px-2 py-0.5 rounded-full ${
                  event.status === 'Upcoming'
                    ? 'bg-success-bg text-success'
                    : event.status === 'Updated'
                    ? 'bg-blue-50 text-blue-700'
                    : event.status === 'Cancelled'
                    ? 'bg-danger-bg text-danger'
                    : 'bg-warning-bg text-warning'
                }`}
              >
                {event.status}
              </span>
            </div>
            <h2 className="text-[18px] font-bold text-primaryText mt-1 leading-snug">
              {isEditing ? (
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  className="w-full font-bold text-primaryText border border-border rounded-lg px-2 py-1 text-[16px] focus:outline-accent"
                />
              ) : (
                event.title
              )}
            </h2>
          </div>

          <div className="flex items-center gap-2">
            {!isEditing ? (
              <button
                onClick={() => setIsEditing(true)}
                className="w-8 h-8 rounded-lg border border-border hover:bg-app flex items-center justify-center text-secondaryText"
                title="Edit event"
              >
                <Edit3 className="w-4 h-4" />
              </button>
            ) : (
              <button
                onClick={handleSave}
                className="w-8 h-8 rounded-lg bg-accent text-white flex items-center justify-center"
                title="Save changes"
              >
                <Save className="w-4 h-4" />
              </button>
            )}
            <button
              onClick={onClose}
              className="w-8 h-8 rounded-lg border border-border hover:bg-app flex items-center justify-center text-secondaryText"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Drawer Body */}
        <div className="flex-1 overflow-y-auto p-5 space-y-5">
          {/* Conflict Warning if present */}
          {event.has_conflict && event.conflict_reason && (
            <div className="p-3.5 rounded-xl bg-amber-50 border border-amber-200 text-amber-900 text-[13px] flex items-start gap-2.5">
              <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
              <div>
                <strong className="font-semibold block mb-0.5">⚠️ Unverified Rumor / Conflict Flagged:</strong>
                {event.conflict_reason}
              </div>
            </div>
          )}

          {/* Key Details Grid */}
          <div className="bg-app rounded-xl p-4 border border-border space-y-3">
            {/* Course */}
            <div className="flex items-center justify-between text-[13px]">
              <span className="text-secondaryText font-medium">Course / Subject</span>
              {isEditing ? (
                <input
                  type="text"
                  value={formData.course_or_subject}
                  onChange={(e) => setFormData({ ...formData, course_or_subject: e.target.value })}
                  className="bg-white border border-border rounded px-2 py-0.5 text-right font-medium text-primaryText"
                />
              ) : (
                <span className="font-semibold text-primaryText">
                  {event.course_or_subject || 'General'}
                </span>
              )}
            </div>

            {/* Date */}
            <div className="flex items-center justify-between text-[13px]">
              <span className="text-secondaryText font-medium flex items-center gap-1.5">
                <Calendar className="w-3.5 h-3.5" /> Date
              </span>
              {isEditing ? (
                <input
                  type="date"
                  value={formData.date}
                  onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                  className="bg-white border border-border rounded px-2 py-0.5 text-right font-medium text-primaryText"
                />
              ) : (
                <span className="font-semibold text-primaryText">
                  {event.date || '⚠️ Date TBA'}
                </span>
              )}
            </div>

            {/* Time */}
            <div className="flex items-center justify-between text-[13px]">
              <span className="text-secondaryText font-medium flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5" /> Time
              </span>
              {isEditing ? (
                <input
                  type="text"
                  placeholder="HH:MM (24h)"
                  value={formData.time}
                  onChange={(e) => setFormData({ ...formData, time: e.target.value })}
                  className="bg-white border border-border rounded px-2 py-0.5 text-right font-medium text-primaryText"
                />
              ) : (
                <span className="font-semibold text-primaryText">
                  {event.time || 'All Day / 23:59'}
                </span>
              )}
            </div>

            {/* Venue */}
            <div className="flex items-center justify-between text-[13px]">
              <span className="text-secondaryText font-medium flex items-center gap-1.5">
                <MapPin className="w-3.5 h-3.5" /> Venue / Link
              </span>
              {isEditing ? (
                <input
                  type="text"
                  value={formData.venue}
                  onChange={(e) => setFormData({ ...formData, venue: e.target.value })}
                  className="bg-white border border-border rounded px-2 py-0.5 text-right font-medium text-primaryText"
                />
              ) : (
                <span className="font-semibold text-primaryText">
                  {event.venue || 'Campus / Online'}
                </span>
              )}
            </div>

            {/* Audience */}
            <div className="flex items-center justify-between text-[13px]">
              <span className="text-secondaryText font-medium flex items-center gap-1.5">
                <Users className="w-3.5 h-3.5" /> Audience
              </span>
              {isEditing ? (
                <input
                  type="text"
                  value={formData.audience}
                  onChange={(e) => setFormData({ ...formData, audience: e.target.value })}
                  className="bg-white border border-border rounded px-2 py-0.5 text-right font-medium text-primaryText"
                />
              ) : (
                <span className="font-semibold text-primaryText">
                  {event.audience || 'All'}
                </span>
              )}
            </div>
          </div>

          {/* Change History */}
          {event.history && event.history.length > 0 && (
            <div>
              <h4 className="text-[13px] font-bold text-primaryText flex items-center gap-1.5 mb-2">
                <History className="w-3.5 h-3.5 text-secondaryText" />
                <span>Audit & Change History</span>
              </h4>
              <div className="space-y-1.5 text-[12px] text-secondaryText">
                {event.history.map((h, i) => (
                  <div key={i} className="flex items-start gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-accent mt-1.5 shrink-0" />
                    <span>{h}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Original WhatsApp Source Messages */}
          <div>
            <h4 className="text-[13px] font-bold text-primaryText flex items-center gap-1.5 mb-2.5">
              <MessageSquare className="w-3.5 h-3.5 text-secondaryText" />
              <span>Original WhatsApp Source Messages ({event.source_details?.length || 0})</span>
            </h4>
            <div className="space-y-2">
              {event.source_details?.map((src) => (
                <div
                  key={src.msg_id}
                  className="p-3.5 rounded-xl bg-app border border-border text-[13px] space-y-1.5"
                >
                  <div className="flex items-center justify-between text-[11px] text-secondaryText font-semibold">
                    <span className="font-mono bg-white px-2 py-0.5 rounded border border-border text-slate-800">
                      Msg #{src.msg_id} • {src.sender}
                    </span>
                    <span>{src.sent_at}</span>
                  </div>
                  <p className="text-primaryText font-medium italic">"{src.text}"</p>
                  {onLocateInChat && (
                    <div className="pt-1 flex justify-end">
                      <button
                        onClick={() => onLocateInChat(src.msg_id)}
                        className="text-[11px] font-semibold text-accent hover:underline flex items-center gap-1 bg-white px-2 py-0.5 rounded border border-accent/20"
                      >
                        <span>View in Chat Stream</span>
                        <ExternalLink className="w-3 h-3" />
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Drawer Actions Footer */}
        <div className="p-4 border-t border-border bg-app flex items-center gap-3">
          <button
            onClick={() => onConfirm(event.id)}
            className="flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl bg-success text-white font-semibold text-[13px] hover:bg-emerald-700 transition-colors shadow-xs"
          >
            <CheckCircle2 className="w-4 h-4" />
            <span>Confirm & Verify</span>
          </button>
          <button
            onClick={() => onReject(event.id)}
            className="flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl bg-white border border-danger-border text-danger font-semibold text-[13px] hover:bg-danger-bg transition-colors shadow-xs"
          >
            <XCircle className="w-4 h-4" />
            <span>Mark Cancelled</span>
          </button>
        </div>
      </div>
    </div>
  );
};

