import { AlertTriangle, CheckCircle2, Info, XCircle, X, Leaf } from 'lucide-react'
import { useState } from 'react'

// ── Alert ─────────────────────────────────────────────────────────────────────
interface AlertProps {
  type?: 'success' | 'error' | 'warning' | 'info'
  title?: string
  message: string
  dismissible?: boolean
}
const alertIcons = { success: CheckCircle2, error: XCircle, warning: AlertTriangle, info: Info }
const alertStyles = {
  success: { bg: 'rgba(220,252,231,0.9)', border: 'rgba(134,239,172,0.6)', color: '#15803d' },
  error:   { bg: 'rgba(254,226,226,0.9)', border: 'rgba(252,165,165,0.6)', color: '#be123c' },
  warning: { bg: 'rgba(255,251,235,0.9)', border: 'rgba(253,211,77,0.55)', color: '#b45309' },
  info:    { bg: 'rgba(219,234,254,0.9)', border: 'rgba(147,197,253,0.6)', color: '#1d4ed8' },
}

export function Alert({ type = 'info', title, message, dismissible = false }: AlertProps) {
  const [visible, setVisible] = useState(true)
  if (!visible) return null
  const Icon = alertIcons[type]
  const s = alertStyles[type]

  return (
    <div className="flex gap-3 p-4 rounded-xl animate-fade-in"
      style={{ background: s.bg, border: `1px solid ${s.border}`, color: s.color }}>
      <Icon className="w-4 h-4 mt-0.5 flex-shrink-0" />
      <div className="flex-1 min-w-0">
        {title && <p className="text-sm font-bold mb-0.5">{title}</p>}
        <p className="text-sm font-medium opacity-90">{message}</p>
      </div>
      {dismissible && (
        <button onClick={() => setVisible(false)} className="hover:opacity-60 transition-opacity">
          <X className="w-4 h-4" />
        </button>
      )}
    </div>
  )
}

// ── Loading Card ──────────────────────────────────────────────────────────────
export function LoadingCard({ label, rows = 4 }: { label?: string; rows?: number }) {
  return (
    <div className="glass-card p-6 space-y-3 animate-fade-in">
      {label && (
        <div className="flex items-center gap-2 mb-1">
          <Leaf className="w-3.5 h-3.5 animate-pulse" style={{ color: '#15803d' }} />
          <p className="text-xs font-bold uppercase tracking-wider animate-pulse" style={{ color: '#15803d' }}>{label}…</p>
        </div>
      )}
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="shimmer h-4 rounded-lg" style={{ width: `${92 - i * 10}%`, animationDelay: `${i * 150}ms` }} />
      ))}
    </div>
  )
}

// ── Page Header ───────────────────────────────────────────────────────────────
export function PageHeader({
  title, subtitle, icon: Icon, badge,
}: {
  title: string; subtitle?: string; icon?: React.ElementType; badge?: string
}) {
  return (
    <div className="flex items-start gap-4 mb-6">
      {Icon && (
        <div className="w-12 h-12 rounded-2xl flex items-center justify-center flex-shrink-0"
          style={{
            background: 'linear-gradient(135deg, #16a34a, #0d9488)',
            boxShadow: '0 4px 16px rgba(21,128,61,0.3)',
          }}>
          <Icon className="w-6 h-6 text-white" />
        </div>
      )}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 flex-wrap">
          <h1 className="text-2xl font-extrabold tracking-tight" style={{ color: '#1a2e22' }}>{title}</h1>
          {badge && <span className="badge badge-green">{badge}</span>}
        </div>
        {subtitle && <p className="text-sm font-medium mt-0.5" style={{ color: '#4b7c5a' }}>{subtitle}</p>}
      </div>
    </div>
  )
}

// ── Stat Card ─────────────────────────────────────────────────────────────────
const statColorMap: Record<string, { bg: string; border: string; textColor: string; iconBg: string }> = {
  green:  { bg: 'rgba(220,252,231,0.7)', border: 'rgba(134,239,172,0.5)', textColor: '#15803d', iconBg: 'rgba(22,163,74,0.12)' },
  gold:   { bg: 'rgba(255,251,235,0.8)', border: 'rgba(253,211,77,0.45)', textColor: '#b45309', iconBg: 'rgba(217,119,6,0.12)' },
  teal:   { bg: 'rgba(204,251,241,0.7)', border: 'rgba(153,246,228,0.5)', textColor: '#0f766e', iconBg: 'rgba(13,148,136,0.12)' },
  red:    { bg: 'rgba(254,226,226,0.7)', border: 'rgba(252,165,165,0.5)', textColor: '#be123c', iconBg: 'rgba(190,18,60,0.12)' },
  blue:   { bg: 'rgba(219,234,254,0.7)', border: 'rgba(147,197,253,0.5)', textColor: '#1d4ed8', iconBg: 'rgba(29,78,216,0.12)' },
  purple: { bg: 'rgba(237,233,254,0.7)', border: 'rgba(196,181,253,0.5)', textColor: '#7c3aed', iconBg: 'rgba(124,58,237,0.12)' },
}

export function StatCard({
  label, value, sub, color = 'green', icon: Icon,
}: {
  label: string; value: string | number; sub?: string; color?: string; icon?: React.ElementType
}) {
  const c = statColorMap[color] || statColorMap.green
  return (
    <div className="p-5 rounded-2xl"
      style={{ background: c.bg, border: `1px solid ${c.border}`, boxShadow: '0 2px 8px rgba(0,0,0,0.04), 0 1px 0 rgba(255,255,255,0.8) inset' }}>
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <p className="text-[10px] font-bold uppercase tracking-[0.08em]" style={{ color: c.textColor, opacity: 0.7 }}>{label}</p>
          <p className="text-2xl font-black mt-1" style={{ color: '#1a2e22' }}>{value}</p>
          {sub && <p className="text-[11px] font-medium mt-0.5" style={{ color: '#6b7280' }}>{sub}</p>}
        </div>
        {Icon && (
          <div className="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0"
            style={{ background: c.iconBg, border: `1px solid ${c.border}` }}>
            <Icon className="w-4.5 h-4.5" style={{ color: c.textColor }} />
          </div>
        )}
      </div>
    </div>
  )
}

// ── Empty State ───────────────────────────────────────────────────────────────
export function EmptyState({ icon: Icon, title, subtitle }: { icon: React.ElementType; title: string; subtitle?: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <div className="w-16 h-16 rounded-2xl flex items-center justify-center mb-4"
        style={{ background: 'rgba(220,252,231,0.6)', border: '1px solid rgba(134,239,172,0.5)' }}>
        <Icon className="w-8 h-8" style={{ color: '#86efac' }} />
      </div>
      <h3 className="text-base font-bold" style={{ color: '#1a2e22' }}>{title}</h3>
      {subtitle && <p className="text-sm font-medium mt-1 max-w-xs" style={{ color: '#6b7280' }}>{subtitle}</p>}
    </div>
  )
}

// ── Confidence Pill ───────────────────────────────────────────────────────────
export function ConfidencePill({ value }: { value: number }) {
  const pct = Math.round(value * 100)
  const color = pct >= 80 ? '#15803d' : pct >= 60 ? '#b45309' : '#be123c'
  const bg = pct >= 80 ? 'rgba(220,252,231,0.9)' : pct >= 60 ? 'rgba(255,251,235,0.9)' : 'rgba(254,226,226,0.9)'
  const border = pct >= 80 ? 'rgba(134,239,172,0.6)' : pct >= 60 ? 'rgba(253,211,77,0.5)' : 'rgba(252,165,165,0.5)'
  return (
    <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold"
      style={{ background: bg, color, border: `1px solid ${border}` }}>
      <span className="w-1.5 h-1.5 rounded-full" style={{ background: color }} />
      {pct}% confidence
    </span>
  )
}

// ── Section Divider ───────────────────────────────────────────────────────────
export function SectionDivider({ label }: { label: string }) {
  return (
    <div className="flex items-center gap-3 my-6">
      <div className="divider-green flex-1" />
      <span className="text-[10px] font-bold uppercase tracking-[0.12em]" style={{ color: '#86efac' }}>{label}</span>
      <div className="divider-green flex-1" />
    </div>
  )
}

// ── Result Panel ──────────────────────────────────────────────────────────────
export function ResultPanel({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="glass-card-emerald p-6 space-y-4 animate-slide-up">
      <div className="flex items-center gap-2">
        <CheckCircle2 className="w-4 h-4" style={{ color: '#15803d' }} />
        <p className="text-xs font-bold uppercase tracking-wider" style={{ color: '#15803d' }}>{title}</p>
      </div>
      {children}
    </div>
  )
}
