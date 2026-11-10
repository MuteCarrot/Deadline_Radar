import React from 'react';
import { Zap, Upload, Plus, Calendar, ChevronRight } from 'lucide-react';

interface QuickActionsWidgetProps {
  onImportClick: () => void;
  onAddEventClick: () => void;
  onDownloadIcs: () => void;
}

export const QuickActionsWidget: React.FC<QuickActionsWidgetProps> = ({
  onImportClick,
  onAddEventClick,
  onDownloadIcs,
}) => {
  const actions = [
    {
      icon: Upload,
      label: 'Import Chat / Upload .txt',
      onClick: onImportClick,
    },
    {
      icon: Plus,
      label: 'Add a new event manually',
      onClick: onAddEventClick,
    },
    {
      icon: Calendar,
      label: 'View & download .ics calendar',
      onClick: onDownloadIcs,
    },
  ];

  return (
    <div className="bg-white rounded-2xl border border-border p-4 shadow-card">
      <div className="flex items-center gap-2 mb-3">
        <Zap className="w-4 h-4 text-accent fill-accent" />
        <h3 className="font-bold text-[14px] text-primaryText">Quick Actions</h3>
      </div>

      <div className="space-y-2">
        {actions.map((act, idx) => {
          const Icon = act.icon;
          return (
            <button
              key={idx}
              onClick={act.onClick}
              className="w-full flex items-center justify-between p-2.5 rounded-xl border border-border hover:border-accent/40 hover:bg-app text-left transition-all group"
            >
              <div className="flex items-center gap-2.5">
                <div className="w-6 h-6 rounded-lg bg-app text-secondaryText group-hover:text-accent flex items-center justify-center transition-colors">
                  <Icon className="w-3.5 h-3.5" />
                </div>
                <span className="text-[13px] font-medium text-primaryText group-hover:text-accent transition-colors">
                  {act.label}
                </span>
              </div>
              <ChevronRight className="w-4 h-4 text-secondaryText/60 group-hover:text-accent group-hover:translate-x-0.5 transition-all" />
            </button>
          );
        })}
      </div>
    </div>
  );
};

