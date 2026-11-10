import React, { useState, useEffect } from 'react';
import { Settings as SettingsIcon, Key, Cpu, Shield, Save, CheckCircle2 } from 'lucide-react';
import { fetchSettings, updateSettings } from '../api';
import { AppSettings } from '../types';

export const SettingsView: React.FC = () => {
  const [settings, setSettings] = useState<AppSettings | null>(null);
  const [apiKey, setApiKey] = useState('');
  const [model, setModel] = useState('gemini-2.5-flash');
  const [isSaved, setIsSaved] = useState(false);

  useEffect(() => {
    fetchSettings().then((s) => {
      setSettings(s);
      setModel(s.model);
    });
  }, []);

  const handleSave = async () => {
    await updateSettings({ api_key: apiKey, model });
    setIsSaved(true);
    setTimeout(() => setIsSaved(false), 3000);
  };

  return (
    <div className="space-y-6 max-w-2xl">
      <div className="bg-white p-5 rounded-2xl border border-border shadow-card">
        <h2 className="text-[18px] font-bold text-primaryText flex items-center gap-2">
          <SettingsIcon className="w-5 h-5 text-accent" />
          <span>Application & Model Settings</span>
        </h2>
        <p className="text-[13px] text-secondaryText mt-0.5">
          Configure Gemini AI credentials, entity extraction models, and campus timezone defaults.
        </p>
      </div>

      {/* Gemini API Key */}
      <div className="bg-white p-5 rounded-2xl border border-border shadow-card space-y-4">
        <div className="flex items-center gap-2.5 border-b border-border pb-3">
          <Key className="w-5 h-5 text-accent" />
          <h3 className="font-bold text-[15px] text-primaryText">Gemini API Configuration</h3>
        </div>

        <div className="space-y-2">
          <label className="text-[13px] font-medium text-primaryText block">
            Gemini API Key
          </label>
          <input
            type="password"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            placeholder="AIzaSy... (Leave empty to use Deterministic Demo Mode)"
            className="w-full p-2.5 bg-app border border-border rounded-xl text-[14px] text-primaryText focus:outline-accent"
          />
          <span className="text-[11px] text-secondaryText block">
            Get a free API key from{' '}
            <a
              href="https://aistudio.google.com/"
              target="_blank"
              rel="noreferrer"
              className="text-accent underline font-semibold"
            >
              Google AI Studio
            </a>
            . In Demo Mode, pre-computed deterministic extraction is used.
          </span>
        </div>

        <div className="space-y-2">
          <label className="text-[13px] font-medium text-primaryText block flex items-center gap-1.5">
            <Cpu className="w-4 h-4 text-secondaryText" />
            <span>Extraction Model</span>
          </label>
          <select
            value={model}
            onChange={(e) => setModel(e.target.value)}
            className="w-full p-2.5 bg-app border border-border rounded-xl text-[13px] font-medium text-primaryText focus:outline-accent"
          >
            <option value="gemini-2.5-flash">gemini-2.5-flash (Recommended, Fast & Multilingual)</option>
            <option value="gemini-1.5-flash">gemini-1.5-flash (Stable)</option>
            <option value="gemini-1.5-pro">gemini-1.5-pro (High Reasoning)</option>
          </select>
        </div>

        <div className="pt-2 flex items-center justify-between">
          <span className="text-[12px] text-secondaryText">
            {settings?.has_api_key ? (
              <span className="text-success font-semibold flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5" /> API Key Configured
              </span>
            ) : (
              <span className="text-amber-700 font-medium">Using Deterministic Demo Mode</span>
            )}
          </span>

          <button
            onClick={handleSave}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-accent text-white font-semibold text-[13px] hover:bg-accent-hover transition-colors shadow-xs"
          >
            <Save className="w-4 h-4" />
            <span>{isSaved ? 'Saved!' : 'Save Settings'}</span>
          </button>
        </div>
      </div>

      {/* Capstone Attribution */}
      <div className="bg-white p-5 rounded-2xl border border-border shadow-card space-y-2">
        <h3 className="font-bold text-[14px] text-primaryText flex items-center gap-2">
          <Shield className="w-4 h-4 text-accent" />
          <span>IIIT Hyderabad AI for Product Management Capstone</span>
        </h3>
        <p className="text-[13px] text-secondaryText leading-relaxed">
          Deadline Radar eliminates communication chaos in university WhatsApp/Telegram channels by
          combining multilingual entity extraction, postponement tracking, and conflict detection with standard RFC 5545 calendar export.
        </p>
      </div>
    </div>
  );
};

