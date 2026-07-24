import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { Leaf, Droplets, FlaskConical, Bug, CalendarDays, Microscope, Wheat, Layers, ShieldCheck, CloudSun } from 'lucide-react'
import {
  getAdvisory, getIrrigation, getFertilizer, getPestDisease,
  getCropCalendar, getSoilHealth, getVarietyRecommendation,
  getIntercropping, getCropInsurance, getWeatherAdvisory,
} from '../api/client'
import { PageHeader, Alert, LoadingCard, ConfidencePill } from '../components/ui'
import { CROPS, SOIL_TYPES, IRRIGATION_SOURCES, SEASONS, GROWTH_STAGES, STATES } from '../lib/constants'
import { useAppStore } from '../store/appStore'
import { formatDate, getPriorityColor } from '../lib/utils'
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer,
} from 'recharts'

type Tab = 'advisory' | 'irrigation' | 'fertilizer' | 'pest' | 'calendar' | 'soil' | 'variety' | 'intercrop' | 'insurance' | 'weather'

const tabs: { id: Tab; icon: React.ElementType; label: string }[] = [
  { id: 'advisory', icon: Leaf, label: 'Farm Advisory' },
  { id: 'irrigation', icon: Droplets, label: 'Irrigation' },
  { id: 'fertilizer', icon: FlaskConical, label: 'Fertilizer' },
  { id: 'pest', icon: Bug, label: 'Pest & Disease' },
  { id: 'calendar', icon: CalendarDays, label: 'Crop Calendar' },
  { id: 'soil', icon: Microscope, label: 'Soil Health' },
  { id: 'variety', icon: Wheat, label: 'Variety' },
  { id: 'intercrop', icon: Layers, label: 'Intercropping' },
  { id: 'insurance', icon: ShieldCheck, label: 'Insurance' },
  { id: 'weather', icon: CloudSun, label: 'Weather' },
]

function CommonFields({ form, onChange }: { form: Record<string, string>; onChange: (k: string, v: string) => void }) {
  const { phone, language } = useAppStore()
  return (
    <>
      <div className="form-group">
        <label className="label">Phone Number</label>
        <input className="input" placeholder="9876543210" value={form.phone || phone} onChange={e => onChange('phone', e.target.value)} />
      </div>
      <div className="form-group">
        <label className="label">Crop Type</label>
        <select className="select" value={form.crop_type} onChange={e => onChange('crop_type', e.target.value)}>
          {CROPS.map(c => <option key={c.value} value={c.value}>{c.label}</option>)}
        </select>
      </div>
      <div className="form-group">
        <label className="label">State</label>
        <select className="select" value={form.state} onChange={e => onChange('state', e.target.value)}>
          {STATES.map(s => <option key={s} value={s}>{s}</option>)}
        </select>
      </div>
      <div className="form-group">
        <label className="label">Language</label>
        <select className="select" value={form.language || language} onChange={e => onChange('language', e.target.value)}>
          {['English','Hindi','Gujarati','Hinglish','Gujlish','Marathi','Tamil','Telugu'].map(l => <option key={l} value={l}>{l}</option>)}
        </select>
      </div>
    </>
  )
}

// ─── Advisory Tab ────────────────────────────────────────────────────────────
function AdvisoryTab() {
  const { phone, language } = useAppStore()
  const [form, setForm] = useState({ phone: phone || '', crop_type: 'cotton', state: 'Gujarat', language: language || 'English', season: 'kharif', area_hectares: '2.5', soil_type: 'black_cotton', irrigation_source: 'borewell', sowing_date: '2026-06-15' })
  const set = (k: string, v: string) => setForm(f => ({ ...f, [k]: v }))

  const mutation = useMutation({
    mutationFn: () => getAdvisory({
      phone: form.phone, crop_type: form.crop_type, season: form.season,
      sowing_date: form.sowing_date, area_hectares: parseFloat(form.area_hectares) || 2.5,
      soil_type: form.soil_type, irrigation_source: form.irrigation_source,
      language: form.language,
      location: { state: form.state, latitude: 23.0, longitude: 72.0 },
    }),
  })

  const data = mutation.data?.data

  return (
    <div className="space-y-5">
      <div className="glass-card p-5 grid grid-cols-1 sm:grid-cols-2 gap-4">
        <CommonFields form={form} onChange={set} />
        <div className="form-group">
          <label className="label">Season</label>
          <select className="select" value={form.season} onChange={e => set('season', e.target.value)}>
            {SEASONS.map(s => <option key={s.value} value={s.value}>{s.label}</option>)}
          </select>
        </div>
        <div className="form-group">
          <label className="label">Sowing Date</label>
          <input type="date" className="input" value={form.sowing_date} onChange={e => set('sowing_date', e.target.value)} />
        </div>
        <div className="form-group">
          <label className="label">Soil Type</label>
          <select className="select" value={form.soil_type} onChange={e => set('soil_type', e.target.value)}>
            {SOIL_TYPES.map(s => <option key={s.value} value={s.value}>{s.label}</option>)}
          </select>
        </div>
        <div className="form-group">
          <label className="label">Irrigation Source</label>
          <select className="select" value={form.irrigation_source} onChange={e => set('irrigation_source', e.target.value)}>
            {IRRIGATION_SOURCES.map(s => <option key={s.value} value={s.value}>{s.label}</option>)}
          </select>
        </div>
        <div className="form-group">
          <label className="label">Farm Area (Hectares)</label>
          <input type="number" className="input" step="0.5" value={form.area_hectares} onChange={e => set('area_hectares', e.target.value)} />
        </div>
        <div className="sm:col-span-2">
          <button className="btn-primary w-full" onClick={() => mutation.mutate()} disabled={mutation.isPending}>
            {mutation.isPending ? 'Generating Advisory…' : 'Get Farm Advisory'}
          </button>
        </div>
      </div>

      {mutation.isPending && <LoadingCard label="Analyzing your farm data with AI" rows={5} />}
      {mutation.isError && <Alert type="error" message={mutation.error?.message || 'Failed to get advisory'} />}

      {data && (
        <div className="space-y-4 animate-slide-up">
          {/* Summary */}
          {data.sms_summary && (
            <div className="glass-card p-4 border border-agri-600/30 bg-agri-900/20">
              <p className="text-xs font-semibold text-agri-400 mb-1 uppercase tracking-wider">📱 SMS Summary</p>
              <p className="text-sm text-white">{data.sms_summary}</p>
            </div>
          )}

          {/* Advisories */}
          {data.advisories?.length > 0 && (
            <div>
              <h3 className="text-sm font-bold text-white mb-3">Recommendations ({data.advisories.length})</h3>
              <div className="space-y-3">
                {data.advisories.map((a: any, i: number) => (
                  <div key={i} className="glass-card p-4 border border-white/8">
                    <div className="flex items-start justify-between gap-3 mb-2">
                      <div>
                        <p className="font-semibold text-white text-sm">{a.title}</p>
                        <span className={`badge mt-1 ${getPriorityColor(a.priority)}`}>{a.priority}</span>
                      </div>
                      <ConfidencePill value={a.confidence_score || 0.75} />
                    </div>
                    <p className="text-sm text-gray-300 leading-relaxed">{a.description}</p>
                    {a.action_items?.length > 0 && (
                      <ul className="mt-3 space-y-1">
                        {a.action_items.map((item: string, j: number) => (
                          <li key={j} className="text-xs text-gray-400 flex items-start gap-2">
                            <span className="text-agri-500 mt-0.5">•</span>{item}
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Yield Prediction */}
          {data.yield_prediction && (
            <div className="glass-card p-4 border border-teal-600/30">
              <h3 className="text-sm font-bold text-white mb-3">📊 Yield Prediction</h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-2xl font-black text-teal-400">{data.yield_prediction.predicted_yield_tonnes_ha?.toFixed(2)}</p>
                  <p className="text-xs text-gray-400">tonnes/hectare</p>
                </div>
                <div>
                  <p className="text-sm text-gray-300">
                    Range: {data.yield_prediction.confidence_interval?.[0]?.toFixed(1)} – {data.yield_prediction.confidence_interval?.[1]?.toFixed(1)} t/ha
                  </p>
                  <ConfidencePill value={data.yield_prediction.confidence_level || 0.75} />
                </div>
              </div>
              {data.yield_prediction.risk_factors?.length > 0 && (
                <div className="mt-3">
                  <p className="text-xs text-gray-500 mb-1">Risk Factors:</p>
                  <div className="flex flex-wrap gap-1.5">
                    {data.yield_prediction.risk_factors.map((r: string, i: number) => (
                      <span key={i} className="badge-red text-[10px]">{r}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Weather forecast chart */}
          {data.weather_forecast?.length > 0 && (
            <div className="glass-card p-4">
              <h3 className="text-sm font-bold text-white mb-3">7-Day Weather Forecast</h3>
              <ResponsiveContainer width="100%" height={160}>
                <AreaChart data={data.weather_forecast.slice(0, 7)}>
                  <defs>
                    <linearGradient id="tempGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#22c55e" stopOpacity={0.4} />
                      <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                  <XAxis dataKey="date" tick={{ fill: '#6b7280', fontSize: 10 }} tickFormatter={v => v?.slice(5)} />
                  <YAxis tick={{ fill: '#6b7280', fontSize: 10 }} />
                  <Tooltip contentStyle={{ background: '#0a1628', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 12, fontSize: 12 }} />
                  <Area type="monotone" dataKey="temp_max" stroke="#22c55e" fill="url(#tempGrad)" name="Max °C" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

// ─── Irrigation Tab ────────────────────────────────────────────────────────────
function IrrigationTab() {
  const { phone, language } = useAppStore()
  const [form, setForm] = useState({ phone: phone || '', crop_type: 'cotton', state: 'Gujarat', language: language || 'English', growth_stage: 'vegetative', soil_type: 'black_cotton', irrigation_source: 'borewell', area_hectares: '2.5' })
  const set = (k: string, v: string) => setForm(f => ({ ...f, [k]: v }))

  const mutation = useMutation({
    mutationFn: () => getIrrigation({
      phone: form.phone, crop_type: form.crop_type, growth_stage: form.growth_stage,
      soil_type: form.soil_type, irrigation_source: form.irrigation_source,
      area_hectares: parseFloat(form.area_hectares),
      language: form.language,
      location: { state: form.state },
    }),
  })
  const data = mutation.data?.data

  return (
    <div className="space-y-5">
      <div className="glass-card p-5 grid grid-cols-1 sm:grid-cols-2 gap-4">
        <CommonFields form={form} onChange={set} />
        <div className="form-group">
          <label className="label">Growth Stage</label>
          <select className="select" value={form.growth_stage} onChange={e => set('growth_stage', e.target.value)}>
            {GROWTH_STAGES.map(g => <option key={g.value} value={g.value}>{g.label}</option>)}
          </select>
        </div>
        <div className="form-group">
          <label className="label">Soil Type</label>
          <select className="select" value={form.soil_type} onChange={e => set('soil_type', e.target.value)}>
            {SOIL_TYPES.map(s => <option key={s.value} value={s.value}>{s.label}</option>)}
          </select>
        </div>
        <div className="form-group">
          <label className="label">Irrigation Source</label>
          <select className="select" value={form.irrigation_source} onChange={e => set('irrigation_source', e.target.value)}>
            {IRRIGATION_SOURCES.map(s => <option key={s.value} value={s.value}>{s.label}</option>)}
          </select>
        </div>
        <div className="form-group">
          <label className="label">Area (Hectares)</label>
          <input type="number" className="input" value={form.area_hectares} onChange={e => set('area_hectares', e.target.value)} />
        </div>
        <div className="sm:col-span-2">
          <button className="btn-primary w-full" onClick={() => mutation.mutate()} disabled={mutation.isPending}>
            {mutation.isPending ? 'Calculating…' : 'Get Irrigation Schedule'}
          </button>
        </div>
      </div>

      {mutation.isPending && <LoadingCard label="Computing optimal irrigation schedule" rows={4} />}
      {mutation.isError && <Alert type="error" message={mutation.error?.message || 'Failed'} />}
      {data && (
        <div className="space-y-4 animate-slide-up">
          {(data.schedule || data.irrigation_schedule) && (
            <div className="glass-card p-5 border border-teal-600/30">
              <h3 className="text-sm font-bold text-white mb-4">Irrigation Schedule</h3>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <div className="text-center">
                  <p className="text-2xl font-bold text-teal-400">
                    {data.schedule?.interval_days || (data.irrigation_schedule?.[0] ? 5 : 7)}
                  </p>
                  <p className="text-xs text-gray-400">Days interval</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-blue-400">
                    {data.schedule?.depth_mm || data.irrigation_schedule?.[0]?.depth_mm || data.etc_mm_per_day || 35}
                  </p>
                  <p className="text-xs text-gray-400">mm depth</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-agri-400">
                    {data.schedule?.volume_m3_per_ha || data.irrigation_schedule?.[0]?.volume_m3 || 350}
                  </p>
                  <p className="text-xs text-gray-400">m³/ha</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-yellow-400">
                    ₹{Math.round(data.schedule?.cost_estimate_inr || (data.schedule?.volume_m3_per_ha || 350) * 15)}
                  </p>
                  <p className="text-xs text-gray-400">est. cost/ha</p>
                </div>
              </div>
              {data.sms_summary && <p className="text-xs text-gray-300 mt-4 border-t border-white/8 pt-3">{data.sms_summary}</p>}
            </div>
          )}
          {(data.schedule_items?.length > 0 || data.irrigation_schedule?.length > 0) && (
            <div className="glass-card p-4">
              <h3 className="text-sm font-bold text-white mb-3">Upcoming Schedule</h3>
              <table className="data-table">
                <thead><tr><th>Date</th><th>Event</th><th>Water (mm)</th></tr></thead>
                <tbody>
                  {(data.schedule_items || data.irrigation_schedule || []).map((item: any, i: number) => (
                    <tr key={i}>
                      <td>{formatDate(item.date)}</td>
                      <td>{item.activity || `Stage: ${item.stage || 'Vegetative'} (${item.water_saving_tip || 'Drip Irrigation'})`}</td>
                      <td>{item.water_mm || item.depth_mm}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

// ─── Fertilizer Tab ────────────────────────────────────────────────────────────
function FertilizerTab() {
  const { phone, language } = useAppStore()
  const [form, setForm] = useState({ phone: phone || '', crop_type: 'cotton', state: 'Gujarat', language: language || 'English', growth_stage: 'vegetative', soil_type: 'black_cotton', area_hectares: '2.5' })
  const set = (k: string, v: string) => setForm(f => ({ ...f, [k]: v }))

  const mutation = useMutation({
    mutationFn: () => getFertilizer({
      phone: form.phone, crop_type: form.crop_type, growth_stage: form.growth_stage,
      soil_type: form.soil_type, area_hectares: parseFloat(form.area_hectares),
      language: form.language, location: { state: form.state },
    }),
  })
  const data = mutation.data?.data

  return (
    <div className="space-y-5">
      <div className="glass-card p-5 grid grid-cols-1 sm:grid-cols-2 gap-4">
        <CommonFields form={form} onChange={set} />
        <div className="form-group"><label className="label">Growth Stage</label>
          <select className="select" value={form.growth_stage} onChange={e => set('growth_stage', e.target.value)}>
            {GROWTH_STAGES.map(g => <option key={g.value} value={g.value}>{g.label}</option>)}
          </select>
        </div>
        <div className="form-group"><label className="label">Soil Type</label>
          <select className="select" value={form.soil_type} onChange={e => set('soil_type', e.target.value)}>
            {SOIL_TYPES.map(s => <option key={s.value} value={s.value}>{s.label}</option>)}
          </select>
        </div>
        <div className="form-group"><label className="label">Area (Hectares)</label>
          <input type="number" className="input" value={form.area_hectares} onChange={e => set('area_hectares', e.target.value)} />
        </div>
        <div className="sm:col-span-2">
          <button className="btn-primary w-full" onClick={() => mutation.mutate()} disabled={mutation.isPending}>
            {mutation.isPending ? 'Optimizing…' : 'Get Fertilizer Recommendation'}
          </button>
        </div>
      </div>
      {mutation.isPending && <LoadingCard label="Computing NPK requirements" rows={4} />}
      {mutation.isError && <Alert type="error" message={mutation.error?.message || 'Failed'} />}
      {data && (
        <div className="space-y-4 animate-slide-up">
          {(data.nutrient_recommendation || data.recommended_npk) && (
            <div className="glass-card p-5 border border-green-600/30">
              <h3 className="text-sm font-bold text-white mb-4">Nutrient Requirement (kg/ha)</h3>
              <div className="flex flex-wrap gap-6">
                {Object.entries(data.nutrient_recommendation || data.recommended_npk || {}).map(([k, v]) => (
                  <div key={k} className="text-center">
                    <p className="text-2xl font-bold text-agri-400">{Number(v).toFixed(1)}</p>
                    <p className="text-xs text-gray-400">{k}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
          {(data.fertilizer_schedule?.length > 0 || data.fertilizers?.length > 0) && (
            <div className="glass-card p-4">
              <h3 className="text-sm font-bold text-white mb-3">Recommended Fertilizers</h3>
              <table className="data-table">
                <thead><tr><th>Fertilizer</th><th>Dose (kg/ha)</th><th>Stage / Timing</th><th>Method</th></tr></thead>
                <tbody>
                  {(data.fertilizer_schedule || data.fertilizers || []).map((f: any, i: number) => (
                    <tr key={i}>
                      <td className="font-medium">{f.fertilizer || f.name}</td>
                      <td>{f.dose_kg_per_ha?.toFixed(1) || f.dose_kg_ha?.toFixed(1)}</td>
                      <td>{f.application_stage || f.timing}</td>
                      <td>{f.application_method || '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <div className="mt-3 pt-3 border-t border-white/8 flex justify-between">
                <span className="text-xs text-gray-400">Total Estimated Cost</span>
                <span className="text-sm font-bold text-agri-400">
                  ₹{Math.round(data.total_fertilizer_cost_inr || data.total_cost_inr || 0)}
                </span>
              </div>
            </div>
          )}
          {data.sms_summary && (
            <div className="glass-card p-4 border border-agri-600/30 bg-agri-900/20">
              <p className="text-xs font-semibold text-agri-400 mb-1">📱 SMS Summary</p>
              <p className="text-sm text-white">{data.sms_summary}</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

// ─── Pest & Disease Tab ───────────────────────────────────────────────────────
function PestTab() {
  const { phone, language } = useAppStore()
  const [form, setForm] = useState({ phone: phone || '', crop_type: 'cotton', state: 'Gujarat', language: language || 'English', growth_stage: 'vegetative', symptoms: '' })
  const set = (k: string, v: string) => setForm(f => ({ ...f, [k]: v }))

  const mutation = useMutation({
    mutationFn: () => getPestDisease({
      phone: form.phone, crop_type: form.crop_type, growth_stage: form.growth_stage,
      symptoms: form.symptoms ? form.symptoms.split(',').map(s => s.trim()) : ['yellowing', 'wilting'],
      language: form.language, location: { state: form.state },
    }),
  })
  const data = mutation.data?.data

  return (
    <div className="space-y-5">
      <div className="glass-card p-5 grid grid-cols-1 sm:grid-cols-2 gap-4">
        <CommonFields form={form} onChange={set} />
        <div className="form-group"><label className="label">Growth Stage</label>
          <select className="select" value={form.growth_stage} onChange={e => set('growth_stage', e.target.value)}>
            {GROWTH_STAGES.map(g => <option key={g.value} value={g.value}>{g.label}</option>)}
          </select>
        </div>
        <div className="form-group sm:col-span-2">
          <label className="label">Symptoms (comma-separated)</label>
          <input className="input" placeholder="e.g. yellowing, leaf curl, white spots" value={form.symptoms} onChange={e => set('symptoms', e.target.value)} />
        </div>
        <div className="sm:col-span-2">
          <button className="btn-primary w-full" onClick={() => mutation.mutate()} disabled={mutation.isPending}>
            {mutation.isPending ? 'Analyzing…' : 'Identify Pest / Disease'}
          </button>
        </div>
      </div>
      {mutation.isPending && <LoadingCard label="Running disease risk classifier" rows={4} />}
      {mutation.isError && <Alert type="error" message={mutation.error?.message || 'Failed'} />}
      {data && (
        <div className="space-y-3 animate-slide-up">
          {(data.matches || data.top_matches || []).map((match: any, i: number) => (
            <div key={i} className="glass-card p-4 border border-agri-600/30 bg-slate-900/90 shadow-md">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="font-bold text-emerald-400 text-base uppercase tracking-wide">{(match.pest_disease_name || match.pest_or_disease || '').replace(/_/g, ' ')}</p>
                  <span className={`badge mt-1 ${match.severity?.toLowerCase() === 'severe' || match.severity?.toLowerCase() === 'high' ? 'badge-red' : match.severity?.toLowerCase() === 'moderate' || match.severity?.toLowerCase() === 'medium' ? 'badge-gold' : 'badge-green'}`}>{match.severity} severity</span>
                </div>
                <ConfidencePill value={match.match_confidence === 'High' ? 0.9 : match.match_confidence === 'Medium' ? 0.7 : match.confidence || 0.6} />
              </div>
              {match.spread_risk && <p className="text-xs text-slate-300 mt-2">Spread risk: <span className="text-emerald-300 font-semibold">{match.spread_risk}</span></p>}
            </div>
          ))}

          {data.immediate_actions?.length > 0 && (
            <div className="glass-card p-4 border border-agri-600/40 bg-slate-900/90 shadow-md">
              <h4 className="text-xs font-bold text-emerald-400 uppercase tracking-wider mb-2">Immediate Action Items</h4>
              <div className="space-y-1.5">
                {data.immediate_actions.map((a: string, j: number) => (
                  <p key={j} className="text-xs text-slate-200 flex gap-2"><span className="text-emerald-400 font-bold">→</span>{a}</p>
                ))}
              </div>
            </div>
          )}

          {data.sms_summary && (
            <div className="glass-card p-4 border border-agri-600/40 bg-slate-900/90 shadow-md">
              <p className="text-xs font-bold text-emerald-400 mb-1 uppercase tracking-wider">📱 SMS Summary</p>
              <p className="text-sm font-medium text-slate-100 leading-relaxed">{data.sms_summary}</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

// ─── Crop Calendar Tab ────────────────────────────────────────────────────────
function CalendarTab() {
  const { phone, language } = useAppStore()
  const [form, setForm] = useState({ phone: phone || '', crop_type: 'cotton', state: 'Gujarat', language: language || 'English', season: 'kharif', sowing_date: '2026-06-15' })
  const set = (k: string, v: string) => setForm(f => ({ ...f, [k]: v }))

  const mutation = useMutation({
    mutationFn: () => getCropCalendar({
      phone: form.phone, crop_type: form.crop_type, season: form.season,
      sowing_date: form.sowing_date, language: form.language, location: { state: form.state },
    }),
  })
  const data = mutation.data?.data

  const categoryColors: Record<string, string> = {
    sowing: 'badge-green', irrigation: 'badge-blue', fertilizer: 'badge-gold',
    pest_management: 'badge-red', harvesting: 'badge-teal', other: 'badge-orange',
  }

  return (
    <div className="space-y-5">
      <div className="glass-card p-5 grid grid-cols-1 sm:grid-cols-2 gap-4">
        <CommonFields form={form} onChange={set} />
        <div className="form-group"><label className="label">Season</label>
          <select className="select" value={form.season} onChange={e => set('season', e.target.value)}>
            {SEASONS.map(s => <option key={s.value} value={s.value}>{s.label}</option>)}
          </select>
        </div>
        <div className="form-group"><label className="label">Sowing Date</label>
          <input type="date" className="input" value={form.sowing_date} onChange={e => set('sowing_date', e.target.value)} />
        </div>
        <div className="sm:col-span-2">
          <button className="btn-primary w-full" onClick={() => mutation.mutate()} disabled={mutation.isPending}>
            {mutation.isPending ? 'Generating…' : 'Generate Crop Calendar'}
          </button>
        </div>
      </div>
      {mutation.isPending && <LoadingCard label="Building crop activity calendar" rows={6} />}
      {mutation.isError && <Alert type="error" message={mutation.error?.message || 'Failed'} />}
      {data && (
        <div className="space-y-4 animate-slide-up">
          {data.key_milestones?.length > 0 && (
            <div className="glass-card p-5 border border-agri-600/20 shadow-sm">
              <h3 className="text-xs font-bold text-agri-700 uppercase tracking-wider mb-3">Key Milestones</h3>
              <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
                {data.key_milestones.map((m: any, i: number) => (
                  <div key={i} className="p-3 rounded-xl bg-agri-500/10 border border-agri-500/20 text-center">
                    <p className="text-xs font-bold text-gray-900">{m.milestone}</p>
                    <p className="text-xs font-bold text-agri-600 mt-1">Day {m.day}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {(data.calendar?.length > 0 || data.events?.length > 0) && (
            <div className="glass-card p-5 border border-agri-600/20 shadow-sm">
              <h3 className="text-sm font-bold text-gray-900 mb-4">Weekly Activity Calendar</h3>
              <div className="space-y-2.5 max-h-96 overflow-y-auto pr-1">
                {(data.calendar || data.events || []).map((e: any, i: number) => (
                  <div key={i} className="flex items-start gap-3 p-3.5 rounded-xl bg-white/70 border border-gray-200/80 shadow-xs hover:bg-white transition-colors">
                    <div className="w-16 text-xs text-agri-700 font-bold flex-shrink-0 pt-0.5">
                      Week {e.week_after_sowing || Math.ceil((e.days_after_sowing || 1) / 7)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <p className="text-sm font-bold text-gray-900">{e.activity}</p>
                        <span className={`badge ${categoryColors[e.category] || 'badge-blue'} text-[10px]`}>
                          {e.growth_stage || e.category?.replace('_', ' ')}
                        </span>
                      </div>
                      {e.description && <p className="text-xs text-gray-600 mt-1 font-medium">{e.description}</p>}
                    </div>
                    {e.estimated_cost_inr && (
                      <div className="text-xs font-bold text-harvest-600 bg-harvest-50 px-2 py-1 rounded-md border border-harvest-200 flex-shrink-0">
                        ₹{e.estimated_cost_inr}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {data.sms_summary && (
            <div className="glass-card p-5 border border-agri-600/30 bg-agri-500/10 shadow-sm">
              <p className="text-xs font-bold text-agri-700 mb-1 uppercase tracking-wider">📱 SMS Summary</p>
              <p className="text-sm font-medium text-gray-900 leading-relaxed">{data.sms_summary}</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

// ─── Soil Health Tab ──────────────────────────────────────────────────────────
function SoilTab() {
  const { phone, language } = useAppStore()
  const [form, setForm] = useState({ phone: phone || '', state: 'Gujarat', language: language || 'English', soil_type: 'black_cotton', ph: '7.2', ec: '0.5', organic_carbon: '0.6', available_n: '200', available_p: '18', available_k: '160' })
  const set = (k: string, v: string) => setForm(f => ({ ...f, [k]: v }))

  const mutation = useMutation({
    mutationFn: () => getSoilHealth({
      phone: form.phone, language: form.language, soil_type: form.soil_type,
      location: { state: form.state },
      soil_parameters: {
        ph: parseFloat(form.ph), ec_ds_m: parseFloat(form.ec),
        organic_carbon_percent: parseFloat(form.organic_carbon),
        available_n_kg_ha: parseFloat(form.available_n),
        available_p_kg_ha: parseFloat(form.available_p),
        available_k_kg_ha: parseFloat(form.available_k),
      },
    }),
  })
  const data = mutation.data?.data

  const COLORS = ['#22c55e', '#14b8a6', '#facc15', '#60a5fa', '#f97316', '#e879f9']

  return (
    <div className="space-y-5">
      <div className="glass-card p-5 grid grid-cols-2 sm:grid-cols-3 gap-4">
        <div className="form-group"><label className="label">State</label>
          <select className="select" value={form.state} onChange={e => set('state', e.target.value)}>
            {STATES.map(s => <option key={s}>{s}</option>)}
          </select>
        </div>
        <div className="form-group"><label className="label">Soil Type</label>
          <select className="select" value={form.soil_type} onChange={e => set('soil_type', e.target.value)}>
            {SOIL_TYPES.map(s => <option key={s.value} value={s.value}>{s.label}</option>)}
          </select>
        </div>
        <div className="form-group"><label className="label">pH</label><input className="input" type="number" step="0.1" value={form.ph} onChange={e => set('ph', e.target.value)} /></div>
        <div className="form-group"><label className="label">EC (dS/m)</label><input className="input" type="number" step="0.1" value={form.ec} onChange={e => set('ec', e.target.value)} /></div>
        <div className="form-group"><label className="label">OC (%)</label><input className="input" type="number" step="0.1" value={form.organic_carbon} onChange={e => set('organic_carbon', e.target.value)} /></div>
        <div className="form-group"><label className="label">Available N (kg/ha)</label><input className="input" type="number" value={form.available_n} onChange={e => set('available_n', e.target.value)} /></div>
        <div className="form-group"><label className="label">Available P (kg/ha)</label><input className="input" type="number" value={form.available_p} onChange={e => set('available_p', e.target.value)} /></div>
        <div className="form-group"><label className="label">Available K (kg/ha)</label><input className="input" type="number" value={form.available_k} onChange={e => set('available_k', e.target.value)} /></div>
        <div className="col-span-2 sm:col-span-3">
          <button className="btn-primary w-full" onClick={() => mutation.mutate()} disabled={mutation.isPending}>
            {mutation.isPending ? 'Analyzing…' : 'Analyze Soil Health'}
          </button>
        </div>
      </div>
      {mutation.isPending && <LoadingCard label="Interpreting soil health card" rows={5} />}
      {mutation.isError && <Alert type="error" message={mutation.error?.message || 'Failed'} />}
      {data && (
        <div className="space-y-4 animate-slide-up">
          {(data.parameters?.length > 0 || data.soil_parameters?.length > 0) && (
            <div className="glass-card p-5 border border-agri-600/20 shadow-sm">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-bold text-gray-900">Soil Parameter Analysis</h3>
                {data.overall_fertility && (
                  <span className="badge-green text-xs font-bold uppercase">Overall Fertility: {data.overall_fertility}</span>
                )}
              </div>
              <div className="space-y-3">
                {(data.parameters || data.soil_parameters || []).map((p: any, i: number) => (
                  <div key={i} className="p-3 rounded-xl bg-white/70 border border-gray-200/80 shadow-xs">
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="text-xs font-bold text-gray-900">{p.parameter}</span>
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-bold text-agri-700">{p.value} {p.unit}</span>
                        <span className={`badge text-[10px] ${p.status === 'optimal' || p.status === 'high' ? 'badge-green' : p.status === 'low' ? 'badge-red' : 'badge-gold'}`}>{p.status}</span>
                      </div>
                    </div>
                    {p.recommendation && <p className="text-xs text-gray-600 mt-1">{p.recommendation}</p>}
                  </div>
                ))}
              </div>
            </div>
          )}

          {data.crop_suitability?.length > 0 && (
            <div className="glass-card p-5 border border-agri-600/20 shadow-sm">
              <h3 className="text-xs font-bold text-agri-700 uppercase tracking-wider mb-3">Crop Suitability</h3>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {data.crop_suitability.map((c: any, i: number) => (
                  <div key={i} className="p-3 rounded-xl bg-agri-500/10 border border-agri-500/20 text-center">
                    <p className="text-xs font-bold text-gray-900">{c.crop}</p>
                    <p className="text-xs font-bold text-agri-600 mt-1">{c.suitability} Suitability</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {(data.amendment_recommendations?.length > 0 || data.recommendations?.length > 0) && (
            <div className="glass-card p-5 border border-agri-600/20 shadow-sm">
              <h3 className="text-sm font-bold text-gray-900 mb-3">Soil Improvement Amendments</h3>
              <div className="space-y-2">
                {(data.amendment_recommendations || data.recommendations || []).map((r: any, i: number) => (
                  <div key={i} className="p-3 rounded-xl bg-white/70 border border-gray-200/80 flex justify-between items-center">
                    <div>
                      <p className="text-xs font-bold text-gray-900">{typeof r === 'string' ? r : r.amendment}</p>
                      {r.purpose && <p className="text-xs text-gray-600 mt-0.5">{r.purpose}</p>}
                    </div>
                    {r.cost_inr_ha && (
                      <span className="text-xs font-bold text-harvest-600 bg-harvest-50 px-2 py-1 rounded-md border border-harvest-200">
                        ₹{r.cost_inr_ha}/ha
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {data.sms_summary && (
            <div className="glass-card p-5 border border-agri-600/30 bg-agri-500/10 shadow-sm">
              <p className="text-xs font-bold text-agri-700 mb-1 uppercase tracking-wider">📱 SMS Summary</p>
              <p className="text-sm font-medium text-gray-900 leading-relaxed">{data.sms_summary}</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

// ─── Generic Tab ──────────────────────────────────────────────────────────────
function GenericTab({ tabId }: { tabId: Tab }) {
  const { phone, language } = useAppStore()
  const [form, setForm] = useState({ phone: phone || '', crop_type: 'cotton', state: 'Gujarat', language: language || 'English' })
  const set = (k: string, v: string) => setForm(f => ({ ...f, [k]: v }))

  const apiFnMap: Record<string, (d: object) => Promise<any>> = {
    variety: getVarietyRecommendation,
    intercrop: getIntercropping,
    insurance: getCropInsurance,
    weather: getWeatherAdvisory,
  }

  const mutation = useMutation({
    mutationFn: () => apiFnMap[tabId]({ phone: form.phone, crop_type: form.crop_type, language: form.language, location: { state: form.state } }),
  })
  const data = mutation.data?.data

  return (
    <div className="space-y-5">
      <div className="glass-card p-5 grid grid-cols-1 sm:grid-cols-2 gap-4">
        <CommonFields form={form} onChange={set} />
        <div className="sm:col-span-2">
          <button className="btn-primary w-full" onClick={() => mutation.mutate()} disabled={mutation.isPending}>
            {mutation.isPending ? 'Analyzing…' : `Get ${tabs.find(t => t.id === tabId)?.label}`}
          </button>
        </div>
      </div>
      {mutation.isPending && <LoadingCard rows={4} label={`Loading ${tabs.find(t => t.id === tabId)?.label}`} />}
      {mutation.isError && <Alert type="error" message={mutation.error?.message || 'Failed'} />}
      
      {data && (
        <div className="space-y-4 animate-slide-up">
          {/* ── Variety Recommendation View ── */}
          {tabId === 'variety' && (
            <>
              {data.recommended_varieties?.length > 0 && (
                <div className="glass-card p-5 border border-agri-600/20 shadow-sm">
                  <h3 className="text-sm font-bold text-gray-900 mb-4">Recommended Crop Varieties</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {data.recommended_varieties.map((v: any, i: number) => (
                      <div key={i} className="p-4 rounded-xl bg-white/70 border border-gray-200/80 shadow-xs flex flex-col justify-between">
                        <div>
                          <div className="flex justify-between items-start mb-2">
                            <h4 className="font-bold text-gray-900 text-base">{v.variety_name}</h4>
                            <span className="badge-green text-xs font-semibold">{v.yield_potential_tonnes_per_ha} t/ha</span>
                          </div>
                          <p className="text-xs text-gray-600 font-medium">Duration: <span className="text-gray-900 font-semibold">{v.duration_days} days</span></p>
                          {v.special_traits?.length > 0 && (
                            <div className="flex flex-wrap gap-1 mt-2">
                              {v.special_traits.map((t: string, j: number) => (
                                <span key={j} className="badge-teal text-[10px]">{t}</span>
                              ))}
                            </div>
                          )}
                        </div>
                        {v.seed_cost_inr_per_kg && (
                          <div className="mt-3 pt-2 border-t border-gray-200/60 flex justify-between items-center text-xs">
                            <span className="text-gray-500">Seed Cost</span>
                            <span className="font-bold text-harvest-600">₹{v.seed_cost_inr_per_kg}/kg</span>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}

          {/* ── Intercropping View ── */}
          {tabId === 'intercrop' && (
            <>
              {data.options?.length > 0 && (
                <div className="glass-card p-5 border border-agri-600/20 shadow-sm">
                  <h3 className="text-sm font-bold text-gray-900 mb-4">Compatible Intercropping Combinations</h3>
                  <div className="space-y-3">
                    {data.options.map((opt: any, i: number) => (
                      <div key={i} className="p-4 rounded-xl bg-white/70 border border-gray-200/80 shadow-xs flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
                        <div>
                          <div className="flex items-center gap-2">
                            <h4 className="font-bold text-gray-900 text-base">{data.main_crop || 'Main Crop'} + {opt.intercrop}</h4>
                            <span className="badge-gold text-xs font-semibold">Ratio {opt.row_ratio}</span>
                          </div>
                          {opt.benefits?.length > 0 && (
                            <p className="text-xs text-gray-600 mt-1">{opt.benefits.join(' • ')}</p>
                          )}
                        </div>
                        {opt.additional_cost_inr && (
                          <span className="text-xs font-bold text-harvest-600 bg-harvest-50 px-2.5 py-1 rounded-lg border border-harvest-200 flex-shrink-0">
                            Est. Cost: ₹{opt.additional_cost_inr}/ha
                          </span>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}

          {/* ── Crop Insurance View ── */}
          {tabId === 'insurance' && (
            <>
              {data.options?.length > 0 && (
                <div className="glass-card p-5 border border-agri-600/20 shadow-sm">
                  <h3 className="text-sm font-bold text-gray-900 mb-4">Available Insurance Schemes</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {data.options.map((ins: any, i: number) => (
                      <div key={i} className="p-4 rounded-xl bg-white/70 border border-gray-200/80 shadow-xs space-y-2">
                        <div className="flex justify-between items-center">
                          <h4 className="font-bold text-gray-900 text-base">{ins.scheme_name}</h4>
                          <span className="badge-blue text-xs font-semibold">Cutoff: {ins.cut_off_date}</span>
                        </div>
                        <p className="text-xs text-gray-600 font-medium">Sum Insured: <span className="text-gray-900 font-bold">₹{ins.sum_insured_per_ha}/ha</span></p>
                        <p className="text-xs text-gray-600 font-medium">Farmer Share: <span className="text-agri-700 font-bold">{ins.farmer_share_percent}%</span></p>
                        {ins.coverage?.length > 0 && (
                          <div className="mt-2 pt-2 border-t border-gray-200/60">
                            <p className="text-[11px] font-bold text-gray-500 uppercase tracking-wider mb-1">Coverage</p>
                            <div className="flex flex-wrap gap-1">
                              {ins.coverage.map((c: string, j: number) => (
                                <span key={j} className="badge-green text-[10px]">{c}</span>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}

          {/* ── Weather Advisory View ── */}
          {tabId === 'weather' && (
            <>
              {data.forecast?.length > 0 && (
                <div className="glass-card p-5 border border-agri-600/20 shadow-sm">
                  <h3 className="text-sm font-bold text-gray-900 mb-4">7-Day Local Weather Forecast</h3>
                  <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-7 gap-2">
                    {data.forecast.slice(0, 7).map((w: any, i: number) => (
                      <div key={i} className="p-3 rounded-xl bg-white/70 border border-gray-200/80 text-center shadow-xs">
                        <p className="text-[11px] font-bold text-gray-500">{formatDate(w.date)}</p>
                        <p className="text-sm font-extrabold text-agri-700 mt-1">{Math.round(w.temp_max_c)}°C</p>
                        <p className="text-[10px] text-gray-500">{w.condition}</p>
                        <p className="text-[10px] font-bold text-blue-600 mt-1">💧 {w.rainfall_mm}mm</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              {data.advisories?.length > 0 && (
                <div className="glass-card p-5 border border-agri-600/20 shadow-sm">
                  <h3 className="text-sm font-bold text-gray-900 mb-3">Weather Action Advisories</h3>
                  <div className="space-y-2">
                    {data.advisories.map((adv: any, i: number) => (
                      <div key={i} className="p-3 rounded-xl bg-white/70 border border-gray-200/80 flex items-start gap-2">
                        <span className={`badge text-[10px] mt-0.5 ${adv.priority === 'high' ? 'badge-red' : 'badge-gold'}`}>{adv.priority}</span>
                        <p className="text-xs text-gray-800 font-medium">{adv.advisory}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}

          {/* SMS Summary Card */}
          {data.sms_summary && (
            <div className="glass-card p-5 border border-agri-600/30 bg-agri-500/10 shadow-sm">
              <p className="text-xs font-bold text-agri-700 mb-1 uppercase tracking-wider">📱 SMS Summary</p>
              <p className="text-sm font-medium text-gray-900 leading-relaxed">{data.sms_summary}</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

// ─── Main Advisory Page ───────────────────────────────────────────────────────
export default function AdvisoryPage() {
  const [activeTab, setActiveTab] = useState<Tab>('advisory')

  return (
    <div className="space-y-5 max-w-5xl mx-auto">
      <PageHeader title="Farm Advisory" subtitle="AI-powered crop intelligence across 10 specialized modules" icon={Leaf} />

      {/* Tab navigation */}
      <div className="flex gap-1.5 flex-wrap">
        {tabs.map(({ id, icon: Icon, label }) => (
          <button
            key={id}
            onClick={() => setActiveTab(id)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold transition-all ${
              activeTab === id
                ? 'bg-agri-700 text-white border border-agri-600/50'
                : 'text-gray-400 hover:text-white hover:bg-white/5 border border-transparent'
            }`}
          >
            <Icon className="w-3.5 h-3.5" />{label}
          </button>
        ))}
      </div>

      {/* Tab content */}
      {activeTab === 'advisory' && <AdvisoryTab />}
      {activeTab === 'irrigation' && <IrrigationTab />}
      {activeTab === 'fertilizer' && <FertilizerTab />}
      {activeTab === 'pest' && <PestTab />}
      {activeTab === 'calendar' && <CalendarTab />}
      {activeTab === 'soil' && <SoilTab />}
      {(activeTab === 'variety' || activeTab === 'intercrop' || activeTab === 'insurance' || activeTab === 'weather') && (
        <GenericTab tabId={activeTab} />
      )}
    </div>
  )
}
