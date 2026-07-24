import { useState } from 'react'
import { Settings, Globe, Phone, Check, Server } from 'lucide-react'
import { PageHeader, Alert } from '../components/ui'
import { useAppStore } from '../store/appStore'
import { LANGUAGES, API_BASE } from '../lib/constants'

export default function SettingsPage() {
  const { phone, setPhone, language, setLanguage } = useAppStore()
  const [phoneInput, setPhoneInput] = useState(phone)
  const [langInput, setLangInput] = useState(language)
  const [saved, setSaved] = useState(false)

  const handleSave = () => {
    setPhone(phoneInput)
    setLanguage(langInput)
    setSaved(true)
    setTimeout(() => setSaved(false), 3000)
  }

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      <PageHeader title="Platform Settings" subtitle="Configure farmer profile, active language, and API connection" icon={Settings} />

      {saved && <Alert type="success" message="Settings saved successfully!" dismissible />}

      {/* Profile Settings */}
      <div className="glass-card p-6 space-y-4">
        <div className="flex items-center gap-2 border-b border-white/8 pb-3">
          <Phone className="w-5 h-5 text-agri-400" />
          <h3 className="text-base font-bold text-white">Farmer Mobile Profile</h3>
        </div>
        <div className="form-group">
          <label className="label">10-Digit Mobile Number (Indian)</label>
          <input
            className="input"
            placeholder="9876543210"
            value={phoneInput}
            onChange={e => setPhoneInput(e.target.value)}
          />
          <p className="text-[11px] text-gray-500 mt-1">Used to identify your farm profile, alerts, and SMS advisory log.</p>
        </div>
      </div>

      {/* Language Settings */}
      <div className="glass-card p-6 space-y-4">
        <div className="flex items-center gap-2 border-b border-white/8 pb-3">
          <Globe className="w-5 h-5 text-teal-400" />
          <h3 className="text-base font-bold text-white">Multilingual AI Preference</h3>
        </div>
        <div className="form-group">
          <label className="label">Preferred Language (14 supported)</label>
          <select className="select" value={langInput} onChange={e => setLangInput(e.target.value)}>
            {LANGUAGES.map(l => (
              <option key={l} value={l}>{l}</option>
            ))}
          </select>
          <p className="text-[11px] text-gray-500 mt-1">
            Responses and SMS summaries will be rendered in your selected language (including script-transliterated languages like Hinglish & Gujlish).
          </p>
        </div>
      </div>

      {/* System Status */}
      <div className="glass-card p-6 space-y-4">
        <div className="flex items-center gap-2 border-b border-white/8 pb-3">
          <Server className="w-5 h-5 text-gold-400" />
          <h3 className="text-base font-bold text-white">Backend API Server</h3>
        </div>
        <div className="flex items-center justify-between py-2 border-b border-white/5">
          <span className="text-xs text-gray-400">Server Endpoint</span>
          <span className="text-xs font-mono text-agri-400">{API_BASE}</span>
        </div>
        <div className="flex items-center justify-between py-2 border-b border-white/5">
          <span className="text-xs text-gray-400">Active Endpoints</span>
          <span className="text-xs font-bold text-white">37 Endpoints Registered</span>
        </div>
        <div className="flex items-center justify-between py-2">
          <span className="text-xs text-gray-400">IoT Integration</span>
          <span className="badge-green text-[10px]">ThingSpeak Enabled</span>
        </div>
      </div>

      <button className="btn-primary w-full py-3 text-base flex items-center justify-center gap-2" onClick={handleSave}>
        <Check className="w-5 h-5" /> Save Preferences
      </button>
    </div>
  )
}
