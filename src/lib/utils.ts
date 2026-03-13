import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatPrice(price: number): string {
  return new Intl.NumberFormat('en-AU', {
    style: 'currency',
    currency: 'AUD',
    maximumFractionDigits: 0,
  }).format(price)
}

export function formatKm(km: number): string {
  return new Intl.NumberFormat('en-AU').format(km) + ' km'
}

/** Couleur hex selon le score (0-100) */
export function getScoreColor(score: number): string {
  if (score >= 75) return '#10b981' // emerald-500
  if (score >= 55) return '#22c55e' // green-500
  if (score >= 40) return '#f59e0b' // amber-500
  return '#ef4444'                   // red-500
}

/** Classes Tailwind badge (bg + text) selon le score */
export function getScoreBadgeClass(score: number): string {
  if (score >= 75) return 'bg-emerald-100 text-emerald-700 border-emerald-200'
  if (score >= 55) return 'bg-green-100 text-green-700 border-green-200'
  if (score >= 40) return 'bg-amber-100 text-amber-700 border-amber-200'
  return 'bg-red-100 text-red-700 border-red-200'
}

/** Couleur de la bordure gauche des cards selon le score */
export function getScoreBorderColor(score: number): string {
  if (score >= 75) return '#10b981'
  if (score >= 55) return '#22c55e'
  if (score >= 40) return '#f59e0b'
  return '#ef4444'
}

/** Classes Tailwind pour les badges de sévérité d'alerte */
export function getSeverityClass(severity: string): string {
  switch (severity) {
    case 'critical': return 'bg-red-100 text-red-700 border-red-200'
    case 'high':     return 'bg-orange-100 text-orange-700 border-orange-200'
    case 'medium':   return 'bg-amber-100 text-amber-700 border-amber-200'
    case 'low':      return 'bg-slate-100 text-slate-600 border-slate-200'
    case 'bonus':    return 'bg-emerald-100 text-emerald-700 border-emerald-200'
    default:         return 'bg-slate-100 text-slate-600 border-slate-200'
  }
}
