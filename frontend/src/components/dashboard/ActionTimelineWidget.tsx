import { memo } from 'react'
import { Calendar, Droplets, Sprout, Bug, Wheat, CheckCircle2, Clock } from 'lucide-react'
import type { DetailedActionItem } from '../../types/dashboard'

const DEFAULT_TIMELINE: DetailedActionItem[] = [
  { id: '1', timeframe: 'Morning', title: 'Irrigate Field #882', description: 'Apply 22 mm root-zone drip irrigation before peak ambient ET0 evapotranspiration loss.', category: 'water', priority: 'High', duration: '45 Mins', status: 'In Progress' },
  { id: '2', timeframe: 'Afternoon', title: 'Top-Dress Nitrogen Fertilizer', description: 'Apply 40 kg/ha Urea prior to expected evening rainfall window.', category: 'fertilizer', priority: 'High', duration: '30 Mins', status: 'Pending' },
  { id: '3', timeframe: 'Evening', title: 'Pest Monitoring & Neem Spray Inspection', description: 'Inspect leaf undersides for Whitefly nymph threshold (>5/leaf). Delay chemical spray if rain occurs.', category: 'pest', priority: 'Medium', duration: '20 Mins', status: 'Pending' },
  { id: '4', timeframe: 'Tomorrow', title: 'Harvest Maturity Assessment', description: 'Check boll maturity and schedule dry harvest labor teams.', category: 'harvest', priority: 'Low', duration: '60 Mins', status: 'Pending' },
]

export const ActionTimelineWidget = memo(function ActionTimelineWidget() {
  return (
    <div className="glass-card p-6 space-y-5 animate-fade-in border-l-4 border-l-purple-600">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl bg-purple-600 text-white flex items-center justify-center shadow-md">
            <Calendar className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-extrabold text-slate-900">💧 Today's AI Action Schedule</h3>
            <p className="text-xs text-slate-500 font-medium">Precision Farming Tasks by Window</p>
          </div>
        </div>
        <span className="px-3 py-1 rounded-full text-xs font-bold bg-purple-100 text-purple-800 border border-purple-200">
          4 Scheduled Tasks
        </span>
      </div>

      {/* Vertical Task Timeline */}
      <div className="relative pl-6 space-y-5 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200">
        {DEFAULT_TIMELINE.map((item) => (
          <div key={item.id} className="relative group">
            {/* Timeline Icon Node */}
            <div className="absolute -left-6 top-0.5 w-5 h-5 rounded-full bg-white border-2 border-purple-600 flex items-center justify-center text-purple-600 shadow-sm group-hover:scale-125 transition-transform">
              <CheckCircle2 className="w-3.5 h-3.5" />
            </div>

            <div className="p-4 rounded-2xl bg-slate-50/90 border border-slate-200/80 hover:border-purple-300 transition-all space-y-1.5">
              <div className="flex items-center justify-between">
                <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider bg-purple-100 text-purple-800">
                  {item.timeframe}
                </span>
                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-bold text-slate-500 flex items-center gap-1">
                    <Clock className="w-3 h-3 text-slate-400" /> {item.duration}
                  </span>
                  {item.category === 'water' && <Droplets className="w-4 h-4 text-sky-600" />}
                  {item.category === 'fertilizer' && <Sprout className="w-4 h-4 text-emerald-600" />}
                  {item.category === 'pest' && <Bug className="w-4 h-4 text-rose-600" />}
                  {item.category === 'harvest' && <Wheat className="w-4 h-4 text-amber-600" />}
                </div>
              </div>
              <h4 className="text-xs font-black text-slate-900">{item.title}</h4>
              <p className="text-xs text-slate-600 font-medium leading-relaxed">{item.description}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
})
