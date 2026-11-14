import React, { useEffect, useState } from 'react';
import {
  Layers,
  MessageSquare,
  Send,
  Mail,
  Search,
  CheckCircle2,
  AlertCircle,
  Info,
  Calendar,
  Clock,
  MapPin,
  ExternalLink,
  Filter,
  Sparkles,
} from 'lucide-react';
import { fetchSources, fetchMessages } from '../api';
import { SourceIntegration, AnnotatedMessage } from '../types';

interface SourcesViewProps {
  onOpenImport: () => void;
  onSelectEvent?: (eventId: string) => void;
}

export const SourcesView: React.FC<SourcesViewProps> = ({ onOpenImport, onSelectEvent }) => {
  const [sources, setSources] = useState<SourceIntegration[]>([]);
  const [messages, setMessages] = useState<AnnotatedMessage[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filterCategory, setFilterCategory] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');

  const loadData = async () => {
    try {
      const [srcs, msgs] = await Promise.all([fetchSources(), fetchMessages()]);
      setSources(srcs);
      setMessages(msgs);
    } catch (e) {
      console.warn('Sources load error:', e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const getIcon = (id: string) => {
    switch (id) {
      case 'whatsapp':
        return <MessageSquare className="w-5 h-5 text-emerald-600" />;
      case 'telegram':
        return <Send className="w-5 h-5 text-sky-600" />;
      case 'gmail':
        return <Mail className="w-5 h-5 text-red-600" />;
      default:
        return <Layers className="w-5 h-5 text-accent" />;
    }
  };

  // Filter messages based on category & search
  const filteredMessages = messages.filter((m) => {
    if (filterCategory === 'notices' && m.category === 'chatter') return false;
    if (filterCategory !== 'all' && filterCategory !== 'notices' && m.category !== filterCategory) return false;
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      const matchText = m.text.toLowerCase().includes(q);
      const matchSender = m.sender.toLowerCase().includes(q);
      const matchTitle = (m.title || '').toLowerCase().includes(q);
      if (!matchText && !matchSender && !matchTitle) return false;
    }
    return true;
  });

  const noticesCount = messages.filter((m) => m.category !== 'chatter').length;
  const chatterCount = messages.filter((m) => m.category === 'chatter').length;

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-white p-5 rounded-2xl border border-border shadow-card flex items-center justify-between">
        <div>
          <h2 className="text-[18px] font-bold text-primaryText">Connected Channels & Chat Provenance</h2>
          <p className="text-[13px] text-secondaryText mt-1">
            Deadline Radar shows the exact WhatsApp / Telegram source message behind every extracted academic notice.
          </p>
        </div>
        <button
          onClick={onOpenImport}
          className="px-4 py-2 rounded-xl bg-accent text-white font-semibold text-[13px] hover:bg-accent-hover transition-colors shadow-xs flex items-center gap-1.5"
        >
          <MessageSquare className="w-4 h-4" />
          <span>Import Chat</span>
        </button>
      </div>

      {/* Connected Source Channels Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {sources.map((src) => {
          const isActive = src.status === 'active';
          const isAvailable = src.status === 'available';

          return (
            <div
              key={src.id}
              className="bg-white rounded-2xl border border-border p-5 shadow-card flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-4">
                  <div className="w-10 h-10 rounded-xl bg-app flex items-center justify-center border border-border">
                    {getIcon(src.id)}
                  </div>

                  <span
                    className={`text-[11px] font-bold px-2.5 py-1 rounded-full flex items-center gap-1.5 ${
                      isActive
                        ? 'bg-success-bg text-success border border-success-border'
                        : isAvailable
                        ? 'bg-app text-secondaryText border border-border'
                        : 'bg-amber-50 text-amber-800 border border-amber-200'
                    }`}
                  >
                    <span
                      className={`w-1.5 h-1.5 rounded-full ${
                        isActive ? 'bg-success' : isAvailable ? 'bg-secondaryText' : 'bg-amber-600'
                      }`}
                    />
                    {src.status_label}
                  </span>
                </div>

                <h3 className="text-[16px] font-bold text-primaryText">{src.name}</h3>
                <div className="text-[12px] text-secondaryText font-medium">{src.type}</div>

                <div className="mt-3 p-3 bg-app rounded-xl border border-border text-[12px] text-primaryText">
                  <strong>Session Status: </strong>
                  <span>{src.details}</span>
                </div>

                <div className="mt-3 text-[12px] text-secondaryText flex items-start gap-1.5">
                  <Info className="w-3.5 h-3.5 text-secondaryText/70 shrink-0 mt-0.5" />
                  <span>{src.instructions}</span>
                </div>
              </div>

              <div className="mt-5 pt-4 border-t border-border">
                {isActive ? (
                  <button
                    onClick={onOpenImport}
                    className="w-full py-2 rounded-xl bg-app hover:bg-slate-200 text-primaryText font-semibold text-[13px] transition-colors"
                  >
                    Import More Messages
                  </button>
                ) : (
                  <div className="text-center text-[12px] text-secondaryText py-2">
                    {isAvailable ? 'Upload export anytime' : 'Configurable in production'}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Chat Messages & AI Provenance Inspector */}
      <div className="bg-white rounded-2xl border border-border p-6 shadow-card space-y-5">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border pb-4">
          <div>
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-accent" />
              <h3 className="text-[16px] font-bold text-primaryText">Chat Ingestion & Extraction Log</h3>
              <span className="text-[12px] font-semibold text-secondaryText bg-app px-2.5 py-0.5 rounded-full border border-border">
                {messages.length} Total Messages
              </span>
            </div>
            <p className="text-[13px] text-secondaryText mt-0.5">
              Inspect how the AI parsed each message and identified where deadlines or events were found.
            </p>
          </div>

          {/* Filter Pills */}
          <div className="flex flex-wrap items-center gap-1.5">
            {[
              { id: 'all', label: `All (${messages.length})` },
              { id: 'notices', label: `Notices (${noticesCount})` },
              { id: 'deadline', label: 'Deadlines' },
              { id: 'event', label: 'Events' },
              { id: 'schedule_change', label: 'Updates' },
              { id: 'cancellation', label: 'Cancelled' },
              { id: 'chatter', label: `Chatter (${chatterCount})` },
            ].map((f) => (
              <button
                key={f.id}
                onClick={() => setFilterCategory(f.id)}
                className={`text-[12px] font-semibold px-3 py-1.5 rounded-lg transition-all ${
                  filterCategory === f.id
                    ? 'bg-accent text-white shadow-xs'
                    : 'bg-app text-secondaryText hover:text-primaryText border border-border'
                }`}
              >
                {f.label}
              </button>
            ))}
          </div>
        </div>

        {/* Search Bar */}
        <div className="relative">
          <Search className="w-4 h-4 text-secondaryText absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search message text, sender name, or extracted title..."
            className="w-full pl-10 pr-4 py-2 bg-app rounded-xl border border-border text-[13px] focus:outline-accent"
          />
        </div>

        {/* Message Stream */}
        <div className="space-y-3 max-h-[550px] overflow-y-auto pr-1">
          {filteredMessages.length === 0 ? (
            <div className="py-12 text-center text-secondaryText text-[13px]">
              No messages found matching the selected filters.
            </div>
          ) : (
            filteredMessages.map((m) => {
              const isNotice = m.category !== 'chatter';

              return (
                <div
                  key={m.id}
                  id={`chat-msg-${m.id}`}
                  className={`p-4 rounded-xl border transition-all ${
                    isNotice
                      ? m.category === 'deadline'
                        ? 'bg-white border-blue-200 hover:border-blue-400'
                        : m.category === 'schedule_change'
                        ? 'bg-white border-amber-200 hover:border-amber-400'
                        : m.category === 'cancellation'
                        ? 'bg-white border-red-200 hover:border-red-400'
                        : 'bg-white border-purple-200 hover:border-purple-400'
                      : 'bg-app/60 border-border text-secondaryText hover:bg-app'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-[11px] font-bold px-2 py-0.5 rounded bg-slate-100 text-slate-700">
                        Msg #{m.id}
                      </span>
                      <span className="text-[13px] font-semibold text-primaryText">{m.sender}</span>
                      <span className="text-[11px] text-secondaryText">• {m.sent_at}</span>
                    </div>

                    {/* Extraction Status Badge */}
                    <div className="flex items-center gap-2">
                      {m.category === 'deadline' && (
                        <span className="text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-blue-100 text-blue-700 border border-blue-200">
                          🟢 Deadline Extracted
                        </span>
                      )}
                      {m.category === 'event' && (
                        <span className="text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-purple-100 text-purple-700 border border-purple-200">
                          🟣 Event Extracted
                        </span>
                      )}
                      {m.category === 'schedule_change' && (
                        <span className="text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-amber-100 text-amber-800 border border-amber-200">
                          🔵 Schedule Change
                        </span>
                      )}
                      {m.category === 'cancellation' && (
                        <span className="text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-red-100 text-red-700 border border-red-200">
                          🔴 Cancellation
                        </span>
                      )}
                      {m.category === 'chatter' && (
                        <span className="text-[11px] font-medium px-2 py-0.5 rounded bg-slate-100 text-slate-500">
                          Chatter (Filtered)
                        </span>
                      )}

                      {m.has_conflict && (
                        <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-amber-500 text-white">
                          ⚠️ Conflict
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Message Body */}
                  <p className="text-[13px] text-primaryText font-medium italic mb-2">
                    "{m.text}"
                  </p>

                  {/* Extracted Entity Details Banner if Notice */}
                  {isNotice && (
                    <div className="mt-2.5 pt-2.5 border-t border-border flex flex-wrap items-center justify-between gap-3 text-[12px] bg-slate-50/70 p-2.5 rounded-lg">
                      <div className="flex flex-wrap items-center gap-3">
                        <span className="font-bold text-primaryText">
                          🎯 {m.title || 'Untitled Notice'}
                        </span>
                        {m.date && (
                          <span className="flex items-center gap-1 text-secondaryText">
                            <Calendar className="w-3.5 h-3.5 text-accent" /> {m.date}
                          </span>
                        )}
                        {m.time && (
                          <span className="flex items-center gap-1 text-secondaryText">
                            <Clock className="w-3.5 h-3.5 text-accent" /> {m.time}
                          </span>
                        )}
                        {m.venue && (
                          <span className="flex items-center gap-1 text-secondaryText">
                            <MapPin className="w-3.5 h-3.5 text-accent" /> {m.venue}
                          </span>
                        )}
                        <span className="text-[11px] text-secondaryText font-medium">
                          Confidence: {Math.round(m.confidence * 100)}%
                        </span>
                      </div>

                      {m.event_id && onSelectEvent && (
                        <button
                          onClick={() => onSelectEvent(m.event_id!)}
                          className="text-[11px] font-bold text-accent hover:underline flex items-center gap-1"
                        >
                          <span>Inspect Event</span>
                          <ExternalLink className="w-3 h-3" />
                        </button>
                      )}
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
};
