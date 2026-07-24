import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import {
  Heart, Syringe, Building2, AlertTriangle, Activity, PhoneCall,
  MapPin, ShieldAlert, CheckCircle2, Calendar, Clock, User, Stethoscope
} from 'lucide-react'
import {
  getHealthAdvisory, getVaccinationSchedule, getHealthCamps, getEmergencyTriage,
} from '../api/client'
import { PageHeader, Alert, LoadingCard } from '../components/ui'
import { STATES } from '../lib/constants'
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
    symptoms: 'fever, fatigue, body ache',
    age: '35',
    gender: 'male',
    child_dob: '2025-06-15',
    radius_km: '20',
    camp_category: 'all',
    bp_sys: '120',
    bp_dia: '80',
    pulse: '75',
    spo2: '98',
    is_emergency: false,
  })

  const set = (k: string, v: any) => setForm(f => ({ ...f, [k]: v }))

  // 1. Health Advisory Mutation
  const advisoryMutation = useMutation({
    mutationFn: () => getHealthAdvisory({
      phone: form.phone,
      language: form.language,
      symptoms: form.symptoms ? form.symptoms.split(',').map(s => s.trim()) : ['fever', 'fatigue'],
      age: parseInt(form.age) || 35,
      gender: form.gender,
      location: { state: form.state },
      vital_signs: {
        bp_sys: parseInt(form.bp_sys) || 120,
        bp_dia: parseInt(form.bp_dia) || 80,
        pulse: parseInt(form.pulse) || 75,
        spo2: parseInt(form.spo2) || 98,
      }
    }),
  })

  // 2. Vaccination Schedule Mutation
  const vaccinationMutation = useMutation({
    mutationFn: () => getVaccinationSchedule({
      phone: form.phone,
      language: form.language,
      child_dob: form.child_dob || '2025-06-15',
    }),
  })

  // 3. Health Camps Mutation
  const campsMutation = useMutation({
    mutationFn: () => getHealthCamps({
      phone: form.phone,
      language: form.language,
      radius_km: parseFloat(form.radius_km) || 20,
      category: form.camp_category === 'all' ? undefined : form.camp_category,
      location: { state: form.state },
    }),
  })

  // 4. Emergency Triage Mutation
  const triageMutation = useMutation({
    mutationFn: () => getEmergencyTriage({
      phone: form.phone,
      language: form.language,
      symptoms: form.symptoms ? form.symptoms.split(',').map(s => s.trim()) : ['chest pain', 'breathlessness'],
      age: parseInt(form.age) || 35,
      gender: form.gender,
      location: { state: form.state },
      is_emergency: form.is_emergency,
      vital_signs: {
        bp_sys: parseInt(form.bp_sys) || 140,
        bp_dia: parseInt(form.bp_dia) || 90,
        pulse: parseInt(form.pulse) || 105,
        spo2: parseInt(form.spo2) || 94,
      }
    }),
  })

  const currentMutation =
    activeTab === 'advisory' ? advisoryMutation :
    activeTab === 'vaccination' ? vaccinationMutation :
    activeTab === 'camps' ? campsMutation : triageMutation

  return (
    <div className="space-y-5 max-w-5xl mx-auto pb-10">
      <PageHeader
        title="Farmer Health & Wellness"
        subtitle="AI clinical symptom advisory, child vaccination schedules, rural health camps, & 108 emergency triage"
        icon={Heart}
      />

      {/* Tab Selectors */}
      <div className="flex gap-2 flex-wrap">
        {tabs.map(({ id, icon: Icon, label }) => (
          <button
            key={id}
            onClick={() => setActiveTab(id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
              activeTab === id
                ? 'bg-emerald-700 text-white shadow-sm shadow-emerald-700/20'
                : 'text-slate-600 hover:text-slate-900 hover:bg-white/60 border border-transparent'
            }`}
          >
            <Icon className="w-4 h-4" />{label}
          </button>
        ))}
      </div>

      {/* Form Input Section */}
      <div className="glass-card p-5 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
        <div className="form-group">
          <label className="label">Phone Number</label>
          <input
            className="input"
            value={form.phone}
            onChange={e => set('phone', e.target.value)}
          />
        </div>

        <div className="form-group">
          <label className="label">Language</label>
          <select
            className="select"
            value={form.language}
            onChange={e => set('language', e.target.value)}
          >
            {['English', 'Hindi', 'Gujarati', 'Marathi', 'Tamil', 'Telugu'].map(l => <option key={l} value={l}>{l}</option>)}
          </select>
        </div>

        <div className="form-group">
          <label className="label">State</label>
          <select
            className="select"
            value={form.state}
            onChange={e => set('state', e.target.value)}
          >
            {STATES.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>

        {/* Tab 1: Advisory & Tab 4: Triage Common Fields */}
        {(activeTab === 'advisory' || activeTab === 'triage') && (
          <>
            <div className="form-group">
              <label className="label">Patient Age (Years)</label>
              <input
                className="input"
                type="number"
                value={form.age}
                onChange={e => set('age', e.target.value)}
              />
            </div>

            <div className="form-group">
              <label className="label">Gender</label>
              <select
                className="select"
                value={form.gender}
                onChange={e => set('gender', e.target.value)}
              >
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="other">Other</option>
              </select>
            </div>

            <div className="form-group md:col-span-3 sm:col-span-2">
              <label className="label">Symptoms (comma separated)</label>
              <input
                className="input"
                placeholder="e.g. skin rash, eye irritation, fever, chest pain"
                value={form.symptoms}
                onChange={e => set('symptoms', e.target.value)}
              />
            </div>
          </>
        )}

        {/* Vital Signs for Triage */}
        {activeTab === 'triage' && (
          <>
            <div className="form-group">
              <label className="label">BP Systolic / Diastolic</label>
              <div className="flex gap-2">
                <input
                  className="input"
                  type="number"
                  placeholder="120"
                  value={form.bp_sys}
                  onChange={e => set('bp_sys', e.target.value)}
                />
                <input
                  className="input"
                  type="number"
                  placeholder="80"
                  value={form.bp_dia}
                  onChange={e => set('bp_dia', e.target.value)}
                />
              </div>
            </div>

            <div className="form-group">
              <label className="label">Pulse Rate (BPM)</label>
              <input
                className="input"
                type="number"
                value={form.pulse}
                onChange={e => set('pulse', e.target.value)}
              />
            </div>

            <div className="form-group">
              <label className="label">Oxygen SpO2 (%)</label>
              <input
                className="input"
                type="number"
                value={form.spo2}
                onChange={e => set('spo2', e.target.value)}
              />
            </div>

            <div className="md:col-span-3 sm:col-span-2 flex items-center gap-2 p-3.5 bg-red-50 border border-red-200 rounded-xl">
              <input
                type="checkbox"
                id="is_emergency"
                checked={form.is_emergency}
                onChange={e => set('is_emergency', e.target.checked)}
                className="w-4 h-4 accent-red-600 rounded cursor-pointer"
              />
              <label htmlFor="is_emergency" className="text-xs text-red-900 font-bold cursor-pointer">
                Critical Emergency? (Dispatches immediate 108 ambulance notification)
              </label>
            </div>
          </>
        )}

        {/* Tab 2: Vaccination Fields */}
        {activeTab === 'vaccination' && (
          <div className="form-group md:col-span-2">
            <label className="label">Child Date of Birth</label>
            <input
              className="input"
              type="date"
              value={form.child_dob}
              onChange={e => set('child_dob', e.target.value)}
            />
          </div>
        )}

        {/* Tab 3: Health Camps Fields */}
        {activeTab === 'camps' && (
          <>
            <div className="form-group">
              <label className="label">Search Radius (KM)</label>
              <input
                className="input"
                type="number"
                value={form.radius_km}
                onChange={e => set('radius_km', e.target.value)}
              />
            </div>
            <div className="form-group md:col-span-2">
              <label className="label">Camp Category</label>
              <select
                className="select"
                value={form.camp_category}
                onChange={e => set('camp_category', e.target.value)}
              >
                <option value="all">All Health Camps</option>
                <option value="general">General Medical Checkup</option>
                <option value="maternal">Maternal Health</option>
                <option value="child">Child Care & Health</option>
                <option value="vaccination">Vaccination Camp</option>
                <option value="nutrition">Nutrition & Malnutrition</option>
                <option value="sanitation">Sanitation & Hygiene</option>
                <option value="emergency">Emergency & First Aid</option>
              </select>
            </div>
          </>
        )}

        {/* Submit Button */}
        <div className="md:col-span-3 sm:col-span-2 pt-2">
          <button
            className="btn-primary w-full"
            onClick={() => currentMutation.mutate()}
            disabled={currentMutation.isPending}
          >
            {currentMutation.isPending ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Analyzing Health Data…
              </>
            ) : (
              <>
                <Stethoscope className="w-4 h-4" />
                Run {tabs.find(t => t.id === activeTab)?.label}
              </>
            )}
          </button>
        </div>
      </div>

      {/* Loading State */}
      {currentMutation.isPending && <LoadingCard label="Evaluating clinical rules & matching health facilities..." rows={4} />}

      {/* Error Alert */}
      {currentMutation.isError && (
        <Alert type="error" message={currentMutation.error?.message || 'Failed to process request.'} />
      )}

      {/* Results Section */}
      {currentMutation.data?.data && (
        <div className="space-y-5 animate-slide-up">

          {/* SMS Alert Box */}
          {currentMutation.data.data.sms_summary && (
            <div className="glass-card p-4 border border-emerald-300/80 bg-emerald-50/80 rounded-2xl flex items-start gap-3 shadow-sm">
              <div className="p-2.5 rounded-xl bg-emerald-100 text-emerald-700 shrink-0">
                <PhoneCall className="w-5 h-5" />
              </div>
              <div>
                <p className="text-xs font-bold uppercase tracking-wider text-emerald-800">📱 Farmer SMS Summary (&lt;=155 chars)</p>
                <p className="text-sm font-semibold text-slate-900 mt-0.5">{currentMutation.data.data.sms_summary}</p>
              </div>
            </div>
          )}

          {/* TAB 1: HEALTH ADVISORY RESULT VIEW */}
          {activeTab === 'advisory' && (
            <div className="space-y-5">
              {/* Red Flags Alert if present */}
              {currentMutation.data.data.red_flags?.length > 0 && (
                <div className="p-4 rounded-2xl bg-red-100 border border-red-300 flex items-start gap-3 shadow-sm">
                  <ShieldAlert className="w-6 h-6 text-red-600 shrink-0 mt-0.5 animate-pulse" />
                  <div>
                    <h4 className="text-sm font-bold text-red-900">⚠️ CRITICAL HEALTH WARNING (RED FLAGS IDENTIFIED)</h4>
                    <ul className="mt-1 text-xs text-red-800 list-disc list-inside space-y-1 font-semibold">
                      {currentMutation.data.data.red_flags.map((rf: string, idx: number) => (
                        <li key={idx}>{rf}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}

              {/* Advisory Cards List */}
              <div className="grid grid-cols-1 gap-4">
                {currentMutation.data.data.advisories?.map((item: any, idx: number) => (
                  <div key={idx} className="glass-card p-5 space-y-3">
                    <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-200/80 pb-3">
                      <div className="flex items-center gap-2">
                        <span className="p-2 rounded-lg bg-emerald-50 text-emerald-700">
                          <Stethoscope className="w-4 h-4" />
                        </span>
                        <h3 className="text-base font-bold text-slate-900">{item.title}</h3>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="badge bg-slate-100 text-slate-700 border border-slate-200">
                          Category: {item.category}
                        </span>
                        <span className={`badge ${
                          item.confidence === 'High' ? 'bg-emerald-100 text-emerald-800 border border-emerald-200' :
                          item.confidence === 'Medium' ? 'bg-amber-100 text-amber-800 border border-amber-200' :
                          'bg-blue-100 text-blue-800 border border-blue-200'
                        }`}>
                          Confidence: {item.confidence}
                        </span>
                      </div>
                    </div>

                    <p className="text-sm text-slate-700 leading-relaxed font-medium">{item.description}</p>

                    {item.rationale && (
                      <p className="text-xs text-amber-900 bg-amber-50/90 p-3 rounded-xl border border-amber-200/60 font-medium italic">
                        💡 Rationale: {item.rationale}
                      </p>
                    )}

                    {item.action_items?.length > 0 && (
                      <div className="space-y-2 pt-1">
                        <h4 className="text-xs font-bold uppercase tracking-wider text-emerald-800">Recommended Actions:</h4>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                          {item.action_items.map((act: string, aIdx: number) => (
                            <div key={aIdx} className="flex items-center gap-2 text-xs text-slate-800 bg-white/90 p-2.5 rounded-xl border border-slate-200 shadow-sm font-medium">
                              <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                              <span>{act}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>

              {/* Nearest Facilities List */}
              {currentMutation.data.data.nearest_facilities?.length > 0 && (
                <div className="glass-card p-5 space-y-3">
                  <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                    <MapPin className="w-4 h-4 text-emerald-700" /> Nearest Medical Facilities & Hospitals
                  </h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {currentMutation.data.data.nearest_facilities.map((fac: any, fIdx: number) => (
                      <div key={fIdx} className="p-3.5 bg-white/90 rounded-xl border border-slate-200 shadow-sm space-y-1">
                        <div className="flex justify-between items-start">
                          <h4 className="text-xs font-bold text-slate-900">{fac.name}</h4>
                          <span className="text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-200">
                            {fac.distance_km} km
                          </span>
                        </div>
                        <p className="text-xs text-slate-500 font-medium">{fac.type} • {fac.address || 'District Health Hub'}</p>
                        <p className="text-xs text-emerald-700 font-bold">📞 Call: {fac.phone || '108 / 104 Emergency'}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB 2: VACCINATION SCHEDULE RESULT VIEW */}
          {activeTab === 'vaccination' && (
            <div className="space-y-4">
              <div className="glass-card p-5 grid grid-cols-1 sm:grid-cols-3 gap-4 text-center">
                <div className="p-3.5 bg-white/90 rounded-xl border border-slate-200 shadow-sm">
                  <p className="text-xs text-slate-500 font-bold uppercase tracking-wider">Child Age</p>
                  <p className="text-xl font-extrabold text-slate-900 mt-1">{currentMutation.data.data.child_age_months || 0} Months</p>
                </div>
                <div className="p-3.5 bg-emerald-50 rounded-xl border border-emerald-200 shadow-sm">
                  <p className="text-xs text-emerald-800 font-bold uppercase tracking-wider">Upcoming Vaccines Due</p>
                  <p className="text-xl font-extrabold text-emerald-700 mt-1">{currentMutation.data.data.upcoming?.length || 0}</p>
                </div>
                <div className="p-3.5 bg-rose-50 rounded-xl border border-rose-200 shadow-sm">
                  <p className="text-xs text-rose-800 font-bold uppercase tracking-wider">Missed Vaccinations</p>
                  <p className="text-xl font-extrabold text-rose-700 mt-1">{currentMutation.data.data.missed?.length || 0}</p>
                </div>
              </div>

              {/* Vaccine List */}
              <div className="glass-card p-5 space-y-3">
                <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                  <Syringe className="w-4 h-4 text-emerald-700" /> Immunization Schedule & Vaccines
                </h3>
                <div className="divide-y divide-slate-200/80">
                  {currentMutation.data.data.schedule?.map((vac: any, vIdx: number) => (
                    <div key={vIdx} className="py-3 flex flex-wrap items-center justify-between gap-3">
                      <div>
                        <div className="flex items-center gap-2">
                          <h4 className="text-sm font-bold text-slate-900">{vac.vaccine_name}</h4>
                          <span className="badge bg-slate-100 text-slate-700 border border-slate-200">
                            Dose #{vac.dose_number}
                          </span>
                        </div>
                        <p className="text-xs text-slate-600 font-medium mt-0.5">Prevents: {vac.disease_prevented}</p>
                        <p className="text-[11px] text-slate-500">Recommended Age: {vac.recommended_age}</p>
                      </div>
                      <div className="text-right">
                        <span className={`badge ${
                          vac.is_due
                            ? 'bg-amber-100 text-amber-800 border border-amber-300'
                            : 'bg-emerald-100 text-emerald-800 border border-emerald-300'
                        }`}>
                          {vac.is_due ? 'Due Now' : 'Scheduled'}
                        </span>
                        <p className="text-[11px] text-slate-500 font-medium mt-1">{vac.nearest_center || 'Nearest PHC Sub-centre'}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* TAB 3: HEALTH CAMPS RESULT VIEW */}
          {activeTab === 'camps' && (
            <div className="glass-card p-5 space-y-4">
              <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                <Building2 className="w-4 h-4 text-emerald-700" /> Free Rural Health Camps Found ({currentMutation.data.data.camps?.length || 0})
              </h3>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {currentMutation.data.data.camps?.map((camp: any, cIdx: number) => (
                  <div key={cIdx} className="p-4 bg-white/90 rounded-2xl border border-slate-200 shadow-sm space-y-2">
                    <div className="flex justify-between items-start">
                      <h4 className="text-sm font-bold text-slate-900">{camp.name}</h4>
                      <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-200">
                        {camp.distance_km} km
                      </span>
                    </div>
                    <p className="text-xs text-emerald-800 font-bold">Organized by: {camp.organizer}</p>
                    <p className="text-xs text-slate-600 flex items-center gap-1.5 font-medium">
                      <Calendar className="w-3.5 h-3.5 text-slate-400" /> {camp.date} ({camp.timings})
                    </p>
                    <p className="text-xs text-slate-600 flex items-center gap-1.5 font-medium">
                      <MapPin className="w-3.5 h-3.5 text-slate-400" /> {camp.venue}
                    </p>
                    {camp.services?.length > 0 && (
                      <div className="pt-1 flex flex-wrap gap-1">
                        {camp.services.map((srv: string, sIdx: number) => (
                          <span key={sIdx} className="text-[10px] bg-slate-100 text-slate-700 px-2 py-0.5 rounded border border-slate-200 font-semibold">
                            {srv}
                          </span>
                        ))}
                      </div>
                    )}
                    <p className="text-xs text-emerald-700 font-bold pt-1">📞 Contact: {camp.contact_phone}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 4: EMERGENCY TRIAGE RESULT VIEW */}
          {activeTab === 'triage' && (
            <div className="space-y-5">
              {/* Triage Status Banner */}
              <div className={`p-5 rounded-2xl border shadow-sm flex flex-col sm:flex-row items-center justify-between gap-4 ${
                currentMutation.data.data.triage_level === 'RED'
                  ? 'bg-red-50 border-red-300' :
                currentMutation.data.data.triage_level === 'YELLOW'
                  ? 'bg-amber-50 border-amber-300' :
                'bg-emerald-50 border-emerald-300'
              }`}>
                <div className="flex items-center gap-4 text-center sm:text-left">
                  <div className={`p-3 rounded-2xl ${
                    currentMutation.data.data.triage_level === 'RED' ? 'bg-red-100 text-red-700' :
                    currentMutation.data.data.triage_level === 'YELLOW' ? 'bg-amber-100 text-amber-700' :
                    'bg-emerald-100 text-emerald-700'
                  }`}>
                    <AlertTriangle className="w-7 h-7" />
                  </div>
                  <div>
                    <p className="text-xs font-bold tracking-widest uppercase text-slate-500">Clinical Emergency Triage Level</p>
                    <h2 className="text-xl font-extrabold text-slate-900">
                      LEVEL: {currentMutation.data.data.triage_level} (
                      {currentMutation.data.data.triage_level === 'RED' ? 'IMMEDIATE EMERGENCY' :
                       currentMutation.data.data.triage_level === 'YELLOW' ? 'URGENT MEDICAL CARE' : 'NON-URGENT / ROUTINE'}
                      )
                    </h2>
                  </div>
                </div>

                {currentMutation.data.data.ambulance_needed && (
                  <a
                    href="tel:108"
                    className="btn-primary bg-red-600 hover:bg-red-700 text-white font-bold text-xs"
                  >
                    <PhoneCall className="w-4 h-4" /> DISPATCH 108 AMBULANCE NOW
                  </a>
                )}
              </div>

              {/* Immediate Actions Checklist */}
              <div className="glass-card p-5 space-y-3">
                <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                  <Activity className="w-4 h-4 text-emerald-700" /> Immediate Medical Actions Required
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {currentMutation.data.data.immediate_actions?.map((act: string, aIdx: number) => (
                    <div key={aIdx} className="p-3 bg-white/90 rounded-xl border border-slate-200 flex items-center gap-2 text-xs font-semibold text-slate-800 shadow-sm">
                      <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                      <span>{act}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Warning Signs */}
              {currentMutation.data.data.warning_signs?.length > 0 && (
                <div className="glass-card p-5 border border-amber-200 bg-amber-50/80 space-y-2">
                  <h4 className="text-xs font-bold text-amber-900 uppercase tracking-wider">Critical Signs to Monitor:</h4>
                  <ul className="text-xs text-amber-800 list-disc list-inside space-y-1 font-semibold">
                    {currentMutation.data.data.warning_signs.map((ws: string, wIdx: number) => (
                      <li key={wIdx}>{ws}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

        </div>
      )}
    </div>
  )
}
