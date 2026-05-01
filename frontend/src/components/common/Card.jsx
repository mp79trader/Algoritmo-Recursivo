import React from 'react'

export function Card({ children, className = '', ...props }) {
  return (
    <div className={`glass-card p-6 ${className}`} {...props}>
      {children}
    </div>
  )
}

export function StatCard({ title, value, change, icon: Icon, className = '' }) {
  const isPositive = change >= 0

  return (
    <Card className={`${className}`}>
      <div className="flex items-center justify-between mb-4">
        {Icon && <Icon className="w-8 h-8 text-accent-gold" />}
        {change !== undefined && (
          <span className={`text-sm font-medium ${isPositive ? 'text-success' : 'text-error'}`}>
            {isPositive ? '+' : ''}{change}%
          </span>
        )}
      </div>
      <h3 className="text-text-secondary text-sm font-medium mb-2">{title}</h3>
      <p className="stat-value">{value}</p>
    </Card>
  )
}

export function InfoCard({ title, items, icon: Icon }) {
  return (
    <Card>
      <div className="flex items-center gap-3 mb-6">
        {Icon && <Icon className="w-6 h-6 text-accent-gold" />}
        <h3 className="text-lg font-semibold">{title}</h3>
      </div>
      <div className="space-y-3">
        {items.map((item, index) => (
          <div key={index} className="flex justify-between items-center py-2 border-b border-white/10 last:border-0">
            <span className="text-text-secondary">{item.label}</span>
            <span className="font-medium">{item.value}</span>
          </div>
        ))}
      </div>
    </Card>
  )
}