import React from 'react'

export function Button({ children, onClick, variant = 'gold', disabled = false, className = '', ...props }) {
  const baseClasses = 'btn-gold'
  const variantClasses = {
    gold: 'btn-gold',
    outline: 'border-2 border-accent-gold text-accent-gold bg-transparent hover:bg-accent-gold hover:text-primary-bg',
    ghost: 'bg-transparent text-accent-gold hover:bg-accent-gold-light'
  }

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`${variantClasses[variant]} ${className} ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
      {...props}
    >
      {children}
    </button>
  )
}

export function Input({ label, type = 'text', value, onChange, placeholder, className = '', ...props }) {
  return (
    <div className="flex flex-col space-y-2">
      {label && <label className="text-sm font-medium text-text-secondary">{label}</label>}
      <input
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        className={`input-glass ${className}`}
        {...props}
      />
    </div>
  )
}

export function Select({ label, value, onChange, children, className = '', ...props }) {
  return (
    <div className="flex flex-col space-y-2">
      {label && <label className="text-sm font-medium text-text-secondary">{label}</label>}
      <select
        value={value}
        onChange={onChange}
        className={`input-glass ${className}`}
        {...props}
      >
        {children}
      </select>
    </div>
  )
}