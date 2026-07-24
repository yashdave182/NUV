import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  ArrowRight, Satellite, BarChart3,
  Activity, Sparkles, Radio, Smartphone,
  Leaf, ShoppingCart, Beef, Heart, ScrollText, Zap, Globe,
  TrendingUp, Droplets, Sun, Wind, Award, Shield,
} from 'lucide-react'
import { api } from '../api/client'
import { useAppStore } from '../store/appStore'
import { ThingspeakWidget } from '../components/ThingspeakWidget'


// ── Carousel Data ────────────────────────────────────────────────────────────
const slides = [
  {
    id: 1,
    eyebrow: 'IoT Hardware Ecosystem',
    title: 'SoilPulse™ Gen 4 IoT Sensor',
    subtitle: 'Enterprise-grade soil moisture, NPK & pH sensors with zero-latency ThingSpeak telemetry. Covers up to 5 acres per node with sub-second readings.',
    metrics: [
      { label: 'Battery Life', val: '3 Years', icon: Zap },
      { label: 'Data Latency', val: '<1 Sec', icon: Activity },
      { label: 'Accuracy', val: '99.2%', icon: Shield },
    ],
    img: '/carousel_iot_field.png',
    tag: 'IoT Hardware',
    accentFrom: '#15803d',
    accentTo: '#0d9488',
    accentLight: '#dcfce7',
    badgeClass: 'badge-green',
    tagColor: '#15803d',
    tagBg: 'rgba(220,252,231,0.92)',
  },
  {
    id: 2,
    eyebrow: 'Satellite Precision Analytics',
    title: 'Crop Health & NDVI AI Monitoring',
    subtitle: 'Real-time multi-spectral satellite feed detects pathogens and moisture stress before they become visible. Covers all of India at 10m resolution.',
    metrics: [
      { label: 'Resolution', val: '10m Multi', icon: Satellite },
      { label: 'Yield Acc.', val: '94.2%', icon: TrendingUp },
      { label: 'Coverage', val: 'Pan-India', icon: Globe },
    ],
    img: '/carousel_satellite.png',
    tag: 'Orbital AI',
    accentFrom: '#0d9488',
    accentTo: '#0369a1',
    accentLight: '#ccfbf1',
    badgeClass: 'badge-teal',
    tagColor: '#0f766e',
    tagBg: 'rgba(204,251,241,0.92)',
  },
  {
    id: 3,
    eyebrow: 'Smart Water Management',
    title: 'AI Drip Irrigation & Probe Network',
    subtitle: 'High-frequency root-zone monitoring with ET-based automated micro-irrigation dispatch, reducing water usage by 35% while maximising yield.',
    metrics: [
      { label: 'Water Saved', val: '35%', icon: Droplets },
      { label: 'Response', val: '<1s', icon: Radio },
      { label: 'Crops', val: '18 Types', icon: Leaf },
    ],
    img: '/carousel_irrigation.png',
    tag: 'Smart Water',
    accentFrom: '#1d4ed8',
    accentTo: '#7c3aed',
    accentLight: '#dbeafe',
    badgeClass: 'badge-blue',
    tagColor: '#1d4ed8',
    tagBg: 'rgba(219,234,254,0.92)',
  },
]

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

// ── Tech Pillars ─────────────────────────────────────────────────────────────
const pillars = [
  { icon: Activity, label: 'Sensor Mesh', sub: 'Real-time NPK + pH + Moisture IoT',  color: '#15803d' },
  { icon: Satellite, label: 'Orbital AI', sub: 'NDVI satellite multi-spectral feed',  color: '#0d9488' },
  { icon: Radio,    label: 'SMS Gateway', sub: 'Low-data alerts in 14 languages',     color: '#d97706' },
  { icon: Shield,   label: 'ML Engine',  sub: 'Scikit-learn + XGBoost predictors',   color: '#7c3aed' },
]



export default function Dashboard() {
  const navigate = useNavigate()
  const { phone, language } = useAppStore()
  const [slide, setSlide] = useState(0)
  const [isTransitioning, setIsTransitioning] = useState(false)
  const [apiStatus, setApiStatus] = useState<'checking' | 'online' | 'offline'>('checking')
  const [apiVersion, setApiVersion] = useState('')
  const [statsVisible, setStatsVisible] = useState(false)
  const statsRef = useRef<HTMLDivElement>(null)

  // API health check
  useEffect(() => {
    api.get('/health').then((r) => {
      setApiStatus('online')
      setApiVersion(r.data?.version || '1.0.0')
    }).catch(() => setApiStatus('offline'))
  }, [])

  // Auto-advance carousel
  useEffect(() => {
    const t = setInterval(() => changeSlide((slide + 1) % slides.length), 6000)
    return () => clearInterval(t)
  }, [slide])

  // Intersection observer for stats animation
  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => { if (entry.isIntersecting) setStatsVisible(true) },
      { threshold: 0.3 }
    )
    if (statsRef.current) observer.observe(statsRef.current)
    return () => observer.disconnect()
  }, [])

  function changeSlide(idx: number) {
    if (isTransitioning) return
    setIsTransitioning(true)
    setTimeout(() => { setSlide(idx); setIsTransitioning(false) }, 300)
  }

  const current = slides[slide]

  return (
    <div className="space-y-10 pb-10">

      {/* ══ HERO SECTION ══════════════════════════════════════════════════════ */}
      <section className="relative overflow-hidden rounded-3xl" style={{
        background: 'linear-gradient(135deg, #f0fdf4 0%, #dcfce7 30%, #f0fdf8 55%, #fef9ee 80%, #f0fdf4 100%)',
        border: '1px solid rgba(134, 239, 172, 0.5)',
        boxShadow: '0 8px 40px -8px rgba(21, 128, 61, 0.12), 0 2px 8px rgba(21,128,61,0.06)',
        minHeight: '340px',
      }}>
        {/* Decorative blobs */}
        <div className="blob" style={{ width: 300, height: 300, top: -80, right: -80, background: 'rgba(134,239,172,0.4)' }} />
        <div className="blob" style={{ width: 200, height: 200, bottom: -60, left: '30%', background: 'rgba(253,211,77,0.25)', animationDelay: '3s', animationDuration: '14s' }} />
        <div className="blob" style={{ width: 150, height: 150, top: '20%', left: -50, background: 'rgba(45,212,191,0.2)', animationDelay: '6s' }} />

        <div className="relative z-10 p-8 lg:p-12">
          {/* Status row */}
          <div className="flex flex-wrap items-center justify-between gap-4 mb-8">
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-bold"
              style={{ background: 'linear-gradient(135deg, #15803d, #0d9488)', color: '#fff', boxShadow: '0 2px 12px rgba(21,128,61,0.35)' }}>
              <Sparkles className="w-3 h-3 animate-pulse" />
              <span>TetraTHON 2026 — Indo-French AI Innovation</span>
            </div>
            <div className="flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-semibold"
              style={{ background: 'rgba(255,255,255,0.85)', backdropFilter: 'blur(12px)', border: '1px solid rgba(134,239,172,0.6)', color: '#374151' }}>
              <span className={`status-dot ${apiStatus === 'online' ? 'online' : 'warning'}`} style={{ width: 7, height: 7 }} />
              <span>{apiStatus === 'online' ? `API v${apiVersion} · Live` : 'Demo Engine Active'}</span>
              {language && (
                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold"
                  style={{ background: 'rgba(220,252,231,0.9)', color: '#15803d', border: '1px solid rgba(134,239,172,0.5)' }}>
                  {language}
                </span>
              )}
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
            {/* Left: Text */}
            <div className="lg:col-span-7 space-y-5">
              <div>
                <p className="text-xs font-bold uppercase tracking-[0.14em] mb-2" style={{ color: '#15803d' }}>
                  AI-Powered Precision Agriculture
                </p>
                <h1 className="text-4xl lg:text-5xl xl:text-6xl font-black leading-[1.1] tracking-tight" style={{ color: '#1a2e22' }}>
                  The Future of<br />
                  <span className="text-gradient-green">Indian Farming</span>
                  <span className="text-4xl lg:text-5xl"> 🌾</span>
                </h1>
              </div>
              <p className="text-base lg:text-lg leading-relaxed max-w-xl" style={{ color: '#4b7c5a' }}>
                Empowering <strong>millions of farmers</strong> with real-time IoT sensor data, satellite NDVI analytics, AI disease diagnostics, and multilingual SMS alerts — all integrated in one platform.
              </p>

              {/* Tech pills */}
              <div className="flex flex-wrap gap-2">
                {pillars.map(({ icon: Icon, label, color }) => (
                  <div key={label} className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold"
                    style={{ background: 'rgba(255,255,255,0.75)', backdropFilter: 'blur(8px)', border: `1px solid ${color}30`, color, boxShadow: '0 1px 4px rgba(0,0,0,0.04)' }}>
                    <Icon className="w-3 h-3" />
                    {label}
                  </div>
                ))}
              </div>

              {/* CTA buttons */}
              <div className="flex flex-wrap items-center gap-3 pt-1">
                <button onClick={() => navigate('/advisory')} className="btn-primary text-sm px-6 py-3">
                  <Leaf className="w-4 h-4" />
                  Explore Advisory
                  <ArrowRight className="w-4 h-4" />
                </button>
                <button onClick={() => navigate('/market')} className="btn-secondary text-sm px-6 py-3">
                  <BarChart3 className="w-4 h-4 text-amber-600" />
                  Mandi Prices
                </button>
              </div>
            </div>

            {/* Right: Live Sensor Widget */}
            <div className="lg:col-span-5">
              <ThingspeakWidget compact />
            </div>

          </div>
        </div>
      </section>

      {/* ══ IMMERSIVE AUTO-SWIPE CAROUSEL ════════════════════════════════════ */}
      <section className="space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-[10px] font-bold uppercase tracking-[0.14em] mb-0.5" style={{ color: '#15803d' }}>Innovation Showcase</p>
            <h2 className="text-2xl font-black" style={{ color: '#1a2e22' }}>Precision Hardware & AI Ecosystem</h2>
          </div>
          {/* Active slide pill indicators */}
          <div className="flex items-center gap-1.5 bg-white/80 backdrop-blur-md px-3 py-1.5 rounded-full border border-emerald-200/80 shadow-xs">
            {slides.map((s, idx) => (
              <button
                key={idx}
                onClick={() => setSlide(idx)}
                className="h-2 rounded-full transition-all duration-500 cursor-pointer"
                style={{
                  width: idx === slide ? 24 : 8,
                  background: idx === slide
                    ? `linear-gradient(90deg, ${s.accentFrom}, ${s.accentTo})`
                    : '#cbd5e1',
                }}
              />
            ))}
            <span className="text-[10px] font-bold text-slate-500 ml-1">{slide + 1}/{slides.length}</span>
          </div>
        </div>

        {/* ── Carousel Card ── */}
        <div
          className="relative overflow-hidden rounded-3xl border border-emerald-200/70 shadow-md transition-all duration-500"
          style={{
            background: 'linear-gradient(135deg, #f0fdf4 0%, #ffffff 50%, #f0fdfa 100%)',
            minHeight: 380,
          }}
        >
          {/* Top colored accent line */}
          <div
            className="absolute top-0 left-0 right-0 h-1.5 z-20 transition-all duration-700"
            style={{ background: `linear-gradient(90deg, ${current.accentFrom}, ${current.accentTo})` }}
          />

          <div className="grid grid-cols-1 lg:grid-cols-12 items-stretch h-full min-h-[380px]">
            {/* Image Container (Left 7 Cols) */}
            <div className="lg:col-span-7 relative min-h-[280px] lg:min-h-[380px] overflow-hidden bg-slate-900">
              <img
                key={current.id}
                src={current.img}
                alt={current.title}
                className={`w-full h-full object-cover transition-all duration-700 ${
                  isTransitioning ? 'opacity-40 scale-105' : 'opacity-100 scale-100'
                }`}
              />
              {/* Dark subtle gradient overlay on image */}
              <div className="absolute inset-0 bg-gradient-to-t from-slate-950/60 via-transparent to-black/20" />
              
              {/* Category Tag */}
              <div className="absolute top-4 left-4 z-10">
                <span
                  className="px-3.5 py-1.5 rounded-full text-xs font-bold shadow-md backdrop-blur-md"
                  style={{
                    background: current.tagBg,
                    color: current.tagColor,
                    border: `1px solid ${current.accentFrom}40`,
                  }}
                >
                  {current.tag}
                </span>
              </div>

              {/* Bottom image overlay text */}
              <div className="absolute bottom-4 left-4 right-4 z-10 flex items-center justify-between text-white/90 text-xs font-semibold backdrop-blur-md bg-black/40 px-4 py-2 rounded-xl border border-white/10">
                <span>{current.eyebrow}</span>
                <span className="text-emerald-400 font-bold">Auto-Syncing</span>
              </div>
            </div>

            {/* Content Container (Right 5 Cols) */}
            <div
              className={`lg:col-span-5 flex flex-col justify-between p-6 lg:p-8 space-y-6 transition-all duration-500 ${
                isTransitioning ? 'opacity-0 translate-x-4' : 'opacity-100 translate-x-0'
              }`}
              style={{
                background: 'linear-gradient(180deg, rgba(240,253,244,0.7) 0%, rgba(255,255,255,0.95) 100%)',
              }}
            >
              <div className="space-y-3">
                <div className="inline-block">
                  <span
                    className="text-[10px] font-extrabold uppercase tracking-widest px-2.5 py-1 rounded-md"
                    style={{
                      background: current.accentLight,
                      color: current.accentFrom,
                      border: `1px solid ${current.accentFrom}30`,
                    }}
                  >
                    {current.eyebrow}
                  </span>
                </div>
                
                <h3 className="text-2xl lg:text-3xl font-black text-slate-900 leading-tight">
                  {current.title}
                </h3>
                
                <p className="text-xs lg:text-sm text-slate-600 leading-relaxed font-medium">
                  {current.subtitle}
                </p>
              </div>

              {/* Key Metrics Chips */}
              <div className="grid grid-cols-3 gap-2.5">
                {current.metrics.map(({ label, val, icon: Icon }) => (
                  <div
                    key={label}
                    className="p-2.5 rounded-xl bg-white border border-emerald-100 shadow-xs text-center hover:border-emerald-300 transition-colors"
                  >
                    <Icon className="w-4 h-4 mx-auto mb-1 text-emerald-600" />
                    <p className="text-sm font-black text-slate-900">{val}</p>
                    <p className="text-[10px] font-semibold text-slate-500 mt-0.5">{label}</p>
                  </div>
                ))}
              </div>

              {/* CTA & Auto-Progress Bar */}
              <div className="space-y-3 pt-2">
                <button
                  onClick={() => navigate('/advisory')}
                  className="w-full py-3 px-4 rounded-xl font-bold text-xs text-white shadow-md transition-all flex items-center justify-center gap-2 group cursor-pointer"
                  style={{
                    background: `linear-gradient(135deg, ${current.accentFrom}, ${current.accentTo})`,
                  }}
                >
                  <span>Explore Technology</span>
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </button>

                {/* Progress bar line */}
                <div className="w-full bg-slate-200/80 h-1.5 rounded-full overflow-hidden">
                  <div
                    key={slide}
                    className="h-full bg-emerald-500 rounded-full animate-progress"
                    style={{
                      animation: 'progress-bar 6s linear infinite',
                    }}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ══ THINGSPEAK IOT TELEMETRY WIDGET ══════════════════════════════════ */}
      <section>
        <ThingspeakWidget />
      </section>

      {/* ══ FEATURE MODULE CARDS ═════════════════════════════════════════════ */}
      <section className="space-y-5">

        <div className="flex items-center justify-between">
          <div>
            <p className="text-[10px] font-bold uppercase tracking-[0.14em] mb-1" style={{ color: '#15803d' }}>Platform Modules</p>
            <h2 className="text-2xl font-black" style={{ color: '#1a2e22' }}>Everything a Farmer Needs</h2>
          </div>
          <span className="badge-green badge">6 AI Modules</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {modules.map(({ icon: Icon, label, desc, to, gradient, border, iconBg, textColor, stat }, i) => (
            <div
              key={i}
              onClick={() => navigate(to)}
              className="group cursor-pointer rounded-2xl p-5 flex flex-col gap-4 card-hover"
              style={{
                background: gradient,
                border: `1px solid ${border}`,
                boxShadow: '0 2px 12px rgba(0,0,0,0.04), 0 1px 0 rgba(255,255,255,0.8) inset',
                animationDelay: `${i * 80}ms`,
              }}
            >
              <div className="flex items-start justify-between">
                <div className="w-11 h-11 rounded-xl flex items-center justify-center flex-shrink-0 shadow-lg"
                  style={{ background: iconBg }}>
                  <Icon className="w-5 h-5 text-white" />
                </div>
                <span className="text-[10px] font-bold px-2.5 py-1 rounded-full"
                  style={{ background: 'rgba(255,255,255,0.7)', color: textColor, border: `1px solid ${border}` }}>
                  {stat}
                </span>
              </div>

              <div>
                <h3 className="font-bold text-base mb-1.5 group-hover:opacity-80 transition-opacity" style={{ color: '#1a2e22' }}>
                  {label}
                </h3>
                <p className="text-sm leading-relaxed" style={{ color: '#4b5563' }}>{desc}</p>
              </div>

              <div className="flex items-center gap-1.5 text-xs font-bold mt-auto pt-3 border-t"
                style={{ borderColor: border, color: textColor }}>
                <span>Open Module</span>
                <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ══ IMPACT STATS ═════════════════════════════════════════════════════ */}
      <section className="space-y-5" ref={statsRef}>
        <div>
          <p className="text-[10px] font-bold uppercase tracking-[0.14em] mb-1" style={{ color: '#15803d' }}>Measurable Impact</p>
          <h2 className="text-2xl font-black" style={{ color: '#1a2e22' }}>Real Numbers. Real Farmers.</h2>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
          {stats.map(({ val, label, sub, color, bg }, i) => (
            <div
              key={i}
              className="rounded-2xl p-4 text-center"
              style={{
                background: bg,
                border: `1px solid ${color}25`,
                boxShadow: '0 2px 8px rgba(0,0,0,0.04), 0 1px 0 rgba(255,255,255,0.7) inset',
                animationDelay: `${i * 100}ms`,
              }}
            >
              <p className="text-3xl font-black" style={{ color, animation: statsVisible ? `count-up 0.6s ${i * 120}ms ease-out both` : 'none' }}>
                {val}
              </p>
              <p className="text-[11px] font-bold mt-1" style={{ color: '#1a2e22' }}>{label}</p>
              <p className="text-[9px] font-medium mt-0.5" style={{ color: '#6b7280' }}>{sub}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ══ SUSTAINABILITY BANNER ════════════════════════════════════════════ */}
      <section className="rounded-3xl overflow-hidden"
        style={{
          background: 'linear-gradient(135deg, #f0fdf4 0%, #dcfce7 40%, #f0fdf8 60%, #fef9ee 100%)',
          border: '1px solid rgba(134,239,172,0.5)',
          boxShadow: '0 8px 32px -6px rgba(21,128,61,0.1)',
        }}>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-0">
          {/* Left */}
          <div className="p-8 lg:p-10 space-y-5">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-bold"
              style={{ background: 'rgba(220,252,231,0.9)', color: '#15803d', border: '1px solid rgba(134,239,172,0.6)' }}>
              <Sun className="w-3.5 h-3.5" />
              Sustainable Agriculture
            </div>
            <h2 className="text-2xl lg:text-3xl font-black leading-snug" style={{ color: '#1a2e22' }}>
              Intelligence Meets<br />
              <span className="text-gradient-green">Environmental Stewardship</span>
            </h2>
            <p className="text-sm leading-relaxed" style={{ color: '#4b7c5a' }}>
              AgriNova bridges traditional agronomy with high-frequency telemetry data, delivering actionable AI recommendations via Web & SMS — bridging the digital divide for rural India.
            </p>
            <div className="space-y-2.5">
              {[
                { icon: Droplets, color: '#0d9488', title: '35% Water Reduction', desc: 'Variable-rate irrigation matches root-zone moisture without depletion' },
                { icon: Wind,     color: '#15803d', title: 'Chemical Optimization', desc: 'Targeted NPK cuts fertilizer runoff by up to 40%, protecting soil health' },
                { icon: Award,    color: '#d97706', title: 'Yield Enhancement',     desc: 'AI crop calendar maximizes harvest windows, reducing crop failure risk' },
              ].map(({ icon: Icon, color, title, desc }) => (
                <div key={title} className="flex items-start gap-3 p-3 rounded-xl"
                  style={{ background: 'rgba(255,255,255,0.6)', border: `1px solid ${color}20` }}>
                  <div className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5"
                    style={{ background: `${color}15` }}>
                    <Icon className="w-4 h-4" style={{ color }} />
                  </div>
                  <div>
                    <p className="text-sm font-bold" style={{ color: '#1a2e22' }}>{title}</p>
                    <p className="text-xs" style={{ color: '#6b7280' }}>{desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Right: Large visual stats */}
          <div className="p-8 lg:p-10 flex flex-col justify-center space-y-4"
            style={{ background: 'linear-gradient(180deg, rgba(220,252,231,0.4) 0%, rgba(204,251,241,0.3) 100%)', borderLeft: '1px solid rgba(134,239,172,0.3)' }}>
            <div className="grid grid-cols-2 gap-4">
              {[
                { val: '18', label: 'Crop Varieties',    sub: 'Supported',       icon: Leaf,        color: '#15803d', bg: 'rgba(220,252,231,0.8)' },
                { val: '37',  label: 'API Endpoints',    sub: 'Production-ready', icon: Zap,         color: '#0d9488', bg: 'rgba(204,251,241,0.8)' },
                { val: '94%', label: 'ML Model R²',      sub: 'Yield accuracy',  icon: TrendingUp,  color: '#7c3aed', bg: 'rgba(237,233,254,0.8)' },
                { val: '14',  label: 'Indian Languages', sub: 'Including SMS',   icon: Globe,        color: '#d97706', bg: 'rgba(253,230,138,0.7)' },
              ].map(({ val, label, sub, icon: Icon, color, bg }) => (
                <div key={label} className="p-5 rounded-2xl text-center"
                  style={{ background: bg, border: `1px solid ${color}25`, boxShadow: '0 2px 8px rgba(0,0,0,0.04)' }}>
                  <Icon className="w-6 h-6 mx-auto mb-2" style={{ color }} />
                  <p className="text-3xl font-black" style={{ color }}>{val}</p>
                  <p className="text-xs font-bold mt-1" style={{ color: '#1a2e22' }}>{label}</p>
                  <p className="text-[10px]" style={{ color: '#6b7280' }}>{sub}</p>
                </div>
              ))}
            </div>
            <button onClick={() => navigate('/advisory')} className="btn-primary w-full justify-center py-3.5">
              <Sparkles className="w-4 h-4" />
              Start AI Advisory Session
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </section>

      {/* ══ PHONE SETUP CALLOUT ══════════════════════════════════════════════ */}
      {!phone && (
        <div className="rounded-2xl p-5 flex flex-col sm:flex-row items-center justify-between gap-4"
          style={{
            background: 'linear-gradient(135deg, rgba(255,251,235,0.95) 0%, rgba(253,230,138,0.5) 100%)',
            border: '1px solid rgba(253,211,77,0.5)',
            boxShadow: '0 4px 20px rgba(180, 83, 9, 0.08)',
          }}>
          <div className="flex items-center gap-3">
            <div className="w-11 h-11 rounded-xl flex items-center justify-center flex-shrink-0"
              style={{ background: 'linear-gradient(135deg, #d97706, #b45309)', boxShadow: '0 4px 12px rgba(180,83,9,0.3)' }}>
              <Smartphone className="w-5 h-5 text-white" />
            </div>
            <div>
              <p className="font-bold text-sm" style={{ color: '#1a2e22' }}>Personalize Your AI Advisory</p>
              <p className="text-xs" style={{ color: '#6b7280' }}>Connect your mobile number to receive customized SMS alerts in your language</p>
            </div>
          </div>
          <button className="btn-secondary whitespace-nowrap text-xs px-5 py-2.5" onClick={() => navigate('/settings')}>
            Setup Profile →
          </button>
        </div>
      )}
    </div>
  )
}
