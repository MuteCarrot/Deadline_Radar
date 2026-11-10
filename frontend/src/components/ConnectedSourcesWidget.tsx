import React from 'react';
import { Mail, Send, MessageSquare, ExternalLink } from 'lucide-react';

interface ConnectedSourcesWidgetProps {
  onManage: () => void;
}

export const ConnectedSourcesWidget: React.FC<ConnectedSourcesWidgetProps> = ({ onManage }) => {
  return (
    <div className="bg-white rounded-2xl border border-border p-4 shadow-card">
      <div className="flex items-center justify-between mb-3.5">
        <h3 className="font-bold text-[14px] text-primaryText">Connected Sources</h3>
        <button
          onClick={onManage}
          className="text-[12px] font-semibold text-accent hover:underline flex items-center gap-1"
        >
          <span>Manage</span>
          <ExternalLink className="w-3 h-3" />
        </button>
      </div>

      <div className="space-y-2.5">
        {/* Gmail */}
        <div className="flex items-center justify-between p-2 rounded-xl hover:bg-app transition-colors">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-red-50 text-red-600 flex items-center justify-center font-bold text-[12px]">
              <Mail className="w-4 h-4" />
            </div>
            <div>
              <div className="text-[13px] font-semibold text-primaryText leading-tight">Gmail</div>
              <div className="text-[11px] text-secondaryText leading-tight">Academic & club notices</div>
            </div>
          </div>
          <span className="text-[11px] font-bold text-amber-700 bg-amber-50 border border-amber-200 px-2 py-0.5 rounded-full">
            Syncing (2 new)
          </span>
        </div>

        {/* Telegram */}
        <div className="flex items-center justify-between p-2 rounded-xl hover:bg-app transition-colors">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-sky-50 text-sky-600 flex items-center justify-center font-bold text-[12px]">
              <Send className="w-4 h-4" />
            </div>
            <div>
              <div className="text-[13px] font-semibold text-primaryText leading-tight">Telegram</div>
              <div className="text-[11px] text-secondaryText leading-tight">Club & course groups</div>
            </div>
          </div>
          <span className="text-[11px] font-bold text-success bg-success-bg border border-success-border px-2 py-0.5 rounded-full flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-success" />
            Live
          </span>
        </div>

        {/* WhatsApp */}
        <div className="flex items-center justify-between p-2 rounded-xl hover:bg-app transition-colors">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center font-bold text-[12px]">
              <MessageSquare className="w-4 h-4" />
            </div>
            <div>
              <div className="text-[13px] font-semibold text-primaryText leading-tight">WhatsApp</div>
              <div className="text-[11px] text-secondaryText leading-tight">Chat exports / forwarded</div>
            </div>
          </div>
          <span className="text-[11px] font-bold text-secondaryText bg-app border border-border px-2 py-0.5 rounded-full flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-secondaryText" />
            Available
          </span>
        </div>
      </div>
    </div>
  );
};

