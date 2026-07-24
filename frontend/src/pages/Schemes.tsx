import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { ScrollText, CheckCircle2, FileSearch, Clock } from 'lucide-react'
import {
  searchSchemes,
  trackApplication, checkEligibility,
} from '../api/client'
import { PageHeader, Alert, LoadingCard } from '../components/ui'
import { STATES, CROPS } from '../lib/constants'
import { useAppStore } from '../store/appStore'

type Tab = 'search' | 'eligibility' | 'track' | 'detail'

const tabs = [
  { id: 'search' as Tab, icon: FileSearch, label: 'Discover Schemes' },
  { id: 'eligibility' as Tab, icon: CheckCircle2, label: 'Check Eligibility' },
  { id: 'track' as Tab, icon: Clock, label: 'Track Application' },
  { id: 'detail' as Tab, icon: ScrollText, label: 'Scheme Details' },
]

export default function SchemesPage() {
  const { phone, language } = useAppStore()
  const [activeTab, setActiveTab] = useState<Tab>('search')
  const [form, setForm] = useState({
    phone: phone || '',
    language: language || 'English',
    state: 'Gujarat',
    category: 'all',
    crop_type: 'cotton',
    land_holding_hectares: '2.5',
    application_id: '',
  })

  const set = (k: string, v: string) => setForm(f => ({ ...f, [k]: v }))

  const searchMutation = useMutation({
    mutationFn: () => searchSchemes({
      phone: form.phone,
      language: form.language,
      category: form.category,
      crop_type: form.crop_type,
      location: { state: form.state },
    }),
  })

  const eligibilityMutation = useMutation({
    mutationFn: () => checkEligibility({
      phone: form.phone,
      language: form.language,
      land_holding_hectares: parseFloat(form.land_holding_hectares),
      crop_type: form.crop_type,
      location: { state: form.state },
    }),
  })

  const trackMutation = useMutation({
    mutationFn: () => trackApplication({
      phone: form.phone,
      application_id: form.application_id || 'APP-2026-8849',
    }),
  })

  const currentMutation = activeTab === 'eligibility' ? eligibilityMutation : activeTab === 'track' ? trackMutation : searchMutation

  return (
    <div className="space-y-5 max-w-5xl mx-auto">
      <PageHeader title="Government Schemes" subtitle="Discover PM-KISAN, PMFBY, KCC & state subsidy schemes with instant eligibility check" icon={ScrollText} />

      <div className="flex gap-1.5 flex-wrap">
        {tabs.map(({ id, icon: Icon, label }) => (
          <button
            key={id}
            onClick={() => setActiveTab(id)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold transition-all ${
              activeTab === id
                ? 'bg-blue-900/80 text-white border border-blue-700/50'
                : 'text-gray-400 hover:text-white hover:bg-white/5 border border-transparent'
            }`}
          >
            <Icon className="w-3.5 h-3.5" />{label}
          </button>
        ))}
      </div>

      <div className="glass-card p-5 grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="form-group">
          <label className="label">Phone</label>
          <input className="input" value={form.phone} onChange={e => set('phone', e.target.value)} />
        </div>
        <div className="form-group">
          <label className="label">State</label>
          <select className="select" value={form.state} onChange={e => set('state', e.target.value)}>
            {STATES.map(s => <option key={s}>{s}</option>)}
          </select>
        </div>

        {activeTab === 'search' && (
          <div className="form-group sm:col-span-2">
            <label className="label">Category</label>
            <select className="select" value={form.category} onChange={e => set('category', e.target.value)}>
              <option value="all">All Categories (Income Support, Insurance, Equipment, Subsidy)</option>
              <option value="financial_support">Direct Financial Support</option>
              <option value="crop_insurance">Crop Insurance</option>
              <option value="equipment_subsidy">Machinery & Solar Subsidy</option>
            </select>
          </div>
        )}

        {activeTab === 'eligibility' && (
          <>
            <div className="form-group">
              <label className="label">Land Holding (Hectares)</label>
              <input className="input" type="number" step="0.5" value={form.land_holding_hectares} onChange={e => set('land_holding_hectares', e.target.value)} />
            </div>
            <div className="form-group">
              <label className="label">Primary Crop</label>
              <select className="select" value={form.crop_type} onChange={e => set('crop_type', e.target.value)}>
                {CROPS.map(c => <option key={c.value} value={c.value}>{c.label}</option>)}
              </select>
            </div>
          </>
        )}

        {activeTab === 'track' && (
          <div className="form-group sm:col-span-2">
            <label className="label">Application Reference ID</label>
            <input className="input" placeholder="e.g. PMK-2026-99381" value={form.application_id} onChange={e => set('application_id', e.target.value)} />
          </div>
        )}

        <div className="sm:col-span-2">
          <button className="btn-primary w-full bg-blue-600 hover:bg-blue-500" onClick={() => currentMutation.mutate()} disabled={currentMutation.isPending}>
            {currentMutation.isPending ? 'Searching Schemes…' : `Run ${tabs.find(t => t.id === activeTab)?.label}`}
          </button>
        </div>
      </div>

      {currentMutation.isPending && <LoadingCard label="Evaluating government scheme databases" rows={4} />}
      {currentMutation.isError && <Alert type="error" message={currentMutation.error?.message || 'Failed'} />}

      {currentMutation.data?.data && (
        <div className="glass-card p-5 animate-slide-up space-y-3">
          {currentMutation.data.data.sms_summary && (
            <div className="glass-card p-4 border border-blue-600/30 bg-blue-900/20">
              <p className="text-xs font-semibold text-blue-400 mb-1">📱 SMS Summary</p>
              <p className="text-sm text-white">{currentMutation.data.data.sms_summary}</p>
            </div>
          )}
          <pre className="text-xs text-gray-300 whitespace-pre-wrap font-mono bg-black/30 rounded-xl p-4 max-h-96 overflow-y-auto">
            {JSON.stringify(currentMutation.data.data, null, 2)}
          </pre>
        </div>
      )}
    </div>
  )
}
