import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import AdvisoryPage from './pages/Advisory'
import MarketPage from './pages/Market'
import LivestockPage from './pages/Livestock'
import HealthPage from './pages/Health'
import SchemesPage from './pages/Schemes'
import SettingsPage from './pages/Settings'
import Login from './pages/Login'
import Signup from './pages/Signup'
import './index.css'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Layout>
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
        </Layout>
      </BrowserRouter>
    </QueryClientProvider>
  </React.StrictMode>
)
