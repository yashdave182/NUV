import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { Heart, Syringe, Building2, AlertTriangle } from 'lucide-react'
import {
  getHealthAdvisory, getEmergencyTriage,
} from '../api/client'
import { PageHeader, Alert, LoadingCard } from '../components/ui'
import { useAppStore } from '../store/appStore'

type Tab = 'advisory' | 'vaccination' | 'camps' | 'triage'

const tabs = [
  { id: 'advisory' as Tab, icon: Heart, label: 'Health Advisory' },
  { id: 'vaccination' as Tab, icon: Syringe, label: 'Vaccination Schedule' },
  { id: 'camps' as Tab, icon: Building2, label: 'Health Camps' },
  { id: 'triage' as Tab, icon: AlertTriangle, label: 'Emergency Triage' },
]

export default function HealthPage() {
  const { phone, language } = useAppStore()
  const [activeTab, setActiveTab] = useState<Tab>('advisory')
  const [form, setForm] = useState({
    phone: phone || '',
    language: language || 'English',
    state: 'Gujarat',
    symptoms: '',
    age: '35',
    gender: 'male',
  })

  const set = (k: string, v: string) => setForm(f => ({ ...f, [k]: v }))

  const advisoryMutation = useMutation({
    mutationFn: () => getHealthAdvisory({
      phone: form.phone,
      language: form.language,
      symptoms: form.symptoms ? form.symptoms.split(',').map(s => s.trim()) : ['fever', 'fatigue'],
      age: parseInt(form.age),
      gender: form.gender,
      location: { state: form.state },
    }),
  })

  const triageMutation = useMutation({
    mutationFn: () => getEmergencyTriage({
      phone: form.phone,
      language: form.language,
      symptoms: form.symptoms ? form.symptoms.split(',').map(s => s.trim()) : ['chest pain', 'breathlessness'],
      age: parseInt(form.age),
      gender: form.gender,
      location: { state: form.state },
    }),
  })

  const currentMutation = activeTab === 'triage' ? triageMutation : advisoryMutation

  return (
    <div className="space-y-5 max-w-5xl mx-auto">
      <PageHeader title="Farmer Health & Wellness" subtitle="AI medical triage, occupational hazard advisories, and local health camps" icon={Heart} />

      <div className="flex gap-1.5 flex-wrap">
        {tabs.map(({ id, icon: Icon, label }) => (
          <button
            key={id}
            onClick={() => setActiveTab(id)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold transition-all ${
              activeTab === id
                ? 'bg-red-900/80 text-white border border-red-700/50'
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
          <label className="label">Language</label>
          <select className="select" value={form.language} onChange={e => set('language', e.target.value)}>
            {['English', 'Hindi', 'Gujarati', 'Marathi'].map(l => <option key={l}>{l}</option>)}
          </select>
        </div>
        <div className="form-group">
          <label className="label">Age</label>
          <input className="input" type="number" value={form.age} onChange={e => set('age', e.target.value)} />
        </div>
        <div className="form-group">
          <label className="label">Gender</label>
          <select className="select" value={form.gender} onChange={e => set('gender', e.target.value)}>
            <option value="male">Male</option>
            <option value="female">Female</option>
            <option value="other">Other</option>
          </select>
        </div>
        <div className="form-group sm:col-span-2">
          <label className="label">Symptoms (comma separated)</label>
          <input className="input" placeholder="e.g. skin rash, eye irritation, fever" value={form.symptoms} onChange={e => set('symptoms', e.target.value)} />
        </div>
        <div className="sm:col-span-2">
          <button className="btn-primary w-full bg-red-700 hover:bg-red-600" onClick={() => currentMutation.mutate()} disabled={currentMutation.isPending}>
            {currentMutation.isPending ? 'Analyzing Health Risk…' : `Get ${tabs.find(t => t.id === activeTab)?.label}`}
          </button>
        </div>
      </div>

      {currentMutation.isPending && <LoadingCard label="Evaluating clinical symptoms" rows={4} />}
      {currentMutation.isError && <Alert type="error" message={currentMutation.error?.message || 'Failed to process request'} />}

      {currentMutation.data?.data && (
        <div className="glass-card p-5 animate-slide-up space-y-3">
          {currentMutation.data.data.sms_summary && (
            <div className="glass-card p-4 border border-red-600/30 bg-red-900/20">
              <p className="text-xs font-semibold text-red-400 mb-1">📱 SMS Alert</p>
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
