export function clsx(...classes: (string | undefined | false | null)[]): string {
  return classes.filter(Boolean).join(' ')
}

export function formatCurrency(amount: number, currency = '₹'): string {
  if (amount >= 100000) return `${currency}${(amount / 100000).toFixed(1)}L`
  if (amount >= 1000) return `${currency}${(amount / 1000).toFixed(1)}K`
  return `${currency}${amount.toFixed(0)}`
}

export function formatDate(dateStr: string): string {
  if (!dateStr) return '—'
  try {
    return new Date(dateStr).toLocaleDateString('en-IN', {
      day: '2-digit', month: 'short', year: 'numeric',
    })
  } catch { return dateStr }
}

export function formatRelativeDate(dateStr: string): string {
  const d = new Date(dateStr)
  const now = new Date()
  const diff = Math.floor((now.getTime() - d.getTime()) / (1000 * 60 * 60 * 24))
  if (diff === 0) return 'Today'
  if (diff === 1) return 'Yesterday'
  if (diff < 7) return `${diff} days ago`
  return formatDate(dateStr)
}

export function getConfidenceColor(confidence: number): string {
  if (confidence >= 0.8) return 'text-agri-400'
  if (confidence >= 0.6) return 'text-yellow-400'
  return 'text-red-400'
}

export function getPriorityColor(priority: string): string {
  const p = priority?.toLowerCase()
  if (p === 'critical' || p === 'high') return 'badge-red'
  if (p === 'medium') return 'badge-gold'
  return 'badge-green'
}

export function getTrendIcon(trend: string): string {
  if (!trend) return '→'
  const t = trend.toLowerCase()
  if (t.includes('up') || t.includes('bullish') || t.includes('rising')) return '↑'
  if (t.includes('down') || t.includes('bearish') || t.includes('falling')) return '↓'
  return '→'
}

export function sleep(ms: number): Promise<void> {
  return new Promise((r) => setTimeout(r, ms))
}

export function truncate(str: string, max = 80): string {
  if (!str) return ''
  return str.length > max ? str.slice(0, max) + '…' : str
}

export function parsePhone(phone: string): string {
  const cleaned = phone.replace(/\D/g, '')
  if (cleaned.startsWith('91') && cleaned.length === 12) return cleaned.slice(2)
  return cleaned.slice(-10)
}
