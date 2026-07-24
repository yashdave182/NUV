import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import {
  User, Phone, MapPin, Sprout, ArrowRight, ArrowLeft,
  CheckCircle2, Languages, ShieldCheck, Lock, Sparkles, AlertCircle, RefreshCw
} from 'lucide-react'
import { useAppStore } from '../store/appStore'
import { registerFarmerProfile } from '../services/authService'

const statesList = ['Gujarat', 'Maharashtra', 'Rajasthan', 'Madhya Pradesh', 'Uttar Pradesh']

const soilTypes = [
  { id: 'black_cotton', label: 'Black Cotton Soil (Kali Mitti)' },
  { id: 'alluvial', label: 'Alluvial Soil (Goradu Mitti)' },
  { id: 'red_sandy', label: 'Red & Sandy Loam' },
  { id: 'clay_loam', label: 'Heavy Clay Loam' },
  { id: 'laterite', label: 'Laterite Soil' },
]

const availableCrops = [
  { id: 'cotton', name: 'Cotton (કપાસ / कपास)' },
  { id: 'wheat', name: 'Wheat (ઘઉં / गेहूं)' },
  { id: 'groundnut', name: 'Groundnut (મગફળી / मूंगफली)' },
  { id: 'bajra', name: 'Bajra (બાજરી / बाजरा)' },
  { id: 'maize', name: 'Maize (મકાઈ / मक्का)' },
  { id: 'cumin', name: 'Cumin (જીરું / जीरा)' },
  { id: 'castor', name: 'Castor (એરંડા / अरंडी)' },
  { id: 'chilli', name: 'Chilli (મરચાં / मिर्च)' },
  { id: 'onion', name: 'Onion (ડુંગળી / प्याज)' },
  { id: 'potato', name: 'Potato (બટાકા / आलू)' },
  { id: 'banana', name: 'Banana (કેળાં / केला)' },
  { id: 'mango', name: 'Mango (કેરી / आम)' },
]

export default function Signup() {
  const navigate = useNavigate()
  const { login } = useAppStore()

  const [step, setStep] = useState<1 | 2 | 3>(1)

  // Form State
  const [name, setName] = useState('')
  const [phone, setPhone] = useState('')
  const [language, setLanguage] = useState('English')
  
  const [state, setState] = useState('Gujarat')
  const [district, setDistrict] = useState('Anand')
  const [landAcres, setLandAcres] = useState<number>(3.5)
  const [soilType, setSoilType] = useState('black_cotton')

  const [selectedCrops, setSelectedCrops] = useState<string[]>(['cotton', 'wheat'])
  const [pin, setPin] = useState('1234')

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const toggleCrop = (cropId: string) => {
    if (selectedCrops.includes(cropId)) {
      if (selectedCrops.length === 1) return // Keep at least one
      setSelectedCrops(selectedCrops.filter(c => c !== cropId))
    } else {
      setSelectedCrops([...selectedCrops, cropId])
    }
  }

  const handleNext = (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    if (step === 1) {
      if (!name.trim()) {
        setError('Please enter your full name.')
        return
      }
      const cleaned = phone.replace(/\D/g, '')
      if (cleaned.length < 10) {
        setError('Please enter a valid 10-digit mobile number.')
        return
      }
      setStep(2)
    } else if (step === 2) {
      if (!district.trim()) {
        setError('Please enter your district.')
        return
      }
      if (!landAcres || landAcres <= 0) {
        setError('Please specify valid landholding in acres.')
        return
      }
      setStep(3)
    }
  }

  const handleRegisterSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    const cleanedPhone = phone.replace(/\D/g, '')

    try {
      const res = await registerFarmerProfile({
        phone: cleanedPhone,
        name: name.trim(),
        state,
        district: district.trim(),
        language,
        land_holding_acres: landAcres,
        soil_type: soilType,
        primary_crops: selectedCrops,
        pin: pin || '1234'
      })

      if (res.success && res.user) {
        login(res.user, res.access_token)
        navigate('/')
      } else {
        setError(res.message || 'Registration failed')
      }
    } catch (err: any) {
      setError(err.message || 'Error creating farmer profile.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-[85vh] flex items-center justify-center p-2 lg:p-6">
      <div className="w-full max-w-xl bg-white rounded-3xl shadow-2xl border border-emerald-100/80 overflow-hidden">
        
        {/* Top Header */}
        <div className="bg-gradient-to-r from-emerald-900 via-emerald-800 to-teal-900 p-6 text-white">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <div className="w-9 h-9 rounded-xl bg-emerald-500/20 border border-emerald-400/30 flex items-center justify-center">
                <Sprout className="w-5 h-5 text-emerald-300" />
              </div>
              <span className="text-lg font-extrabold tracking-tight">AgriNova</span>
            </div>
            <span className="text-xs font-bold bg-emerald-700/60 px-3 py-1 rounded-full border border-emerald-500/30">
              Farmer Onboarding
            </span>
          </div>

          <h2 className="text-xl font-bold">Register New Farmer Profile</h2>
          <p className="text-xs text-emerald-200/80 mt-1">
            Setup your farm details for automated AI irrigation, market intelligence & scheme matching.
          </p>

          {/* Stepper Progress */}
          <div className="mt-5 flex items-center justify-between relative px-2">
            <div className="absolute left-6 right-6 top-1/2 -translate-y-1/2 h-0.5 bg-emerald-700/60 -z-0" />
            
            {[1, 2, 3].map((s) => (
              <div
                key={s}
                className={`relative z-10 flex items-center justify-center w-8 h-8 rounded-full font-bold text-xs transition-all ${
                  step >= s
                    ? 'bg-emerald-400 text-emerald-950 ring-4 ring-emerald-900'
                    : 'bg-emerald-900 text-emerald-300 border border-emerald-700'
                }`}
              >
                {step > s ? <CheckCircle2 className="w-4 h-4 text-emerald-950" /> : s}
              </div>
            ))}
          </div>

          <div className="flex justify-between text-[11px] font-semibold text-emerald-200 mt-2 px-1">
            <span className={step === 1 ? 'text-white font-bold' : ''}>Personal Info</span>
            <span className={step === 2 ? 'text-white font-bold' : ''}>Farm Details</span>
            <span className={step === 3 ? 'text-white font-bold' : ''}>Crops & PIN</span>
          </div>
        </div>

        {/* Form Body */}
        <div className="p-6">
          
          {error && (
            <div className="mb-4 p-3 rounded-2xl bg-rose-50 border border-rose-200 flex items-start gap-2 text-rose-700 text-xs font-medium animate-fade-in">
              <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          {/* STEP 1: Personal Info */}
          {step === 1 && (
            <form onSubmit={handleNext} className="space-y-4 animate-fade-in">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1.5">
                  Full Name (ખેડૂતનું નામ / किसान का नाम) *
                </label>
                <div className="relative flex items-center">
                  <User className="w-4 h-4 absolute left-3.5 text-slate-400" />
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="e.g. Ramesh Patel"
                    className="w-full pl-10 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-2xl text-slate-900 font-semibold text-sm focus:bg-white focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none transition-all"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1.5">
                  Mobile Number (મોબાઇલ નંબર) *
                </label>
                <div className="relative flex items-center">
                  <div className="absolute left-3.5 flex items-center gap-1 text-slate-500 text-sm font-semibold select-none">
                    <span>🇮🇳 +91</span>
                    <span className="w-px h-4 bg-slate-300" />
                  </div>
                  <input
                    type="tel"
                    maxLength={10}
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    placeholder="90993 14955"
                    className="w-full pl-24 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-2xl text-slate-900 font-bold text-base focus:bg-white focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none transition-all"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1.5">
                  Preferred Advisory Language (ભાષા)
                </label>
                <div className="relative flex items-center">
                  <Languages className="w-4 h-4 absolute left-3.5 text-slate-400" />
                  <select
                    value={language}
                    onChange={(e) => setLanguage(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-2xl text-slate-900 font-semibold text-sm focus:bg-white focus:border-emerald-500 outline-none cursor-pointer"
                  >
                    <option value="English">English</option>
                    <option value="Gujarati">ગુજરાતી (Gujarati)</option>
                    <option value="Hindi">हिंदी (Hindi)</option>
                    <option value="Marathi">मराठी (Marathi)</option>
                  </select>
                </div>
              </div>

              <div className="pt-4 flex justify-end">
                <button
                  type="submit"
                  className="w-full py-3.5 px-4 bg-emerald-600 hover:bg-emerald-700 active:scale-[0.99] text-white font-bold text-sm rounded-2xl shadow-lg shadow-emerald-600/25 flex items-center justify-center gap-2 transition-all cursor-pointer"
                >
                  <span>Continue to Farm Details</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </form>
          )}

          {/* STEP 2: Location & Farm Info */}
          {step === 2 && (
            <form onSubmit={handleNext} className="space-y-4 animate-fade-in">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1.5">
                    State (રાજ્ય) *
                  </label>
                  <select
                    value={state}
                    onChange={(e) => setState(e.target.value)}
                    className="w-full px-3 py-3 bg-slate-50 border border-slate-200 rounded-2xl text-slate-900 font-semibold text-sm focus:bg-white focus:border-emerald-500 outline-none cursor-pointer"
                  >
                    {statesList.map((st) => (
                      <option key={st} value={st}>{st}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1.5">
                    District (જિલ્લો) *
                  </label>
                  <input
                    type="text"
                    value={district}
                    onChange={(e) => setDistrict(e.target.value)}
                    placeholder="e.g. Anand"
                    className="w-full px-3 py-3 bg-slate-50 border border-slate-200 rounded-2xl text-slate-900 font-semibold text-sm focus:bg-white focus:border-emerald-500 outline-none"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1.5">
                  Landholding Size (જમીનનું ક્ષેત્રફળ - Acres)
                </label>
                <div className="flex items-center gap-3">
                  <input
                    type="number"
                    step="0.5"
                    min="0.5"
                    max="100"
                    value={landAcres}
                    onChange={(e) => setLandAcres(parseFloat(e.target.value) || 1)}
                    className="w-32 px-4 py-3 bg-slate-50 border border-slate-200 rounded-2xl text-slate-900 font-bold text-base focus:bg-white focus:border-emerald-500 outline-none"
                    required
                  />
                  <span className="text-xs font-bold text-slate-600">Acres (એકર)</span>
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1.5">
                  Primary Soil Type (જમીનનો પ્રકાર)
                </label>
                <select
                  value={soilType}
                  onChange={(e) => setSoilType(e.target.value)}
                  className="w-full px-3 py-3 bg-slate-50 border border-slate-200 rounded-2xl text-slate-900 font-semibold text-sm focus:bg-white focus:border-emerald-500 outline-none cursor-pointer"
                >
                  {soilTypes.map((st) => (
                    <option key={st.id} value={st.id}>{st.label}</option>
                  ))}
                </select>
              </div>

              <div className="pt-4 flex items-center justify-between gap-3">
                <button
                  type="button"
                  onClick={() => setStep(1)}
                  className="py-3 px-4 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs rounded-2xl flex items-center gap-1.5 transition-all cursor-pointer"
                >
                  <ArrowLeft className="w-4 h-4" />
                  <span>Back</span>
                </button>

                <button
                  type="submit"
                  className="flex-1 py-3.5 px-4 bg-emerald-600 hover:bg-emerald-700 active:scale-[0.99] text-white font-bold text-sm rounded-2xl shadow-lg shadow-emerald-600/25 flex items-center justify-center gap-2 transition-all cursor-pointer"
                >
                  <span>Select Crops & PIN</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </form>
          )}

          {/* STEP 3: Primary Crops & Security PIN */}
          {step === 3 && (
            <form onSubmit={handleRegisterSubmit} className="space-y-5 animate-fade-in">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1.5">
                  Select Primary Cultivated Crops (મુખ્ય પાક) *
                </label>
                <p className="text-[11px] text-slate-500 mb-2">
                  Select one or more crops to customize your irrigation schedules and market price alerts:
                </p>

                <div className="grid grid-cols-2 gap-2 max-h-48 overflow-y-auto pr-1">
                  {availableCrops.map((c) => {
                    const isSelected = selectedCrops.includes(c.id)
                    return (
                      <button
                        type="button"
                        key={c.id}
                        onClick={() => toggleCrop(c.id)}
                        className={`p-2.5 rounded-xl border text-left text-xs font-bold transition-all flex items-center justify-between cursor-pointer ${
                          isSelected
                            ? 'border-emerald-600 bg-emerald-50 text-emerald-900 shadow-sm'
                            : 'border-slate-200 bg-slate-50 text-slate-600 hover:bg-slate-100'
                        }`}
                      >
                        <span className="truncate">{c.name}</span>
                        {isSelected && <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />}
                      </button>
                    )
                  })}
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1.5">
                  Set 4-Digit Security PIN (PIN નંબર)
                </label>
                <div className="relative flex items-center">
                  <Lock className="w-4 h-4 absolute left-3.5 text-slate-400" />
                  <input
                    type="password"
                    maxLength={4}
                    value={pin}
                    onChange={(e) => setPin(e.target.value)}
                    placeholder="1234"
                    className="w-full pl-11 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-2xl text-slate-900 font-extrabold tracking-widest text-lg focus:bg-white focus:border-emerald-500 outline-none"
                    required
                  />
                </div>
                <p className="text-[11px] text-slate-400 mt-1">
                  Allows quick passwordless sign-in across mobile devices.
                </p>
              </div>

              <div className="pt-3 flex items-center justify-between gap-3">
                <button
                  type="button"
                  onClick={() => setStep(2)}
                  className="py-3 px-4 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs rounded-2xl flex items-center gap-1.5 transition-all cursor-pointer"
                >
                  <ArrowLeft className="w-4 h-4" />
                  <span>Back</span>
                </button>

                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 py-3.5 px-4 bg-emerald-600 hover:bg-emerald-700 active:scale-[0.99] text-white font-bold text-sm rounded-2xl shadow-lg shadow-emerald-600/25 flex items-center justify-center gap-2 transition-all cursor-pointer disabled:opacity-50"
                >
                  {loading ? (
                    <RefreshCw className="w-4 h-4 animate-spin" />
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4" />
                      <span>Complete Registration</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          )}

          {/* Login Link */}
          <div className="mt-6 text-center text-xs text-slate-600 font-medium">
            Already registered?{' '}
            <Link to="/login" className="text-emerald-700 font-extrabold hover:underline">
              Sign In with OTP / PIN &rarr;
            </Link>
          </div>

        </div>
      </div>
    </div>
  )
}
