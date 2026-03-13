'use client'

import { useState, useEffect } from 'react'
import type { TcoResult } from '@/types'
import { useListings } from '@/hooks/useListings'
import { useStats } from '@/hooks/useStats'
import { fetchTco } from '@/api'
import TcoForm from './TcoForm'
import TcoBreakdown from './TcoBreakdown'
import ModelComparison from './ModelComparison'

const DEFAULT_INPUT = {
  make: 'Toyota',
  model: 'Corolla',
  year: 2016,
  km: 100000,
  price: 12500,
  years: 5,
}

export default function TcoTab() {
  const { listings } = useListings({ max_price: 15000, max_km: 200000, models: [], seller_type: 'all' })
  const { stats } = useStats()

  const [input, setInput] = useState(DEFAULT_INPUT)
  const [tco, setTco] = useState<TcoResult | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    fetchTco(input)
      .then(result => { if (!cancelled) setTco(result) })
      .catch(() => {})
      .finally(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [input])

  return (
    <div>
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-slate-900">Coût total de possession (TCO)</h2>
        <p className="text-sm text-slate-500 mt-1">
          Estimation achat + entretiens + réparations − revente sur N années
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 mb-8">
        {/* Formulaire */}
        <TcoForm listings={listings} value={input} onChange={setInput} />

        {/* Résultats */}
        <div>
          {loading && (
            <div className="flex items-center justify-center h-48 text-slate-400">
              <svg className="animate-spin w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
              </svg>
              Calcul en cours…
            </div>
          )}
          {!loading && tco && (
            <TcoBreakdown tco={tco} years={input.years} />
          )}
        </div>
      </div>

      {/* Comparaison 4 modèles */}
      <div>
        <h3 className="text-base font-semibold text-slate-900 mb-3">
          Comparaison modèles — {input.years} an{input.years > 1 ? 's' : ''} (prix médian marché)
        </h3>
        <ModelComparison stats={stats} years={input.years} />
      </div>
    </div>
  )
}
