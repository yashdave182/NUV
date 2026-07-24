import { memo } from 'react'
import { X, Activity, Satellite, Radio, Shield, CheckCircle2, Send, Cpu, Sparkles } from 'lucide-react'

export type TechPillarType = 'sensor' | 'orbital' | 'sms' | 'ml' | null

interface Props {
  activePillar: TechPillarType
  onClose: () => void
}

export const TechPillarsModal = memo(function TechPillarsModal({ activePillar, onClose }: Props) {
  if (!activePillar) return null

  return (
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-md flex items-center justify-center p-4 animate-fade-in">
      <div className="bg-white rounded-3xl max-w-lg w-full p-6 shadow-2xl border border-emerald-100 space-y-5 animate-slide-up relative">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-600 transition-colors cursor-pointer"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Modal Header & Content based on pillar type */}
        {activePillar === 'sensor' && (
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-2xl bg-emerald-600 text-white flex items-center justify-center shadow-lg">
                <Activity className="w-6 h-6 animate-pulse" />
              </div>
              <div>
                <h3 className="text-lg font-black text-slate-900">SoilPulse™ Sensor Mesh Engine</h3>
                <p className="text-xs font-bold text-emerald-700">IoT Hardware & Real-Time Probes</p>
              </div>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed font-medium">
              SoilPulse™ Gen 4 nodes collect sub-second Soil Moisture (42.8%), Ambient Temperature (28.5°C), and Relative Humidity (62.0%) over LoRaWAN & ThingSpeak API.
            </p>
            <div className="p-3.5 rounded-2xl bg-emerald-50 border border-emerald-200 space-y-2 text-xs">
              <div className="flex items-center justify-between font-bold text-emerald-900">
                <span>ThingSpeak Channel ID: #3430931</span>
                <span className="px-2 py-0.5 rounded-full bg-emerald-600 text-white text-[10px]">LIVE CONNECTED</span>
              </div>
              <p className="text-[11px] text-slate-700 font-semibold">
                ✓ Coverage: Up to 5 Acres / Node | Battery: 3-Year Solar LiFePO4
              </p>
            </div>
          </div>
        )}

        {activePillar === 'orbital' && (
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-2xl bg-teal-600 text-white flex items-center justify-center shadow-lg">
                <Satellite className="w-6 h-6" />
              </div>
              <div>
                <h3 className="text-lg font-black text-slate-900">Orbital AI Satellite NDVI Feed</h3>
                <p className="text-xs font-bold text-teal-700">Sentinel-2 & NASA POWER Multi-Spectral Analytics</p>
              </div>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed font-medium">
              Real-time 10m resolution canopy health index mapping. Detects nitrogen stress, leaf moisture deficits, and fungal pathogens 7-10 days before visual symptoms appear.
            </p>
            <div className="p-3.5 rounded-2xl bg-teal-50 border border-teal-200 space-y-2 text-xs">
              <div className="flex items-center justify-between font-bold text-teal-900">
                <span>NDVI Index: 0.725 (Optimal)</span>
                <span className="px-2 py-0.5 rounded-full bg-teal-600 text-white text-[10px]">PAN-INDIA 10m</span>
              </div>
              <p className="text-[11px] text-slate-700 font-semibold">
                ✓ Multi-Spectral Bands: B4 (Red) + B8 (NIR) | Re-visit Cycle: 5 Days
              </p>
            </div>
          </div>
        )}

        {activePillar === 'sms' && (
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-2xl bg-amber-600 text-white flex items-center justify-center shadow-lg">
                <Radio className="w-6 h-6 animate-pulse" />
              </div>
              <div>
                <h3 className="text-lg font-black text-slate-900">Multilingual SMS Alert Gateway</h3>
                <p className="text-xs font-bold text-amber-700">Feature Phone & Low-Data Connectivity</p>
              </div>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed font-medium">
              Dispatches critical weather advisories, mandi price alert triggers, and pest emergency warnings via SMS/WhatsApp in 14 Indian languages.
            </p>
            <div className="p-3.5 rounded-2xl bg-amber-50 border border-amber-200 space-y-2 text-xs text-amber-950">
              <div className="flex items-center justify-between font-bold">
                <span>Sample SMS (Gujlish):</span>
                <span className="px-2 py-0.5 rounded-full bg-amber-600 text-white text-[10px]">SENT</span>
              </div>
              <p className="text-[11px] font-mono bg-white p-2 rounded-xl border border-amber-200 text-slate-800">
                "AgriNova Alert: Cotton Mandi price ₹6,880/q hit target! Rain tomorrow 27mm, delay pesticide spray."
              </p>
            </div>
          </div>
        )}

        {activePillar === 'ml' && (
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-2xl bg-purple-600 text-white flex items-center justify-center shadow-lg">
                <Shield className="w-6 h-6" />
              </div>
              <div>
                <h3 className="text-lg font-black text-slate-900">Scikit-Learn & XGBoost ML Engine</h3>
                <p className="text-xs font-bold text-purple-700">Predictive Yield & Disease Classifier</p>
              </div>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed font-medium">
              Trained on 15,000+ historical crop yield records and agronomic parameters. Achieves R² = 0.94 yield prediction accuracy across 18 Indian crop varieties.
            </p>
            <div className="p-3.5 rounded-2xl bg-purple-50 border border-purple-200 space-y-2 text-xs text-purple-950">
              <div className="flex items-center justify-between font-bold">
                <span>Model Metrics:</span>
                <span className="px-2 py-0.5 rounded-full bg-purple-600 text-white text-[10px]">R² = 0.94</span>
              </div>
              <p className="text-[11px] font-semibold text-slate-700">
                ✓ 18 Yield Models Loaded | Spoilage Decay Curves | Disease Rule Classifier
              </p>
            </div>
          </div>
        )}

        <button
          onClick={onClose}
          className="w-full py-3 bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs rounded-xl transition-all cursor-pointer"
        >
          Close Tech Inspector
        </button>
      </div>
    </div>
  )
})
