import React, { useEffect, useState } from 'react';
import { Layers, MessageSquare, Send, Mail, CheckCircle2, AlertCircle, Info, ExternalLink } from 'lucide-react';
import { fetchSources } from '../api';
import { SourceIntegration } from '../types';

interface SourcesViewProps {
  onOpenImport: () => void;
}

export const SourcesView: React.FC<SourcesViewProps> = ({ onOpenImport }) => {
  const [sources, setSources] = useState<SourceIntegration[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchSources()
      .then((data) => setSources(data))
      .catch(() => {})
      .finally(() => setIsLoading(false));
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

  return (
    <div className="space-y-6">
      <div className="bg-white p-5 rounded-2xl border border-border shadow-card">
        <h2 className="text-[18px] font-bold text-primaryText">Connected Information Sources</h2>
        <p className="text-[13px] text-secondaryText mt-1">
          Deadline Radar aggregates and reconciles notices from your university channels. 
          Real connectivity statuses are reported below without simulated mock syncs.
        </p>
      </div>

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
                  <button
                    disabled
                    className="w-full py-2 rounded-xl bg-app text-secondaryText/50 font-semibold text-[13px] cursor-not-allowed"
                  >
                    Integration Required
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

