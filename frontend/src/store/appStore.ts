import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export type UserProfile = {
  phone: string
  name: string
  state: string
  district: string
  language: string
  land_holding_acres: number
  soil_type: string
  primary_crops: string[]
  role?: string
  created_at?: string
}

interface AppStore {
  phone: string
  setPhone: (p: string) => void
  language: string
  setLanguage: (l: string) => void
  user: UserProfile | null
  token: string | null
  isAuthenticated: boolean
  login: (user: UserProfile, token: string) => void
  logout: () => void
  updateUserProfile: (profile: Partial<UserProfile>) => void
  isOnline: boolean
  setIsOnline: (v: boolean) => void
  theme: 'dark'
}

export const useAppStore = create<AppStore>()(
  persist(
    (set) => ({
      phone: '9099314955',
      setPhone: (p) => { set({ phone: p }); localStorage.setItem('agrinova_phone', p) },
      language: 'English',
      setLanguage: (l) => { set({ language: l }); localStorage.setItem('agrinova_lang', l) },
      user: {
        phone: '9099314955',
        name: 'Ramesh Patel',
        state: 'Gujarat',
        district: 'Anand',
        language: 'English',
        land_holding_acres: 3.5,
        soil_type: 'black_cotton',
        primary_crops: ['cotton', 'wheat', 'groundnut'],
        role: 'farmer'
      },
      token: 'agritech_token_9099314955_demo',
      isAuthenticated: true,
      login: (user, token) => set({
        user,
        token,
        phone: user.phone,
        language: user.language || 'English',
        isAuthenticated: true
      }),
      logout: () => set({
        user: null,
        token: null,
        isAuthenticated: false
      }),
      updateUserProfile: (updatedFields) => set((state) => ({
        user: state.user ? { ...state.user, ...updatedFields } : null
      })),
      isOnline: navigator.onLine,
      setIsOnline: (v) => set({ isOnline: v }),
      theme: 'dark',
    }),
    { name: 'agrinova-app' }
  )
)
