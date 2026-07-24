import { memo, useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowRight, Satellite, Activity, Radio, Sparkles } from 'lucide-react'

const slides = [
  {
    id: 1,
    title: 'SoilPulse™ Gen 4 IoT Sensor Mesh',
    subtitle: 'Zero-latency ThingSpeak telemetry probes covering 5 acres per node',
    tag: 'IoT Hardware',
    icon: Activity,
    img: '/carousel_iot_field.png',
  },
  {
    id: 2,
    title: 'Orbital AI & NDVI Telemetry',
    subtitle: 'Sentinel-2 10m multi-spectral canopy health & moisture mapping',
    tag: 'Orbital AI',
    icon: Satellite,
    img: '/carousel_satellite.png',
  },
  {
    id: 3,
    title: 'AI Micro-Irrigation Probe Network',
    subtitle: 'ET-based automated root-zone drip dispatch saving 35% water',
    tag: 'Smart Water',
    icon: Radio,
    img: '/carousel_irrigation.png',
  },
]

export const MiniEcosystemCarousel = memo(function MiniEcosystemCarousel() {
  const navigate = useNavigate()
  const [slide, setSlide] = useState(0)

  const nextSlide = useCallback(() => {
    setSlide((s) => (s + 1) % slides.length)
  }, [])

  useEffect(() => {
    const t = setInterval(nextSlide, 5000)
    return () => clearInterval(t)
  }, [nextSlide])

  const current = slides[slide]
  const Icon = current.icon

  return (
    <div
      onClick={() => navigate('/advisory')}
      className="group cursor-pointer relative overflow-hidden rounded-2xl flex-1 min-h-[230px] h-full border border-emerald-300/80 shadow-md transition-all hover:shadow-xl hover:border-emerald-500 flex flex-col justify-between p-5 bg-slate-900"
    >
      {/* Background Slide Image with Dark Gradient Overlay */}
      <img
        key={current.id}
        src={current.img}
        alt={current.title}
        className="absolute inset-0 w-full h-full object-cover transition-opacity duration-700 opacity-60 group-hover:scale-105 transition-transform duration-700"
        onError={(e) => {
          // If image fails, keep dark gradient
          ;(e.target as HTMLElement).style.display = 'none'
        }}
      />
      <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-900/60 to-black/30 pointer-events-none" />

      {/* Top Tag & Indicator Dots */}
      <div className="relative z-10 flex items-center justify-between">
        <span className="px-2.5 py-0.5 rounded-full text-[9px] font-black uppercase tracking-wider bg-emerald-600/90 text-white border border-emerald-400/60 shadow-sm flex items-center gap-1">
          <Icon className="w-3 h-3" />
          {current.tag}
        </span>

        {/* Slide Indicator Dots */}
        <div className="flex items-center gap-1.5 bg-black/40 backdrop-blur-md px-2 py-1 rounded-full border border-white/20">
          {slides.map((_, idx) => (
            <button
              key={idx}
              onClick={(e) => {
                e.stopPropagation()
                setSlide(idx)
              }}
              className={`h-1.5 rounded-full transition-all cursor-pointer ${
                slide === idx ? 'w-4 bg-emerald-400' : 'w-1.5 bg-white/50 hover:bg-white'
              }`}
            />
          ))}
        </div>
      </div>

      {/* Bottom Title, Description & CTA Button */}
      <div className="relative z-10 flex items-end justify-between gap-3">
        <div className="space-y-0.5 max-w-[78%]">
          <h4 className="text-xs font-black text-white group-hover:text-emerald-300 transition-colors drop-shadow-sm">
            {current.title}
          </h4>
          <p className="text-[10px] text-slate-200 font-medium leading-tight drop-shadow-xs line-clamp-2">
            {current.subtitle}
          </p>
        </div>

        <button className="p-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs transition-colors flex items-center gap-1 cursor-pointer flex-shrink-0 shadow-md">
          <Sparkles className="w-3.5 h-3.5" />
          <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
        </button>
      </div>
    </div>
  )
})
