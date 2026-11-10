import React from 'react';
import { AlertTriangle, CheckCircle2, XCircle, Edit3, MessageSquare, ShieldAlert } from 'lucide-react';
import { EventItem } from '../types';

interface NeedsReviewViewProps {
  events: EventItem[];
  onConfirm: (id: string) => void;
  onReject: (id: string) => void;
  onEditClick: (event: EventItem) => void;
}

export const NeedsReviewView: React.FC<NeedsReviewViewProps> = ({
  events,
  onConfirm,
  onReject,
  onEditClick,
}) => {
  const reviewItems = events.filter((e) => e.needs_review || e.has_conflict);

  return (
    <div className="space-y-6">
      {/* Overview Banner */}
      <div className="bg-amber-50/80 border border-amber-200 rounded-2xl p-5 flex items-start gap-4">
        <div className="w-10 h-10 rounded-xl bg-amber-500 text-white flex items-center justify-center shrink-0 shadow-sm shadow-amber-500/20">
          <ShieldAlert className="w-5 h-5" />
        </div>
        <div>
          <h2 className="text-[16px] font-bold text-amber-950">
            {reviewItems.length} Announcements Require Human Verification
          </h2>
          <p className="text-[13px] text-amber-900/80 mt-1 leading-relaxed">
            Deadline Radar guards your academic calendar against hearsay. Conflicting student rumors, unverified
            cancellations, and notices with missing dates are held in this queue so they never silently corrupt your schedule.
          </p>
        </div>
      </div>

      {reviewItems.length === 0 ? (
        <div className="bg-white rounded-2xl border border-border p-12 text-center">
          <CheckCircle2 className="w-12 h-12 text-success mx-auto mb-3" />
          <h3 className="font-bold text-[18px] text-primaryText">All Notices Verified!</h3>
          <p className="text-[14px] text-secondaryText mt-1">
            No conflicting rumors or ambiguous notices currently pending review.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {reviewItems.map((item) => {
            const confPct = Math.round((item.confidence || 0.6) * 100);

            return (
              <div
                key={item.id}
                className="bg-white rounded-2xl border border-amber-200 shadow-card p-5 space-y-4 hover:shadow-subtle transition-all"
              >
                {/* Header */}
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-amber-100 text-amber-800 border border-amber-200">
                        {item.has_conflict ? 'Conflicting Update' : 'Needs Verification'}
                      </span>
                      <span className="text-[12px] text-secondaryText font-medium">
                        Confidence: <strong>{confPct}%</strong>
                      </span>
                      <span className="text-[12px] text-secondaryText">• Course: <strong>{item.course_or_subject || 'General'}</strong></span>
                    </div>

                    <h3 className="text-[17px] font-bold text-primaryText mt-1.5">{item.title}</h3>
                    <div className="text-[13px] text-secondaryText mt-0.5">
                      Target Date: <strong>{item.date || '⚠️ Missing Date (TBA)'}</strong> {item.time && `at ${item.time}`} • Venue: {item.venue || 'Campus'}
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2 shrink-0">
                    <button
                      onClick={() => onConfirm(item.id)}
                      className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-success text-white text-[13px] font-semibold hover:bg-emerald-700 transition-colors shadow-xs"
                    >
                      <CheckCircle2 className="w-4 h-4" />
                      <span>Confirm Official</span>
                    </button>

                    <button
                      onClick={() => onReject(item.id)}
                      className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-white border border-danger-border text-danger text-[13px] font-semibold hover:bg-danger-bg transition-colors shadow-xs"
                    >
                      <XCircle className="w-4 h-4" />
                      <span>Reject</span>
                    </button>

                    <button
                      onClick={() => onEditClick(item)}
                      className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-app border border-border text-primaryText text-[13px] font-semibold hover:bg-slate-200 transition-colors"
                    >
                      <Edit3 className="w-4 h-4 text-secondaryText" />
                      <span>Edit</span>
                    </button>
                  </div>
                </div>

                {/* Reason Explanation Box */}
                <div className="p-3 rounded-xl bg-amber-50/70 border border-amber-200/80 text-[13px] text-amber-950 flex items-start gap-2">
                  <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
                  <div>
                    <strong className="font-semibold">Why this was flagged: </strong>
                    {item.conflict_reason || 'Uncertain date or low confidence extraction.'}
                  </div>
                </div>

                {/* Supporting Source Messages Side-by-Side or Stacked */}
                <div>
                  <h4 className="text-[12px] font-bold text-secondaryText uppercase tracking-wider flex items-center gap-1.5 mb-2">
                    <MessageSquare className="w-3.5 h-3.5" />
                    <span>Contributing WhatsApp Source Messages ({item.source_details?.length || 0})</span>
                  </h4>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
                    {item.source_details?.map((src, i) => (
                      <div
                        key={src.msg_id}
                        className={`p-3 rounded-xl border text-[13px] ${
                          i === 0
                            ? 'bg-blue-50/40 border-blue-200'
                            : 'bg-amber-50/40 border-amber-200'
                        }`}
                      >
                        <div className="flex items-center justify-between text-[11px] font-bold mb-1">
                          <span className={i === 0 ? 'text-blue-700' : 'text-amber-800'}>
                            {i === 0 ? '📢 Initial Notice' : '⚠️ Later / Contradictory Claim'} (Msg #{src.msg_id})
                          </span>
                          <span className="text-secondaryText font-normal">{src.sent_at}</span>
                        </div>
                        <div className="text-[11px] text-secondaryText font-medium mb-1">
                          Sender: <strong>{src.sender}</strong>
                        </div>
                        <p className="text-primaryText italic font-medium">"{src.text}"</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

