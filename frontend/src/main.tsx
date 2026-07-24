import React, { lazy, Suspense } from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import Layout from './components/Layout'
import './index.css'

// Dynamic Route Imports for Code-Splitting
const Dashboard = lazy(() => import('./pages/Dashboard'))
const AdvisoryPage = lazy(() => import('./pages/Advisory'))
const MarketPage = lazy(() => import('./pages/Market'))
const LivestockPage = lazy(() => import('./pages/Livestock'))
const HealthPage = lazy(() => import('./pages/Health'))
const SchemesPage = lazy(() => import('./pages/Schemes'))
const SettingsPage = lazy(() => import('./pages/Settings'))
const Login = lazy(() => import('./pages/Login'))
const Signup = lazy(() => import('./pages/Signup'))

const PageLoader = () => (
  <div className="flex flex-col items-center justify-center min-h-[60vh] gap-3">
    <div className="w-10 h-10 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
    <p className="text-slate-400 text-sm animate-pulse">Loading AgriNova module...</p>
  </div>
)

import { openDB } from 'idb'

// IndexedDB Storage Manager for Query Caching
const dbPromise = openDB('agrinova-query-db', 1, {
  upgrade(db) {
    if (!db.objectStoreNames.contains('queries')) {
      db.createObjectStore('queries')
    }
  },
})

export const idbPersister = {
  getItem: async (key: string) => {
    try {
      const db = await dbPromise
      return (await db.get('queries', key)) || null
    } catch {
      return null
    }
  },
  setItem: async (key: string, value: string) => {
    try {
      const db = await dbPromise
      await db.put('queries', value, key)
    } catch {}
  },
  removeItem: async (key: string) => {
    try {
      const db = await dbPromise
      await db.delete('queries', key)
    } catch {}
  },
}

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2,
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 10000),
      refetchOnWindowFocus: false,
      staleTime: 1000 * 60 * 10, // 10 minutes fresh cache
      gcTime: 1000 * 60 * 60 * 24, // 24 hours persistence
      networkMode: 'offlineFirst',
    },
  },
})

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Layout>
          <Suspense fallback={<PageLoader />}>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/advisory" element={<AdvisoryPage />} />
              <Route path="/market" element={<MarketPage />} />
              <Route path="/livestock" element={<LivestockPage />} />
              <Route path="/health" element={<HealthPage />} />
              <Route path="/schemes" element={<SchemesPage />} />
              <Route path="/settings" element={<SettingsPage />} />
              <Route path="/login" element={<Login />} />
              <Route path="/signup" element={<Signup />} />
            </Routes>
          </Suspense>
        </Layout>
      </BrowserRouter>
    </QueryClientProvider>
  </React.StrictMode>
)

