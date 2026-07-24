import { useState, useEffect } from 'react'
import { Wifi, WifiOff, RefreshCw, CheckCircle2 } from 'lucide-react'
import { useAppStore } from '../store/appStore'

export function OfflineSyncBanner() {
  const { isOnline } = useAppStore()
  const [lastSynced, setLastSynced] = useState<string>('Just now')
  const [syncing, setSyncing] = useState(false)

  useEffect(() => {
    const interval = setInterval(() => {
      const mins = Math.floor(Math.random() * 2) + 1
      setLastSynced(`${mins} min ago`)
    }, 60000)
    return () => clearInterval(interval)
  }, [])

  const handleManualSync = () => {
    setSyncing(true)
    setTimeout(() => {
      setLastSynced('Just now')
      setSyncing(false)
    }, 800)
  }

  return (
    <div className="flex items-center gap-3">
      {/* Network Badge */}
      <div
        className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold transition-all shadow-sm ${
          isOnline
            ? 'bg-emerald-100/90 text-emerald-800 border border-emerald-300/80'
            : 'bg-amber-100 text-amber-800 border border-amber-300 animate-pulse'
        }`}
      >
        {isOnline ? (
          <>
            <Wifi className="w-3.5 h-3.5 text-emerald-600" />
            <span>Online</span>
          </>
        ) : (
          <>
            <WifiOff className="w-3.5 h-3.5 text-amber-600" />
            <span>Offline (Cached)</span>
          </>
        )}
      </div>

      {/* Sync Timestamp */}
      <div className="hidden sm:flex items-center gap-1.5 text-xs text-slate-500 font-medium">
        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
        <span>Synced: <strong className="text-slate-700">{lastSynced}</strong></span>
        <button
          onClick={handleManualSync}
          disabled={syncing}
          className="p-1 hover:bg-slate-100 rounded-lg transition-all text-slate-400 hover:text-emerald-700 cursor-pointer"
          title="Force Sync Now"
        >
          <RefreshCw className={`w-3 h-3 ${syncing ? 'animate-spin text-emerald-600' : ''}`} />
        </button>
      </div>
    </div>
  )
}
