import { memo, useMemo } from 'react'
import { Sun, CloudRain, Wind, Droplets, Sparkles, AlertTriangle, Thermometer } from 'lucide-react'
import type { WeatherData } from '../../types/dashboard'

interface Props {
  data?: Partial<WeatherData>
}

export const WeatherIntelligenceCard = memo(function WeatherIntelligenceCard({ data }: Props) {
  const weather: WeatherData = useMemo(() => ({
    currentTempC: data?.currentTempC ?? 34,
    humidityPercent: data?.humidityPercent ?? 68,
    windSpeedKmph: data?.windSpeedKmph ?? 14,
    rainProbabilityPercent: data?.rainProbabilityPercent ?? 85,
    condition: data?.condition ?? 'Moderate Rain Expected',
    locationName: data?.locationName ?? 'Anand, Gujarat',
    todayForecast: data?.todayForecast ?? {
      date: '2026-07-24', dayLabel: 'Today', tempMaxC: 34, tempMinC: 26, humidityPercent: 68, rainfallMm: 12.4, windSpeedKmph: 14, condition: 'Passing Showers', iconType: 'rain'
    },
    next3Days: data?.next3Days ?? [
      { date: '2026-07-25', dayLabel: 'Tomorrow', tempMaxC: 30, tempMinC: 24, humidityPercent: 82, rainfallMm: 27.4, windSpeedKmph: 18, condition: 'Heavy Rain', iconType: 'rain' },
      { date: '2026-07-26', dayLabel: 'Sat', tempMaxC: 31, tempMinC: 25, humidityPercent: 74, rainfallMm: 4.2, windSpeedKmph: 12, condition: 'Breezy', iconType: 'wind' },
      { date: '2026-07-27', dayLabel: 'Sun', tempMaxC: 33, tempMinC: 26, humidityPercent: 62, rainfallMm: 0, windSpeedKmph: 10, condition: 'Sunny', iconType: 'sun' },
    ],
    aiRecommendation: data?.aiRecommendation ?? {
      type: 'pesticide',
      title: 'Rain Expected within 24 Hours (85% Chance)',
      recommendation: 'Delay pesticide & fertilizer spraying by 48 hours to prevent rainwater wash-off and chemical wastage.',
      badgeColor: 'bg-amber-500/20 text-amber-900 border-amber-300'
    }
  }), [data])

  return (
    <div className="glass-card p-6 border-l-4 border-l-sky-600 space-y-5 animate-fade-in">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-sky-500 to-blue-600 text-white flex items-center justify-center shadow-md">
            <CloudRain className="w-5 h-5 animate-bounce" />
          </div>
          <div>
            <h3 className="text-base font-extrabold text-slate-900">AI Weather Intelligence & Forecast</h3>
            <p className="text-xs text-slate-500 font-medium">Micro-Climate Telemetry · {weather.locationName}</p>
          </div>
        </div>

        {/* Live Weather Badge */}
        <span className="px-3 py-1 rounded-full text-xs font-black bg-sky-100 text-sky-800 border border-sky-300 flex items-center gap-1.5 shadow-xs">
          <span className="w-2 h-2 rounded-full bg-sky-500 animate-ping"></span>
          Live Satellite Feed
        </span>
      </div>

      {/* Main Temp & Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Current Temp Card */}
        <div className="p-4 rounded-2xl bg-gradient-to-br from-sky-50 to-blue-50/80 border border-sky-100 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-sky-600 text-white flex items-center justify-center shadow-sm">
            <Thermometer className="w-6 h-6" />
          </div>
          <div>
            <p className="text-3xl font-black text-slate-900 tracking-tight">{weather.currentTempC}°C</p>
            <p className="text-xs font-bold text-sky-700">{weather.condition}</p>
          </div>
        </div>

        {/* Humidity */}
        <div className="p-4 rounded-2xl bg-white border border-slate-200/80 flex items-center gap-3">
          <Droplets className="w-6 h-6 text-teal-600 flex-shrink-0" />
          <div>
            <p className="text-xs text-slate-500 font-semibold">Relative Humidity</p>
            <p className="text-lg font-black text-slate-800">{weather.humidityPercent}%</p>
          </div>
        </div>

        {/* Wind Speed */}
        <div className="p-4 rounded-2xl bg-white border border-slate-200/80 flex items-center gap-3">
          <Wind className="w-6 h-6 text-indigo-600 flex-shrink-0" />
          <div>
            <p className="text-xs text-slate-500 font-semibold">Wind Velocity</p>
            <p className="text-lg font-black text-slate-800">{weather.windSpeedKmph} km/h</p>
          </div>
        </div>

        {/* Rain Probability */}
        <div className="p-4 rounded-2xl bg-white border border-slate-200/80 flex items-center gap-3">
          <CloudRain className="w-6 h-6 text-blue-600 flex-shrink-0" />
          <div>
            <p className="text-xs text-slate-500 font-semibold">Rain Probability</p>
            <p className="text-lg font-black text-blue-700">{weather.rainProbabilityPercent}%</p>
          </div>
        </div>
      </div>

      {/* AI Action Recommendation Highlighted Badge */}
      <div className={`p-4 rounded-2xl border flex items-start gap-3 shadow-xs ${weather.aiRecommendation.badgeColor}`}>
        <Sparkles className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5 animate-pulse" />
        <div className="space-y-1">
          <p className="text-xs font-black uppercase tracking-wider text-amber-900">
            AI Action Alert: {weather.aiRecommendation.title}
          </p>
          <p className="text-xs font-semibold leading-relaxed text-slate-800">
            {weather.aiRecommendation.recommendation}
          </p>
        </div>
      </div>

      {/* 3-Day Forecast Window */}
      <div className="space-y-2 pt-1">
        <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">3-Day Micro-Forecast Window</p>
        <div className="grid grid-cols-3 gap-3">
          {weather.next3Days.map((day, idx) => (
            <div key={idx} className="p-3 rounded-2xl bg-slate-50 border border-slate-200/80 text-center space-y-1 hover:border-sky-300 transition-colors">
              <p className="text-xs font-bold text-slate-700">{day.dayLabel}</p>
              {day.iconType === 'rain' && <CloudRain className="w-5 h-5 mx-auto text-blue-600 animate-bounce" />}
              {day.iconType === 'sun' && <Sun className="w-5 h-5 mx-auto text-amber-500" />}
              {day.iconType === 'wind' && <Wind className="w-5 h-5 mx-auto text-teal-600" />}
              <p className="text-xs font-extrabold text-slate-900">{day.tempMaxC}°C / {day.tempMinC}°C</p>
              <p className="text-[10px] text-slate-500 font-medium">{day.condition}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
})
