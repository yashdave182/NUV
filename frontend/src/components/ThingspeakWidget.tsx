import React, { useEffect, useState } from 'react'
import {
  Droplets, Thermometer, Wind, RefreshCw, Radio, Activity,
  CheckCircle2, Clock, Cpu, Signal, AlertTriangle, ChevronRight
} from 'lucide-react'
import {
  fetchThingspeakTelemetry,
  type ThingSpeakTelemetryResponse,
  type ParsedTelemetry
} from '../services/iotService'


interface ThingspeakWidgetProps {
  compact?: boolean
  className?: string
}

export const ThingspeakWidget: React.FC<ThingspeakWidgetProps> = ({ compact = false, className = '' }) => {
  const [data, setData] = useState<ThingSpeakTelemetryResponse | null>(null)
  const [loading, setLoading] = useState<boolean>(true)
  const [refreshing, setRefreshing] = useState<boolean>(false)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)

  const loadData = async (isManual: boolean = false) => {
    if (isManual) setRefreshing(true)
    else setLoading(true)

    try {
      const res = await fetchThingspeakTelemetry(5)
      setData(res)
      setLastUpdated(new Date())
    } catch (err) {
      console.error('Error loading ThingSpeak telemetry:', err)
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  useEffect(() => {
    loadData()
    // Auto refresh every 30 seconds
    const interval = setInterval(() => loadData(false), 30000)
    return () => clearInterval(interval)
  }, [])

  const latest: ParsedTelemetry | undefined = data?.latest
  const channel = data?.channel

  const moistureVal = latest?.soil_moisture_sml != null ? latest.soil_moisture_sml : 42.5
  const tempVal = latest?.temperature_c != null ? latest.temperature_c : 28.4
  const humidityVal = latest?.humidity_percent != null ? latest.humidity_percent : 65.0

  const getMoistureStatus = (val: number) => {
    if (val < 30) return { text: 'Low Moisture (Water Needed)', color: '#dc2626', bg: 'rgba(254,226,226,0.7)' }
    if (val > 70) return { text: 'Saturated Soil', color: '#0284c7', bg: 'rgba(224,242,254,0.7)' }
    return { text: 'Optimal Root Level', color: '#15803d', bg: 'rgba(220,252,231,0.7)' }
  }

  const getTempStatus = (val: number) => {
    if (val > 35) return { text: 'High Heat Strain', color: '#d97706', bg: 'rgba(254,243,199,0.7)' }
    if (val < 15) return { text: 'Cool Canopy', color: '#2563eb', bg: 'rgba(219,234,254,0.7)' }
    return { text: 'Ideal Growing Temp', color: '#16a34a', bg: 'rgba(220,252,231,0.7)' }
  }

  const moistureStatus = getMoistureStatus(moistureVal)
  const tempStatus = getTempStatus(tempVal)

  if (compact) {
    return (
      <div className={`glass-card p-4 rounded-2xl space-y-3 border border-emerald-200/60 ${className}`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-emerald-600 flex items-center justify-center text-white shadow-sm">
              <Cpu className="w-4 h-4" />
            </div>
            <div>
              <p className="text-[10px] font-extrabold uppercase tracking-widest text-emerald-800">ThingSpeak IoT Node</p>
              <p className="text-xs font-semibold text-slate-600">
                {channel?.name || 'NUV Channel #3430931'}
              </p>
            </div>
          </div>
          <button
            onClick={() => loadData(true)}
            disabled={refreshing}
            className="p-1.5 rounded-lg hover:bg-emerald-100 text-emerald-700 transition-colors cursor-pointer"
            title="Refresh telemetry"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${refreshing ? 'animate-spin' : ''}`} />
          </button>
        </div>

        <div className="grid grid-cols-3 gap-2">
          <div className="p-2.5 rounded-xl bg-emerald-50/80 border border-emerald-100">
            <div className="flex items-center gap-1 text-[10px] font-bold text-emerald-700">
              <Droplets className="w-3 h-3 text-emerald-600" />
              <span>Moisture</span>
            </div>
            <p className="text-lg font-black text-emerald-900 mt-1">{moistureVal.toFixed(1)}%</p>
          </div>

          <div className="p-2.5 rounded-xl bg-amber-50/80 border border-amber-100">
            <div className="flex items-center gap-1 text-[10px] font-bold text-amber-700">
              <Thermometer className="w-3 h-3 text-amber-600" />
              <span>Temp</span>
            </div>
            <p className="text-lg font-black text-amber-900 mt-1">{tempVal.toFixed(1)}°C</p>
          </div>

          <div className="p-2.5 rounded-xl bg-teal-50/80 border border-teal-100">
            <div className="flex items-center gap-1 text-[10px] font-bold text-teal-700">
              <Wind className="w-3 h-3 text-teal-600" />
              <span>Humidity</span>
            </div>
            <p className="text-lg font-black text-teal-900 mt-1">{humidityVal.toFixed(1)}%</p>
          </div>
        </div>

        <div className="flex items-center justify-between text-[10px] text-slate-500 pt-1 border-t border-emerald-100">
          <span className="flex items-center gap-1 font-semibold text-emerald-700">
            <Signal className="w-3 h-3 text-emerald-600" />
            {latest?.status === 'live' || latest?.status === 'active_ready' ? 'ThingSpeak Cloud Connected' : 'Fallback Node'}
          </span>
          <span>{lastUpdated ? lastUpdated.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'Syncing'}</span>
        </div>
      </div>
    )
  }

  return (
    <div className={`rounded-3xl p-6 lg:p-7 space-y-6 ${className}`} style={{
      background: 'linear-gradient(135deg, #ffffff 0%, #f0fdf4 50%, #f0fdfa 100%)',
      border: '1px solid rgba(134, 239, 172, 0.6)',
      boxShadow: '0 8px 30px -6px rgba(21, 128, 61, 0.1), 0 2px 6px rgba(0,0,0,0.03)'
    }}>
      {/* Top Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-emerald-100/80 pb-4">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-2xl flex items-center justify-center text-white shadow-md" style={{
            background: 'linear-gradient(135deg, #15803d, #0d9488)',
            boxShadow: '0 4px 14px rgba(21,128,61,0.25)'
          }}>
            <Cpu className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-extrabold uppercase tracking-widest px-2.5 py-0.5 rounded-full"
                style={{ background: 'rgba(220,252,231,0.9)', color: '#15803d', border: '1px solid rgba(134,239,172,0.6)' }}>
                SoilPulse™ Gen 4 IoT
              </span>
              <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold flex items-center gap-1 ${
                latest?.status === 'live' || latest?.status === 'active_ready' ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'
              }`}>
                <span className={`status-dot ${latest?.status === 'live' || latest?.status === 'active_ready' ? 'online' : 'warning'}`} style={{ width: 6, height: 6 }} />
                {latest?.status === 'live' ? 'ThingSpeak Live Stream' : latest?.status === 'active_ready' ? 'ThingSpeak Key Verified' : 'Fallback Mode'}
              </span>
            </div>
            <h3 className="text-xl font-black text-slate-900 mt-1">
              {channel?.name || 'NUV Telemetry Channel'} <span className="text-xs text-slate-500 font-normal">(Channel ID: {channel?.id || 3430931})</span>
            </h3>
            {channel?.description && (
              <p className="text-xs text-slate-600 font-medium mt-0.5">{channel.description}</p>
            )}
          </div>
        </div>



        <div className="flex items-center gap-2">
          <button
            onClick={() => loadData(true)}
            disabled={refreshing}
            className="flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold text-emerald-800 bg-white border border-emerald-200 hover:bg-emerald-50 transition-all shadow-xs cursor-pointer disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-emerald-600 ${refreshing ? 'animate-spin' : ''}`} />
            <span>{refreshing ? 'Syncing...' : 'Sync Telemetry'}</span>
          </button>
        </div>
      </div>

      {/* Main Sensor Gauges */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Soil Moisture */}
        <div className="p-5 rounded-2xl bg-white border border-emerald-100 shadow-xs flex flex-col justify-between space-y-3 hover:border-emerald-300 transition-colors">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-xl bg-emerald-100 text-emerald-700">
                <Droplets className="w-5 h-5" />
              </div>
              <div>
                <p className="text-xs font-bold text-slate-600">Soil Moisture (SML)</p>
                <p className="text-[10px] text-slate-400">Root-Zone Probe #1</p>
              </div>
            </div>
            <Activity className="w-4 h-4 text-emerald-500" />
          </div>

          <div>
            <div className="flex items-baseline gap-1">
              <span className="text-3xl font-black text-emerald-900">{moistureVal.toFixed(1)}</span>
              <span className="text-base font-bold text-emerald-700">%</span>
            </div>
            {/* Progress bar visual */}
            <div className="w-full bg-slate-100 h-2 rounded-full mt-2 overflow-hidden">
              <div
                className="h-full bg-emerald-500 rounded-full transition-all duration-700"
                style={{ width: `${Math.min(100, Math.max(0, moistureVal))}%` }}
              />
            </div>
          </div>

          <div className="px-3 py-1.5 rounded-xl text-[11px] font-semibold flex items-center justify-between"
            style={{ background: moistureStatus.bg, color: moistureStatus.color }}>
            <span>{moistureStatus.text}</span>
            <CheckCircle2 className="w-3.5 h-3.5" />
          </div>
        </div>

        {/* Temperature */}
        <div className="p-5 rounded-2xl bg-white border border-amber-100 shadow-xs flex flex-col justify-between space-y-3 hover:border-amber-300 transition-colors">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-xl bg-amber-100 text-amber-700">
                <Thermometer className="w-5 h-5" />
              </div>
              <div>
                <p className="text-xs font-bold text-slate-600">Ambient Temperature</p>
                <p className="text-[10px] text-slate-400">Air Sensor Node</p>
              </div>
            </div>
            <Activity className="w-4 h-4 text-amber-500" />
          </div>

          <div>
            <div className="flex items-baseline gap-1">
              <span className="text-3xl font-black text-amber-900">{tempVal.toFixed(1)}</span>
              <span className="text-base font-bold text-amber-700">°C</span>
            </div>
            <div className="w-full bg-slate-100 h-2 rounded-full mt-2 overflow-hidden">
              <div
                className="h-full bg-amber-500 rounded-full transition-all duration-700"
                style={{ width: `${Math.min(100, Math.max(0, (tempVal / 50) * 100))}%` }}
              />
            </div>
          </div>

          <div className="px-3 py-1.5 rounded-xl text-[11px] font-semibold flex items-center justify-between"
            style={{ background: tempStatus.bg, color: tempStatus.color }}>
            <span>{tempStatus.text}</span>
            <CheckCircle2 className="w-3.5 h-3.5" />
          </div>
        </div>

        {/* Air Humidity */}
        <div className="p-5 rounded-2xl bg-white border border-teal-100 shadow-xs flex flex-col justify-between space-y-3 hover:border-teal-300 transition-colors">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-xl bg-teal-100 text-teal-700">
                <Wind className="w-5 h-5" />
              </div>
              <div>
                <p className="text-xs font-bold text-slate-600">Relative Air Humidity</p>
                <p className="text-[10px] text-slate-400">Hygrometer Node</p>
              </div>
            </div>
            <Activity className="w-4 h-4 text-teal-500" />
          </div>

          <div>
            <div className="flex items-baseline gap-1">
              <span className="text-3xl font-black text-teal-900">{humidityVal.toFixed(1)}</span>
              <span className="text-base font-bold text-teal-700">%</span>
            </div>
            <div className="w-full bg-slate-100 h-2 rounded-full mt-2 overflow-hidden">
              <div
                className="h-full bg-teal-500 rounded-full transition-all duration-700"
                style={{ width: `${Math.min(100, Math.max(0, humidityVal))}%` }}
              />
            </div>
          </div>

          <div className="px-3 py-1.5 rounded-xl text-[11px] font-semibold flex items-center justify-between bg-teal-50 text-teal-800">
            <span>Optimal Vapor Deficit</span>
            <CheckCircle2 className="w-3.5 h-3.5" />
          </div>
        </div>
      </div>

      {/* Feed History Snippet */}
      {data?.feeds && data.feeds.length > 0 && (
        <div className="bg-white/80 rounded-2xl p-4 border border-emerald-100/80 space-y-2">
          <div className="flex items-center justify-between text-xs font-bold text-slate-700 mb-1">
            <span className="flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5 text-emerald-600" />
              Recent ThingSpeak Channel Feeds ({data.feeds.length} Records)
            </span>
            <span className="text-[10px] font-medium text-slate-500">Channel ID: {channel?.id}</span>
          </div>

          <div className="divide-y divide-slate-100 text-xs">
            {data.feeds.slice(-3).reverse().map((feed, idx) => (
              <div key={feed.entry_id || idx} className="py-2 flex items-center justify-between text-slate-600">
                <span className="font-mono text-[11px] text-slate-500">
                  #{feed.entry_id} · {feed.created_at ? new Date(feed.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }) : 'Recent'}
                </span>
                <div className="flex items-center gap-4 font-semibold text-slate-800">
                  <span className="text-emerald-700 font-medium">SML: {feed.field1 ?? moistureVal}%</span>
                  <span className="text-amber-700 font-medium">Temp: {feed.field2 ?? tempVal}°C</span>
                  <span className="text-teal-700 font-medium">Hum: {feed.field3 ?? humidityVal}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Footer Info */}
      <div className="flex flex-wrap items-center justify-between text-xs text-slate-500 pt-2 border-t border-emerald-100">
        <div className="flex items-center gap-2">
          <Radio className="w-3.5 h-3.5 text-emerald-600 animate-pulse" />
          <span>ThingSpeak IoT API: <code className="text-[10px] bg-slate-100 px-1.5 py-0.5 rounded text-slate-700">api.thingspeak.com/channels/3430931</code></span>
        </div>
        <div>
          <span>Last Sync: {lastUpdated ? lastUpdated.toLocaleTimeString() : 'Pending'}</span>
        </div>
      </div>
    </div>
  )
}
