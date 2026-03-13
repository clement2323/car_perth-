'use client'

import * as Slider from '@radix-ui/react-slider'
import * as Checkbox from '@radix-ui/react-checkbox'
import type { Filters, TabId } from '@/types'
import { formatPrice, formatKm } from '@/lib/utils'
import { triggerRefresh } from '@/api'
import { useState } from 'react'

const NAV_ITEMS: { id: TabId; label: string; icon: string }[] = [
  { id: 'deals',   label: 'Meilleures affaires', icon: '⭐' },
  { id: 'market',  label: 'Analyse marché',       icon: '📊' },
  { id: 'capital', label: 'Capital Motors',        icon: '🏪' },
  { id: 'tco',     label: 'Coût total (TCO)',      icon: '💰' },
]

const ALL_MODELS = [
  'Toyota Corolla',
  'Mazda 3',
  'Honda Civic',
  'Hyundai i30',
  'Honda Jazz',
  'Suzuki Swift',
]

interface Props {
  activeTab: TabId
  onTabChange: (tab: TabId) => void
  filters: Filters
  onFiltersChange: (f: Filters) => void
}

export default function Sidebar({ activeTab, onTabChange, filters, onFiltersChange }: Props) {
  const [refreshing, setRefreshing] = useState(false)
  const [toast, setToast] = useState('')

  function toggleModel(model: string) {
    const next = filters.models.includes(model)
      ? filters.models.filter(m => m !== model)
      : [...filters.models, model]
    onFiltersChange({ ...filters, models: next })
  }

  async function handleRefresh() {
    setRefreshing(true)
    try {
      const res = await triggerRefresh()
      setToast(res.message)
      setTimeout(() => setToast(''), 4000)
    } catch {
      setToast('Erreur lors de l\'actualisation')
      setTimeout(() => setToast(''), 3000)
    } finally {
      setRefreshing(false)
    }
  }

  return (
    <aside className="flex flex-col h-screen w-60 bg-slate-900 text-slate-100 shrink-0">
      {/* Logo */}
      <div className="px-5 py-5 border-b border-slate-700">
        <p className="text-sm font-semibold text-slate-300 uppercase tracking-widest">Perth WA</p>
        <h1 className="text-lg font-bold text-white leading-tight">Achat Voiture</h1>
      </div>

      {/* Navigation */}
      <nav className="px-3 py-4 border-b border-slate-700 space-y-0.5">
        {NAV_ITEMS.map(item => (
          <button
            key={item.id}
            onClick={() => onTabChange(item.id)}
            className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors
              ${activeTab === item.id
                ? 'bg-indigo-600 text-white'
                : 'text-slate-400 hover:bg-slate-800 hover:text-slate-100'
              }`}
          >
            <span className="text-base">{item.icon}</span>
            {item.label}
          </button>
        ))}
      </nav>

      {/* Filtres */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-5">
        <p className="text-xs font-semibold text-slate-500 uppercase tracking-widest">Filtres</p>

        {/* Prix max */}
        <div className="space-y-2">
          <div className="flex justify-between">
            <label className="text-xs font-medium text-slate-300">Prix max</label>
            <span className="text-xs text-indigo-400 font-medium">{formatPrice(filters.max_price)}</span>
          </div>
          <Slider.Root
            className="relative flex items-center select-none touch-none w-full h-5"
            value={[filters.max_price]}
            min={5000} max={15000} step={500}
            onValueChange={([v]) => onFiltersChange({ ...filters, max_price: v })}
          >
            <Slider.Track className="bg-slate-700 relative grow rounded-full h-1.5">
              <Slider.Range className="absolute bg-indigo-500 rounded-full h-full" />
            </Slider.Track>
            <Slider.Thumb className="block w-4 h-4 bg-white rounded-full shadow border-2 border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-400" />
          </Slider.Root>
          <div className="flex justify-between text-xs text-slate-600">
            <span>$5 000</span><span>$15 000</span>
          </div>
        </div>

        {/* KM max */}
        <div className="space-y-2">
          <div className="flex justify-between">
            <label className="text-xs font-medium text-slate-300">KM max</label>
            <span className="text-xs text-indigo-400 font-medium">{formatKm(filters.max_km)}</span>
          </div>
          <Slider.Root
            className="relative flex items-center select-none touch-none w-full h-5"
            value={[filters.max_km]}
            min={30000} max={200000} step={5000}
            onValueChange={([v]) => onFiltersChange({ ...filters, max_km: v })}
          >
            <Slider.Track className="bg-slate-700 relative grow rounded-full h-1.5">
              <Slider.Range className="absolute bg-indigo-500 rounded-full h-full" />
            </Slider.Track>
            <Slider.Thumb className="block w-4 h-4 bg-white rounded-full shadow border-2 border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-400" />
          </Slider.Root>
          <div className="flex justify-between text-xs text-slate-600">
            <span>30 k</span><span>200 k</span>
          </div>
        </div>

        {/* Modèles */}
        <div className="space-y-2">
          <label className="text-xs font-medium text-slate-300">Modèles</label>
          <div className="space-y-1.5">
            {ALL_MODELS.map(model => (
              <label key={model} className="flex items-center gap-2.5 cursor-pointer group">
                <Checkbox.Root
                  className="flex h-4 w-4 shrink-0 items-center justify-center rounded border border-slate-600 bg-slate-800 data-[state=checked]:bg-indigo-600 data-[state=checked]:border-indigo-500 focus:outline-none"
                  checked={filters.models.includes(model)}
                  onCheckedChange={() => toggleModel(model)}
                >
                  <Checkbox.Indicator>
                    <svg viewBox="0 0 12 12" fill="none" className="w-3 h-3 text-white" stroke="currentColor" strokeWidth={2}>
                      <path d="M2 6l3 3 5-5" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  </Checkbox.Indicator>
                </Checkbox.Root>
                <span className="text-xs text-slate-400 group-hover:text-slate-200 transition-colors">{model}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Type vendeur */}
        <div className="space-y-1.5">
          <label className="text-xs font-medium text-slate-300">Vendeur</label>
          {(['all', 'dealer', 'private'] as const).map(type => (
            <label key={type} className="flex items-center gap-2.5 cursor-pointer">
              <input
                type="radio"
                name="seller_type"
                value={type}
                checked={filters.seller_type === type}
                onChange={() => onFiltersChange({ ...filters, seller_type: type })}
                className="accent-indigo-500"
              />
              <span className="text-xs text-slate-400 capitalize">
                {type === 'all' ? 'Tous' : type === 'dealer' ? 'Concessionnaire' : 'Particulier'}
              </span>
            </label>
          ))}
        </div>

        {/* Reset */}
        <button
          onClick={() => onFiltersChange({ max_price: 15000, max_km: 200000, models: [], seller_type: 'all' })}
          className="w-full text-xs text-slate-500 hover:text-slate-300 transition-colors py-1"
        >
          Réinitialiser les filtres
        </button>
      </div>

      {/* Refresh */}
      <div className="px-4 py-4 border-t border-slate-700">
        {toast && (
          <p className="text-xs text-emerald-400 mb-2 leading-tight">{toast}</p>
        )}
        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-lg
            bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm font-medium
            transition-colors disabled:opacity-50"
        >
          <svg
            className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`}
            fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}
          >
            <path strokeLinecap="round" strokeLinejoin="round"
              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          {refreshing ? 'Actualisation…' : 'Actualiser'}
        </button>
      </div>
    </aside>
  )
}
