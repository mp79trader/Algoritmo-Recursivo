import React, { Suspense } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import './index.css'

import { LoadingSpinner } from './components/common/LoadingSpinner'
import { Layout } from './components/layout/Layout'
import { Home } from './pages/Home'
// import { Dashboard } from './pages/Dashboard'
import { Analysis } from './pages/Analysis'
import { LiveTrading } from './pages/LiveTrading'
// import { Compare } from './pages/Compare'
import { Documentation } from './pages/Documentation'
// import { History } from './pages/History'
import { Settings } from './pages/Settings'

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Suspense fallback={<LoadingSpinner />}>
          <Routes>
            <Route path="/" element={<Home />} />
            {/* <Route path="/dashboard" element={<Dashboard />} /> */}
            <Route path="/analysis/:symbol" element={<Analysis />} />
            <Route path="/live/:symbol" element={<LiveTrading />} />
            {/* <Route path="/compare" element={<Compare />} /> */}
            <Route path="/documentation" element={<Documentation />} />
            {/* <Route path="/history" element={<History />} /> */}
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </Suspense>
      </Layout>
    </BrowserRouter>
  )
}

export default App