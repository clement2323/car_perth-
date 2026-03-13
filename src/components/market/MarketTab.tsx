'use client'

import type { Filters } from '@/types'
import { useListings } from '@/hooks/useListings'
import { useStats } from '@/hooks/useStats'
import ScatterChart from './ScatterChart'
import StatCard from '@/components/ui/StatCard'
import { formatPrice, formatKm } from '@/lib/utils'

interface Props {
  filters: Filters
}

export default function MarketTab({ filters }: Props) {
  const { listings, loading: listLoading } = useListings(filters)
  const { stats, loading: statsLoading } = useStats()

  const loading = listLoading || statsLoading

  return (
    <div>
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-slate-900">Analyse du marché</h2>
        <p className="text-sm text-slate-500 mt-1">Prix vs kilométrage par modèle — Perth WA</p>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-48 text-slate-400">
          <svg className="animate-spin w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
          </svg>
          Chargement…
        </div>
      ) : (
        <>
          {/* Scatter plot */}
          <div className="bg-white rounded-xl border border-slate-200 p-5 mb-6">
            <h3 className="text-sm font-semibold text-slate-700 mb-4">Prix vs Kilométrage</h3>
            <ScatterChart listings={listings} />
          </div>

          {/* Stats par modèle */}
          <h3 className="text-sm font-semibold text-slate-700 mb-3">Résumé par modèle</h3>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
            {stats.map(stat => (
              <div key={`${stat.make}-${stat.model}`}
                className="bg-white rounded-xl border border-slate-200 p-4">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h4 className="font-semibold text-slate-900">{stat.make} {stat.model}</h4>
                    <p className="text-xs text-slate-500">{stat.count} annonce{stat.count > 1 ? 's' : ''}</p>
                  </div>
                  {stat.avg_score && (
                    <span className="text-sm font-medium text-indigo-600">
                      Score moy. {stat.avg_score}
                    </span>
                  )}
                </div>
                <div className="grid grid-cols-3 gap-2">
                  <StatCard label="Médiane" value={formatPrice(stat.median_price)} />
                  <StatCard label="Min" value={formatPrice(stat.min_price)} />
                  <StatCard label="KM médian" value={formatKm(stat.median_km)} />
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  )
}
