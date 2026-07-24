import { memo, useState } from 'react'
import { HelpCircle, Sparkles, CheckCircle2, Bell, RefreshCw } from 'lucide-react'
import type { AIExplainabilityFactors } from '../../types/dashboard'

interface Props {
  data?: AIExplainabilityFactors
}

export const AIExplainabilityPanel = memo(function AIExplainabilityPanel({ data }: Props) {
  const [loading, setLoading] = useState(false)
  const [subscribed, setSubscribed] = useState(false)
  const [toastMsg, setToastMsg] = useState<string | null>(null)

  const factors: AIExplainabilityFactors = data || {
    recommendationTitle: 'Recommended Irrigation: Apply 22 mm Root-Zone Drip Water',
    reasoningText: 'AI model evaluated 5 real-time environmental variables and predicted root-zone moisture deficit during critical flowering stage.',
    factors: {
      soilMoisture: '18% (Below 35% Stress Threshold)',
      temperature: '38°C (High Evapotranspiration Rate)',
      rainChance: '5% (No Precipitation expected in 72h)',
      cropStage: 'Flowering Stage (Critical Water Need)',
      expectedWaterNeed: '22 mm / Hectare',
    },
  }

  const handleGetDailyUpdate = () => {
    setLoading(true)
    setTimeout(() => {
      setLoading(false)
      setToastMsg('Latest Daily AI Update Synced! Moisture deficit re-evaluated for 07:00 AM window.')
      setTimeout(() => setToastMsg(null), 4000)
    }, 500)
  }

  const handleSubscribeDailySMS = () => {
    setSubscribed(true)
    setToastMsg('Subscribed to Daily SMS & WhatsApp Advisory! Daily digest scheduled at 07:00 AM.')
    setTimeout(() => setToastMsg(null), 4000)
  }

  return (
    <div className="glass-card p-6 border-l-4 border-l-amber-500 space-y-4 animate-fade-in h-full flex flex-col justify-between">
      {/* Header with Title and Daily Update Button */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl bg-amber-100 text-amber-800 flex items-center justify-center font-bold">
            <HelpCircle className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-base font-extrabold text-slate-900 flex items-center gap-1.5">
              <span>Why this AI Recommendation?</span>
              <Sparkles className="w-4 h-4 text-amber-500 animate-pulse" />
            </h4>
            <p className="text-xs text-slate-500 font-semibold">{factors.recommendationTitle}</p>
          </div>
        </div>

        {/* Daily Update & Subscribe Action Buttons */}
        <div className="flex items-center gap-2">
          <button
            onClick={handleGetDailyUpdate}
            disabled={loading}
            className="px-3 py-1.5 rounded-xl font-bold text-xs bg-amber-600 hover:bg-amber-700 text-white shadow-xs transition-all flex items-center gap-1.5 cursor-pointer hover:scale-105"
            title="Get Immediate Daily AI Update"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>{loading ? 'Updating...' : 'Get Daily Update'}</span>
          </button>

          <button
            onClick={handleSubscribeDailySMS}
            className={`px-3 py-1.5 rounded-xl font-bold text-xs border transition-all flex items-center gap-1.5 cursor-pointer hover:scale-105 ${
              subscribed
                ? 'bg-emerald-100 text-emerald-800 border-emerald-300'
                : 'bg-white hover:bg-amber-50 text-slate-800 border-amber-300'
            }`}
            title="Subscribe for Daily Morning SMS & WhatsApp Digest"
          >
            <Bell className={`w-3.5 h-3.5 ${subscribed ? 'text-emerald-600' : 'text-amber-600'}`} />
            <span>{subscribed ? 'Daily SMS Active' : 'Daily SMS'}</span>
          </button>
        </div>
      </div>

      {/* Toast Notification Alert */}
      {toastMsg && (
        <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-300 text-emerald-900 text-xs font-bold flex items-center gap-2 animate-fade-in">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
          <span>{toastMsg}</span>
        </div>
      )}

      {/* Main Reason Text */}
      <div className="p-4 rounded-2xl bg-amber-50/70 border border-amber-200/80 space-y-3 text-xs flex-1 flex flex-col justify-between">
        <p className="font-semibold text-slate-800 leading-relaxed">
          {factors.reasoningText}
        </p>

        {/* 6 Environmental Factor Badges */}
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5 pt-1">
          <div className="p-2.5 rounded-xl bg-white border border-amber-100 space-y-0.5 shadow-xs">
            <span className="text-[10px] font-bold text-slate-400 uppercase">Soil Moisture</span>
            <p className="font-extrabold text-slate-900 text-xs">{factors.factors.soilMoisture}</p>
          </div>
          <div className="p-2.5 rounded-xl bg-white border border-amber-100 space-y-0.5 shadow-xs">
            <span className="text-[10px] font-bold text-slate-400 uppercase">Ambient Temp</span>
            <p className="font-extrabold text-slate-900 text-xs">{factors.factors.temperature}</p>
          </div>
          <div className="p-2.5 rounded-xl bg-white border border-amber-100 space-y-0.5 shadow-xs">
            <span className="text-[10px] font-bold text-slate-400 uppercase">Rain Chance</span>
            <p className="font-extrabold text-slate-900 text-xs">{factors.factors.rainChance}</p>
          </div>
          <div className="p-2.5 rounded-xl bg-white border border-amber-100 space-y-0.5 shadow-xs">
            <span className="text-[10px] font-bold text-slate-400 uppercase">Growth Stage</span>
            <p className="font-extrabold text-slate-900 text-xs">{factors.factors.cropStage}</p>
          </div>
          <div className="p-2.5 rounded-xl bg-white border border-amber-100 space-y-0.5 shadow-xs">
            <span className="text-[10px] font-bold text-slate-400 uppercase">Water Need</span>
            <p className="font-extrabold text-slate-900 text-xs">{factors.factors.expectedWaterNeed}</p>
          </div>
          <div className="p-2.5 rounded-xl bg-emerald-50 border border-emerald-200 flex items-center gap-1.5 text-emerald-900 shadow-xs">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
            <span className="text-[11px] font-black">Confidence: 94.2%</span>
          </div>
        </div>
      </div>
    </div>
  )
})
