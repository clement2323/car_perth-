'use client'

import { useState, useEffect } from 'react'
import type { ModelStat, TcoResult } from '@/types'
import { fetchTco } from '@/api'
import { formatPrice } from '@/lib/utils'

const COMPARE_MODELS = [
  { make: 'Toyota', model: 'Corolla' },
  { make: 'Mazda',  model: '3' },
  { make: 'Honda',  model: 'Civic' },
  { make: 'Hyundai', model: 'i30' },
]

interface Props {
  stats: ModelStat[]
  years: number
}

interface ModelTco {
  make: string
  model: string
  price: number
  tco: TcoResult | null
}

export default function ModelComparison({ stats, years }: Props) {
  const [results, setResults] = useState<ModelTco[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function compute() {
      setLoading(true)
      const computed = await Promise.all(
        COMPARE_MODELS.map(async ({ make, model }) => {
          const stat = stats.find(s => s.make === make && s.model === model)
          if (!stat) return { make, model, price: 0, tco: null }
          try {
            const tco = await fetchTco({
              make, model,
              year: 2016,
              km: Math.round(stat.median_km),
              price: stat.median_price,
              years,
            })
            return { make, model, price: stat.median_price, tco }
          } catch {
            return { make, model, price: stat.median_price, tco: null }
          }
        })
      )
      setResults(computed)
      setLoading(false)
    }
    if (stats.length > 0) compute()
  }, [stats, years])

  if (loading) return (
    <div className="flex items-center justify-center h-32 text-slate-400 text-sm">
      Calcul en cours…
    </div>
  )

  const best = results.reduce<ModelTco | null>((min, r) =>
    r.tco && (!min || !min.tco || r.tco.net_total_cost < min.tco.net_total_cost) ? r : min, null
  )

  return (
    <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
      {results.map(({ make, model, tco }) => {
        const isBest = best?.make === make && best?.model === model
        return (
          <div
            key={`${make}-${model}`}
            className={`rounded-xl border p-4 bg-white transition-shadow
              ${isBest ? 'border-emerald-300 ring-1 ring-emerald-300' : 'border-slate-200'}`}
          >
            <div className="flex items-start justify-between mb-3">
              <h4 className="text-sm font-semibold text-slate-900">{make} {model}</h4>
              {isBest && (
                <span className="text-xs bg-emerald-100 text-emerald-700 px-1.5 py-0.5 rounded-full font-medium">
                  Meilleur
                </span>
              )}
            </div>
            {tco ? (
              <div className="space-y-1.5 text-xs">
                <div className="flex justify-between">
                  <span className="text-slate-500">Achat</span>
                  <span className="font-medium text-slate-900">{formatPrice(tco.purchase_price)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Entretiens</span>
                  <span className="text-amber-600">{formatPrice(tco.total_service)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Réparations</span>
                  <span className="text-red-600">{formatPrice(tco.total_repairs)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Revente</span>
                  <span className="text-emerald-600">-{formatPrice(tco.resale_value)}</span>
                </div>
                <div className="border-t border-slate-100 pt-1.5 flex justify-between">
                  <span className="font-semibold text-slate-700">TCO net</span>
                  <span className="font-bold text-slate-900">{formatPrice(tco.net_total_cost)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Par an</span>
                  <span className="font-semibold text-indigo-600">{formatPrice(tco.annual_cost)}</span>
                </div>
              </div>
            ) : (
              <p className="text-xs text-slate-400">Données insuffisantes</p>
            )}
          </div>
        )
      })}
    </div>
  )
}
