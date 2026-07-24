import React, { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import {
  Smartphone, Lock, ShieldCheck, ArrowRight, Sparkles,
  Languages, CheckCircle2, UserPlus, Sprout, RefreshCw, AlertCircle
} from 'lucide-react'
import { useAppStore } from '../store/appStore'
import { requestOtp, verifyOtpCode, loginWithPin } from '../services/authService'

const languages = [
  { code: 'English', label: 'English (EN)' },
  { code: 'Hindi', label: 'हिंदी (Hindi)' },
  { code: 'Gujarati', label: 'ગુજરાતી (Gujarati)' },
  { code: 'Marathi', label: 'मराठी (Marathi)' },
]

export default function Login() {
  const navigate = useNavigate()
  const { login, language, setLanguage } = useAppStore()

  const [authMode, setAuthMode] = useState<'otp' | 'pin'>('otp')
  const [step, setStep] = useState<'phone' | 'otp'>('phone')
  
  const [phone, setPhone] = useState('9099314955')
  const [otpCode, setOtpCode] = useState(['1', '2', '3', '4', '5', '6'])
  const [pin, setPin] = useState('1234')
  
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [infoMsg, setInfoMsg] = useState<string | null>(null)
  const [resendTimer, setResendTimer] = useState(30)

  useEffect(() => {
    let interval: any = null
    if (step === 'otp' && resendTimer > 0) {
      interval = setInterval(() => {
        setResendTimer((prev) => prev - 1)
      }, 1000)
    }
    return () => clearInterval(interval)
  }, [step, resendTimer])

  const handleSendOtp = async (e?: React.FormEvent) => {
    if (e) e.preventDefault()
    setError(null)
    setInfoMsg(null)

    const cleaned = phone.replace(/\D/g, '')
    if (cleaned.length < 10) {
      setError('Please enter a valid 10-digit Indian mobile number.')
      return
    }

    setLoading(true)
    try {
      const res = await requestOtp(cleaned, 'login')
      if (res.success) {
        setStep('otp')
        setResendTimer(30)
        setInfoMsg(`OTP code sent to +91 ${cleaned}. (Demo OTP: ${res.otp_code || '123456'})`)
      } else {
        setError(res.message || 'Failed to send OTP')
      }
    } catch (err: any) {
      setError(err.message || 'Error connecting to auth service.')
    } finally {
      setLoading(false)
    }
  }

  const handleVerifyOtp = async (e?: React.FormEvent) => {
    if (e) e.preventDefault()
    setError(null)
    setInfoMsg(null)

    const codeStr = otpCode.join('')
    if (codeStr.length !== 6) {
      setError('Please enter all 6 digits of the OTP.')
      return
    }

    setLoading(true)
    try {
      const res = await verifyOtpCode(phone, codeStr)
      if (res.success && res.user) {
        login(res.user, res.access_token)
        navigate('/')
      } else {
        setError(res.message || 'Invalid OTP code.')
      }
    } catch (err: any) {
      setError(err.message || 'Verification failed.')
    } finally {
      setLoading(false)
    }
  }

  const handlePinLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setInfoMsg(null)

    const cleaned = phone.replace(/\D/g, '')
    if (cleaned.length < 10) {
      setError('Please enter a valid 10-digit mobile number.')
      return
    }
    if (pin.length < 4) {
      setError('Please enter your 4-digit PIN.')
      return
    }

    setLoading(true)
    try {
      const res = await loginWithPin(cleaned, pin)
      if (res.success && res.user) {
        login(res.user, res.access_token)
        navigate('/')
      } else {
        setError(res.message || 'Invalid mobile number or PIN.')
      }
    } catch (err: any) {
      setError(err.message || 'PIN Login failed.')
    } finally {
      setLoading(false)
    }
  }

  const handleQuickDemoLogin = async (demoPhone: string, demoName: string) => {
    setLoading(true)
    setPhone(demoPhone)
    setError(null)
    try {
      const res = await verifyOtpCode(demoPhone, '123456')
      if (res.success && res.user) {
        login({ ...res.user, name: demoName }, res.access_token)
        navigate('/')
      }
    } catch (err: any) {
      setError('Quick Demo login failed.')
    } finally {
      setLoading(false)
    }
  }

  const handleOtpInput = (index: number, val: string) => {
    if (!/^\d*$/.test(val)) return
    const newArr = [...otpCode]
    newArr[index] = val.slice(-1)
    setOtpCode(newArr)

    // Auto focus next input
    if (val && index < 5) {
      const nextInput = document.getElementById(`otp-input-${index + 1}`)
      if (nextInput) nextInput.focus()
    }
  }

  return (
    <div className="min-h-[85vh] flex items-center justify-center p-2 lg:p-6">
      <div className="w-full max-w-md bg-white rounded-3xl shadow-2xl border border-emerald-100/80 overflow-hidden">
        
        {/* Header Banner */}
        <div className="bg-gradient-to-br from-emerald-900 via-emerald-800 to-teal-900 p-6 text-white relative">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2.5">
              <div className="w-10 h-10 rounded-2xl bg-emerald-500/20 backdrop-blur-md border border-emerald-400/30 flex items-center justify-center">
                <Sprout className="w-6 h-6 text-emerald-300" />
              </div>
              <span className="text-xl font-extrabold tracking-tight">AgriNova</span>
            </div>
            
            {/* Language Selector */}
            <div className="relative">
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="bg-emerald-950/60 text-xs font-semibold text-emerald-100 py-1.5 px-3 rounded-xl border border-emerald-500/30 outline-none cursor-pointer hover:bg-emerald-900/80 transition-colors"
              >
                {languages.map((l) => (
                  <option key={l.code} value={l.code} className="bg-slate-900 text-white">
                    {l.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <h2 className="text-xl font-bold text-emerald-50">Farmer Portal Sign In</h2>
          <p className="text-xs text-emerald-200/80 mt-1">
            Access personalized AI crop advisory, mandi prices & IoT telemetry.
          </p>
        </div>

        {/* Auth Mode Toggle Tabs */}
        <div className="flex border-b border-emerald-100 bg-emerald-50/50 p-1.5 gap-1">
          <button
            onClick={() => { setAuthMode('otp'); setStep('phone'); setError(null); }}
            className={`flex-1 py-2.5 text-xs font-bold rounded-xl transition-all flex items-center justify-center gap-1.5 ${
              authMode === 'otp'
                ? 'bg-white text-emerald-800 shadow-sm'
                : 'text-slate-500 hover:text-slate-700'
            }`}
          >
            <Smartphone className="w-4 h-4 text-emerald-600" />
            Mobile OTP Login
          </button>

          <button
            onClick={() => { setAuthMode('pin'); setError(null); }}
            className={`flex-1 py-2.5 text-xs font-bold rounded-xl transition-all flex items-center justify-center gap-1.5 ${
              authMode === 'pin'
                ? 'bg-white text-emerald-800 shadow-sm'
                : 'text-slate-500 hover:text-slate-700'
            }`}
          >
            <Lock className="w-4 h-4 text-amber-600" />
            PIN / Password
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6">

          {/* Feedback Messages */}
          {error && (
            <div className="mb-4 p-3 rounded-2xl bg-rose-50 border border-rose-200 flex items-start gap-2 text-rose-700 text-xs font-medium animate-fade-in">
              <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          {infoMsg && (
            <div className="mb-4 p-3 rounded-2xl bg-emerald-50 border border-emerald-200 flex items-start gap-2 text-emerald-800 text-xs font-medium animate-fade-in">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0 mt-0.5" />
              <span>{infoMsg}</span>
            </div>
          )}

          {/* ── OTP Flow ──────────────────────── */}
          {authMode === 'otp' && (
            <>
              {step === 'phone' ? (
                <form onSubmit={handleSendOtp} className="space-y-4">
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1.5">
                      Enter Mobile Number
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
                    <p className="text-[11px] text-slate-500 mt-1.5 flex items-center gap-1">
                      <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
                      Instant 6-digit OTP will be sent via SMS / Demo mode
                    </p>
                  </div>

                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full py-3.5 px-4 bg-emerald-600 hover:bg-emerald-700 active:scale-[0.99] text-white font-bold text-sm rounded-2xl shadow-lg shadow-emerald-600/25 flex items-center justify-center gap-2 transition-all disabled:opacity-50 cursor-pointer"
                  >
                    {loading ? (
                      <RefreshCw className="w-4 h-4 animate-spin" />
                    ) : (
                      <>
                        <span>Get Verification Code</span>
                        <ArrowRight className="w-4 h-4" />
                      </>
                    )}
                  </button>
                </form>
              ) : (
                /* Step 2: 6-Digit OTP Entry */
                <form onSubmit={handleVerifyOtp} className="space-y-5 animate-fade-in">
                  <div className="text-center">
                    <p className="text-xs text-slate-600 font-medium">
                      Enter the 6-digit verification code sent to
                    </p>
                    <p className="text-sm font-extrabold text-slate-800 mt-0.5">
                      +91 {phone}
                      <button
                        type="button"
                        onClick={() => setStep('phone')}
                        className="ml-2 text-xs text-emerald-600 hover:underline font-semibold"
                      >
                        Change
                      </button>
                    </p>
                  </div>

                  {/* 6 Digit Inputs */}
                  <div className="flex items-center justify-between gap-1.5">
                    {otpCode.map((digit, idx) => (
                      <input
                        key={idx}
                        id={`otp-input-${idx}`}
                        type="text"
                        maxLength={1}
                        value={digit}
                        onChange={(e) => handleOtpInput(idx, e.target.value)}
                        className="w-11 h-12 text-center text-xl font-bold bg-slate-50 border-2 border-slate-200 rounded-xl focus:border-emerald-600 focus:bg-white focus:ring-2 focus:ring-emerald-600/20 outline-none transition-all"
                      />
                    ))}
                  </div>

                  <div className="flex items-center justify-between text-xs text-slate-500 font-medium">
                    <span>Didn't receive code?</span>
                    {resendTimer > 0 ? (
                      <span className="text-slate-400">Resend in {resendTimer}s</span>
                    ) : (
                      <button
                        type="button"
                        onClick={() => handleSendOtp()}
                        className="text-emerald-700 font-bold hover:underline"
                      >
                        Resend OTP
                      </button>
                    )}
                  </div>

                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full py-3.5 px-4 bg-emerald-600 hover:bg-emerald-700 active:scale-[0.99] text-white font-bold text-sm rounded-2xl shadow-lg shadow-emerald-600/25 flex items-center justify-center gap-2 transition-all disabled:opacity-50 cursor-pointer"
                  >
                    {loading ? (
                      <RefreshCw className="w-4 h-4 animate-spin" />
                    ) : (
                      <>
                        <ShieldCheck className="w-4 h-4" />
                        <span>Verify & Sign In</span>
                      </>
                    )}
                  </button>
                </form>
              )}
            </>
          )}

          {/* ── PIN Flow ──────────────────────── */}
          {authMode === 'pin' && (
            <form onSubmit={handlePinLogin} className="space-y-4 animate-fade-in">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1.5">
                  Mobile Number
                </label>
                <div className="relative flex items-center">
                  <div className="absolute left-3.5 text-slate-500 text-sm font-semibold select-none">
                    +91
                  </div>
                  <input
                    type="tel"
                    maxLength={10}
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    placeholder="90993 14955"
                    className="w-full pl-14 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-2xl text-slate-900 font-bold text-sm focus:bg-white focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none transition-all"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1.5">
                  4-Digit Security PIN
                </label>
                <div className="relative flex items-center">
                  <Lock className="w-4 h-4 absolute left-3.5 text-slate-400" />
                  <input
                    type="password"
                    maxLength={4}
                    value={pin}
                    onChange={(e) => setPin(e.target.value)}
                    placeholder="••••"
                    className="w-full pl-11 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-2xl text-slate-900 font-extrabold tracking-widest text-lg focus:bg-white focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 outline-none transition-all"
                    required
                  />
                </div>
                <p className="text-[11px] text-slate-400 mt-1">Default demo PIN: 1234</p>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-3.5 px-4 bg-amber-600 hover:bg-amber-700 active:scale-[0.99] text-white font-bold text-sm rounded-2xl shadow-lg shadow-amber-600/25 flex items-center justify-center gap-2 transition-all disabled:opacity-50 cursor-pointer"
              >
                {loading ? (
                  <RefreshCw className="w-4 h-4 animate-spin" />
                ) : (
                  <>
                    <Lock className="w-4 h-4" />
                    <span>Sign In with PIN</span>
                  </>
                )}
              </button>
            </form>
          )}

          {/* Quick Demo Access Bar */}
          <div className="mt-6 pt-5 border-t border-slate-100">
            <div className="flex items-center justify-between mb-3">
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1">
                <Sparkles className="w-3 h-3 text-amber-500" /> Quick Hackathon Demo Login
              </span>
              <span className="text-[10px] text-emerald-700 font-bold bg-emerald-100/70 px-2 py-0.5 rounded-full">
                1-Click
              </span>
            </div>

            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => handleQuickDemoLogin('9099314955', 'Ramesh Patel')}
                className="p-2.5 rounded-2xl border border-emerald-200 bg-emerald-50/60 hover:bg-emerald-100/80 text-left transition-all group cursor-pointer"
              >
                <p className="text-xs font-extrabold text-emerald-900 group-hover:text-emerald-950">
                  Ramesh Patel
                </p>
                <p className="text-[10px] text-emerald-700 font-semibold mt-0.5">
                  Anand, GJ · 3.5 Acres
                </p>
              </button>

              <button
                type="button"
                onClick={() => handleQuickDemoLogin('9876543210', 'Suresh Kumar')}
                className="p-2.5 rounded-2xl border border-teal-200 bg-teal-50/60 hover:bg-teal-100/80 text-left transition-all group cursor-pointer"
              >
                <p className="text-xs font-extrabold text-teal-900 group-hover:text-teal-950">
                  Suresh Kumar
                </p>
                <p className="text-[10px] text-teal-700 font-semibold mt-0.5">
                  Rajkot, GJ · 5.0 Acres
                </p>
              </button>
            </div>
          </div>

          {/* Signup Link Footer */}
          <div className="mt-6 text-center text-xs text-slate-600 font-medium">
            New to AgriNova?{' '}
            <Link to="/signup" className="text-emerald-700 font-extrabold hover:underline">
              Register Farmer Profile &rarr;
            </Link>
          </div>

        </div>
      </div>
    </div>
  )
}
