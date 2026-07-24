import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { Beef, Syringe, Stethoscope, Pill, UtensilsCrossed, Heart, Milk, AlertTriangle, ScrollText } from 'lucide-react'
import {
  getLivestockProfile, getLivestockVaccination, getLivestockDiagnosis,
  getDeworming, getFeedFormulation, getBreedingAdvice,
  getMilkQuality, getDiseaseAlerts, getLivestockSchemes,
} from '../api/client'
import { PageHeader, Alert, LoadingCard, ConfidencePill } from '../components/ui'
import { ANIMAL_TYPES, STATES } from '../lib/constants'
import { useAppStore } from '../store/appStore'

type Tab = 'profile'|'vaccination'|'diagnosis'|'deworming'|'feed'|'breeding'|'milk'|'alerts'|'schemes'

const tabs = [
  { id: 'profile' as Tab, icon: Beef, label: 'Animal Profile' },
  { id: 'vaccination' as Tab, icon: Syringe, label: 'Vaccination' },
  { id: 'diagnosis' as Tab, icon: Stethoscope, label: 'Diagnosis' },
  { id: 'deworming' as Tab, icon: Pill, label: 'Deworming' },
  { id: 'feed' as Tab, icon: UtensilsCrossed, label: 'Feed Optimizer' },
  { id: 'breeding' as Tab, icon: Heart, label: 'Breeding' },
  { id: 'milk' as Tab, icon: Milk, label: 'Milk Quality' },
  { id: 'alerts' as Tab, icon: AlertTriangle, label: 'Disease Alerts' },
  { id: 'schemes' as Tab, icon: ScrollText, label: 'Schemes' },
]

function CommonForm({ form, onChange }: { form: Record<string,string>; onChange: (k:string,v:string) => void }) {
  return (
    <>
      <div className="form-group"><label className="label">Phone</label>
        <input className="input" placeholder="9876543210" value={form.phone} onChange={e => onChange('phone', e.target.value)} />
      </div>
      <div className="form-group"><label className="label">Animal Type</label>
        <select className="select" value={form.animal_type} onChange={e => onChange('animal_type', e.target.value)}>
          {ANIMAL_TYPES.map(a => <option key={a.value} value={a.value}>{a.label}</option>)}
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

function ProfileTab() {
  const { phone, language } = useAppStore()
  const [form, setForm] = useState({ phone: phone||'', animal_type: 'cow', state: 'Gujarat', language: language||'English', breed: 'HF', age_months: '36', weight_kg: '450', lactation_stage: 'mid_lactation' })
  const set = (k:string,v:string) => setForm(f => ({...f,[k]:v}))
  const mutation = useMutation({
    mutationFn: () => getLivestockProfile({
      phone: form.phone, animal_type: form.animal_type, breed: form.breed,
      age_months: parseInt(form.age_months), weight_kg: parseFloat(form.weight_kg),
      lactation_stage: form.lactation_stage, language: form.language,
      location: { state: form.state },
    }),
  })
  const data = mutation.data?.data

  return (
    <div className="space-y-5">
      <div className="glass-card p-5 grid grid-cols-1 sm:grid-cols-2 gap-4">
        <CommonForm form={form} onChange={set} />
        <div className="form-group"><label className="label">Breed</label><input className="input" placeholder="HF / Gir / Murrah" value={form.breed} onChange={e => set('breed', e.target.value)} /></div>
        <div className="form-group"><label className="label">Age (Months)</label><input className="input" type="number" value={form.age_months} onChange={e => set('age_months', e.target.value)} /></div>
        <div className="form-group"><label className="label">Weight (kg)</label><input className="input" type="number" value={form.weight_kg} onChange={e => set('weight_kg', e.target.value)} /></div>
        <div className="form-group"><label className="label">Lactation Stage</label>
          <select className="select" value={form.lactation_stage} onChange={e => set('lactation_stage', e.target.value)}>
            {['early_lactation','mid_lactation','late_lactation','dry_period','heifer','calf'].map(s => <option key={s} value={s}>{s.replace('_',' ')}</option>)}
          </select>
        </div>
        <div className="sm:col-span-2"><button className="btn-primary w-full" onClick={() => mutation.mutate()} disabled={mutation.isPending}>{mutation.isPending ? 'Analyzing…' : 'Get Animal Profile & Health'}</button></div>
      </div>
      {mutation.isPending && <LoadingCard label="Assessing animal health" rows={5} />}
      {mutation.isError && <Alert type="error" message={mutation.error?.message||'Failed'} />}
      {data && (
        <div className="space-y-4 animate-slide-up">
          {data.health_assessment && (
            <div className="glass-card p-5 border border-agri-600/30 bg-white/80 shadow-sm">
              <div className="flex items-center gap-4">
                <div className="w-14 h-14 rounded-2xl bg-agri-500/10 border border-agri-500/30 flex items-center justify-center">
                  <Beef className="w-8 h-8 text-agri-700" />
                </div>
                <div>
                  <p className="text-xs text-agri-700 font-bold uppercase tracking-wider">Health Status & Assessment</p>
                  <p className="text-xl font-bold text-gray-900 capitalize">{data.health_assessment}</p>
                  {data.profile_summary && (
                    <p className="text-xs text-gray-600 mt-0.5">
                      Age: <span className="font-bold text-gray-800">{data.profile_summary.age_months} mos</span> • Weight: <span className="font-bold text-gray-800">{data.profile_summary.weight_kg} kg</span>
                    </p>
                  )}
                </div>
                <div className="ml-auto"><ConfidencePill value={0.85} /></div>
              </div>
            </div>
          )}

          {data.recommendations?.length > 0 && (
            <div className="glass-card p-5 border border-agri-600/20 shadow-sm">
              <h3 className="text-sm font-bold text-gray-900 mb-3">Health & Management Recommendations</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {data.recommendations.map((r: string, i: number) => (
                  <div key={i} className="p-3 rounded-xl bg-white/70 border border-gray-200/80 text-xs font-medium text-gray-800 flex items-center gap-2">
                    <span className="text-agri-600 font-bold">●</span> {r}
                  </div>
                ))}
              </div>
            </div>
          )}

          {data.upcoming_vaccinations?.length > 0 && (
            <div className="glass-card p-5 border border-agri-600/20 shadow-sm">
              <h3 className="text-sm font-bold text-gray-900 mb-3">Vaccination & Deworming Schedule</h3>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                {data.upcoming_vaccinations.map((v: any, i: number) => (
                  <div key={i} className="p-3 rounded-xl bg-white/70 border border-gray-200/80 shadow-xs flex justify-between items-center">
                    <div>
                      <p className="font-bold text-gray-900 text-sm">{v.vaccine}</p>
                      <p className="text-xs text-gray-500">Due: {v.due_date}</p>
                    </div>
                    <span className={`badge ${v.status === 'overdue' ? 'badge-red' : 'badge-gold'} text-[10px]`}>{v.status}</span>
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

function FeedTab() {
  const { phone, language } = useAppStore()
  const [form, setForm] = useState({ phone: phone||'', animal_type: 'cow', state: 'Gujarat', language: language||'English', milk_yield_kg_day: '12', body_weight_kg: '450', lactation_stage: 'mid_lactation' })
  const set = (k:string,v:string) => setForm(f => ({...f,[k]:v}))
  const mutation = useMutation({
    mutationFn: () => getFeedFormulation({
      phone: form.phone, animal_type: form.animal_type, language: form.language,
      milk_yield_kg_day: parseFloat(form.milk_yield_kg_day),
      body_weight_kg: parseFloat(form.body_weight_kg),
      lactation_stage: form.lactation_stage,
      location: { state: form.state },
    }),
  })
  const data = mutation.data?.data

  return (
    <div className="space-y-5">
      <div className="glass-card p-5 grid grid-cols-1 sm:grid-cols-2 gap-4">
        <CommonForm form={form} onChange={set} />
        <div className="form-group"><label className="label">Milk Yield (kg/day)</label><input className="input" type="number" value={form.milk_yield_kg_day} onChange={e => set('milk_yield_kg_day', e.target.value)} /></div>
        <div className="form-group"><label className="label">Body Weight (kg)</label><input className="input" type="number" value={form.body_weight_kg} onChange={e => set('body_weight_kg', e.target.value)} /></div>
        <div className="form-group"><label className="label">Lactation Stage</label>
          <select className="select" value={form.lactation_stage} onChange={e => set('lactation_stage', e.target.value)}>
            {['early_lactation','mid_lactation','late_lactation','dry_period'].map(s => <option key={s} value={s}>{s.replace('_',' ')}</option>)}
          </select>
        </div>
        <div className="sm:col-span-2"><button className="btn-primary w-full" onClick={() => mutation.mutate()} disabled={mutation.isPending}>{mutation.isPending ? 'Optimizing…' : 'Get Least-Cost Feed Formulation'}</button></div>
      </div>
      {mutation.isPending && <LoadingCard label="Computing optimal feed formula" rows={5} />}
      {mutation.isError && <Alert type="error" message={mutation.error?.message||'Failed'} />}
      {data && (
        <div className="space-y-4 animate-slide-up">
          {/* Recommended Formulation Summary */}
          {data.recommended_formulation && (
            <div className="glass-card p-5 border border-agri-600/30 bg-white/80 shadow-sm">
              <div className="flex justify-between items-start mb-3">
                <div>
                  <p className="text-xs text-agri-700 font-bold uppercase tracking-wider">Optimal Least-Cost Feed Formula</p>
                  <h4 className="text-lg font-bold text-gray-900">Balanced Ration Mix</h4>
                </div>
                <div className="text-right">
                  <p className="text-xl font-bold text-agri-700">₹{data.recommended_formulation.total_cost_per_day_inr?.toFixed(0)}/day</p>
                  <p className="text-xs text-gray-500 font-medium">₹{data.recommended_formulation.cost_per_litre_milk_inr?.toFixed(2)} / Litre Milk</p>
                </div>
              </div>

              {data.recommended_formulation.ingredients?.length > 0 && (
                <div className="overflow-x-auto rounded-xl border border-gray-200/80 bg-white/70 shadow-xs">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-agri-500/10 text-agri-700 font-bold border-b border-gray-200">
                      <tr>
                        <th className="p-3">Ingredient</th>
                        <th className="p-3">Qty (kg/day)</th>
                        <th className="p-3">Rate (₹/kg)</th>
                        <th className="p-3">Daily Cost (₹)</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200/70 text-gray-900 font-medium">
                      {data.recommended_formulation.ingredients.map((ing: any, i: number) => (
                        <tr key={i} className="hover:bg-agri-500/5">
                          <td className="p-3 capitalize font-bold text-gray-900">{(ing.ingredient || ing.name || '').replace(/_/g, ' ')}</td>
                          <td className="p-3">{ing.quantity_kg_per_day?.toFixed(2) || ing.quantity_kg?.toFixed(2)} kg</td>
                          <td className="p-3 text-gray-600">₹{ing.cost_per_kg_inr || 0}</td>
                          <td className="p-3 font-bold text-agri-700">₹{(ing.cost_per_kg_inr * (ing.quantity_kg_per_day || ing.quantity_kg || 0))?.toFixed(1)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
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

function GenericLivestockTab({ tabId }: { tabId: Tab }) {
  const { phone, language } = useAppStore()
  const [form, setForm] = useState({ phone: phone||'', animal_type: 'cow', state: 'Gujarat', language: language||'English', symptoms: '' })
  const set = (k:string,v:string) => setForm(f => ({...f,[k]:v}))

  const apiFnMap: Record<string, (d:object)=>Promise<any>> = {
    vaccination: getLivestockVaccination,
    diagnosis: getLivestockDiagnosis,
    deworming: getDeworming,
    breeding: getBreedingAdvice,
    milk: getMilkQuality,
    alerts: getDiseaseAlerts,
    schemes: getLivestockSchemes,
  }

  const mutation = useMutation({
    mutationFn: () => apiFnMap[tabId]({
      phone: form.phone, animal_type: form.animal_type, language: form.language,
      symptoms: form.symptoms ? form.symptoms.split(',').map(s=>s.trim()) : [],
      location: { state: form.state },
    }),
  })
  const data = mutation.data?.data

  return (
    <div className="space-y-5">
      <div className="glass-card p-5 grid grid-cols-1 sm:grid-cols-2 gap-4">
        <CommonForm form={form} onChange={set} />
        {tabId === 'diagnosis' && (
          <div className="form-group sm:col-span-2">
            <label className="label">Symptoms (comma-separated)</label>
            <input className="input" placeholder="e.g. fever, loss of appetite, diarrhea" value={form.symptoms} onChange={e => set('symptoms', e.target.value)} />
          </div>
        )}
        <div className="sm:col-span-2"><button className="btn-primary w-full" onClick={() => mutation.mutate()} disabled={mutation.isPending}>{mutation.isPending ? 'Loading…' : `Get ${tabs.find(t=>t.id===tabId)?.label}`}</button></div>
      </div>
      {mutation.isPending && <LoadingCard rows={5} label={`Processing ${tabs.find(t=>t.id===tabId)?.label}`} />}
      {mutation.isError && <Alert type="error" message={mutation.error?.message||'Failed'} />}
      
      {data && (
        <div className="space-y-4 animate-slide-up">
          {/* ── Vaccination Schedule View ── */}
          {tabId === 'vaccination' && data.schedule?.length > 0 && (
            <div className="glass-card p-5 border border-agri-600/20 shadow-sm space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold text-gray-900">Vaccination Schedule & Status</h3>
                <div className="flex gap-2">
                  <span className="badge-red text-xs font-bold">{data.overdue_count || 0} Overdue</span>
                  <span className="badge-green text-xs font-bold">{data.completed_count || 0} Completed</span>
                </div>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {data.schedule.map((vac: any, i: number) => (
                  <div key={i} className="p-4 rounded-xl bg-white/70 border border-gray-200/80 shadow-xs space-y-1">
                    <div className="flex items-center justify-between">
                      <p className="font-bold text-gray-900 text-sm">{vac.vaccine_name}</p>
                      <span className={`badge ${vac.status === 'overdue' ? 'badge-red' : 'badge-green'} text-[10px]`}>{vac.status}</span>
                    </div>
                    <p className="text-xs font-medium text-agri-700">{vac.disease_prevented}</p>
                    <p className="text-[11px] text-gray-600">
                      Dose: <span className="font-bold text-gray-800">{vac.dose_ml} ({vac.route})</span> • Due: <span className="font-bold text-gray-800">{vac.recommended_date}</span>
                    </p>
                    {vac.notes && <p className="text-[11px] text-gray-500 italic">Note: {vac.notes}</p>}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* ── Diagnosis View ── */}
          {tabId === 'diagnosis' && (
            <>
              {data.most_likely && (
                <div className="glass-card p-5 border border-agri-600/30 bg-white/80 shadow-sm">
                  <div className="flex items-center justify-between mb-3">
                    <div>
                      <p className="text-xs text-agri-700 font-bold uppercase tracking-wider">Most Likely Diagnosis</p>
                      <h4 className="text-xl font-bold text-gray-900">{data.most_likely.disease_name}</h4>
                    </div>
                    <span className={`badge ${data.most_likely.urgency === 'emergency' ? 'badge-red' : 'badge-gold'} font-bold`}>
                      {(data.most_likely.probability * 100).toFixed(0)}% Match ({data.most_likely.urgency})
                    </span>
                  </div>
                  {data.immediate_actions?.length > 0 && (
                    <div className="pt-3 border-t border-gray-200/80">
                      <p className="text-xs font-bold text-red-600 uppercase tracking-wider mb-1">🚨 Immediate Actions Needed</p>
                      <ul className="space-y-1 text-xs font-medium text-gray-800">
                        {data.immediate_actions.map((act: string, idx: number) => (
                          <li key={idx} className="flex items-center gap-2"><span className="text-red-500 font-bold">●</span> {act}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}

              {data.differential_diagnoses?.length > 0 && (
                <div className="glass-card p-5 border border-agri-600/20 shadow-sm">
                  <h3 className="text-sm font-bold text-gray-900 mb-3">Differential Diagnoses</h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {data.differential_diagnoses.map((diag: any, i: number) => (
                      <div key={i} className="p-4 rounded-xl bg-white/70 border border-gray-200/80 shadow-xs space-y-1">
                        <div className="flex items-center justify-between">
                          <p className="font-bold text-gray-900 text-sm">{diag.disease_name}</p>
                          <span className="badge-green text-[10px]">{(diag.probability * 100).toFixed(0)}%</span>
                        </div>
                        <p className="text-xs text-gray-600">Urgency: <span className="font-semibold text-gray-800 capitalize">{diag.urgency}</span></p>
                        {diag.key_differentiating_features?.length > 0 && (
                          <p className="text-[11px] text-gray-500">Key Features: {diag.key_differentiating_features.join(', ')}</p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}

          {/* ── Deworming View ── */}
          {tabId === 'deworming' && (
            <>
              {data.recommended_dewormers?.length > 0 && (
                <div className="glass-card p-5 border border-agri-600/20 shadow-sm">
                  <h3 className="text-sm font-bold text-gray-900 mb-3">Recommended Dewormers</h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {data.recommended_dewormers.map((dew: any, i: number) => (
                      <div key={i} className="p-4 rounded-xl bg-white/70 border border-gray-200/80 shadow-xs space-y-1">
                        <div className="flex items-center justify-between">
                          <p className="font-bold text-gray-900 text-sm">{dew.dewormer_name}</p>
                          <span className="badge-green text-[10px]">₹{dew.cost_per_dose_inr}/dose</span>
                        </div>
                        <p className="text-xs font-medium text-agri-700">Dose: {dew.dose_per_kg} ({dew.route})</p>
                        <p className="text-[11px] text-gray-600">
                          Pregnancy Safe: <span className={`font-bold ${dew.safe_in_pregnancy ? 'text-green-600' : 'text-red-600'}`}>{dew.safe_in_pregnancy ? 'Yes' : 'No'}</span> • Lactation Safe: <span className={`font-bold ${dew.safe_in_lactation ? 'text-green-600' : 'text-red-600'}`}>{dew.safe_in_lactation ? 'Yes' : 'No'}</span>
                        </p>
                        {dew.target_parasites?.length > 0 && (
                          <p className="text-[11px] text-gray-500">Target Parasites: {dew.target_parasites.join(', ')}</p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}

          {/* ── Breeding View ── */}
          {tabId === 'breeding' && (
            <>
              {data.optimal_breeding_window && (
                <div className="glass-card p-5 border border-agri-600/30 bg-white/80 shadow-sm">
                  <p className="text-xs text-agri-700 font-bold uppercase tracking-wider">Optimal Breeding Window</p>
                  <h4 className="text-lg font-bold text-gray-900 mt-0.5">{data.optimal_breeding_window}</h4>
                  {data.ai_vs_natural_service?.recommendation && (
                    <p className="text-xs text-gray-700 font-medium mt-1">
                      Recommendation: <span className="font-bold text-agri-700">{data.ai_vs_natural_service.recommendation}</span>
                    </p>
                  )}
                </div>
              )}

              {data.heat_detection_guide?.length > 0 && (
                <div className="glass-card p-5 border border-agri-600/20 shadow-sm">
                  <h3 className="text-sm font-bold text-gray-900 mb-3">Heat Detection Guide</h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    {data.heat_detection_guide.map((sign: string, i: number) => (
                      <div key={i} className="p-3 rounded-xl bg-white/70 border border-gray-200/80 text-xs font-medium text-gray-800 flex items-center gap-2">
                        <span className="text-agri-600 font-bold">●</span> {sign}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}

          {/* ── Milk Quality View ── */}
          {tabId === 'milk' && (
            <>
              {data.quality_grade && (
                <div className="glass-card p-5 border border-agri-600/30 bg-white/80 shadow-sm">
                  <div className="flex items-center justify-between mb-3">
                    <div>
                      <p className="text-xs text-agri-700 font-bold uppercase tracking-wider">Milk Quality Grade</p>
                      <h4 className="text-xl font-bold text-gray-900">{data.quality_grade}</h4>
                    </div>
                    <span className="badge-green font-bold">Compliant</span>
                  </div>

                  {data.parameters && (
                    <div className="grid grid-cols-2 gap-3 pt-3 border-t border-gray-200/80 text-center">
                      <div className="p-3 rounded-xl bg-white/70 border border-gray-200/80">
                        <p className="text-xs text-gray-500">Fat Percent</p>
                        <p className="text-lg font-bold text-agri-700">{data.parameters.fat_percent?.value}%</p>
                      </div>
                      <div className="p-3 rounded-xl bg-white/70 border border-gray-200/80">
                        <p className="text-xs text-gray-500">SNF Percent</p>
                        <p className="text-lg font-bold text-agri-700">{data.parameters.snf_percent?.value}%</p>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </>
          )}

          {/* ── Disease Alerts View ── */}
          {tabId === 'alerts' && (
            <>
              {data.active_alerts?.length > 0 && (
                <div className="glass-card p-5 border border-agri-600/20 shadow-sm">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="text-sm font-bold text-gray-900">Active Disease Outbreak Alerts</h3>
                    <span className="badge-red text-xs font-bold">Overall Risk: {data.overall_risk}</span>
                  </div>
                  <div className="space-y-3">
                    {data.active_alerts.map((alt: any, i: number) => (
                      <div key={i} className="p-4 rounded-xl bg-white/70 border border-red-200 shadow-xs space-y-1">
                        <div className="flex items-center justify-between">
                          <p className="font-bold text-gray-900 text-sm">{alt.disease_name}</p>
                          <span className={`badge ${alt.risk_level === 'critical' ? 'badge-red' : 'badge-gold'} text-[10px]`}>{alt.risk_level}</span>
                        </div>
                        {alt.symptoms_to_watch?.length > 0 && (
                          <p className="text-xs text-gray-700 font-medium">Symptoms: {alt.symptoms_to_watch.join(', ')}</p>
                        )}
                        {alt.preventive_measures?.length > 0 && (
                          <p className="text-[11px] text-gray-600">Measures: {alt.preventive_measures.join(' • ')}</p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}

          {/* ── Livestock Schemes View ── */}
          {tabId === 'schemes' && data.schemes?.length > 0 && (
            <div className="glass-card p-5 border border-agri-600/20 shadow-sm space-y-3">
              <h3 className="text-sm font-bold text-gray-900">Government Livestock Schemes</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {data.schemes.map((s: any, i: number) => (
                  <div key={i} className="p-4 rounded-xl bg-white/70 border border-gray-200/80 shadow-xs space-y-2">
                    <div className="flex items-center justify-between">
                      <p className="font-bold text-gray-900 text-sm">{s.scheme_name}</p>
                      <span className="badge-green text-[10px] font-bold">{s.subsidy_amount || 'Active'}</span>
                    </div>
                    <p className="text-xs text-gray-600">{s.description}</p>
                    {s.benefits?.length > 0 && (
                      <div className="pt-1">
                        <p className="text-[11px] font-bold text-agri-700">Benefits:</p>
                        <p className="text-[11px] text-gray-700">{s.benefits.join(' • ')}</p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* ── Generic Fallback View ── */}
          {tabId !== 'vaccination' && tabId !== 'diagnosis' && tabId !== 'deworming' && tabId !== 'breeding' && tabId !== 'milk' && tabId !== 'alerts' && tabId !== 'schemes' && (
            <div className="glass-card p-5 border border-agri-600/20 shadow-sm space-y-3">
              <h3 className="text-sm font-bold text-gray-900">{tabs.find(t=>t.id===tabId)?.label} Summary & Advisory</h3>
              <div className="p-4 rounded-xl bg-white/70 border border-gray-200/80 text-xs text-gray-800 font-medium">
                {data.recommendations?.length > 0 ? (
                  <ul className="space-y-1.5">
                    {data.recommendations.map((r: string, idx: number) => (
                      <li key={idx} className="flex gap-2 items-center"><span className="text-agri-600 font-bold">●</span> {r}</li>
                    ))}
                  </ul>
                ) : (
                  <p>{data.summary || data.diagnosis || data.advice || data.message || 'Request completed successfully.'}</p>
                )}
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

export default function LivestockPage() {
  const [activeTab, setActiveTab] = useState<Tab>('profile')

  return (
    <div className="space-y-5 max-w-5xl mx-auto">
      <PageHeader title="Livestock Management" subtitle="Complete animal health, feed optimization, and breeding advisory" icon={Beef} />
      <div className="flex gap-1.5 flex-wrap">
        {tabs.map(({ id, icon: Icon, label }) => (
          <button key={id} onClick={() => setActiveTab(id)} className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold transition-all ${activeTab===id?'bg-agri-700 text-white border border-agri-600/50':'text-gray-400 hover:text-white hover:bg-white/5 border border-transparent'}`}>
            <Icon className="w-3.5 h-3.5" />{label}
          </button>
        ))}
      </div>
      {activeTab === 'profile' && <ProfileTab />}
      {activeTab === 'feed' && <FeedTab />}
      {(activeTab !== 'profile' && activeTab !== 'feed') && <GenericLivestockTab tabId={activeTab} />}
    </div>
  )
}
