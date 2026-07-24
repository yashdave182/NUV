import { memo } from 'react'
import { Sparkles, Sun, Droplets, ShieldCheck, ArrowUpRight, MessageSquareText, FileSpreadsheet, Radio, Activity, RefreshCw } from 'lucide-react'

interface Props {
  onAskAI?: () => void
  onViewSensors?: () => void
}

export const HeroSection = memo(function HeroSection({ onAskAI, onViewSensors }: Props) {
  return (
    <section className="relative overflow-hidden rounded-3xl p-6 lg:p-8 space-y-6 text-slate-900 border border-emerald-200/80 shadow-xl"
      style={{
        background: 'linear-gradient(135deg, #ffffff 0%, #f0fdf4 40%, #ecfdf5 70%, #fef9ee 100%)',
        boxShadow: '0 12px 40px -8px rgba(21, 128, 61, 0.12), 0 4px 12px rgba(0,0,0,0.02)'
      }}
    >
      {/* Background Decorative Blob */}
      <div className="absolute top-0 right-0 w-96 h-96 rounded-full bg-emerald-300/20 blur-3xl pointer-events-none -mr-20 -mt-20" />

      {/* Top Header Row */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-emerald-100/80 pb-5 relative z-10">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-emerald-600 to-teal-700 text-white flex items-center justify-center shadow-md">
            <Sun className="w-6 h-6 animate-spin" style={{ animationDuration: '18s' }} />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-black uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-300">
                Anand, Gujarat · 3.5 Acres
              </span>
              <span className="text-[10px] font-bold text-slate-500 flex items-center gap-1">
                <RefreshCw className="w-3 h-3 text-emerald-600" /> Synced: Just now
              </span>
            </div>
            <h1 className="text-2xl lg:text-3xl font-black tracking-tight text-slate-900 mt-0.5">
              Good Morning, Farmer 👋
            </h1>
          </div>
        </div>

        {/* Live Status Badge */}
        <div className="flex items-center gap-2">
          <span className="px-3 py-1.5 rounded-full text-xs font-black bg-emerald-100 text-emerald-800 border border-emerald-300 flex items-center gap-1.5 shadow-xs">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-ping"></span>
            SoilPulse™ Mesh Active
          </span>
        </div>
      </div>

      {/* Hero Content Grid (2 Cols) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 relative z-10 items-center">
        {/* Left Column: Today's AI Recommendation (7 Cols) */}
        <div className="lg:col-span-7 space-y-4">
          <div className="p-4 rounded-2xl bg-white/90 border border-emerald-200/90 shadow-xs space-y-2">
            <div className="flex items-center gap-2 text-xs font-black text-emerald-800">
              <Sparkles className="w-4 h-4 text-emerald-600 animate-pulse" />
              <span>TODAY'S AI PRECISION ADVISORY</span>
            </div>
            <p className="text-sm lg:text-base font-extrabold text-slate-900 leading-snug">
              Cotton vegetative stage (45 DAS). Rain expected tomorrow (27.4mm). Delay pesticide spray by 48 hours & apply 40 kg/ha Nitrogen top-dressing today.
            </p>
            <div className="flex items-center gap-4 text-xs font-bold text-slate-600 pt-1">
              <span className="flex items-center gap-1 text-emerald-700">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" /> Confidence: 94.2%
              </span>
              <span className="flex items-center gap-1 text-sky-700">
                <Droplets className="w-3.5 h-3.5 text-sky-600" /> Root Moisture: 42.8%
              </span>
            </div>
          </div>

          {/* Quick Action Buttons */}
          <div className="flex items-center gap-3 flex-wrap">
            <button
              onClick={onAskAI}
              className="px-4 py-2.5 rounded-xl font-bold text-xs bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white shadow-md transition-all flex items-center gap-2 cursor-pointer hover:scale-105"
            >
              <MessageSquareText className="w-4 h-4" />
              <span>Ask AI Assistant</span>
            </button>

            <button
              onClick={onViewSensors}
              className="px-4 py-2.5 rounded-xl font-bold text-xs bg-white hover:bg-emerald-50 text-slate-800 border border-emerald-300 shadow-xs transition-all flex items-center gap-2 cursor-pointer hover:scale-105"
            >
              <Radio className="w-4 h-4 text-emerald-600" />
              <span>Live Sensor Control</span>
            </button>

            <a
              href="#farm-health"
              className="px-4 py-2.5 rounded-xl font-bold text-xs bg-white hover:bg-emerald-50 text-slate-800 border border-emerald-300 shadow-xs transition-all flex items-center gap-2 cursor-pointer hover:scale-105"
            >
              <FileSpreadsheet className="w-4 h-4 text-teal-600" />
              <span>View Full Report</span>
            </a>
          </div>
        </div>

        {/* Right Column: Health Score Card (5 Cols) */}
        <div className="lg:col-span-5 p-5 rounded-2xl bg-gradient-to-br from-emerald-600 via-teal-700 to-emerald-800 text-white shadow-lg space-y-3 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs font-black uppercase tracking-wider text-emerald-200">
              Composite Farm Rating
            </span>
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black bg-white/20 text-white border border-white/30">
              OPTIMAL
            </span>
          </div>

          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-full bg-white/10 border-4 border-emerald-400 flex items-center justify-center flex-shrink-0">
              <span className="text-2xl font-black text-white">92</span>
            </div>
            <div>
              <p className="text-lg font-black text-white">92 / 100 Health Score</p>
              <p className="text-xs text-emerald-100 font-medium">Top 5% Soil & Moisture condition across Gujarat</p>
            </div>
          </div>

          <div className="pt-2 border-t border-white/20 flex items-center justify-between text-xs font-semibold text-emerald-100">
            <span>Soil: 94% · Weather: 86% · Water: 96%</span>
            <ArrowUpRight className="w-4 h-4 text-emerald-300" />
          </div>
        </div>
      </div>
    </section>
  )
})
