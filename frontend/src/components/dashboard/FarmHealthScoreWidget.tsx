import { memo } from 'react'
import { Award, ShieldCheck } from 'lucide-react'
import type { HealthScoreBreakdown } from '../../types/dashboard'

interface Props {
  score?: number
  breakdown?: HealthScoreBreakdown
}

export const FarmHealthScoreWidget = memo(function FarmHealthScoreWidget({
  score = 92,
  breakdown = { soilHealth: 94, weather: 86, water: 96, disease: 88, market: 92 }
}: Props) {
  const radius = 52
  const circumference = 2 * Math.PI * radius
  const strokeDashoffset = circumference - (score / 100) * circumference

  return (
    <div className="glass-card p-6 space-y-5 animate-fade-in border-l-4 border-l-emerald-600 h-full flex flex-col justify-between">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl bg-emerald-600 text-white flex items-center justify-center shadow-md">
            <Award className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-extrabold text-slate-900">Farm Health Score Engine</h3>
            <p className="text-xs text-slate-500 font-medium">Composite Agronomic Rating</p>
          </div>
        </div>
        <span className="badge badge-green">Healthy Farm</span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-12 gap-6 items-center">
        {/* SVG Circular Progress Widget (5 Cols) */}
        <div className="sm:col-span-5 flex flex-col items-center justify-center p-4 rounded-2xl bg-gradient-to-b from-emerald-50/80 to-slate-50 border border-emerald-100 relative">
          <div className="relative w-36 h-36 flex items-center justify-center">
            <svg className="w-full h-full transform -rotate-90">
              <circle
                cx="72"
                cy="72"
                r={radius}
                className="text-slate-200"
                strokeWidth="10"
                stroke="currentColor"
                fill="transparent"
              />
              <circle
                cx="72"
                cy="72"
                r={radius}
                className="text-emerald-600 transition-all duration-1000 ease-out"
                strokeWidth="10"
                strokeDasharray={circumference}
                strokeDashoffset={strokeDashoffset}
                strokeLinecap="round"
                stroke="currentColor"
                fill="transparent"
              />
            </svg>
            <div className="absolute flex flex-col items-center justify-center text-center">
              <span className="text-3xl font-black text-slate-900 tracking-tight">{score}</span>
              <span className="text-[10px] font-extrabold text-emerald-700 uppercase tracking-widest">/ 100</span>
            </div>
          </div>
          <p className="text-xs font-bold text-slate-700 mt-2 flex items-center gap-1">
            <ShieldCheck className="w-4 h-4 text-emerald-600" />
            <span>Optimal Crop Condition</span>
          </p>
        </div>

        {/* Animated Progress Bars Breakdown (7 Cols) */}
        <div className="sm:col-span-7 space-y-3">
          <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Metric Breakdown</p>
          
          <div className="space-y-2 text-xs">
            <div>
              <div className="flex justify-between font-bold text-slate-700 mb-1">
                <span>Soil Health (pH 7.8, NPK balance)</span>
                <span className="text-emerald-700">{breakdown.soilHealth}%</span>
              </div>
              <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
                <div className="bg-emerald-600 h-2 rounded-full transition-all duration-700" style={{ width: `${breakdown.soilHealth}%` }} />
              </div>
            </div>

            <div>
              <div className="flex justify-between font-bold text-slate-700 mb-1">
                <span>Weather Window & Microclimate</span>
                <span className="text-sky-700">{breakdown.weather}%</span>
              </div>
              <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
                <div className="bg-sky-600 h-2 rounded-full transition-all duration-700" style={{ width: `${breakdown.weather}%` }} />
              </div>
            </div>

            <div>
              <div className="flex justify-between font-bold text-slate-700 mb-1">
                <span>Water & Root-Zone Moisture</span>
                <span className="text-teal-700">{breakdown.water}%</span>
              </div>
              <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
                <div className="bg-teal-600 h-2 rounded-full transition-all duration-700" style={{ width: `${breakdown.water}%` }} />
              </div>
            </div>

            <div>
              <div className="flex justify-between font-bold text-slate-700 mb-1">
                <span>Disease & Pathogen Safety</span>
                <span className="text-purple-700">{breakdown.disease}%</span>
              </div>
              <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
                <div className="bg-purple-600 h-2 rounded-full transition-all duration-700" style={{ width: `${breakdown.disease}%` }} />
              </div>
            </div>

            <div>
              <div className="flex justify-between font-bold text-slate-700 mb-1">
                <span>Market Demand & Mandi Price Trend</span>
                <span className="text-amber-700">{breakdown.market}%</span>
              </div>
              <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
                <div className="bg-amber-600 h-2 rounded-full transition-all duration-700" style={{ width: `${breakdown.market}%` }} />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
})
