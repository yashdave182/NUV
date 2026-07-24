export interface WeatherForecastDay {
  date: string
  dayLabel: string
  tempMaxC: number
  tempMinC: number
  humidityPercent: number
  rainfallMm: number
  windSpeedKmph: number
  condition: string
  iconType: 'sun' | 'rain' | 'wind' | 'cloud'
}

export interface WeatherAIRecommendation {
  type: 'irrigation' | 'pesticide' | 'fertilizer' | 'general'
  title: string
  recommendation: string
  badgeColor: string
}

export interface WeatherData {
  currentTempC: number
  humidityPercent: number
  windSpeedKmph: number
  rainProbabilityPercent: number
  condition: string
  locationName: string
  todayForecast: WeatherForecastDay
  next3Days: WeatherForecastDay[]
  aiRecommendation: WeatherAIRecommendation
}

export interface MandiTickerItem {
  id: string
  cropName: string
  mandiName: string
  priceINR: number
  unit: string
  changePercent: number
  isUp: boolean
}

export interface KPIMetric {
  id: string
  label: string
  value: string
  unit: string
  change: string
  isPositive: boolean
  icon: string
  trendData: { time: string; val: number }[]
  color: string
}

export interface FarmHealthInput {
  crop: string
  state: string
  soilType: string
}

export interface HealthScoreBreakdown {
  soilHealth: number
  weather: number
  water: number
  disease: number
  market: number
}

export interface FarmHealthResult {
  overallScore: number
  statusText: string
  breakdown: HealthScoreBreakdown
  soilStatus: string
  diseaseRisk: 'Low' | 'Medium' | 'High'
  waterRequirement: string
  fertilizerSuggestion: string
  expectedYield: string
  marketRecommendation: string
  weatherAlert: string
}

export interface DetailedActionItem {
  id: string
  timeframe: 'Morning' | 'Afternoon' | 'Evening' | 'Tomorrow'
  title: string
  description: string
  category: 'water' | 'fertilizer' | 'pest' | 'harvest'
  priority: 'High' | 'Medium' | 'Low'
  duration: string
  status: 'Pending' | 'In Progress' | 'Completed'
}

export interface SensorDataPoint {
  time: string
  moisture: number
  temperature: number
  humidity: number
}

export interface SensorTelemetry {
  soilMoisturePercent: number
  temperatureC: number
  humidityPercent: number
  connectionStatus: 'Online' | 'Degraded' | 'Offline'
  lastUpdated: string
  history: SensorDataPoint[]
}

export interface AIExplainabilityFactors {
  recommendationTitle: string
  reasoningText: string
  factors: {
    soilMoisture: string
    temperature: string
    rainChance: string
    cropStage: string
    expectedWaterNeed: string
  }
}
