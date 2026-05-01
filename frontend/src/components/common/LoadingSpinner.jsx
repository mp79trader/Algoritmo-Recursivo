import React from 'react'

export function LoadingSpinner() {
  return (
    <div className="loading-container">
      <div className="loader-logo">
        <div className="loader-circle">
          <svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="50" cy="50" r="40" stroke="#fbbf24" strokeWidth="2" />
            <path
              d="M50 10 L50 20 M50 80 L50 90 M10 50 L20 50 M80 50 L90 50 M22 22 L29 29 M71 71 L78 78 M22 78 L29 71 M71 29 L78 22"
              stroke="#fbbf24"
              strokeWidth="2"
              strokeLinecap="round"
            />
          </svg>
        </div>
      </div>
      <p className="text-xl font-semibold text-accent-gold mt-6 animate-pulse">
        Loading...
      </p>
    </div>
  )
}

export default LoadingSpinner