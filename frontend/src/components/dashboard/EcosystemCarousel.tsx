import { memo, useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowRight, Satellite, Activity, Radio, Leaf, Zap, Globe, TrendingUp, Shield } from 'lucide-react'

const slides = [
  {
    id: 1,
    eyebrow: 'IoT Hardware Ecosystem',
    title: 'SoilPulse™ Gen 4 IoT Sensor Mesh',
    subtitle: 'Enterprise-grade soil moisture, NPK & pH sensors with zero-latency ThingSpeak telemetry. Covers up to 5 acres per node with sub-second readings.',
    metrics: [
      { label: 'Battery Life', val: '3 Years', icon: Zap },
      { label: 'Data Latency', val: '<1 Sec', icon: Activity },
      { label: 'Accuracy', val: '99.2%', icon: Shield },
    ],
    img: '/carousel_iot_field.png',
    tag: 'IoT Hardware',
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
  },
  {
    id: 3,
    eyebrow: 'Smart Water Management',
    title: 'AI Drip Irrigation & Probe Network',
    subtitle: 'High-frequency root-zone monitoring with ET-based automated micro-irrigation dispatch, reducing water usage by 35% while maximising yield.',
    metrics: [
      { label: 'Water Saved', val: '35%', icon: Zap },
      { label: 'Response', val: '<1s', icon: Radio },
      { label: 'Crops', val: '18 Types', icon: Leaf },
    ],
    img: '/carousel_irrigation.png',
    tag: 'Smart Water',
  },
]

export const EcosystemCarousel = memo(function EcosystemCarousel() {
  const navigate = useNavigate()
  const [slide, setSlide] = useState(0)
  const [isTransitioning, setIsTransitioning] = useState(false)

  const changeSlide = useCallback((idx: number) => {
    if (isTransitioning) return
    setIsTransitioning(true)
    setTimeout(() => { setSlide(idx); setIsTransitioning(false) }, 300)
  }, [isTransitioning])

  useEffect(() => {
    const t = setInterval(() => changeSlide((slide + 1) % slides.length), 6000)
    return () => clearInterval(t)
  }, [slide, changeSlide])

  const current = slides[slide]

  return (
    <section className="space-y-3 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-emerald-800 mb-0.5">AgriNova Ecosystem</p>
          <h2 className="text-xl font-black text-slate-900">Hardware & Orbital Intelligence</h2>
        </div>
        <div className="flex items-center gap-1.5">
          {slides.map((_, i) => (
            <button
              key={i}
              onClick={() => changeSlide(i)}
              className={`h-2 rounded-full transition-all cursor-pointer ${
                slide === i ? 'w-6 bg-emerald-600' : 'w-2 bg-slate-300 hover:bg-slate-400'
              }`}
            />
          ))}
        </div>
      </div>

      <div className="relative overflow-hidden rounded-3xl border border-emerald-200/90 shadow-lg bg-white">
        <div className="grid grid-cols-1 lg:grid-cols-12 items-stretch min-h-[320px]">
          <div className="lg:col-span-7 relative min-h-[240px] lg:min-h-[320px] overflow-hidden bg-slate-900">
            <img
              key={current.id}
              src={current.img}
              alt={current.title}
              className={`w-full h-full object-cover transition-all duration-700 ${
                isTransitioning ? 'opacity-40 scale-105' : 'opacity-100 scale-100'
              }`}
              onError={(e) => {
                // Fallback gradient if image asset path is missing
                ;(e.target as HTMLElement).style.display = 'none'
              }}
            />
            <div className="absolute inset-0 bg-gradient-to-t from-slate-950/70 via-slate-900/40 to-black/30 flex items-end p-6">
              <span className="px-3.5 py-1 rounded-full text-xs font-black shadow-md bg-emerald-600 text-white border border-emerald-400">
                {current.tag}
              </span>
            </div>
          </div>

          <div className="lg:col-span-5 flex flex-col justify-between p-6 space-y-4 bg-gradient-to-b from-emerald-50/80 via-white to-teal-50/30">
            <div className="space-y-2">
              <span className="text-[10px] font-black uppercase tracking-widest px-2.5 py-0.5 rounded-md bg-emerald-100 text-emerald-800 border border-emerald-200">
                {current.eyebrow}
              </span>
              <h3 className="text-xl font-black text-slate-900 leading-tight">
                {current.title}
              </h3>
              <p className="text-xs text-slate-600 font-medium leading-relaxed">
                {current.subtitle}
              </p>
            </div>

            <div className="grid grid-cols-3 gap-2">
              {current.metrics.map(({ label, val, icon: Icon }) => (
                <div key={label} className="p-2 rounded-xl bg-white border border-emerald-200/80 text-center shadow-xs">
                  <Icon className="w-4 h-4 mx-auto mb-0.5 text-emerald-600" />
                  <p className="text-xs font-black text-slate-900">{val}</p>
                  <p className="text-[9px] font-semibold text-slate-500">{label}</p>
                </div>
              ))}
            </div>

            <button
              onClick={() => navigate('/advisory')}
              className="w-full py-2.5 px-4 rounded-xl font-extrabold text-xs text-white bg-gradient-to-r from-emerald-600 via-teal-600 to-emerald-700 shadow-md hover:shadow-lg transition-all flex items-center justify-center gap-2 cursor-pointer hover:scale-[1.01]"
            >
              <span>Explore Ecosystem</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </section>
  )
})
