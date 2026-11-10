import React from 'react';
import { Upload, Calendar, Bell } from 'lucide-react';

interface HeaderProps {
  title?: string;
  subtitle?: string;
  onOpenImport: () => void;
  onDownloadIcs: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  title = 'Good morning! 👋',
  subtitle = 'Your academic life, organised with AI.',
  onOpenImport,
  onDownloadIcs,
}) => {
  return (
    <header className="flex items-center justify-between pb-6 pt-2">
      <div>
        <h1 className="text-[26px] font-bold text-primaryText tracking-tight">{title}</h1>
        <p className="text-[14px] text-secondaryText mt-0.5">{subtitle}</p>
      </div>

      <div className="flex items-center gap-3">
        {/* Import Messages Button */}
        <button
          onClick={onOpenImport}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-accent hover:bg-accent-hover text-white text-[14px] font-semibold transition-all shadow-sm shadow-accent/20 active:scale-[0.98]"
        >
          <Upload className="w-4 h-4" />
          <span>Import Messages</span>
        </button>

        {/* Download Calendar Button */}
        <button
          onClick={onDownloadIcs}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-white border border-border hover:bg-app text-primaryText text-[14px] font-semibold transition-all shadow-xs active:scale-[0.98]"
        >
          <Calendar className="w-4 h-4 text-secondaryText" />
          <span>Download Calendar</span>
        </button>

        {/* Notification Bell */}
        <button className="w-10 h-10 rounded-xl bg-white border border-border hover:bg-app flex items-center justify-center text-secondaryText transition-all">
          <Bell className="w-4 h-4" />
        </button>
      </div>
    </header>
  );
};

