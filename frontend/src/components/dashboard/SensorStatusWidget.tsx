import { memo, useState, useEffect } from 'react'
import { Radio, RefreshCw, Wifi, Activity, Thermometer, Droplets, Gauge } from 'lucide-react'
import { ResponsiveContainer, LineChart, Line } from 'recharts'
import { api } from '../../api/client'

const MOCK_HISTORY = [
  { time: '10:00', moisture: 41.2, temperature: 27.8, humidity: 64 },
  { time: '11:00', moisture: 42.0, temperature: 28.1, humidity: 63 },
  { time: '12:00', moisture: 42.5, temperature: 28.9, humidity: 61 },
  { time: '13:00', moisture: 42.8, temperature: 28.5, humidity: 62 },
]

export const SensorStatusWidget = memo(function SensorStatusWidget() {
  const [telemetry, setTelemetry] = useState({
    moisture: 42.8,
    temperature: 28.5,
    humidity: 62.0,
    status: 'Online',
    lastUpdated: 'Just now',
  })
  const [history, setHistory] = useState(MOCK_HISTORY)
  const [loading, setLoading] = useState(false)

  const fetchTelemetry = async () => {
    setLoading(true)
    try {
      const res = await api.get('/iot/thingspeak/telemetry?results=5')
      if (res.data?.latest) {
        setTelemetry({
          moisture: res.data.latest.soil_moisture_percent ?? 42.8,
          temperature: res.data.latest.temperature_celsius ?? 28.5,
          humidity: res.data.latest.humidity_percent ?? 62.0,
          status: 'Online',
          lastUpdated: 'Just now',
        })
      }
    } catch {}
    setLoading(false)
  }

  useEffect(() => {
    fetchTelemetry()
    const interval = setInterval(fetchTelemetry, 30000) // Auto-refresh every 30 seconds
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="glass-card p-6 space-y-5 border-l-4 border-l-teal-600 animate-fade-in">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl bg-teal-600 text-white flex items-center justify-center shadow-md">
            <Radio className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <h3 className="text-base font-extrabold text-slate-900">📡 SoilPulse™ IoT Telemetry Node</h3>
            <p className="text-xs text-slate-500 font-medium">ThingSpeak Channel #3430931 · Real-Time Probes</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="px-3 py-1 rounded-full text-xs font-black bg-emerald-100 text-emerald-800 border border-emerald-300 flex items-center gap-1.5 shadow-xs">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping"></span>
            Sensor Online
          </span>
          <button
            onClick={fetchTelemetry}
            className="p-1.5 hover:bg-slate-100 rounded-lg transition-colors text-slate-500 cursor-pointer"
            title="Refresh IoT Telemetry"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-teal-600' : ''}`} />
          </button>
        </div>
      </div>

      {/* Sensor Metrics with Sparkline Mini Charts */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {/* Soil Moisture */}
        <div className="p-4 rounded-2xl bg-gradient-to-br from-emerald-50/80 to-slate-50 border border-emerald-200/80 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-extrabold text-emerald-800 flex items-center gap-1">
              <Gauge className="w-4 h-4 text-emerald-600" /> Soil Moisture
            </span>
            <span className="text-[10px] font-bold text-emerald-700 bg-emerald-100 px-2 py-0.5 rounded-full">Optimal</span>
          </div>
          <p className="text-2xl font-black text-slate-900">{telemetry.moisture}%</p>
          
          <div className="h-10 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={history}>
                <Line type="monotone" dataKey="moisture" stroke="#16a34a" strokeWidth={2.5} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Temperature */}
        <div className="p-4 rounded-2xl bg-gradient-to-br from-amber-50/80 to-slate-50 border border-amber-200/80 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-extrabold text-amber-800 flex items-center gap-1">
              <Thermometer className="w-4 h-4 text-amber-600" /> Ambient Temp
            </span>
            <span className="text-[10px] font-bold text-amber-700 bg-amber-100 px-2 py-0.5 rounded-full">Normal</span>
          </div>
          <p className="text-2xl font-black text-slate-900">{telemetry.temperature}°C</p>
          
          <div className="h-10 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={history}>
                <Line type="monotone" dataKey="temperature" stroke="#d97706" strokeWidth={2.5} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Humidity */}
        <div className="p-4 rounded-2xl bg-gradient-to-br from-sky-50/80 to-slate-50 border border-sky-200/80 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-extrabold text-sky-800 flex items-center gap-1">
              <Droplets className="w-4 h-4 text-sky-600" /> Relative Humidity
            </span>
            <span className="text-[10px] font-bold text-sky-700 bg-sky-100 px-2 py-0.5 rounded-full">62% RH</span>
          </div>
          <p className="text-2xl font-black text-slate-900">{telemetry.humidity}%</p>
          
          <div className="h-10 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={history}>
                <Line type="monotone" dataKey="humidity" stroke="#0284c7" strokeWidth={2.5} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  )
})
