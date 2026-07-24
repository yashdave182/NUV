import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { ScrollText, CheckCircle2, FileSearch, Clock, ChevronRight, AlertCircle, PhoneCall, ExternalLink, ShieldCheck, FileText } from 'lucide-react'
import {
  searchSchemes, getSchemeDetail, trackApplication, checkEligibility,
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
  const [selectedSchemeId, setSelectedSchemeId] = useState<string>('PMKISAN')

  const [form, setForm] = useState({
    phone: phone || '',
    language: language || 'English',

    state: 'Gujarat',
    category: 'all',
    crop_type: 'cotton',
    land_holding_hectares: '2.5',
    application_id: 'APP-2026-8849',
    scheme_id: 'PMKISAN',
  })

  const set = (k: string, v: string) => setForm(f => ({ ...f, [k]: v }))

  // 1. Search Schemes Mutation
  const searchMutation = useMutation({
    mutationFn: () => searchSchemes({
      phone: form.phone,
      language: form.language,
      category: form.category === 'all' ? undefined : form.category,
      location: { state: form.state },
    }),
  })

  // 2. Eligibility Mutation
  const eligibilityMutation = useMutation({
    mutationFn: () => checkEligibility({
      phone: form.phone,
      language: form.language,
      scheme_id: form.scheme_id || selectedSchemeId,
      land_holding_hectares: parseFloat(form.land_holding_hectares) || 2.5,
      crop_type: form.crop_type,
      location: { state: form.state },
    }),
  })

  // 3. Track Application Mutation
  const trackMutation = useMutation({
    mutationFn: () => trackApplication({
      phone: form.phone,
      language: form.language,
      application_id: form.application_id || 'APP-2026-8849',
    }),
  })

  // 4. Scheme Detail Mutation
  const detailMutation = useMutation({
    mutationFn: () => getSchemeDetail({
      phone: form.phone,
      language: form.language,
      scheme_id: selectedSchemeId || form.scheme_id || 'PMKISAN',
    }),
  })

  const currentMutation =
    activeTab === 'eligibility' ? eligibilityMutation :
    activeTab === 'track' ? trackMutation :
    activeTab === 'detail' ? detailMutation : searchMutation

  const handleSelectSchemeDetail = (schemeId: string) => {
    setSelectedSchemeId(schemeId)
    set('scheme_id', schemeId)
    setActiveTab('detail')
    setTimeout(() => {
      detailMutation.mutate()
    }, 50)
  }

  return (
    <div className="space-y-5 max-w-5xl mx-auto pb-10">
      <PageHeader
        title="Government Schemes"
        subtitle="Discover PM-KISAN, PMFBY, KCC & state subsidy schemes with instant eligibility check"
        icon={ScrollText}
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

      {/* Form Input Container */}
      <div className="glass-card p-5 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
        <div className="form-group">
          <label className="label">Phone Number</label>
          <input className="input" value={form.phone} onChange={e => set('phone', e.target.value)} />
        </div>

        <div className="form-group">
          <label className="label">State</label>
          <select className="select" value={form.state} onChange={e => set('state', e.target.value)}>
            {STATES.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>

        <div className="form-group">
          <label className="label">Language</label>
          <select className="select" value={form.language} onChange={e => set('language', e.target.value)}>
            {['English', 'Hindi', 'Gujarati', 'Marathi', 'Tamil', 'Telugu'].map(l => <option key={l} value={l}>{l}</option>)}
          </select>
        </div>

        {activeTab === 'search' && (
          <div className="form-group md:col-span-3 sm:col-span-2">
            <label className="label">Category</label>
            <select className="select" value={form.category} onChange={e => set('category', e.target.value)}>
              <option value="all">All Categories (Income Support, Insurance, Equipment, Subsidy)</option>
              <option value="income_support">Direct Financial / Income Support</option>
              <option value="crop_insurance">Crop Insurance</option>
              <option value="credit_subsidy">Kisan Credit Card & Credit Subsidy</option>
              <option value="machinery_subsidy">Farm Machinery & Solar Subsidy</option>
            </select>
          </div>
        )}

        {activeTab === 'eligibility' && (
          <>
            <div className="form-group">
              <label className="label">Select Target Scheme</label>
              <select className="select" value={form.scheme_id} onChange={e => set('scheme_id', e.target.value)}>
                <option value="PMKISAN">PM-KISAN (₹6,000/yr Direct Transfer)</option>
                <option value="PMFBY">PM Fasal Bima Yojana (Crop Insurance)</option>
                <option value="KCC">Kisan Credit Card (Concessional Credit)</option>
                <option value="SMAM">Sub-Mission on Agricultural Mechanization</option>
              </select>
            </div>

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
          <div className="form-group md:col-span-3 sm:col-span-2">
            <label className="label">Application Reference ID</label>
            <input className="input" placeholder="e.g. APP-2026-8849" value={form.application_id} onChange={e => set('application_id', e.target.value)} />
          </div>
        )}

        {activeTab === 'detail' && (
          <div className="form-group md:col-span-3 sm:col-span-2">
            <label className="label">Scheme Code / ID</label>
            <select className="select" value={selectedSchemeId} onChange={e => setSelectedSchemeId(e.target.value)}>
              <option value="PMKISAN">PM-KISAN (PM Kisan Samman Nidhi)</option>
              <option value="PMFBY">PMFBY (Pradhan Mantri Fasal Bima Yojana)</option>
              <option value="KCC">KCC (Kisan Credit Card Scheme)</option>
              <option value="SMAM">SMAM (Agricultural Mechanization Subsidy)</option>
            </select>
          </div>
        )}

        <div className="md:col-span-3 sm:col-span-2 pt-1">
          <button className="btn-primary w-full" onClick={() => currentMutation.mutate()} disabled={currentMutation.isPending}>
            {currentMutation.isPending ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Processing Request…
              </>
            ) : (
              `Run ${tabs.find(t => t.id === activeTab)?.label}`
            )}
          </button>
        </div>
      </div>

      {/* Loading State */}
      {currentMutation.isPending && <LoadingCard label="Querying national government scheme databases" rows={4} />}

      {/* Error Alert */}
      {currentMutation.isError && <Alert type="error" message={currentMutation.error?.message || 'Failed to search schemes'} />}

      {/* Results Section */}
      {currentMutation.data?.data && (
        <div className="space-y-5 animate-slide-up">

          {/* SMS Summary Banner */}
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

          {/* TAB 1: DISCOVER SCHEMES RESULT VIEW */}
          {activeTab === 'search' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold text-slate-900">
                  Matched Government Schemes ({currentMutation.data.data.matched_schemes?.length || currentMutation.data.data.total_count || 0})
                </h3>
              </div>

              <div className="grid grid-cols-1 gap-4">
                {currentMutation.data.data.matched_schemes?.map((sch: any, idx: number) => (
                  <div key={idx} className="glass-card p-5 space-y-3">
                    <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-200/80 pb-3">
                      <div>
                        <div className="flex items-center gap-2">
                          <h3 className="text-base font-bold text-slate-900">{sch.name}</h3>
                          <span className="badge bg-emerald-100 text-emerald-800 border border-emerald-300">
                            {sch.scheme_id}
                          </span>
                        </div>
                        <p className="text-xs text-slate-500 font-medium mt-0.5">Agency: {sch.implementing_agency} ({sch.level})</p>
                      </div>

                      <button
                        onClick={() => handleSelectSchemeDetail(sch.scheme_id)}
                        className="btn-outline text-xs py-1.5 px-3 flex items-center gap-1"
                      >
                        View Full Details <ChevronRight className="w-3.5 h-3.5" />
                      </button>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                      <div className="p-3 bg-emerald-50/70 rounded-xl border border-emerald-200/60">
                        <p className="font-bold text-emerald-900 uppercase tracking-wider text-[10px]">Financial Benefits:</p>
                        <p className="font-semibold text-emerald-950 mt-0.5">{sch.benefit_summary}</p>
                      </div>
                      <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
                        <p className="font-bold text-slate-700 uppercase tracking-wider text-[10px]">Eligibility Criteria:</p>
                        <p className="font-medium text-slate-800 mt-0.5">{sch.eligibility_summary || 'All smallholder farmers'}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 2: ELIGIBILITY CHECK RESULT VIEW */}
          {activeTab === 'eligibility' && currentMutation.data.data.result && (
            <div className="space-y-4">
              <div className={`p-5 rounded-2xl border shadow-sm flex flex-col sm:flex-row items-center justify-between gap-4 ${
                currentMutation.data.data.result.is_eligible
                  ? 'bg-emerald-50 border-emerald-300'
                  : 'bg-amber-50 border-amber-300'
              }`}>
                <div className="flex items-center gap-4">
                  <div className={`p-3 rounded-2xl ${
                    currentMutation.data.data.result.is_eligible ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'
                  }`}>
                    <ShieldCheck className="w-7 h-7" />
                  </div>
                  <div>
                    <p className="text-xs font-bold uppercase tracking-wider text-slate-500">Eligibility Status</p>
                    <h2 className="text-xl font-extrabold text-slate-900">
                      {currentMutation.data.data.result.scheme_name}: {' '}
                      <span className={currentMutation.data.data.result.is_eligible ? 'text-emerald-700' : 'text-amber-800'}>
                        {currentMutation.data.data.result.is_eligible ? '✅ ELIGIBLE' : '⚠️ PARTIALLY ELIGIBLE'}
                      </span>
                    </h2>
                    <p className="text-xs font-semibold text-slate-600 mt-0.5">
                      Match Score: {currentMutation.data.data.result.eligibility_score}%
                    </p>
                  </div>
                </div>

                {currentMutation.data.data.result.estimated_benefit && (
                  <div className="p-3 bg-white/90 rounded-xl border border-slate-200 text-center shrink-0 shadow-sm">
                    <p className="text-[10px] font-bold text-slate-500 uppercase">Estimated Benefit</p>
                    <p className="text-base font-extrabold text-emerald-700">{currentMutation.data.data.result.estimated_benefit}</p>
                  </div>
                )}
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {/* Met Criteria */}
                <div className="glass-card p-5 space-y-2">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-emerald-800 flex items-center gap-1.5">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600" /> Criteria Met ({currentMutation.data.data.result.met_criteria?.length || 0})
                  </h4>
                  <ul className="space-y-1.5 text-xs text-slate-800 font-medium">
                    {currentMutation.data.data.result.met_criteria?.map((c: string, cIdx: number) => (
                      <li key={cIdx} className="flex items-center gap-2 p-2 bg-emerald-50/60 rounded-lg border border-emerald-100">
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                        <span>{c}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Missing / Next Steps */}
                <div className="glass-card p-5 space-y-2">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-800 flex items-center gap-1.5">
                    <FileText className="w-4 h-4 text-slate-600" /> Next Steps & Required Documents
                  </h4>
                  <ul className="space-y-1.5 text-xs text-slate-800 font-medium">
                    {currentMutation.data.data.result.next_steps?.map((step: string, sIdx: number) => (
                      <li key={sIdx} className="flex items-start gap-2 p-2 bg-slate-50 rounded-lg border border-slate-200">
                        <span className="text-emerald-700 font-bold">•</span>
                        <span>{step}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}

          {/* TAB 3: TRACK APPLICATION RESULT VIEW */}
          {activeTab === 'track' && currentMutation.data.data.application && (
            <div className="glass-card p-5 space-y-4">
              <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200/80 pb-3">
                <div>
                  <p className="text-xs font-bold text-slate-500 uppercase tracking-wider">Application Ref: {currentMutation.data.data.application.application_id}</p>
                  <h3 className="text-lg font-bold text-slate-900">{currentMutation.data.data.application.scheme_name}</h3>
                </div>
                <span className="badge bg-emerald-100 text-emerald-800 border border-emerald-300 font-bold px-3 py-1 text-xs uppercase">
                  Status: {currentMutation.data.data.application.status?.replace('_', ' ')}
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
                <div className="p-3 bg-white/90 rounded-xl border border-slate-200">
                  <p className="text-[10px] text-slate-500 font-bold uppercase">Current Stage</p>
                  <p className="font-bold text-slate-900 mt-0.5">{currentMutation.data.data.application.current_stage}</p>
                </div>
                <div className="p-3 bg-white/90 rounded-xl border border-slate-200">
                  <p className="text-[10px] text-slate-500 font-bold uppercase">Submitted Date</p>
                  <p className="font-bold text-slate-900 mt-0.5">{currentMutation.data.data.application.submitted_date}</p>
                </div>
                <div className="p-3 bg-white/90 rounded-xl border border-slate-200">
                  <p className="text-[10px] text-slate-500 font-bold uppercase">Expected Completion</p>
                  <p className="font-bold text-slate-900 mt-0.5">{currentMutation.data.data.application.expected_completion}</p>
                </div>
              </div>

              {currentMutation.data.data.application.remarks && (
                <div className="p-3 bg-emerald-50/80 rounded-xl border border-emerald-200 text-xs text-emerald-950 font-medium">
                  💬 Official Remarks: {currentMutation.data.data.application.remarks}
                </div>
              )}
            </div>
          )}

          {/* TAB 4: SCHEME DETAILS RESULT VIEW */}
          {activeTab === 'detail' && (
            <div className="space-y-4">
              <div className="glass-card p-5 space-y-3">
                <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200/80 pb-3">
                  <div>
                    <h3 className="text-xl font-extrabold text-slate-900">{currentMutation.data.data.name}</h3>
                    <p className="text-xs text-slate-500 font-medium">Agency: {currentMutation.data.data.implementing_agency} ({currentMutation.data.data.level})</p>
                  </div>
                  {currentMutation.data.data.helpline && (
                    <div className="p-2.5 bg-emerald-50 rounded-xl border border-emerald-200 text-xs font-bold text-emerald-800">
                      📞 Helpline: {currentMutation.data.data.helpline}
                    </div>
                  )}
                </div>

                <p className="text-sm text-slate-700 leading-relaxed font-medium">{currentMutation.data.data.description}</p>

                {/* Benefits List */}
                {currentMutation.data.data.benefits?.length > 0 && (
                  <div className="space-y-2 pt-2">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-emerald-800">Scheme Benefits:</h4>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                      {currentMutation.data.data.benefits.map((b: any, bIdx: number) => (
                        <div key={bIdx} className="p-3 bg-emerald-50/70 rounded-xl border border-emerald-200/80 text-xs">
                          <p className="font-bold text-emerald-950">{b.type || 'Benefit'}</p>
                          <p className="text-emerald-800 font-semibold">{b.amount || b.details || 'Provided'}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Application Process Steps */}
                {currentMutation.data.data.application_process?.length > 0 && (
                  <div className="space-y-2 pt-3">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-slate-800">Application Workflow & Steps:</h4>
                    <div className="space-y-2">
                      {currentMutation.data.data.application_process.map((step: any, sIdx: number) => (
                        <div key={sIdx} className="p-3 bg-white/90 rounded-xl border border-slate-200 flex items-start gap-3 text-xs shadow-sm">
                          <span className="w-6 h-6 rounded-full bg-emerald-700 text-white font-bold flex items-center justify-center shrink-0 text-[11px]">
                            {step.step_number || sIdx + 1}
                          </span>
                          <div>
                            <p className="font-bold text-slate-900">{step.title}</p>
                            <p className="text-slate-600 font-medium">{step.description}</p>
                            <p className="text-[11px] text-slate-500 mt-0.5">Channel: {step.channel} • Authority: {step.authority}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

        </div>
      )}
    </div>
  )
}
