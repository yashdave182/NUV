import { memo } from 'react'
import { Thermometer, Droplets, Wind, Wheat, TrendingUp, TrendingDown } from 'lucide-react'
import { ResponsiveContainer, LineChart, Line } from 'recharts'
import type { KPIMetric } from '../../types/dashboard'

const KPI_DATA: KPIMetric[] = [
  {
    id: 'temp',
    label: 'Ambient Temp',
    value: '34.2',
    unit: '°C',
    change: '+1.2° vs yesterday',
    isPositive: true,
    icon: 'temp',
    color: '#d97706',
    trendData: [
      { time: '08:00', val: 28 }, { time: '10:00', val: 31 }, { time: '12:00', val: 34.2 }, { time: '14:00', val: 33 }
    ]
  },
  {
    id: 'moisture',
    label: 'Soil Moisture',
    value: '42.8',
    unit: '%',
    change: 'Optimal root zone',
    isPositive: true,
    icon: 'droplet',
    color: '#16a34a',
    trendData: [
      { time: '08:00', val: 40 }, { time: '10:00', val: 41.5 }, { time: '12:00', val: 42.8 }, { time: '14:00', val: 42.2 }
    ]
  },
  {
    id: 'humidity',
    label: 'Air Humidity',
    value: '62.0',
    unit: '% RH',
    change: '62% Vapor deficit',
    isPositive: true,
    icon: 'wind',
    color: '#0284c7',
    trendData: [
      { time: '08:00', val: 68 }, { time: '10:00', val: 65 }, { time: '12:00', val: 62 }, { time: '14:00', val: 63 }
    ]
  },
  {
    id: 'yield',
    label: 'Predicted Yield',
    value: '2.8',
    unit: 'T / Ha',
    change: '+12% vs state avg',
    isPositive: true,
    icon: 'wheat',
    color: '#7c3aed',
    trendData: [
      { time: '08:00', val: 2.4 }, { time: '10:00', val: 2.6 }, { time: '12:00', val: 2.8 }, { time: '14:00', val: 2.8 }
    ]
  },
]

export const KPICards = memo(function KPICards() {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 animate-fade-in">
      {KPI_DATA.map((kpi) => (
        <div
          key={kpi.id}
          className="p-5 rounded-2xl bg-white border border-slate-200/80 shadow-xs hover:shadow-md hover:-translate-y-1 transition-all space-y-3"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-xl" style={{ backgroundColor: `${kpi.color}15`, color: kpi.color }}>
                {kpi.icon === 'temp' && <Thermometer className="w-5 h-5" />}
                {kpi.icon === 'droplet' && <Droplets className="w-5 h-5" />}
                {kpi.icon === 'wind' && <Wind className="w-5 h-5" />}
                {kpi.icon === 'wheat' && <Wheat className="w-5 h-5" />}
              </div>
              <span className="text-xs font-bold text-slate-600">{kpi.label}</span>
            </div>
            <span className="text-[10px] font-extrabold px-2 py-0.5 rounded-full flex items-center gap-0.5" style={{ backgroundColor: `${kpi.color}15`, color: kpi.color }}>
              {kpi.isPositive ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
              {kpi.change}
            </span>
          </div>

          <div className="flex items-baseline justify-between">
            <div>
              <span className="text-3xl font-black text-slate-900 tracking-tight">{kpi.value}</span>
              <span className="text-sm font-bold text-slate-500 ml-1">{kpi.unit}</span>
            </div>
          </div>

          {/* Sparkline Mini Chart */}
          <div className="h-10 w-full pt-1">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={kpi.trendData}>
                <Line type="monotone" dataKey="val" stroke={kpi.color} strokeWidth={2.5} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      ))}
    </div>
  )
})
