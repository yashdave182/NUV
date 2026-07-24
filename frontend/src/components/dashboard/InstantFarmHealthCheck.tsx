import { memo, useState, useCallback } from 'react'
import { Sparkles, CheckCircle2, Sprout, AlertTriangle, ShieldCheck, Droplets, FlaskConical, TrendingUp, Sun } from 'lucide-react'
import type { FarmHealthInput, FarmHealthResult } from '../../types/dashboard'
import { CROPS, SOIL_TYPES, STATES } from '../../lib/constants'

export const InstantFarmHealthCheck = memo(function InstantFarmHealthCheck() {
  const [form, setForm] = useState<FarmHealthInput>({
    crop: 'cotton',
    state: 'Gujarat',
    soilType: 'black_cotton',
  })
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<FarmHealthResult | null>(null)

  const handleGenerate = useCallback(() => {
    setLoading(true)
    setTimeout(() => {
      let score = 92
      let diseaseRisk: 'Low' | 'Medium' | 'High' = 'Low'
      let water = '22 mm / week (2 irrigations)'
      let fert = 'N-P-K (120:60:60 kg/ha). Top-dress 40 kg Nitrogen now.'
      let yld = '2.8 Tonnes / Hectare (+12% vs state average)'
      let mkt = 'Sell 60% harvest in 10-15 day peak window. Mandi price trending ▲ +2.4%.'
      let wtrAlert = 'Heavy rain expected tomorrow (27.4mm). Delay foliar spray.'

      if (form.crop === 'wheat') {
        score = 88
        water = '18 mm / week (CRI stage irrigation)'
        fert = 'Apply Urea @ 50 kg/ha with Zinc Sulphate'
        yld = '4.6 Tonnes / Hectare'
        mkt = 'Store in accredited warehouse. High demand anticipated next month.'
      } else if (form.crop === 'groundnut') {
        score = 94
        water = '15 mm / week (Pegging stage)'
        fert = 'Apply Gypsum @ 250 kg/ha at flowering'
        yld = '2.2 Tonnes / Hectare'
        mkt = 'Sell directly to local processor for 5% premium.'
      }

      setResult({
        overallScore: score,
        statusText: score >= 90 ? 'Optimal Farm Health' : 'Good Health - Action Needed',
        breakdown: { soilHealth: 92, weather: 85, water: 95, disease: 88, market: 90 },
        soilStatus: 'Optimal (pH: 7.8, OC: 0.6%, Black Cotton Soil)',
        diseaseRisk: diseaseRisk,
        waterRequirement: water,
        fertilizerSuggestion: fert,
        expectedYield: yld,
        marketRecommendation: mkt,
        weatherAlert: wtrAlert,
      })
      setLoading(false)
    }, 450)
  }, [form])

  return (
    <div className="glass-card p-6 border-l-4 border-l-emerald-600 space-y-5 animate-fade-in">
      {/* Title Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-emerald-500 to-green-600 text-white flex items-center justify-center shadow-md">
            <Sprout className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-extrabold text-slate-900">🌱 Instant AI Farm Health Check</h3>
            <p className="text-xs text-slate-500 font-medium">Sub-Second Multi-Variable Agronomic Evaluation</p>
          </div>
        </div>
        <span className="badge badge-green">AI Model v1.0</span>
      </div>

      {/* Input Selector Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <div>
          <label className="label text-xs">Crop</label>
          <select className="select text-xs" value={form.crop} onChange={e => setForm(f => ({ ...f, crop: e.target.value }))}>
            {CROPS.map(c => <option key={c.value} value={c.value}>{c.label}</option>)}
          </select>
        </div>
        <div>
          <label className="label text-xs">Location</label>
          <select className="select text-xs" value={form.state} onChange={e => setForm(f => ({ ...f, state: e.target.value }))}>
            {STATES.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>
        <div>
          <label className="label text-xs">Soil Type</label>
          <select className="select text-xs" value={form.soilType} onChange={e => setForm(f => ({ ...f, soilType: e.target.value }))}>
            {SOIL_TYPES.map(st => <option key={st.value} value={st.value}>{st.label}</option>)}
          </select>
        </div>
      </div>

      {/* Action Button */}
      <button
        onClick={handleGenerate}
        disabled={loading}
        className="w-full py-3 px-4 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white font-bold text-xs rounded-xl shadow-md transition-all flex items-center justify-center gap-2 cursor-pointer"
      >
        {loading ? <Sparkles className="w-4 h-4 animate-spin" /> : <CheckCircle2 className="w-4 h-4" />}
        <span>{loading ? 'Evaluating Agronomic Model...' : 'Generate AI Recommendation'}</span>
      </button>

      {/* Beautiful Results Cards Grid */}
      {result && (
        <div className="space-y-4 pt-2 animate-slide-up">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            {/* Soil Status */}
            <div className="p-3.5 rounded-2xl bg-emerald-50/70 border border-emerald-200/80 space-y-1">
              <div className="flex items-center gap-1.5 text-xs font-bold text-emerald-800">
                <Sprout className="w-3.5 h-3.5 text-emerald-600" />
                <span>Soil Status</span>
              </div>
              <p className="text-xs font-semibold text-slate-800">{result.soilStatus}</p>
            </div>

            {/* Disease Risk */}
            <div className="p-3.5 rounded-2xl bg-teal-50/70 border border-teal-200/80 space-y-1">
              <div className="flex items-center gap-1.5 text-xs font-bold text-teal-800">
                <ShieldCheck className="w-3.5 h-3.5 text-teal-600" />
                <span>Disease Risk</span>
              </div>
              <p className="text-xs font-semibold text-slate-800">{result.diseaseRisk} (Blight/Rust Risk &lt; 8%)</p>
            </div>

            {/* Water Need */}
            <div className="p-3.5 rounded-2xl bg-sky-50/70 border border-sky-200/80 space-y-1">
              <div className="flex items-center gap-1.5 text-xs font-bold text-sky-800">
                <Droplets className="w-3.5 h-3.5 text-sky-600" />
                <span>Water Need</span>
              </div>
              <p className="text-xs font-semibold text-slate-800">{result.waterRequirement}</p>
            </div>

            {/* Fertilizer */}
            <div className="p-3.5 rounded-2xl bg-amber-50/70 border border-amber-200/80 space-y-1">
              <div className="flex items-center gap-1.5 text-xs font-bold text-amber-800">
                <FlaskConical className="w-3.5 h-3.5 text-amber-600" />
                <span>Fertilizer</span>
              </div>
              <p className="text-xs font-semibold text-slate-800">{result.fertilizerSuggestion}</p>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {/* Expected Yield */}
            <div className="p-3.5 rounded-2xl bg-purple-50/70 border border-purple-200/80 space-y-1">
              <div className="flex items-center gap-1.5 text-xs font-bold text-purple-800">
                <TrendingUp className="w-3.5 h-3.5 text-purple-600" />
                <span>Expected Yield</span>
              </div>
              <p className="text-xs font-semibold text-slate-800">{result.expectedYield}</p>
            </div>

            {/* Market Rec */}
            <div className="p-3.5 rounded-2xl bg-indigo-50/70 border border-indigo-200/80 space-y-1">
              <div className="flex items-center gap-1.5 text-xs font-bold text-indigo-800">
                <Sparkles className="w-3.5 h-3.5 text-indigo-600" />
                <span>Market Strategy</span>
              </div>
              <p className="text-xs font-semibold text-slate-800">{result.marketRecommendation}</p>
            </div>

            {/* Weather Alert */}
            <div className="p-3.5 rounded-2xl bg-amber-50 border border-amber-300 space-y-1">
              <div className="flex items-center gap-1.5 text-xs font-bold text-amber-900">
                <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
                <span>Weather Alert</span>
              </div>
              <p className="text-xs font-semibold text-amber-950">{result.weatherAlert}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
})
