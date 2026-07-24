import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { ShoppingCart, TrendingUp, Truck, Warehouse, AlertCircle, BarChart3, Bell, Brain, MapPin } from 'lucide-react'
import {
  getMandiPrices, getPriceTrend, getSellDecision, getTransportOptimize,
  getStorageAdvisory, getSpoilagePrediction, setPriceAlert, checkPriceAlert,
  getMarketIntelligence, getMandiList,
} from '../api/client'
import { PageHeader, Alert, LoadingCard, ConfidencePill } from '../components/ui'
import { CROPS, STATES } from '../lib/constants'
import { useAppStore } from '../store/appStore'
import { formatDate, getTrendIcon } from '../lib/utils'
import {
  AreaChart, Area, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine,
} from 'recharts'

type Tab = 'prices' | 'forecast' | 'sell' | 'transport' | 'storage' | 'spoilage' | 'alert' | 'intelligence' | 'mandis'

const tabs = [
  { id: 'prices' as Tab, icon: ShoppingCart, label: 'Mandi Prices' },
  { id: 'forecast' as Tab, icon: TrendingUp, label: 'Price Forecast' },
  { id: 'sell' as Tab, icon: Brain, label: 'Sell Decision' },
  { id: 'transport' as Tab, icon: Truck, label: 'Transport' },
  { id: 'storage' as Tab, icon: Warehouse, label: 'Storage' },
  { id: 'spoilage' as Tab, icon: AlertCircle, label: 'Spoilage Risk' },
  { id: 'alert' as Tab, icon: Bell, label: 'Price Alert' },
  { id: 'intelligence' as Tab, icon: BarChart3, label: 'Intelligence' },
  { id: 'mandis' as Tab, icon: MapPin, label: 'Find Mandis' },
]

function CommonForm({ form, onChange }: { form: Record<string,string>; onChange: (k:string,v:string) => void }) {
  return (
    <>
      <div className="form-group"><label className="label">Phone</label>
        <input className="input" placeholder="9876543210" value={form.phone} onChange={e => onChange('phone', e.target.value)} />
      </div>
      <div className="form-group"><label className="label">Crop Type</label>
        <select className="select" value={form.crop_type} onChange={e => onChange('crop_type', e.target.value)}>
          {CROPS.map(c => <option key={c.value} value={c.value}>{c.label}</option>)}
        </select>
      </div>
      <div className="form-group"><label className="label">State</label>
        <select className="select" value={form.state} onChange={e => onChange('state', e.target.value)}>
          {STATES.map(s => <option key={s} value={s}>{s}</option>)}
        </select>
      </div>
    </>
  )
}

// ─── Mandi Prices ─────────────────────────────────────────────────────────────
function MandiPricesTab() {
  const { phone, language } = useAppStore()
  const [form, setForm] = useState({ phone: phone||'', crop_type: 'cotton', state: 'Gujarat', language: language||'English' })
  const set = (k:string,v:string) => setForm(f => ({...f,[k]:v}))
  const mutation = useMutation({ mutationFn: () => getMandiPrices({ phone: form.phone, crop_type: form.crop_type, language: form.language, location: { state: form.state } }) })
  const data = mutation.data?.data

  return (
    <div className="space-y-5">
      <div className="glass-card p-5 grid grid-cols-1 sm:grid-cols-2 gap-4">
        <CommonForm form={form} onChange={set} />
        <div className="form-group"><label className="label">Language</label>
          <select className="select" value={form.language} onChange={e => set('language', e.target.value)}>
            {['English','Hindi','Gujarati','Marathi'].map(l => <option key={l}>{l}</option>)}
          </select>
        </div>
        <div className="sm:col-span-2"><button className="btn-primary w-full" onClick={() => mutation.mutate()} disabled={mutation.isPending}>{mutation.isPending ? 'Fetching…' : 'Get Real Mandi Prices'}</button></div>
      </div>
      {mutation.isPending && <LoadingCard label="Fetching live mandi data" rows={5} />}
      {mutation.isError && <Alert type="error" message={mutation.error?.message||'Failed'} />}
      {data && (
        <div className="space-y-4 animate-slide-up">
          {data.sms_summary && (
            <div className="glass-card p-4 border border-agri-600/30 bg-agri-900/20">
              <p className="text-xs font-semibold text-agri-400 mb-1">📱 SMS Summary</p>
              <p className="text-sm text-white">{data.sms_summary}</p>
            </div>
          )}
          {data.prices?.length > 0 && (
            <div className="glass-card p-4">
              <h3 className="text-sm font-bold text-white mb-3">Current Mandi Prices</h3>
              <table className="data-table">
                <thead><tr><th>Mandi</th><th>Modal (₹/q)</th><th>Min</th><th>Max</th><th>Arrivals</th><th>Date</th></tr></thead>
                <tbody>
                  {data.prices.map((p:any, i:number) => (
                    <tr key={i}>
                      <td className="font-medium">{p.mandi_name}</td>
                      <td className="font-bold text-agri-400">₹{p.modal_price?.toLocaleString()}</td>
                      <td className="text-gray-400">₹{p.min_price?.toLocaleString()}</td>
                      <td className="text-gray-400">₹{p.max_price?.toLocaleString()}</td>
                      <td>{p.arrival_tonnes} t</td>
                      <td className="text-gray-400">{formatDate(p.date)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          {data.price_statistics && (
            <div className="grid grid-cols-3 gap-3">
              {[
                { label: 'Average Price', value: `₹${data.price_statistics.avg_price?.toLocaleString()}`, sub: '/quintal' },
                { label: 'Best Price', value: `₹${data.price_statistics.max_price?.toLocaleString()}`, sub: 'max modal' },
                { label: 'Total Arrivals', value: `${data.price_statistics.total_arrival_tonnes?.toFixed(1)}t`, sub: 'today' },
              ].map(({ label, value, sub }) => (
                <div key={label} className="glass-card p-4 text-center border border-white/8">
                  <p className="text-xl font-bold text-agri-400">{value}</p>
                  <p className="text-[10px] text-gray-400">{label}</p>
                  <p className="text-[10px] text-gray-600">{sub}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

// ─── Price Forecast ───────────────────────────────────────────────────────────
function ForecastTab() {
  const { phone, language } = useAppStore()
  const [form, setForm] = useState({ phone: phone||'', crop_type: 'cotton', state: 'Gujarat', language: language||'English', horizon_days: '14' })
  const set = (k:string,v:string) => setForm(f => ({...f,[k]:v}))
  const mutation = useMutation({ mutationFn: () => getPriceTrend({ phone: form.phone, crop_type: form.crop_type, horizon_days: parseInt(form.horizon_days), language: form.language, location: { state: form.state } }) })
  const data = mutation.data?.data

  return (
    <div className="space-y-5">
      <div className="glass-card p-5 grid grid-cols-1 sm:grid-cols-2 gap-4">
        <CommonForm form={form} onChange={set} />
        <div className="form-group"><label className="label">Forecast Horizon (days)</label>
          <select className="select" value={form.horizon_days} onChange={e => set('horizon_days', e.target.value)}>
            {['7','14','21','30'].map(d => <option key={d} value={d}>{d} days</option>)}
          </select>
        </div>
        <div className="sm:col-span-2"><button className="btn-primary w-full" onClick={() => mutation.mutate()} disabled={mutation.isPending}>{mutation.isPending ? 'Forecasting…' : 'Get ML Price Forecast'}</button></div>
      </div>
      {mutation.isPending && <LoadingCard label="Running price forecasting model" rows={4} />}
      {mutation.isError && <Alert type="error" message={mutation.error?.message||'Failed'} />}
      {data && (
        <div className="space-y-4 animate-slide-up">
          {/* Summary / Statistics Header Cards */}
          {data.statistics && (
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div className="glass-card p-4 text-center border border-agri-600/20 bg-white/70 shadow-xs">
                <p className="text-xl font-bold text-gray-900">₹{data.statistics.current?.toLocaleString()}</p>
                <p className="text-xs text-gray-500 font-medium mt-0.5">Current Price / q</p>
              </div>
              <div className="glass-card p-4 text-center border border-agri-600/20 bg-white/70 shadow-xs">
                <p className="text-xl font-bold text-agri-600">₹{Math.round(data.statistics.avg)?.toLocaleString()}</p>
                <p className="text-xs text-gray-500 font-medium mt-0.5">30-Day Avg</p>
              </div>
              <div className="glass-card p-4 text-center border border-agri-600/20 bg-white/70 shadow-xs">
                <p className={`text-xl font-bold ${data.statistics.change_7d >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {data.statistics.change_7d >= 0 ? '+' : ''}{data.statistics.change_7d}%
                </p>
                <p className="text-xs text-gray-500 font-medium mt-0.5">7-Day Change</p>
              </div>
              <div className="glass-card p-4 text-center border border-agri-600/20 bg-white/70 shadow-xs">
                <p className="text-xl font-bold text-harvest-600 uppercase text-xs tracking-wider pt-1">{data.trend || data.price_volatility || 'Stable'}</p>
                <p className="text-xs text-gray-500 font-medium mt-1">Market Trend</p>
              </div>
            </div>
          )}

          {/* Price Trend Area Chart */}
          {(data.trend_data?.length > 0 || data.price_trend?.length > 0) && (
            <div className="glass-card p-5 border border-agri-600/20 shadow-sm">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-bold text-gray-900">Price Trend & Horizon Forecast</h3>
                {(data.trend || data.summary?.trend) && (
                  <span className={`badge ${ (data.trend || data.summary?.trend).includes('up') || (data.trend || data.summary?.trend).includes('bull') ? 'badge-green' : (data.trend || data.summary?.trend).includes('down') ? 'badge-red' : 'badge-gold' }`}>
                    {getTrendIcon(data.trend || data.summary?.trend)} {data.trend || data.summary?.trend}
                  </span>
                )}
              </div>
              <ResponsiveContainer width="100%" height={230}>
                <AreaChart data={data.trend_data || data.price_trend}>
                  <defs>
                    <linearGradient id="priceGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#16a34a" stopOpacity={0.4}/>
                      <stop offset="95%" stopColor="#16a34a" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.06)" />
                  <XAxis dataKey="date" tick={{ fill: '#4b5563', fontSize: 10 }} tickFormatter={v => v?.slice(5)} />
                  <YAxis tick={{ fill: '#4b5563', fontSize: 10 }} tickFormatter={v => `₹${v}`} domain={['dataMin - 100', 'dataMax + 100']} />
                  <Tooltip contentStyle={{ background: '#ffffff', border: '1px solid rgba(0,0,0,0.1)', borderRadius: 12, fontSize: 12, boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }} formatter={(v: any) => [`₹${v?.toLocaleString()}`, 'Modal Price']} />
                  <Area type="monotone" dataKey="modal_price" stroke="#16a34a" strokeWidth={2.5} fill="url(#priceGrad)" name="Modal Price ₹/q" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Observations & Insights */}
          {data.key_observations?.length > 0 && (
            <div className="glass-card p-5 border border-agri-600/20 shadow-sm">
              <h3 className="text-sm font-bold text-gray-900 mb-3">Key Observations</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {data.key_observations.map((obs: string, i: number) => (
                  <div key={i} className="p-3 rounded-xl bg-white/70 border border-gray-200/80 text-xs font-medium text-gray-800 flex items-center gap-2">
                    <span className="text-agri-600 font-bold">●</span> {obs}
                  </div>
                ))}
              </div>
            </div>
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

// ─── Sell Decision ────────────────────────────────────────────────────────────
function SellDecisionTab() {
  const { phone, language } = useAppStore()
  const [form, setForm] = useState({ phone: phone||'', crop_type: 'cotton', state: 'Gujarat', language: language||'English', quantity_tonnes: '5', current_price: '6500', storage_available: 'false' })
  const set = (k:string,v:string) => setForm(f => ({...f,[k]:v}))
  const mutation = useMutation({
    mutationFn: () => getSellDecision({
      phone: form.phone, crop_type: form.crop_type, language: form.language,
      quantity_tonnes: parseFloat(form.quantity_tonnes),
      current_price: parseFloat(form.current_price),
      storage_available: form.storage_available === 'true',
      location: { state: form.state },
    }),
  })
  const data = mutation.data?.data

  const decisionColors: Record<string,string> = { sell: 'border-agri-600/50 bg-agri-900/20', store: 'border-teal-600/50 bg-teal-900/20', transport: 'border-yellow-600/50 bg-yellow-900/20' }

  return (
    <div className="space-y-5">
      <div className="glass-card p-5 grid grid-cols-1 sm:grid-cols-2 gap-4">
        <CommonForm form={form} onChange={set} />
        <div className="form-group"><label className="label">Quantity (Tonnes)</label><input className="input" type="number" value={form.quantity_tonnes} onChange={e => set('quantity_tonnes', e.target.value)} /></div>
        <div className="form-group"><label className="label">Current Price (₹/q)</label><input className="input" type="number" value={form.current_price} onChange={e => set('current_price', e.target.value)} /></div>
        <div className="form-group"><label className="label">Storage Available?</label>
          <select className="select" value={form.storage_available} onChange={e => set('storage_available', e.target.value)}>
            <option value="true">Yes</option><option value="false">No</option>
          </select>
        </div>
        <div className="sm:col-span-2"><button className="btn-primary w-full" onClick={() => mutation.mutate()} disabled={mutation.isPending}>{mutation.isPending ? 'Analyzing…' : 'Get Sell/Store/Transport Decision'}</button></div>
      </div>
      {mutation.isPending && <LoadingCard label="Computing optimal post-harvest strategy" rows={5} />}
      {mutation.isError && <Alert type="error" message={mutation.error?.message||'Failed'} />}
      {data && (
        <div className="space-y-4 animate-slide-up">
          {data.recommended_action && (
            <div className="glass-card p-5 border border-agri-600/30 bg-white/80 shadow-sm">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-12 h-12 rounded-2xl bg-agri-500/10 border border-agri-500/30 flex items-center justify-center">
                  <Brain className="w-6 h-6 text-agri-700" />
                </div>
                <div>
                  <p className="text-xs text-agri-700 uppercase font-bold tracking-wider">AI Recommendation</p>
                  <p className="text-lg font-bold text-gray-900 capitalize">
                    {data.recommended_action.mandi_name ? `${data.recommended_action.mandi_name} (${data.recommended_action.mandi_distance_km} km)` : (data.recommended_action.action || '').replace(/_/g,' ')}
                  </p>
                </div>
                <div className="ml-auto"><ConfidencePill value={0.88} /></div>
              </div>
              <p className="text-xs font-medium text-gray-700 leading-relaxed mb-3">
                {data.recommended_action.reasoning || 'Transport to highest realization mandi.'}
              </p>

              {data.recommended_action.total_net_income && (
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-3 border-t border-gray-200/80">
                  <div className="text-center">
                    <p className="text-xs text-gray-500">Expected Price</p>
                    <p className="text-sm font-bold text-agri-700">₹{data.recommended_action.expected_price_per_quintal}/q</p>
                  </div>
                  <div className="text-center">
                    <p className="text-xs text-gray-500">Net / Quintal</p>
                    <p className="text-sm font-bold text-agri-700">₹{data.recommended_action.net_realisation_per_quintal}/q</p>
                  </div>
                  <div className="text-center">
                    <p className="text-xs text-gray-500">Total Net Income</p>
                    <p className="text-sm font-bold text-harvest-600">₹{data.recommended_action.total_net_income?.toLocaleString()}</p>
                  </div>
                  <div className="text-center">
                    <p className="text-xs text-gray-500">Total Costs</p>
                    <p className="text-sm font-bold text-gray-900">₹{data.recommended_action.total_costs}</p>
                  </div>
                </div>
              )}
            </div>
          )}

          {data.options?.length > 0 && (
            <div className="glass-card p-5 border border-agri-600/20 shadow-sm">
              <h3 className="text-sm font-bold text-gray-900 mb-3">Mandi Option Comparison</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {data.options.map((opt: any, i: number) => (
                  <div key={i} className={`p-4 rounded-xl border ${i === 0 ? 'border-agri-600/50 bg-agri-500/10' : 'border-gray-200/80 bg-white/70'} shadow-xs space-y-2`}>
                    <div className="flex items-center justify-between">
                      <p className="font-bold text-gray-900 text-sm">{opt.mandi_name || opt.action?.replace(/_/g,' ')}</p>
                      {i === 0 && <span className="badge-green text-[10px]">Best Choice</span>}
                    </div>
                    <div className="flex justify-between items-baseline">
                      <p className="text-xl font-bold text-agri-700">₹{opt.total_net_income?.toLocaleString() || opt.expected_revenue?.toLocaleString()}</p>
                      <span className="text-xs font-semibold text-gray-500">{opt.mandi_distance_km ? `${opt.mandi_distance_km} km` : ''}</span>
                    </div>
                    <p className="text-[11px] text-gray-600">
                      Expected Price: <span className="font-bold text-gray-900">₹{opt.expected_price_per_quintal}/q</span> • Total Costs: <span className="font-bold text-gray-900">₹{opt.total_costs}</span>
                    </p>
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

// ─── Spoilage Prediction ──────────────────────────────────────────────────────
function SpoilageTab() {
  const { phone, language } = useAppStore()
  const [form, setForm] = useState({ phone: phone||'', crop_type: 'cotton', state: 'Gujarat', language: language||'English', storage_days: '30', temperature: '28', humidity: '75', storage_type: 'warehouse' })
  const set = (k:string,v:string) => setForm(f => ({...f,[k]:v}))
  const mutation = useMutation({
    mutationFn: () => getSpoilagePrediction({
      phone: form.phone, crop_type: form.crop_type, language: form.language,
      storage_days: parseInt(form.storage_days),
      temperature_celsius: parseFloat(form.temperature),
      humidity_percent: parseFloat(form.humidity),
      storage_type: form.storage_type,
      location: { state: form.state },
    }),
  })
  const data = mutation.data?.data

  return (
    <div className="space-y-5">
      <div className="glass-card p-5 grid grid-cols-1 sm:grid-cols-2 gap-4">
        <CommonForm form={form} onChange={set} />
        <div className="form-group"><label className="label">Storage Days</label><input className="input" type="number" value={form.storage_days} onChange={e => set('storage_days', e.target.value)} /></div>
        <div className="form-group"><label className="label">Temperature (°C)</label><input className="input" type="number" value={form.temperature} onChange={e => set('temperature', e.target.value)} /></div>
        <div className="form-group"><label className="label">Humidity (%)</label><input className="input" type="number" value={form.humidity} onChange={e => set('humidity', e.target.value)} /></div>
        <div className="form-group"><label className="label">Storage Type</label>
          <select className="select" value={form.storage_type} onChange={e => set('storage_type', e.target.value)}>
            {['open','shed','warehouse','cold_storage'].map(t => <option key={t} value={t}>{t.replace('_',' ')}</option>)}
          </select>
        </div>
        <div className="sm:col-span-2"><button className="btn-primary w-full" onClick={() => mutation.mutate()} disabled={mutation.isPending}>{mutation.isPending ? 'Predicting…' : 'Predict Spoilage Risk'}</button></div>
      </div>
      {mutation.isPending && <LoadingCard label="Modeling spoilage curves" rows={4} />}
      {data && (
        <div className="space-y-4 animate-slide-up">
          {(data.predictions?.length > 0 || data.spoilage_curve?.length > 0) && (
            <div className="glass-card p-5 border border-agri-600/20 shadow-sm">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-sm font-bold text-gray-900">30-Day Spoilage & Quality Risk Curve</h3>
                {data.critical_threshold_day && (
                  <span className="badge-gold text-xs font-bold">Action By Day {data.recommended_action_day || 15}</span>
                )}
              </div>
              <ResponsiveContainer width="100%" height={220}>
                <AreaChart data={data.predictions || data.spoilage_curve}>
                  <defs>
                    <linearGradient id="spoilGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#dc2626" stopOpacity={0.4}/>
                      <stop offset="95%" stopColor="#dc2626" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.06)" />
                  <XAxis dataKey="day" tick={{ fill: '#4b5563', fontSize: 10 }} label={{ value: 'Storage Days', position: 'insideBottom', fill: '#6b7280', fontSize: 10, offset: -2 }} />
                  <YAxis tick={{ fill: '#4b5563', fontSize: 10 }} tickFormatter={v => `${v}%`} domain={[90, 100]} />
                  <Tooltip contentStyle={{ background: '#ffffff', border: '1px solid rgba(0,0,0,0.1)', borderRadius: 12, fontSize: 12, boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }} formatter={(v:any) => [`${v?.toFixed(1)}%`, 'Quality']} />
                  <ReferenceLine y={95} stroke="#d97706" strokeDasharray="4 2" label={{ value: 'Warning', fill: '#d97706', fontSize: 10 }} />
                  <Area type="monotone" dataKey="remaining_quality_percent" stroke="#dc2626" strokeWidth={2.5} fill="url(#spoilGrad)" name="Remaining Quality %" />
                </AreaChart>
              </ResponsiveContainer>
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

// ─── Price Alert Tab ──────────────────────────────────────────────────────────
function PriceAlertTab() {
  const { phone } = useAppStore()
  const [form, setForm] = useState({ phone: phone||'', crop_type: 'cotton', state: 'Gujarat', threshold_price: '7000', alert_type: 'above' })
  const set = (k:string,v:string) => setForm(f => ({...f,[k]:v}))
  const setupMutation = useMutation({
    mutationFn: () => setPriceAlert({ phone: form.phone, crop_type: form.crop_type, threshold_price: parseFloat(form.threshold_price), alert_type: form.alert_type, location: { state: form.state } }),
  })
  const checkMutation = useMutation({
    mutationFn: () => checkPriceAlert({ phone: form.phone, crop_type: form.crop_type, location: { state: form.state } }),
  })

  return (
    <div className="space-y-5">
      <div className="glass-card p-5 grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="form-group"><label className="label">Phone</label><input className="input" value={form.phone} onChange={e => set('phone', e.target.value)} /></div>
        <div className="form-group"><label className="label">Crop</label>
          <select className="select" value={form.crop_type} onChange={e => set('crop_type', e.target.value)}>
            {CROPS.map(c => <option key={c.value} value={c.value}>{c.label}</option>)}
          </select>
        </div>
        <div className="form-group"><label className="label">State</label>
          <select className="select" value={form.state} onChange={e => set('state', e.target.value)}>
            {STATES.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>
        <div className="form-group"><label className="label">Threshold Price (₹/q)</label><input className="input" type="number" value={form.threshold_price} onChange={e => set('threshold_price', e.target.value)} /></div>
        <div className="form-group"><label className="label">Alert When Price Is</label>
          <select className="select" value={form.alert_type} onChange={e => set('alert_type', e.target.value)}>
            <option value="above">Above threshold</option><option value="below">Below threshold</option>
          </select>
        </div>
        <div className="flex gap-3 sm:col-span-2">
          <button className="btn-primary flex-1" onClick={() => setupMutation.mutate()} disabled={setupMutation.isPending}>{setupMutation.isPending ? 'Setting Up…' : 'Setup Price Alert'}</button>
          <button className="btn-secondary flex-1" onClick={() => checkMutation.mutate()} disabled={checkMutation.isPending}>{checkMutation.isPending ? 'Checking…' : 'Check Alert Status'}</button>
        </div>
      </div>
      {setupMutation.isSuccess && <Alert type="success" message={setupMutation.data?.data?.message || 'Price alert configured successfully!'} />}
      {setupMutation.isError && <Alert type="error" message={setupMutation.error?.message||'Failed'} />}
      {checkMutation.isSuccess && checkMutation.data?.data && (
        <div className="glass-card p-5 border border-agri-600/30 bg-white/80 shadow-sm animate-slide-up space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-gray-900">Price Alert Status</h3>
            <span className={`badge ${checkMutation.data.data.triggered ? 'badge-red' : 'badge-green'} font-bold`}>
              {checkMutation.data.data.triggered ? 'Triggered!' : 'Active & Monitoring'}
            </span>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 pt-2 text-center">
            <div className="p-3 rounded-xl bg-white/70 border border-gray-200/80">
              <p className="text-xs text-gray-500">Threshold Price</p>
              <p className="text-sm font-bold text-agri-700">₹{checkMutation.data.data.threshold_price}/q</p>
            </div>
            <div className="p-3 rounded-xl bg-white/70 border border-gray-200/80">
              <p className="text-xs text-gray-500">Current Market Price</p>
              <p className="text-sm font-bold text-gray-900">₹{checkMutation.data.data.current_price}/q</p>
            </div>
            <div className="p-3 rounded-xl bg-white/70 border border-gray-200/80 col-span-2 sm:col-span-1">
              <p className="text-xs text-gray-500">Recommended Action</p>
              <p className="text-xs font-bold text-harvest-600 mt-0.5">{checkMutation.data.data.recommended_action || 'Monitor'}</p>
            </div>
          </div>
          {checkMutation.data.data.sms_summary && (
            <div className="glass-card p-4 border border-agri-600/30 bg-agri-500/10 mt-2">
              <p className="text-xs font-bold text-agri-700 mb-1 uppercase tracking-wider">📱 SMS Summary</p>
              <p className="text-xs font-medium text-gray-900">{checkMutation.data.data.sms_summary}</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

// ─── Generic Market Tab ────────────────────────────────────────────────────────
function GenericMarketTab({ tabId }: { tabId: Tab }) {
  const { phone, language } = useAppStore()
  const [form, setForm] = useState({ phone: phone||'', crop_type: 'cotton', state: 'Gujarat', language: language||'English', quantity_tonnes: '5' })
  const set = (k:string,v:string) => setForm(f => ({...f,[k]:v}))

  const apiFnMap: Record<string, (d: object) => Promise<any>> = {
    transport: getTransportOptimize,
    storage: getStorageAdvisory,
    intelligence: getMarketIntelligence,
    mandis: getMandiList,
  }

  const mutation = useMutation({
    mutationFn: () => apiFnMap[tabId]({ phone: form.phone, crop_type: form.crop_type, language: form.language, quantity_tonnes: parseFloat(form.quantity_tonnes), location: { state: form.state } }),
  })
  const data = mutation.data?.data

  return (
    <div className="space-y-5">
      <div className="glass-card p-5 grid grid-cols-1 sm:grid-cols-2 gap-4">
        <CommonForm form={form} onChange={set} />
        <div className="form-group"><label className="label">Quantity (Tonnes)</label><input className="input" type="number" value={form.quantity_tonnes} onChange={e => set('quantity_tonnes', e.target.value)} /></div>
        <div className="sm:col-span-2"><button className="btn-primary w-full" onClick={() => mutation.mutate()} disabled={mutation.isPending}>{mutation.isPending ? 'Analyzing…' : `Get ${tabs.find(t=>t.id===tabId)?.label}`}</button></div>
      </div>
      {mutation.isPending && <LoadingCard rows={5} label={`Loading ${tabs.find(t=>t.id===tabId)?.label}`} />}
      {mutation.isError && <Alert type="error" message={mutation.error?.message||'Failed'} />}
      
      {data && (
        <div className="space-y-4 animate-slide-up">
          {/* ── Transport Optimization View ── */}
          {tabId === 'transport' && (
            <>
              {data.recommended_option && (
                <div className="glass-card p-5 border border-agri-600/30 bg-white/80 shadow-sm">
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <p className="text-xs text-agri-700 font-bold uppercase tracking-wider">Optimal Transport Vehicle</p>
                      <h4 className="text-lg font-bold text-gray-900 capitalize">{(data.recommended_option.transport_mode || '').replace(/_/g, ' ')}</h4>
                    </div>
                    <span className="badge-green text-xs font-bold">₹{data.recommended_option.cost_per_quintal}/q</span>
                  </div>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-3 border-t border-gray-200/80 text-center">
                    <div><p className="text-xs text-gray-500">Distance</p><p className="text-sm font-bold text-gray-900">{data.recommended_option.distance_km} km</p></div>
                    <div><p className="text-xs text-gray-500">Est. Time</p><p className="text-sm font-bold text-gray-900">{data.recommended_option.estimated_time_hours} hrs</p></div>
                    <div><p className="text-xs text-gray-500">Total Cost</p><p className="text-sm font-bold text-agri-700">₹{data.recommended_option.total_cost}</p></div>
                    <div><p className="text-xs text-gray-500">Est. Savings</p><p className="text-sm font-bold text-harvest-600">₹{data.cost_savings_vs_default || 0}</p></div>
                  </div>
                </div>
              )}

              {data.options?.length > 0 && (
                <div className="glass-card p-5 border border-agri-600/20 shadow-sm">
                  <h3 className="text-sm font-bold text-gray-900 mb-3">Available Logistics Options</h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {data.options.map((opt: any, i: number) => (
                      <div key={i} className={`p-4 rounded-xl border ${i === 0 ? 'border-agri-600/40 bg-agri-500/10' : 'border-gray-200/80 bg-white/70'} shadow-xs flex justify-between items-center`}>
                        <div>
                          <p className="font-bold text-gray-900 text-sm capitalize">{(opt.transport_mode || '').replace(/_/g, ' ')}</p>
                          <p className="text-xs text-gray-600 mt-0.5">Est. Time: {opt.estimated_time_hours} hrs • {opt.availability || 'Available'}</p>
                        </div>
                        <div className="text-right">
                          <p className="text-base font-bold text-agri-700">₹{opt.total_cost}</p>
                          <p className="text-[11px] text-gray-500">₹{opt.cost_per_quintal}/q</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}

          {/* ── Storage Advisory View ── */}
          {tabId === 'storage' && (
            <>
              {data.recommended_storage && (
                <div className="glass-card p-5 border border-agri-600/30 bg-white/80 shadow-sm">
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <p className="text-xs text-agri-700 font-bold uppercase tracking-wider">Recommended Storage Method</p>
                      <h4 className="text-lg font-bold text-gray-900 capitalize">{(data.recommended_storage.storage_condition || '').replace(/_/g, ' ')}</h4>
                    </div>
                    <span className="badge-green text-xs font-bold">{data.recommended_storage.expected_recovery_percent}% Expected Recovery</span>
                  </div>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-3 border-t border-gray-200/80 text-center">
                    <div><p className="text-xs text-gray-500">Max Months</p><p className="text-sm font-bold text-gray-900">{data.recommended_storage.max_storage_months} mos</p></div>
                    <div><p className="text-xs text-gray-500">Spoilage Rate</p><p className="text-sm font-bold text-gray-900">{data.recommended_storage.spoilage_rate_per_month_percent}% / mo</p></div>
                    <div><p className="text-xs text-gray-500">Quality Retention</p><p className="text-sm font-bold text-agri-700 capitalize">{data.recommended_storage.quality_retention}</p></div>
                    <div><p className="text-xs text-gray-500">Est. Cost</p><p className="text-sm font-bold text-harvest-600">₹{data.recommended_storage.total_cost_for_period}</p></div>
                  </div>
                </div>
              )}

              {data.options?.length > 0 && (
                <div className="glass-card p-5 border border-agri-600/20 shadow-sm">
                  <h3 className="text-sm font-bold text-gray-900 mb-3">Storage Condition Options</h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {data.options.map((opt: any, i: number) => (
                      <div key={i} className={`p-4 rounded-xl border ${opt.storage_condition === data.recommended_storage?.storage_condition ? 'border-agri-600/40 bg-agri-500/10' : 'border-gray-200/80 bg-white/70'} shadow-xs flex justify-between items-center`}>
                        <div>
                          <p className="font-bold text-gray-900 text-sm capitalize">{(opt.storage_condition || '').replace(/_/g, ' ')}</p>
                          <p className="text-xs text-gray-600 mt-0.5">Quality: <span className="font-semibold text-gray-800 capitalize">{opt.quality_retention}</span> • Max {opt.max_storage_months} mos</p>
                        </div>
                        <div className="text-right">
                          <p className="text-sm font-bold text-agri-700">{opt.expected_recovery_percent}% Rec.</p>
                          <p className="text-[11px] text-gray-500">₹{opt.total_cost_for_period}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}

          {/* ── Market Intelligence View ── */}
          {tabId === 'intelligence' && (
            <>
              {data.current_market_summary && (
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  <div className="glass-card p-4 text-center border border-agri-600/20 bg-white/70 shadow-xs">
                    <p className="text-xl font-bold text-gray-900">₹{data.current_market_summary.average_price?.toLocaleString()}</p>
                    <p className="text-xs text-gray-500 font-medium mt-0.5">Avg Price / q</p>
                  </div>
                  <div className="glass-card p-4 text-center border border-agri-600/20 bg-white/70 shadow-xs">
                    <p className="text-xl font-bold text-agri-700">₹{data.current_market_summary.best_price?.toLocaleString()}</p>
                    <p className="text-xs text-gray-500 font-medium mt-0.5">Best Price ({data.current_market_summary.best_mandi})</p>
                  </div>
                  <div className="glass-card p-4 text-center border border-agri-600/20 bg-white/70 shadow-xs">
                    <p className="text-xl font-bold text-harvest-600">{data.current_market_summary.total_arrivals?.toFixed(1)}t</p>
                    <p className="text-xs text-gray-500 font-medium mt-0.5">Total Mandi Arrivals</p>
                  </div>
                  <div className="glass-card p-4 text-center border border-agri-600/20 bg-white/70 shadow-xs">
                    <p className="text-xl font-bold text-emerald-600 uppercase text-xs tracking-wider pt-1">{data.demand_supply_analysis?.demand_trend || 'Stable'}</p>
                    <p className="text-xs text-gray-500 font-medium mt-1">Demand Trend</p>
                  </div>
                </div>
              )}

              {data.trading_recommendations?.length > 0 && (
                <div className="glass-card p-5 border border-agri-600/20 shadow-sm">
                  <h3 className="text-sm font-bold text-gray-900 mb-3">Strategic Recommendations</h3>
                  <div className="space-y-2">
                    {data.trading_recommendations.map((rec: string, i: number) => (
                      <div key={i} className="p-3 rounded-xl bg-white/70 border border-gray-200/80 text-xs font-medium text-gray-800 flex items-center gap-2">
                        <span className="text-agri-600 font-bold">●</span> {rec}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}

          {/* ── Mandi List View ── */}
          {tabId === 'mandis' && (
            <>
              {data.mandis?.length > 0 && (
                <div className="glass-card p-5 border border-agri-600/20 shadow-sm">
                  <h3 className="text-sm font-bold text-gray-900 mb-3">Nearby Mandi Markets</h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {data.mandis.map((m: any, i: number) => (
                      <div key={i} className="p-4 rounded-xl bg-white/70 border border-gray-200/80 shadow-xs flex justify-between items-center">
                        <div>
                          <p className="font-bold text-gray-900 text-sm">{m.mandi_name || m.name}</p>
                          <p className="text-xs text-gray-600 mt-0.5">{m.district}, {m.state} {m.e_nam_enabled ? '• e-NAM Enabled' : ''}</p>
                        </div>
                        <span className="badge-green text-xs font-bold">{m.distance_km} km</span>
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

export default function MarketPage() {
  const [activeTab, setActiveTab] = useState<Tab>('prices')

  return (
    <div className="space-y-5 max-w-5xl mx-auto">
      <PageHeader title="Market Intelligence" subtitle="Real mandi data, ML price forecasts, and post-harvest optimization" icon={ShoppingCart} />
      <div className="flex gap-1.5 flex-wrap">
        {tabs.map(({ id, icon: Icon, label }) => (
          <button key={id} onClick={() => setActiveTab(id)} className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold transition-all ${activeTab===id?'bg-agri-700 text-white border border-agri-600/50':'text-gray-400 hover:text-white hover:bg-white/5 border border-transparent'}`}>
            <Icon className="w-3.5 h-3.5" />{label}
          </button>
        ))}
      </div>
      {activeTab === 'prices' && <MandiPricesTab />}
      {activeTab === 'forecast' && <ForecastTab />}
      {activeTab === 'sell' && <SellDecisionTab />}
      {activeTab === 'spoilage' && <SpoilageTab />}
      {activeTab === 'alert' && <PriceAlertTab />}
      {(activeTab === 'transport' || activeTab === 'storage' || activeTab === 'intelligence' || activeTab === 'mandis') && <GenericMarketTab tabId={activeTab} />}
    </div>
  )
}
