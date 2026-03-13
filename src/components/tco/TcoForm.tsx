'use client'

import { useState } from 'react'
import type { Listing } from '@/types'
import { formatPrice, formatKm } from '@/lib/utils'

interface TcoInput {
  make: string
  model: string
  year: number
  km: number
  price: number
  years: number
}

interface Props {
  listings: Listing[]
  value: TcoInput
  onChange: (v: TcoInput) => void
}

const MODELS = ['Toyota Corolla', 'Mazda 3', 'Honda Civic', 'Hyundai i30', 'Honda Jazz', 'Suzuki Swift']

export default function TcoForm({ listings, value, onChange }: Props) {
  const [mode, setMode] = useState<'listing' | 'manual'>('listing')

  function fromListing(l: Listing) {
    onChange({
      make: l.make,
      model: l.model,
      year: l.year,
      km: l.km,
      price: l.price,
      years: value.years,
    })
  }

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5 space-y-4">
      <h3 className="text-sm font-semibold text-slate-700">Véhicule à analyser</h3>

      {/* Mode toggle */}
      <div className="flex gap-2">
        {(['listing', 'manual'] as const).map(m => (
          <button
            key={m}
            onClick={() => setMode(m)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors
              ${mode === m ? 'bg-indigo-600 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'}`}
          >
            {m === 'listing' ? 'Depuis une annonce' : 'Saisie manuelle'}
          </button>
        ))}
      </div>

      {mode === 'listing' ? (
        <div className="space-y-2">
          <p className="text-xs text-slate-500">Sélectionner une annonce chargée :</p>
          <div className="max-h-48 overflow-y-auto space-y-1.5 pr-1">
            {listings.length === 0 && (
              <p className="text-xs text-slate-400">Aucune annonce chargée — allez d&apos;abord dans &quot;Meilleures affaires&quot;</p>
            )}
            {listings.map((l, i) => (
              <button
                key={i}
                onClick={() => fromListing(l)}
                className={`w-full text-left px-3 py-2 rounded-lg border text-xs transition-colors
                  ${value.make === l.make && value.model === l.model && value.price === l.price
                    ? 'border-indigo-300 bg-indigo-50 text-indigo-900'
                    : 'border-slate-200 hover:bg-slate-50 text-slate-700'}`}
              >
                <span className="font-medium">{l.year} {l.make} {l.model}</span>
                <span className="text-slate-400"> · {formatKm(l.km)} · {formatPrice(l.price)}</span>
              </button>
            ))}
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-xs font-medium text-slate-600 block mb-1">Modèle</label>
            <select
              value={`${value.make} ${value.model}`}
              onChange={e => {
                const [make, ...rest] = e.target.value.split(' ')
                onChange({ ...value, make, model: rest.join(' ') })
              }}
              className="w-full text-xs border border-slate-200 rounded-lg px-2 py-1.5 bg-white text-slate-900 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            >
              {MODELS.map(m => <option key={m} value={m}>{m}</option>)}
            </select>
          </div>
          <div>
            <label className="text-xs font-medium text-slate-600 block mb-1">Année</label>
            <input
              type="number"
              value={value.year}
              min={2010} max={2024}
              onChange={e => onChange({ ...value, year: +e.target.value })}
              className="w-full text-xs border border-slate-200 rounded-lg px-2 py-1.5 bg-white text-slate-900 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>
          <div>
            <label className="text-xs font-medium text-slate-600 block mb-1">Kilométrage</label>
            <input
              type="number"
              value={value.km}
              min={0} max={300000} step={5000}
              onChange={e => onChange({ ...value, km: +e.target.value })}
              className="w-full text-xs border border-slate-200 rounded-lg px-2 py-1.5 bg-white text-slate-900 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>
          <div>
            <label className="text-xs font-medium text-slate-600 block mb-1">Prix (AUD)</label>
            <input
              type="number"
              value={value.price}
              min={1000} max={50000} step={500}
              onChange={e => onChange({ ...value, price: +e.target.value })}
              className="w-full text-xs border border-slate-200 rounded-lg px-2 py-1.5 bg-white text-slate-900 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>
        </div>
      )}

      {/* Horizon */}
      <div>
        <div className="flex justify-between mb-1">
          <label className="text-xs font-medium text-slate-600">Horizon de possession</label>
          <span className="text-xs font-medium text-indigo-600">{value.years} an{value.years > 1 ? 's' : ''}</span>
        </div>
        <input
          type="range"
          min={1} max={10} step={1}
          value={value.years}
          onChange={e => onChange({ ...value, years: +e.target.value })}
          className="w-full accent-indigo-600"
        />
        <div className="flex justify-between text-xs text-slate-400 mt-0.5">
          <span>1 an</span><span>10 ans</span>
        </div>
      </div>
    </div>
  )
}
