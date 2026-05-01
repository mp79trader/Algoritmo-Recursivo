import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Home, TrendingUp, BarChart2, FileText, History, Settings, Menu, X, ChevronLeft, ChevronRight, Activity } from 'lucide-react'
import { useState } from 'react'
import { Button } from '../common/Button'

export function Sidebar({ isOpen, setIsOpen, isDesktopCollapsed, setIsDesktopCollapsed }) {
  const location = useLocation()

  const navigation = [
    { name: 'Inicio', href: '/', icon: Home },
    { name: 'Análisis (MNQ=F)', href: '/analysis/MNQ=F', icon: BarChart2 },
    { name: 'Trading en Vivo', href: '/live/MNQ=F', icon: Activity },
    { name: 'Documentación', href: '/documentation', icon: FileText },
    { name: 'Configuración', href: '/settings', icon: Settings },
  ]

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 md:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside className={`
        sidebar fixed left-0 top-0 h-full z-50 transition-all duration-300 
        ${isOpen ? 'translate-x-0' : '-translate-x-full'} 
        md:translate-x-0
        ${isDesktopCollapsed ? 'w-20' : 'w-64'}
      `}>
        <div className="p-4 flex flex-col h-full">
          <div className={`flex items-center ${isDesktopCollapsed ? 'justify-center' : 'justify-between'} mb-8`}>
            {!isDesktopCollapsed && (
              <Link to="/" className="flex items-center gap-3">
                <div className="w-16 h-16 flex items-center justify-center">
                  <img src="/assets/llama2.png" alt="QuantumFFT" className="w-full h-full object-contain" />
                </div>
                <span className="text-xl font-bold text-accent-gold truncate">QuantuM FFT</span>
              </Link>
            )}
            {isDesktopCollapsed && (
              <Link to="/" className="flex items-center justify-center">
                 <div className="w-12 h-12 flex items-center justify-center">
                  <img src="/assets/llama2.png" alt="QuantumFFT" className="w-full h-full object-contain" />
                </div>
              </Link>
            )}
            <button 
              className="md:hidden text-text-secondary hover:text-accent-gold"
              onClick={() => setIsOpen(false)}
            >
              <X size={24} />
            </button>
          </div>

          <nav className="space-y-2 flex-1 overflow-hidden">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href || location.pathname.startsWith(item.href + '/')
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`
                    sidebar-link flex items-center 
                    ${isDesktopCollapsed ? 'justify-center px-2' : 'px-4'} 
                    py-3 rounded-lg transition-colors
                    ${isActive ? 'bg-accent-gold/10 text-accent-gold' : 'text-text-secondary hover:bg-white/5 hover:text-white'}
                  `}
                  title={isDesktopCollapsed ? item.name : ''}
                  onClick={() => setIsOpen(false)}
                >
                  <item.icon size={24} className={`flex-shrink-0 ${isDesktopCollapsed ? '' : 'mr-3'}`} />
                  <span className={`whitespace-nowrap transition-opacity duration-300 ${isDesktopCollapsed ? 'opacity-0 w-0' : 'opacity-100'}`}>
                    {item.name}
                  </span>
                </Link>
              )
            })}
          </nav>
          
          <div className="hidden md:flex justify-end pt-4 border-t border-white/10 mt-auto">
            <button
              onClick={() => setIsDesktopCollapsed(!isDesktopCollapsed)}
              className="p-2 text-text-secondary hover:text-accent-gold transition-colors w-full flex justify-center"
            >
              {isDesktopCollapsed ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
            </button>
          </div>
        </div>
      </aside>
    </>
  )
}

export function Header({ setIsOpen }) {
  return (
    <header className="z-30 backdrop-blur-md bg-primary-bg/80 border-b border-white/10">
      <div className="flex items-center justify-between px-6 py-4">
        <div className="flex items-center gap-4">
          <button 
            className="md:hidden text-text-secondary hover:text-accent-gold"
            onClick={() => setIsOpen(true)}
          >
            <Menu size={24} />
          </button>
          <div className="hidden md:flex items-center gap-2">
            <Link to="/" className="flex items-center gap-2">
              <span className="text-lg font-bold text-accent-gold">LlamaIA FFT V1.0.0</span>
            </Link>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <Link to="/">
            <Button variant="ghost">Inicio</Button>
          </Link>
          <Link to="/analysis/MNQ=F">
            <Button>Análisis</Button>
          </Link>
        </div>
      </div>
    </header>
  )
}

export function Footer() {
  return (
    <footer className="w-full py-4 px-6 border-t border-white/10 text-center text-sm text-text-secondary bg-primary-bg/95 backdrop-blur-sm">
      <div className="flex flex-col md:flex-row justify-between items-center gap-4 max-w-7xl mx-auto">
        
        {/* Punto&Coma */}
        <a href="https://www.youtube.com/@puntoicomatrading" target="_blank" rel="noopener noreferrer" className="flex items-center gap-3 hover:opacity-80 transition-opacity">
          <img src="/assets/LogoNew.png" alt="Punto&Coma" className="h-10 w-auto object-contain" />
          <div className="text-left">
            <div className="font-bold text-white text-xs">Punto&Coma Trading</div>
            <div className="text-[10px] text-accent-gold">@puntoicomatrading</div>
          </div>
        </a>

        {/* Links */}
        <div className="flex flex-col items-center gap-1">
          <div className="flex gap-6 text-xs">
            <a href="https://www.youtube.com/@puntoicomatrading" target="_blank" rel="noopener noreferrer" className="hover:text-accent-gold transition-colors">Sitio Web</a>
            <span className="text-white/20">|</span>
            <a href="https://www.nbmsystemas.com/" target="_blank" rel="noopener noreferrer" className="hover:text-accent-gold transition-colors">Canal Oficial</a>
          </div>
          <div className="text-[10px] text-white/40 mt-1">
            QuantuM FFT v1.0.0
          </div>
        </div>

        {/* NBM */}
        <a href="https://www.nbmsystemas.com/" target="_blank" rel="noopener noreferrer" className="flex items-center gap-3 hover:opacity-80 transition-opacity">
          <div className="text-right">
            <div className="font-bold text-white text-xs">NBM Sistemas</div>
            <div className="text-[10px] text-text-secondary">Desarrollo de Software</div>
          </div>
          <img src="/assets/logonbm.png" alt="NBM" className="h-10 w-auto object-contain" />
        </a>
      </div>
    </footer>
  )
}

export function Layout({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [isDesktopCollapsed, setIsDesktopCollapsed] = useState(false)

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar 
        isOpen={sidebarOpen} 
        setIsOpen={setSidebarOpen} 
        isDesktopCollapsed={isDesktopCollapsed}
        setIsDesktopCollapsed={setIsDesktopCollapsed}
      />
      
      <main className={`flex-1 flex flex-col h-full transition-all duration-300 ${isDesktopCollapsed ? 'md:ml-20' : 'md:ml-64'}`}>
        <Header setIsOpen={setSidebarOpen} />
        <div className="p-6 flex-1 overflow-y-auto">
          {children}
        </div>
        <Footer />
      </main>
    </div>
  )
}