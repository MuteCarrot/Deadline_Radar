import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { OverviewView } from './views/OverviewView';
import { DeadlinesView } from './views/DeadlinesView';
import { EventsView } from './views/EventsView';
import { NeedsReviewView } from './views/NeedsReviewView';
import { SourcesView } from './views/SourcesView';
import { CalendarView } from './views/CalendarView';
import { SettingsView } from './views/SettingsView';
import { EventDetailDrawer } from './components/EventDetailDrawer';
import { ImportModal } from './components/ImportModal';
import {
  fetchOverview,
  fetchEvents,
  confirmEvent,
  rejectEvent,
  updateEvent,
} from './api';
import { OverviewData, EventItem } from './types';

export const App: React.FC = () => {
  const [currentView, setCurrentView] = useState('overview');
  const [overviewData, setOverviewData] = useState<OverviewData | null>(null);
  const [events, setEvents] = useState<EventItem[]>([]);
  const [selectedEvent, setSelectedEvent] = useState<EventItem | null>(null);
  const [isImportOpen, setIsImportOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  const loadData = async () => {
    try {
      const [ov, evts] = await Promise.all([fetchOverview(), fetchEvents()]);
      setOverviewData(ov);
      setEvents(evts);
    } catch (err) {
      console.error('Failed to load data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleConfirm = async (id: string) => {
    try {
      await confirmEvent(id);
      await loadData();
      setSelectedEvent(null);
    } catch (err) {
      console.error('Failed to confirm event:', err);
    }
  };

  const handleReject = async (id: string) => {
    try {
      await rejectEvent(id);
      await loadData();
      setSelectedEvent(null);
    } catch (err) {
      console.error('Failed to reject event:', err);
    }
  };

  const handleSave = async (id: string, updated: Partial<EventItem>) => {
    try {
      await updateEvent(id, updated);
      await loadData();
      setSelectedEvent(null);
    } catch (err) {
      console.error('Failed to update event:', err);
    }
  };

  const handleDownloadIcs = () => {
    window.open('/api/export/ics', '_blank');
  };

  // Header contextual text based on current view
  let headerTitle = 'Good morning! 👋';
  let headerSubtitle = 'Your academic life, organised with AI.';

  if (currentView === 'deadlines') {
    headerTitle = 'Academic Deadlines';
    headerSubtitle = 'Track and prioritize all assignments, submissions, and forms.';
  } else if (currentView === 'events') {
    headerTitle = 'Scheduled Campus Events';
    headerSubtitle = 'Quizzes, lab sessions, seminars, and lectures in chronological order.';
  } else if (currentView === 'needs_review') {
    headerTitle = 'Human Review Queue';
    headerSubtitle = 'Verify conflicting updates and incomplete announcements before calendar sync.';
  } else if (currentView === 'sources') {
    headerTitle = 'Connected Information Channels';
    headerSubtitle = 'Monitor chat export ingestion and university broadcast status.';
  } else if (currentView === 'calendar') {
    headerTitle = 'Academic Calendar & Schedule';
    headerSubtitle = 'Month and day views anchored to Asia/Kolkata timezone.';
  } else if (currentView === 'settings') {
    headerTitle = 'Application Settings';
    headerSubtitle = 'Configure Gemini AI models, API keys, and privacy parameters.';
  }

  return (
    <div className="flex min-h-screen bg-app">
      {/* Left Persistent Sidebar */}
      <Sidebar
        currentView={currentView}
        onNavigate={(view) => setCurrentView(view)}
        metrics={
          overviewData?.metrics || {
            active_deadlines: 0,
            upcoming_events: 0,
            updated_postponed: 0,
            needs_review: 0,
            total_messages_parsed: 0,
          }
        }
      />

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col min-w-0 overflow-y-auto px-8 py-6">
        <Header
          title={headerTitle}
          subtitle={headerSubtitle}
          onOpenImport={() => setIsImportOpen(true)}
          onDownloadIcs={handleDownloadIcs}
        />

        {isLoading ? (
          <div className="flex-1 flex items-center justify-center py-20 text-secondaryText">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-accent mr-3"></div>
            <span>Loading academic schedule...</span>
          </div>
        ) : (
          <div className="flex-1 pb-12">
            {currentView === 'overview' && overviewData && (
              <OverviewView
                overviewData={overviewData}
                onEventClick={(evt) => setSelectedEvent(evt)}
                onOpenImport={() => setIsImportOpen(true)}
                onDownloadIcs={handleDownloadIcs}
                onNavigate={(view) => setCurrentView(view)}
              />
            )}

            {currentView === 'deadlines' && (
              <DeadlinesView
                events={events}
                onEventClick={(evt) => setSelectedEvent(evt)}
              />
            )}

            {currentView === 'events' && (
              <EventsView
                events={events}
                onEventClick={(evt) => setSelectedEvent(evt)}
              />
            )}

            {currentView === 'needs_review' && (
              <NeedsReviewView
                events={events}
                onConfirm={handleConfirm}
                onReject={handleReject}
                onEditClick={(evt) => setSelectedEvent(evt)}
              />
            )}

            {currentView === 'sources' && (
              <SourcesView
                onOpenImport={() => setIsImportOpen(true)}
                onSelectEvent={(eventId) => {
                  const evt = events.find((e) => e.id === eventId);
                  if (evt) setSelectedEvent(evt);
                }}
              />
            )}

            {currentView === 'calendar' && (
              <CalendarView
                events={events}
                onDownloadIcs={handleDownloadIcs}
                onEventClick={(evt) => setSelectedEvent(evt)}
              />
            )}

            {currentView === 'settings' && <SettingsView />}
          </div>
        )}
      </main>

      {/* Single-Event Slide-over Detail Drawer */}
      <EventDetailDrawer
        event={selectedEvent}
        onClose={() => setSelectedEvent(null)}
        onConfirm={handleConfirm}
        onReject={handleReject}
        onSave={handleSave}
        onLocateInChat={(msgId) => {
          setCurrentView('sources');
          setSelectedEvent(null);
          setTimeout(() => {
            const el = document.getElementById(`chat-msg-${msgId}`);
            if (el) {
              el.scrollIntoView({ behavior: 'smooth', block: 'center' });
              el.classList.add('ring-4', 'ring-accent', 'scale-[1.01]');
              setTimeout(() => {
                el.classList.remove('ring-4', 'ring-accent', 'scale-[1.01]');
              }, 3000);
            }
          }, 250);
        }}
      />

      {/* Import Modal */}
      <ImportModal
        isOpen={isImportOpen}
        onClose={() => setIsImportOpen(false)}
        onImportComplete={loadData}
      />
    </div>
  );
};

