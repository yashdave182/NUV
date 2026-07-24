import React, { useState } from 'react'
import { NavLink, Link, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard, Leaf, ShoppingCart, Heart, ScrollText,
  Beef, Settings, Wifi, Sprout, Bell, Zap, User, LogOut,
  ChevronDown, MapPin, Layers, Globe, ShieldCheck, UserPlus, LogIn
} from 'lucide-react'
import { useAppStore } from '../store/appStore'
import { OfflineSyncBanner } from './OfflineSyncBanner'
import { FloatingAIAssistant } from './FloatingAIAssistant'

const navItems = [
  { to: '/',          icon: LayoutDashboard, label: 'Dashboard',   color: 'text-emerald-600' },
  { to: '/advisory',  icon: Leaf,            label: 'Advisory',    color: 'text-green-600'   },
  { to: '/market',    icon: ShoppingCart,    label: 'Market',      color: 'text-amber-600'   },
  { to: '/livestock', icon: Beef,            label: 'Livestock',   color: 'text-orange-500'  },
  { to: '/health',    icon: Heart,           label: 'Health',      color: 'text-rose-500'    },
  { to: '/schemes',   icon: ScrollText,      label: 'Schemes',     color: 'text-blue-600'    },
  { to: '/settings',  icon: Settings,        label: 'Settings',    color: 'text-slate-500'   },
]

const prefetchMap: Record<string, () => Promise<unknown>> = {
  '/': () => import('../pages/Dashboard'),
  '/advisory': () => import('../pages/Advisory'),
  '/market': () => import('../pages/Market'),
  '/livestock': () => import('../pages/Livestock'),
  '/health': () => import('../pages/Health'),
  '/schemes': () => import('../pages/Schemes'),
  '/settings': () => import('../pages/Settings'),
  '/login': () => import('../pages/Login'),
  '/signup': () => import('../pages/Signup'),
}

export default function Layout({ children }: { children: React.ReactNode }) {
  const navigate = useNavigate()
  const { isOnline, phone, user, isAuthenticated, logout } = useAppStore()
  const [profileMenuOpen, setProfileMenuOpen] = useState(false)

  const handleLogout = () => {
    logout()
    setProfileMenuOpen(false)
    navigate('/login')
  }

  const handlePrefetch = (path: string) => {
    if (prefetchMap[path]) {
      prefetchMap[path]()
    }
  }

  return (
    <div className="flex h-screen overflow-hidden" style={{ background: '#f0f7f4' }}>

      {/* ── Premium Sidebar ─────────────────────────── */}
      <aside className="hidden lg:flex flex-col w-64 flex-shrink-0 sidebar">

        {/* Logo Header */}
        <div className="px-5 py-5 border-b border-emerald-100/70">
          <div className="flex items-center gap-3">
            <div className="sidebar-logo w-11 h-11 flex items-center justify-center flex-shrink-0">
              <Sprout className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-extrabold tracking-tight" style={{ color: '#1a2e22' }}>
                Agri<span className="text-gradient-green">Nova</span>
              </h1>
              <p className="text-[9px] font-bold uppercase tracking-[0.12em]" style={{ color: '#15803d' }}>
                Precision AgriTech · AI
              </p>
            </div>
          </div>
        </div>

        {/* Connection & Auth Status */}
        <div className="px-5 py-3 border-b border-emerald-100/60"
          style={{ background: 'linear-gradient(90deg, rgba(240,253,244,0.8) 0%, rgba(240,253,250,0.6) 100%)' }}>
          <div className={`flex items-center gap-2 text-xs font-semibold ${isOnline ? 'text-emerald-700' : 'text-amber-600'}`}>
            <span className={`status-dot ${isOnline ? 'online' : 'warning'}`} />
            {isOnline ? 'Live API Connected' : 'Offline Demo Mode'}
          </div>
          
          {isAuthenticated && user ? (
            <div className="mt-2 pt-2 border-t border-emerald-200/50 flex items-center justify-between">
              <div>
                <p className="text-xs font-extrabold text-slate-800 truncate">{user.name}</p>
                <p className="text-[10px] text-slate-500 font-semibold">+91 {user.phone}</p>
              </div>
              <button
                onClick={() => setProfileMenuOpen(!profileMenuOpen)}
                className="w-7 h-7 rounded-full bg-emerald-600 text-white font-bold text-xs flex items-center justify-center shadow hover:bg-emerald-700 transition-colors cursor-pointer"
                title="View Profile Details"
              >
                {user.name.charAt(0)}
              </button>
            </div>
          ) : (
            <div className="mt-2 pt-2 border-t border-emerald-200/50 flex items-center justify-between">
              <span className="text-xs text-slate-500 font-medium">Guest Access</span>
              <Link
                to="/login"
                className="text-xs font-bold text-emerald-700 hover:underline flex items-center gap-1"
              >
                <LogIn className="w-3 h-3" /> Sign In
              </Link>
            </div>
          )}
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-0.5">
          <p className="text-[9px] uppercase font-bold tracking-[0.14em] px-3 pb-2.5 pt-1" style={{ color: '#15803d' }}>
            Main Navigation
          </p>
          {navItems.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              onMouseEnter={() => handlePrefetch(to)}
              onFocus={() => handlePrefetch(to)}
              className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
            >
              <Icon className="w-4 h-4 flex-shrink-0" />
              <span>{label}</span>
            </NavLink>
          ))}

          <div className="pt-3 mt-3 border-t border-emerald-100/60">
            <p className="text-[9px] uppercase font-bold tracking-[0.14em] px-3 pb-2 pt-1 text-slate-400">
              Account
            </p>
            {isAuthenticated ? (
              <button
                onClick={handleLogout}
                className="w-full text-left px-3 py-2 rounded-xl text-xs font-bold text-rose-600 hover:bg-rose-50 flex items-center gap-2 transition-colors cursor-pointer"
              >
                <LogOut className="w-4 h-4" />
                <span>Sign Out</span>
              </button>
            ) : (
              <div className="space-y-1">
                <NavLink to="/login" className="nav-item">
                  <LogIn className="w-4 h-4 text-emerald-600" />
                  <span>Login with OTP</span>
                </NavLink>
                <NavLink to="/signup" className="nav-item">
                  <UserPlus className="w-4 h-4 text-teal-600" />
                  <span>Farmer Onboarding</span>
                </NavLink>
              </div>
            )}
          </div>
        </nav>

        {/* Footer badge */}
        <div className="px-5 py-4 border-t border-emerald-100/70">
          <div className="glass-card-emerald px-4 py-3">
            <div className="flex items-center gap-2 mb-1">
              <div className="w-6 h-6 rounded-lg bg-emerald-600 flex items-center justify-center">
                <Zap className="w-3 h-3 text-white" />
              </div>
              <span className="text-xs font-bold text-emerald-800">TetraTHON 2026</span>
            </div>
            <p className="text-[10px] text-emerald-700 font-medium leading-tight">
              Indo–French AI Hackathon<br />
              <span className="text-emerald-600 font-bold">Innovation Track</span>
            </p>
          </div>
        </div>
      </aside>

      {/* ── Main Content ──────────────────────────────── */}
      <main className="flex-1 flex flex-col overflow-hidden relative">

        {/* Desktop Top Header Bar */}
        <header className="hidden lg:flex items-center justify-between px-8 py-3.5 bg-white/80 backdrop-blur-md border-b border-emerald-100/80 z-20">
          <div className="flex items-center gap-3">
            <h2 className="text-sm font-extrabold text-slate-800">
              Welcome to AgriNova AI
            </h2>
            {user && (
              <span className="text-xs font-bold text-emerald-800 bg-emerald-100/80 px-2.5 py-0.5 rounded-full border border-emerald-200">
                🌾 {user.state} ({user.district}) · {user.land_holding_acres} Acres
              </span>
            )}
          </div>

          <div className="flex items-center gap-4">
            <OfflineSyncBanner />

            {isAuthenticated && user ? (
              <div className="relative">
                <button
                  onClick={() => setProfileMenuOpen(!profileMenuOpen)}
                  className="flex items-center gap-2.5 p-1.5 pr-3 rounded-2xl bg-emerald-50 hover:bg-emerald-100/80 border border-emerald-200/80 transition-all cursor-pointer"
                >
                  <div className="w-8 h-8 rounded-xl bg-emerald-600 text-white font-extrabold text-sm flex items-center justify-center shadow-sm">
                    {user.name.charAt(0)}
                  </div>
                  <div className="text-left">
                    <p className="text-xs font-bold text-slate-900 leading-tight">{user.name}</p>
                    <p className="text-[10px] text-emerald-700 font-semibold">{user.language}</p>
                  </div>
                  <ChevronDown className="w-3.5 h-3.5 text-slate-500 ml-1" />
                </button>

                {/* Profile Popup Menu */}
                {profileMenuOpen && (
                  <div className="absolute right-0 mt-2 w-72 bg-white rounded-2xl shadow-xl border border-emerald-100 p-4 z-50 animate-fade-in">
                    <div className="flex items-center gap-3 pb-3 border-b border-slate-100">
                      <div className="w-10 h-10 rounded-2xl bg-emerald-600 text-white font-extrabold text-base flex items-center justify-center shadow-md">
                        {user.name.charAt(0)}
                      </div>
                      <div>
                        <p className="text-sm font-bold text-slate-900">{user.name}</p>
                        <p className="text-xs text-slate-500 font-medium">+91 {user.phone}</p>
                      </div>
                    </div>

                    <div className="py-3 space-y-2 text-xs">
                      <div className="flex items-center justify-between text-slate-600">
                        <span className="flex items-center gap-1.5"><MapPin className="w-3.5 h-3.5 text-emerald-600" /> Location:</span>
                        <span className="font-bold text-slate-800">{user.district}, {user.state}</span>
                      </div>
                      <div className="flex items-center justify-between text-slate-600">
                        <span className="flex items-center gap-1.5"><Layers className="w-3.5 h-3.5 text-amber-600" /> Landholding:</span>
                        <span className="font-bold text-slate-800">{user.land_holding_acres} Acres</span>
                      </div>
                      <div className="flex items-center justify-between text-slate-600">
                        <span className="flex items-center gap-1.5"><Globe className="w-3.5 h-3.5 text-blue-600" /> Language:</span>
                        <span className="font-bold text-slate-800">{user.language}</span>
                      </div>
                      <div className="pt-2">
                        <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Primary Crops:</p>
                        <div className="flex flex-wrap gap-1">
                          {user.primary_crops.map(crop => (
                            <span key={crop} className="text-[10px] font-bold text-emerald-800 bg-emerald-100 px-2 py-0.5 rounded-full capitalize">
                              {crop}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>

                    <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
                      <Link
                        to="/settings"
                        onClick={() => setProfileMenuOpen(false)}
                        className="text-xs text-slate-600 font-bold hover:text-emerald-700"
                      >
                        Edit Profile
                      </Link>
                      <button
                        onClick={handleLogout}
                        className="text-xs text-rose-600 font-bold hover:underline flex items-center gap-1 cursor-pointer"
                      >
                        <LogOut className="w-3.5 h-3.5" /> Sign Out
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Link
                  to="/login"
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs rounded-xl shadow-sm transition-all flex items-center gap-1.5"
                >
                  <LogIn className="w-3.5 h-3.5" /> Sign In
                </Link>
                <Link
                  to="/signup"
                  className="px-4 py-2 bg-emerald-50 hover:bg-emerald-100 text-emerald-800 font-bold text-xs rounded-xl border border-emerald-200 transition-all flex items-center gap-1.5"
                >
                  <UserPlus className="w-3.5 h-3.5" /> Register
                </Link>
              </div>
            )}
          </div>
        </header>

        {/* Mobile top bar */}
        <header className="lg:hidden flex items-center justify-between px-4 py-2.5 border-b border-emerald-100"
          style={{ background: 'rgba(255,255,255,0.9)', backdropFilter: 'blur(16px)' }}>
          <div className="flex items-center gap-2.5">
            <div className="sidebar-logo w-8 h-8 flex items-center justify-center">
              <Sprout className="w-4 h-4 text-white" />
            </div>
            <span className="font-extrabold text-base" style={{ color: '#1a2e22' }}>
              Agri<span className="text-gradient-green">Nova</span>
            </span>
          </div>
          <div className="flex items-center gap-2">
            <OfflineSyncBanner />
            {isAuthenticated ? (
              <button
                onClick={() => setProfileMenuOpen(!profileMenuOpen)}
                className="w-7 h-7 rounded-full bg-emerald-600 text-white font-bold text-xs flex items-center justify-center"
              >
                {user?.name.charAt(0) || 'F'}
              </button>
            ) : (
              <Link to="/login" className="text-xs font-bold text-emerald-700">
                Sign In
              </Link>
            )}
          </div>
        </header>

        {/* Scrollable content area */}
        <div className="flex-1 overflow-y-auto" onClick={() => setProfileMenuOpen(false)}>
          <div className="p-4 lg:p-8 animate-fade-in max-w-7xl mx-auto">
            {children}
          </div>
        </div>

        {/* Floating AI Assistant Widget */}
        <FloatingAIAssistant />

        {/* Mobile adaptive bottom navigation */}
        <nav className="lg:hidden flex items-center justify-around py-2 px-1 border-t border-emerald-100 z-30"
          style={{ background: 'rgba(255,255,255,0.96)', backdropFilter: 'blur(16px)' }}>
          {navItems.slice(0, 6).map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              onMouseEnter={() => handlePrefetch(to)}
              onFocus={() => handlePrefetch(to)}
              className={({ isActive }) =>
                `flex flex-col items-center gap-0.5 px-3 py-1.5 rounded-2xl transition-all duration-200 ${
                  isActive
                    ? 'text-emerald-800 bg-emerald-100/90 font-extrabold shadow-sm border border-emerald-200/80 scale-105'
                    : 'text-slate-500 font-medium hover:text-emerald-600'
                }`
              }
            >
              <Icon className="w-4 h-4" />
              <span className="text-[9px]">{label}</span>
            </NavLink>
          ))}
        </nav>
      </main>
    </div>
  )
}
