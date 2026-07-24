import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface AppStore {
  phone: string
  setPhone: (p: string) => void
  language: string
  setLanguage: (l: string) => void
  isOnline: boolean
  setIsOnline: (v: boolean) => void
  theme: 'dark'
}

export const useAppStore = create<AppStore>()(
  persist(
    (set) => ({
      phone: '',
      setPhone: (p) => { set({ phone: p }); localStorage.setItem('agrinova_phone', p) },
      language: 'English',
      setLanguage: (l) => { set({ language: l }); localStorage.setItem('agrinova_lang', l) },
      isOnline: navigator.onLine,
      setIsOnline: (v) => set({ isOnline: v }),
      theme: 'dark',
    }),
    { name: 'agrinova-app' }
  )
)
