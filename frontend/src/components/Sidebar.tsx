import React from 'react';
import {
  LayoutDashboard,
  Clock,
  Calendar,
  AlertTriangle,
  Layers,
  CalendarDays,
  Settings,
  Radio,
  Zap,
  ChevronRight,
} from 'lucide-react';
import { OverviewMetrics } from '../types';

interface SidebarProps {
  currentView: string;
  onNavigate: (view: string) => void;
  metrics: OverviewMetrics;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentView, onNavigate, metrics }) => {
  const navItems = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'deadlines', label: 'Deadlines', icon: Clock, count: metrics.active_deadlines },
    { id: 'events', label: 'Events', icon: Calendar, count: metrics.upcoming_events },
    {
      id: 'needs_review',
      label: 'Needs Review',
      icon: AlertTriangle,
      badge: metrics.needs_review > 0 ? metrics.needs_review : undefined,
      badgeType: 'warning',
    },
    { id: 'sources', label: 'Chat & Sources', icon: Layers, dot: true },
    { id: 'calendar', label: 'Calendar & Reminders', icon: CalendarDays },
  ];

  return (
    <aside className="w-64 bg-white border-r border-border h-screen flex flex-col shrink-0 select-none sticky top-0">
      {/* Brand Header */}
      <div className="p-5 flex items-center gap-3 border-b border-border">
        <div className="w-9 h-9 rounded-xl bg-accent flex items-center justify-center text-white shadow-sm shadow-accent/30">
          <Radio className="w-5 h-5" />
        </div>
        <div>
          <h1 className="font-bold text-[16px] text-primaryText tracking-tight leading-tight">
            Deadline Radar
          </h1>
          <p className="text-[12px] text-secondaryText leading-tight">IIIT Hyderabad</p>
        </div>
      </div>

      {/* Main Navigation Links */}
      <nav className="p-3 space-y-1 flex-1 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentView === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-[14px] font-medium transition-colors ${
                isActive
                  ? 'bg-accent-light text-accent font-semibold shadow-sm'
                  : 'text-secondaryText hover:text-primaryText hover:bg-app'
              }`}
            >
              <div className="flex items-center gap-3">
                <Icon className={`w-4 h-4 ${isActive ? 'text-accent' : 'text-secondaryText'}`} />
                <span>{item.label}</span>
              </div>

              {item.count !== undefined && (
                <span
                  className={`text-[12px] font-semibold px-2 py-0.5 rounded-full ${
                    isActive ? 'bg-accent/15 text-accent' : 'bg-app text-secondaryText'
                  }`}
                >
                  {item.count}
                </span>
              )}

              {item.badge !== undefined && (
                <span className="text-[12px] font-semibold px-2 py-0.5 rounded-full bg-amber-100 text-amber-800">
                  {item.badge}
                </span>
              )}

              {item.dot && (
                <span className="w-2 h-2 rounded-full bg-success ring-4 ring-success/15" />
              )}
            </button>
          );
        })}
      </nav>

      {/* Bottom Section */}
      <div className="p-3 border-t border-border space-y-3">
        {/* Automated Sources Card */}
        <div className="p-3 rounded-xl bg-accent-light/80 border border-accent/20 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-6 h-6 rounded-lg bg-accent/20 text-accent flex items-center justify-center">
              <Zap className="w-3.5 h-3.5" />
            </div>
            <div>
              <div className="text-[12px] font-semibold text-primaryText">Automated Sources</div>
              <div className="text-[10px] text-secondaryText">Gmail • Telegram • WhatsApp</div>
            </div>
          </div>
          <span className="text-[10px] font-bold text-success bg-white px-2 py-0.5 rounded-md shadow-xs">
            Live
          </span>
        </div>

        {/* Settings Button */}
        <button
          onClick={() => onNavigate('settings')}
          className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-[14px] font-medium transition-colors ${
            currentView === 'settings'
              ? 'bg-accent-light text-accent font-semibold'
              : 'text-secondaryText hover:text-primaryText hover:bg-app'
          }`}
        >
          <Settings className="w-4 h-4 text-secondaryText" />
          <span>Settings</span>
        </button>

        {/* User Profile */}
        <div className="pt-2 flex items-center justify-between px-2">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-full bg-accent/15 text-accent flex items-center justify-center font-bold text-[13px]">
              S
            </div>
            <div className="text-left">
              <div className="text-[13px] font-semibold text-primaryText leading-tight">Student</div>
              <div className="text-[11px] text-secondaryText leading-tight">student@iiit.ac.in</div>
            </div>
          </div>
          <ChevronRight className="w-4 h-4 text-secondaryText/60" />
        </div>
      </div>
    </aside>
  );
};

