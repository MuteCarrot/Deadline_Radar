import React, { useState } from 'react';
import { X, Upload, FileText, CheckCircle2, Shield, Sparkles, AlertCircle } from 'lucide-react';
import { importText, importFile, loadDataset } from '../api';

interface ImportModalProps {
  isOpen: boolean;
  onClose: () => void;
  onImportComplete: () => void;
}

export const ImportModal: React.FC<ImportModalProps> = ({
  isOpen,
  onClose,
  onImportComplete,
}) => {
  if (!isOpen) return null;

  const [activeTab, setActiveTab] = useState<'upload' | 'paste' | 'courses'>('courses');
  const [pastedText, setPastedText] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [anonymize, setAnonymize] = useState(true);
  const [useLiveAi, setUseLiveAi] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleRunImport = async () => {
    setIsLoading(true);
    setError(null);
    try {
      if (activeTab === 'upload' && selectedFile) {
        await importFile(selectedFile, anonymize, useLiveAi);
      } else if (activeTab === 'paste' && pastedText.trim()) {
        await importText(pastedText, anonymize, useLiveAi);
      }
      onImportComplete();
      onClose();
    } catch (err: any) {
      setError(err.message || 'Import failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectCourse = async (key: string) => {
    setIsLoading(true);
    setError(null);
    try {
      await loadDataset(key);
      onImportComplete();
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to load course dataset');
    } finally {
      setIsLoading(false);
    }
  };

  const courseList = [
    { key: 'benchmark_16', title: '⚡ Synthetic Benchmark', desc: '16 notices with all edge cases (postponement, rumor conflict, missing date)' },
    { key: 'm26_pm', title: '📚 M26: Product Management', desc: 'Team selection Google Form deadline (Aug 7 11:59 PM), team matching polls' },
    { key: 'm26_dt', title: '📚 M26: Design Thinking', desc: 'TA Keshav Assignment 1 on Moodle (Aug 16 11:59 PM), team project forms' },
    { key: 'm26_bf', title: '📚 M26: Business Fundamentals', desc: 'Lecture notices 2:00 PM - 5:00 PM, SH3 Vindhya A2 venue shift' },
    { key: 'm26_ai_pm', title: '📚 M26: AI for Product Managers', desc: 'Raman Sir lecture in H101 at 8:30 AM, holiday rescheduling notice' },
    { key: 'm26_all', title: '🎓 All 4 M26 Courses Combined', desc: 'Multi-channel academic feed with 930+ messages reconciled' },
  ];

  return (
    <div className="fixed inset-0 z-50 overflow-hidden flex items-center justify-center p-4">
      {/* Backdrop */}
      <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs" onClick={onClose} />

      {/* Modal Card */}
      <div className="relative w-full max-w-xl bg-white rounded-2xl border border-border shadow-2xl p-6 z-10 animate-in fade-in zoom-in-95 duration-150">
        <div className="flex items-center justify-between pb-4 border-b border-border">
          <div>
            <h2 className="text-[18px] font-bold text-primaryText">Import Campus Chat Export</h2>
            <p className="text-[13px] text-secondaryText">Upload WhatsApp/Telegram .txt or select an authentic course chat</p>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-lg border border-border hover:bg-app flex items-center justify-center text-secondaryText"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {error && (
          <div className="mt-4 p-3 rounded-xl bg-danger-bg border border-danger-border text-danger text-[13px] flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Tab Selector */}
        <div className="flex p-1 bg-app rounded-xl border border-border my-4">
          <button
            onClick={() => setActiveTab('courses')}
            className={`flex-1 py-1.5 text-[13px] font-semibold rounded-lg transition-all ${
              activeTab === 'courses' ? 'bg-white text-accent shadow-xs' : 'text-secondaryText hover:text-primaryText'
            }`}
          >
            IIIT-H Course Chats
          </button>
          <button
            onClick={() => setActiveTab('upload')}
            className={`flex-1 py-1.5 text-[13px] font-semibold rounded-lg transition-all ${
              activeTab === 'upload' ? 'bg-white text-accent shadow-xs' : 'text-secondaryText hover:text-primaryText'
            }`}
          >
            Upload .txt File
          </button>
          <button
            onClick={() => setActiveTab('paste')}
            className={`flex-1 py-1.5 text-[13px] font-semibold rounded-lg transition-all ${
              activeTab === 'paste' ? 'bg-white text-accent shadow-xs' : 'text-secondaryText hover:text-primaryText'
            }`}
          >
            Paste Text
          </button>
        </div>

        {/* Courses Tab Content */}
        {activeTab === 'courses' && (
          <div className="space-y-2 max-h-72 overflow-y-auto pr-1">
            {courseList.map((c) => (
              <button
                key={c.key}
                disabled={isLoading}
                onClick={() => handleSelectCourse(c.key)}
                className="w-full text-left p-3 rounded-xl border border-border hover:border-accent hover:bg-accent-light/40 transition-all flex items-start justify-between group"
              >
                <div>
                  <div className="font-semibold text-[14px] text-primaryText group-hover:text-accent">
                    {c.title}
                  </div>
                  <div className="text-[12px] text-secondaryText mt-0.5">{c.desc}</div>
                </div>
                <span className="text-[11px] font-bold text-accent bg-accent-light px-2 py-0.5 rounded-md shrink-0 ml-2">
                  Load
                </span>
              </button>
            ))}
          </div>
        )}

        {/* Upload Tab Content */}
        {activeTab === 'upload' && (
          <div className="border-2 border-dashed border-border rounded-xl p-8 text-center hover:border-accent transition-colors">
            <input
              type="file"
              accept=".txt"
              id="file-upload"
              className="hidden"
              onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
            />
            <label htmlFor="file-upload" className="cursor-pointer flex flex-col items-center">
              <div className="w-12 h-12 rounded-xl bg-accent-light text-accent flex items-center justify-center mb-3">
                <Upload className="w-6 h-6" />
              </div>
              <span className="font-semibold text-[14px] text-primaryText">
                {selectedFile ? selectedFile.name : 'Click to select WhatsApp chat export .txt'}
              </span>
              <span className="text-[12px] text-secondaryText mt-1">Supports standard iOS & Android formats</span>
            </label>
          </div>
        )}

        {/* Paste Tab Content */}
        {activeTab === 'paste' && (
          <div>
            <textarea
              rows={6}
              value={pastedText}
              onChange={(e) => setPastedText(e.target.value)}
              placeholder="Paste WhatsApp messages here..."
              className="w-full p-3 rounded-xl border border-border text-[13px] font-mono focus:outline-accent bg-app"
            />
          </div>
        )}

        {/* Privacy & Engine Controls */}
        <div className="mt-4 pt-3 border-t border-border flex items-center justify-between text-[13px]">
          <label className="flex items-center gap-2 cursor-pointer text-secondaryText select-none">
            <input
              type="checkbox"
              checked={anonymize}
              onChange={(e) => setAnonymize(e.target.checked)}
              className="rounded text-accent focus:ring-accent"
            />
            <Shield className="w-3.5 h-3.5 text-success" />
            <span>Anonymize student phone numbers & names</span>
          </label>

          <label className="flex items-center gap-2 cursor-pointer text-secondaryText select-none">
            <input
              type="checkbox"
              checked={useLiveAi}
              onChange={(e) => setUseLiveAi(e.target.checked)}
              className="rounded text-accent focus:ring-accent"
            />
            <Sparkles className="w-3.5 h-3.5 text-accent" />
            <span>Live Gemini Extraction</span>
          </label>
        </div>

        {/* Action Button */}
        {activeTab !== 'courses' && (
          <div className="mt-5">
            <button
              onClick={handleRunImport}
              disabled={isLoading || (activeTab === 'upload' && !selectedFile) || (activeTab === 'paste' && !pastedText.trim())}
              className="w-full py-2.5 rounded-xl bg-accent text-white font-semibold text-[14px] hover:bg-accent-hover transition-all disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <span>Extracting with AI...</span>
              ) : (
                <>
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Analyse & Reconcile Messages</span>
                </>
              )}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

