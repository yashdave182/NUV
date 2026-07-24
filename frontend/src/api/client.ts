import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:7860'

export const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

// Request interceptor
api.interceptors.request.use((config) => {
  const phone = localStorage.getItem('agrinova_phone') || ''
  const lang = localStorage.getItem('agrinova_lang') || 'English'
  if (phone) config.headers['X-Phone'] = phone
  config.headers['Accept-Language'] = lang
  return config
})

// Response interceptor
api.interceptors.response.use(
  (res) => res,
  (err) => {
    let raw = err?.response?.data?.detail || err?.response?.data?.error || err?.message || 'Request failed'
    if (typeof raw === 'object') {
      if (Array.isArray(raw)) {
        raw = raw.map(e => e.msg || e.detail || JSON.stringify(e)).join(', ')
      } else {
        raw = JSON.stringify(raw)
      }
    }
    return Promise.reject(new Error(String(raw)))
  }
)

// ─── Agriculture ─────────────────────────────────────────────
export const getAdvisory = (data: object) => api.post('/agriculture/advisory', data)
export const getIrrigation = (data: object) => api.post('/agriculture/irrigation', data)
export const getFertilizer = (data: object) => api.post('/agriculture/fertilizer', data)
export const getPestDisease = (data: object) => api.post('/agriculture/pest-disease', data)
export const getCropCalendar = (data: object) => api.post('/agriculture/calendar', data)
export const getSoilHealth = (data: object) => api.post('/agriculture/soil-health', data)
export const getVarietyRecommendation = (data: object) => api.post('/agriculture/variety-recommendation', data)
export const getIntercropping = (data: object) => api.post('/agriculture/intercropping', data)
export const getCropInsurance = (data: object) => api.post('/agriculture/crop-insurance', data)
export const getWeatherAdvisory = (data: object) => api.post('/agriculture/weather-advisory', data)

// ─── Market ──────────────────────────────────────────────────
export const getMandiPrices = (data: object) => api.post('/market/mandi-prices', data)
export const getPriceTrend = (data: object) => api.post('/market/price-trend', data)
export const getSellDecision = (data: object) => api.post('/market/sell-decision', data)
export const getTransportOptimize = (data: object) => api.post('/market/transport-optimize', data)
export const getStorageAdvisory = (data: object) => api.post('/market/storage-advisory', data)
export const getSpoilagePrediction = (data: object) => api.post('/market/spoilage-prediction', data)
export const setPriceAlert = (data: object) => api.post('/market/price-alert', data)
export const checkPriceAlert = (data: object) => api.post('/market/price-alert/check', data)
export const getMarketIntelligence = (data: object) => api.post('/market/market-intelligence', data)
export const getMandiList = (data: object) => api.post('/market/mandi-list', data)

// ─── Livestock ────────────────────────────────────────────────
export const getLivestockProfile = (data: object) => api.post('/livestock/profile', data)
export const getLivestockVaccination = (data: object) => api.post('/livestock/vaccination-schedule', data)
export const getLivestockDiagnosis = (data: object) => api.post('/livestock/health-diagnosis', data)
export const getDeworming = (data: object) => api.post('/livestock/deworming', data)
export const getFeedFormulation = (data: object) => api.post('/livestock/feed-formulation', data)
export const getBreedingAdvice = (data: object) => api.post('/livestock/breeding-advice', data)
export const getMilkQuality = (data: object) => api.post('/livestock/milk-quality', data)
export const getDiseaseAlerts = (data: object) => api.post('/livestock/disease-alerts', data)
export const getLivestockSchemes = (data: object) => api.post('/livestock/schemes', data)

// ─── Health ───────────────────────────────────────────────────
export const getHealthAdvisory = (data: object) => api.post('/health/advisory', data)
export const getVaccinationSchedule = (data: object) => api.post('/health/vaccination-schedule', data)
export const getHealthCamps = (data: object) => api.post('/health/health-camps', data)
export const getEmergencyTriage = (data: object) => api.post('/health/emergency-triage', data)

// ─── Schemes ──────────────────────────────────────────────────
export const searchSchemes = (data: object) => api.post('/schemes/search', data)
export const getSchemeDetail = (data: object) => api.post('/schemes/detail', data)
export const trackApplication = (data: object) => api.post('/schemes/track', data)
export const checkEligibility = (data: object) => api.post('/schemes/eligibility', data)
