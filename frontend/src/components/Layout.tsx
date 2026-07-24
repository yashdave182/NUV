import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard, Leaf, ShoppingCart, Heart, ScrollText,
  Beef, Settings, Wifi, Sprout, Bell, Zap,
} from 'lucide-react'
import { useAppStore } from '../store/appStore'

const navItems = [
  { to: '/',          icon: LayoutDashboard, label: 'Dashboard',   color: 'text-emerald-600' },
  { to: '/advisory',  icon: Leaf,            label: 'Advisory',    color: 'text-green-600'   },
  { to: '/market',    icon: ShoppingCart,    label: 'Market',      color: 'text-amber-600'   },
  { to: '/livestock', icon: Beef,            label: 'Livestock',   color: 'text-orange-500'  },
  { to: '/health',    icon: Heart,           label: 'Health',      color: 'text-rose-500'    },
  { to: '/schemes',   icon: ScrollText,      label: 'Schemes',     color: 'text-blue-600'    },
  { to: '/settings',  icon: Settings,        label: 'Settings',    color: 'text-slate-500'   },
]

export default function Layout({ children }: { children: React.ReactNode }) {
  const { isOnline, phone } = useAppStore()

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

        {/* Connection status */}
        <div className="px-5 py-3 border-b border-emerald-100/60"
          style={{ background: 'linear-gradient(90deg, rgba(240,253,244,0.8) 0%, rgba(240,253,250,0.6) 100%)' }}>
          <div className={`flex items-center gap-2 text-xs font-semibold ${isOnline ? 'text-emerald-700' : 'text-amber-600'}`}>
            <span className={`status-dot ${isOnline ? 'online' : 'warning'}`} />
            {isOnline ? 'Live API Connected' : 'Offline Demo Mode'}
          </div>
          {phone && (
            <p className="text-[10px] text-slate-500 font-medium mt-0.5 flex items-center gap-1">
              <Wifi className="w-2.5 h-2.5" /> +91 {phone}
            </p>
          )}
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-0.5">
          <p className="text-[9px] uppercase font-bold tracking-[0.14em] px-3 pb-2.5 pt-1" style={{ color: '#86efac' }}>
            Main Navigation
          </p>
          {navItems.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
            >
              <Icon className="w-4 h-4 flex-shrink-0" />
              <span>{label}</span>
            </NavLink>
          ))}
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
      <main className="flex-1 flex flex-col overflow-hidden">

        {/* Mobile top bar */}
        <header className="lg:hidden flex items-center justify-between px-4 py-3 border-b border-emerald-100"
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
            <div className={`flex items-center gap-1.5 text-xs font-semibold ${isOnline ? 'text-emerald-700' : 'text-amber-600'}`}>
              <span className={`status-dot ${isOnline ? 'online' : 'warning'}`} style={{ width: '6px', height: '6px' }} />
              {isOnline ? 'Online' : 'Offline'}
            </div>
            <Bell className="w-4 h-4 text-slate-400" />
          </div>
        </header>

        {/* Scrollable content area */}
        <div className="flex-1 overflow-y-auto">
          <div className="p-4 lg:p-8 animate-fade-in max-w-7xl mx-auto">
            {children}
          </div>
        </div>

        {/* Mobile bottom navigation */}
        <nav className="lg:hidden flex items-center justify-around py-2 border-t border-emerald-100"
          style={{ background: 'rgba(255,255,255,0.95)', backdropFilter: 'blur(16px)' }}>
          {navItems.slice(0, 6).map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                `flex flex-col items-center gap-0.5 px-2 py-1.5 rounded-xl transition-all ${
                  isActive
                    ? 'text-emerald-700 bg-emerald-50 font-bold'
                    : 'text-slate-500'
                }`
              }
            >
              <Icon className="w-5 h-5" />
              <span className="text-[9px] font-semibold">{label}</span>
            </NavLink>
          ))}
        </nav>
      </main>
    </div>
  )
}
