import { useState, useEffect, useRef, memo, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  ArrowRight, Satellite, Leaf, ShoppingCart, Beef, Heart, ScrollText,
} from 'lucide-react'
import { api } from '../api/client'

// Modular Component Imports
import { HeroSection } from '../components/dashboard/HeroSection'
import { KPICards } from '../components/dashboard/KPICards'
import { WeatherIntelligenceCard } from '../components/dashboard/WeatherIntelligenceCard'
import { LiveMandiTicker } from '../components/dashboard/LiveMandiTicker'
import { InstantFarmHealthCheck } from '../components/dashboard/InstantFarmHealthCheck'
import { FarmHealthScoreWidget } from '../components/dashboard/FarmHealthScoreWidget'
import { ActionTimelineWidget } from '../components/dashboard/ActionTimelineWidget'
import { SensorStatusWidget } from '../components/dashboard/SensorStatusWidget'
import { AIExplainabilityPanel } from '../components/dashboard/AIExplainabilityPanel'
import { MiniEcosystemCarousel } from '../components/dashboard/MiniEcosystemCarousel'
import { AIAssistantModal } from '../components/dashboard/AIAssistantModal'

// ── Feature Modules ──────────────────────────────────────────────────────────
const modules = [
  {
    icon: Leaf,
    label: 'Crop Advisory',
    desc: 'Soil health, pest diagnostics, irrigation scheduling, and variety recommendations.',
    to: '/advisory',
    gradient: 'linear-gradient(135deg, #f0fdf4 0%, #dcfce7 60%, #bbf7d0 100%)',
    border: 'rgba(134, 239, 172, 0.6)',
    iconBg: 'linear-gradient(135deg, #16a34a, #15803d)',
    textColor: '#15803d',
    stat: '10 Modules',
  },
  {
    icon: ShoppingCart,
    label: 'Market Intel',
    desc: 'Live mandi prices, AI price forecasting, spoilage curves, and storage decisions.',
    to: '/market',
    gradient: 'linear-gradient(135deg, #fffbeb 0%, #fef3c7 60%, #fde68a 100%)',
    border: 'rgba(253, 211, 77, 0.5)',
    iconBg: 'linear-gradient(135deg, #d97706, #b45309)',
    textColor: '#b45309',
    stat: '9 Features',
  },
  {
    icon: Beef,
    label: 'Livestock AI',
    desc: 'Vaccination schedules, disease diagnosis, feed optimization, and breeding advice.',
    to: '/livestock',
    gradient: 'linear-gradient(135deg, #fff7ed 0%, #ffedd5 60%, #fed7aa 100%)',
    border: 'rgba(253, 186, 116, 0.55)',
    iconBg: 'linear-gradient(135deg, #ea580c, #c2410c)',
    textColor: '#c2410c',
    stat: '9 Tools',
  },
  {
    icon: Heart,
    label: 'Health Advisory',
    desc: 'Emergency triage, vaccination drives, and nearest health camp locations.',
    to: '/health',
    gradient: 'linear-gradient(135deg, #fff1f2 0%, #ffe4e6 60%, #fecdd3 100%)',
    border: 'rgba(252, 165, 165, 0.55)',
    iconBg: 'linear-gradient(135deg, #e11d48, #be123c)',
    textColor: '#be123c',
    stat: '4 Services',
  },
  {
    icon: ScrollText,
    label: 'Gov. Schemes',
    desc: 'Search, eligibility check, and track PM Kisan, Fasal Bima, and 40+ schemes.',
    to: '/schemes',
    gradient: 'linear-gradient(135deg, #eff6ff 0%, #dbeafe 60%, #bfdbfe 100%)',
    border: 'rgba(147, 197, 253, 0.55)',
    iconBg: 'linear-gradient(135deg, #2563eb, #1d4ed8)',
    textColor: '#1d4ed8',
    stat: '40+ Schemes',
  },
  {
    icon: Satellite,
    label: 'Satellite NDVI',
    desc: 'Live canopy health index, nitrogen stress mapping, and yield predictions.',
    to: '/advisory',
    gradient: 'linear-gradient(135deg, #f5f3ff 0%, #ede9fe 60%, #ddd6fe 100%)',
    border: 'rgba(196, 181, 253, 0.55)',
    iconBg: 'linear-gradient(135deg, #7c3aed, #6d28d9)',
    textColor: '#6d28d9',
    stat: 'Real-time',
  },
]

// ── Impact Stats ─────────────────────────────────────────────────────────────
const stats = [
  { val: '85%',   label: 'Yield Accuracy',      sub: 'ML model R² = 0.94',    color: '#15803d', bg: 'rgba(220,252,231,0.7)' },
  { val: '35%',   label: 'Water Savings',        sub: 'Smart irrigation AI',   color: '#0d9488', bg: 'rgba(204,251,241,0.7)' },
  { val: '2.4K+', label: 'Active IoT Nodes',     sub: 'Real-time telemetry',   color: '#d97706', bg: 'rgba(253,230,138,0.5)' },
  { val: '40+',   label: 'Gov. Schemes Indexed', sub: 'Auto-eligibility check', color: '#1d4ed8', bg: 'rgba(219,234,254,0.7)' },
  { val: '14',    label: 'Indian Languages',     sub: 'Including Hinglish',    color: '#7c3aed', bg: 'rgba(237,233,254,0.7)' },
  { val: '30%',   label: 'Post-Harvest Loss Cut', sub: 'Spoilage curve AI',    color: '#be123c', bg: 'rgba(254,228,226,0.7)' },
]

export default memo(function Dashboard() {
  const navigate = useNavigate()
  const [statsVisible, setStatsVisible] = useState(false)
  const [isAIModalOpen, setIsAIModalOpen] = useState(false)
  const statsRef = useRef<HTMLDivElement>(null)

  // Intersection observer for stats animation
  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => { if (entry.isIntersecting) setStatsVisible(true) },
      { threshold: 0.3 }
    )
    if (statsRef.current) observer.observe(statsRef.current)
    return () => observer.disconnect()
  }, [])

  const scrollToSensors = useCallback(() => {
    const el = document.getElementById('iot-sensors')
    if (el) el.scrollIntoView({ behavior: 'smooth' })
  }, [])

  return (
    <div className="space-y-6 pb-12">

      {/* 1. HERO GREETING & TODAY'S AI ADVISORY */}
      <HeroSection onAskAI={() => setIsAIModalOpen(true)} onViewSensors={scrollToSensors} />

      {/* Interactive AI Kisan Assistant Chat Modal */}
      <AIAssistantModal isOpen={isAIModalOpen} onClose={() => setIsAIModalOpen(false)} />

      {/* 2. LIVE MANDI PRICE TICKER */}
      <LiveMandiTicker />

      {/* 3. DASHBOARD KPI OVERVIEW CARDS (Temp, Moisture, Humidity, Yield) */}
      <KPICards />

      {/* 4. AI WEATHER INTELLIGENCE & FORECAST CARD */}
      <WeatherIntelligenceCard />

      {/* 5. INSTANT AI FARM HEALTH CHECK (1-Click Agronomic Evaluator) */}
      <div id="farm-health">
        <InstantFarmHealthCheck />
      </div>

      {/* 6. FARM HEALTH SCORE GAUGE & AI EXPLAINABILITY PANEL */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
        <div className="lg:col-span-6 flex flex-col">
          <FarmHealthScoreWidget />
        </div>
        <div className="lg:col-span-6 flex flex-col">
          <AIExplainabilityPanel />
        </div>
      </div>

      {/* 7. TODAY'S ACTION TIMELINE & LIVE IOT TELEMETRY */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-6">
          <ActionTimelineWidget />
        </div>
        <div id="iot-sensors" className="lg:col-span-6 flex flex-col gap-4">
          <SensorStatusWidget />
          <MiniEcosystemCarousel />
        </div>
      </div>

      {/* 9. PLATFORM MODULE CARDS */}
      <section className="space-y-4 pt-2">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-emerald-800 mb-0.5">Platform Modules</p>
            <h2 className="text-xl font-black text-slate-900">Everything a Farmer Needs</h2>
          </div>
          <span className="badge-green badge">6 AI Modules</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {modules.map(({ icon: Icon, label, desc, to, gradient, border, iconBg, textColor, stat }, i) => (
            <div
              key={i}
              onClick={() => navigate(to)}
              className="group cursor-pointer rounded-2xl p-5 flex flex-col gap-4 card-hover shadow-xs"
              style={{
                background: gradient,
                border: `1px solid ${border}`,
              }}
            >
              <div className="flex items-start justify-between">
                <div className="w-10 h-10 rounded-xl flex items-center justify-center shadow-md text-white" style={{ background: iconBg }}>
                  <Icon className="w-5 h-5" />
                </div>
                <span className="text-[10px] font-extrabold uppercase px-2 py-0.5 rounded-full bg-white/80 border border-slate-200/60" style={{ color: textColor }}>
                  {stat}
                </span>
              </div>
              <div className="space-y-1">
                <h3 className="text-base font-extrabold text-slate-900">{label}</h3>
                <p className="text-xs font-medium text-slate-600 leading-relaxed">{desc}</p>
              </div>
              <div className="mt-auto pt-1 flex items-center gap-1 text-xs font-bold" style={{ color: textColor }}>
                <span>Open Module</span>
                <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* 9. MEASURABLE IMPACT STATS */}
      <section ref={statsRef} className="space-y-4 pt-2">
        <div>
          <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-emerald-800 mb-0.5">Measurable Impact</p>
          <h2 className="text-xl font-black text-slate-900">Real Numbers. Real Farmers.</h2>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          {stats.map(({ val, label, sub, color, bg }, i) => (
            <div
              key={i}
              className={`p-4 rounded-2xl border text-center transition-all ${
                statsVisible ? 'animate-slide-up' : 'opacity-0'
              }`}
              style={{ background: bg, borderColor: `${color}30` }}
            >
              <p className="text-2xl font-black tracking-tight" style={{ color }}>{val}</p>
              <p className="text-xs font-bold text-slate-800 mt-1 leading-tight">{label}</p>
              <p className="text-[9px] font-semibold text-slate-500 mt-0.5">{sub}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
})
