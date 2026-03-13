'use client'

import { useCapital } from '@/hooks/useCapital'
import CapitalBarChart from './CapitalBarChart'
import DiffBadge from './DiffBadge'
import StatCard from '@/components/ui/StatCard'
import { formatPrice, formatKm } from '@/lib/utils'

export default function CapitalTab() {
  const { listings, loading, error } = useCapital()

  const goodDeals  = listings.filter(l => (l.diff_pct ?? 0) <= -10).length
  const overpriced = listings.filter(l => (l.diff_pct ?? 0) >= 10).length
  const withDiff   = listings.filter(l => l.diff_pct !== null)
  const avgDiff    = withDiff.length
    ? withDiff.reduce((s, l) => s + (l.diff_pct ?? 0), 0) / withDiff.length
    : null

  return (
    <div>
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-slate-900">Capital Motors WA</h2>
        <p className="text-sm text-slate-500 mt-1">
          Inventaire du dealer vs médiane marché carsales.com.au
        </p>
      </div>

      {loading && (
        <div className="flex items-center justify-center h-48 text-slate-400">
          <svg className="animate-spin w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
          </svg>
          Chargement…
        </div>
      )}

      {error && (
        <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          Erreur : {error}
        </div>
      )}

      {!loading && !error && (
        <>
          {/* Stats */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-6">
            <StatCard label="Véhicules" value={listings.length} />
            <StatCard label="Bonnes affaires" value={goodDeals} sub="≤ -10% vs marché" accent />
            <StatCard label="Sur-évalués" value={overpriced} sub="≥ +10% vs marché" />
            {avgDiff !== null && (
              <StatCard
                label="Écart moyen"
                value={`${avgDiff > 0 ? '+' : ''}${avgDiff.toFixed(1)}%`}
              />
            )}
          </div>

          {/* Graphique */}
          <div className="bg-white rounded-xl border border-slate-200 p-5 mb-6">
            <h3 className="text-sm font-semibold text-slate-700 mb-1">
              Écart prix Capital Motors vs marché
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              Vert = sous le marché · Amber = dans la norme · Rouge = au-dessus
            </p>
            <CapitalBarChart listings={listings} />
          </div>

          {/* Tableau */}
          <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-100 bg-slate-50">
                  <th className="text-left px-4 py-3 text-xs font-medium text-slate-500 uppercase tracking-wide">Véhicule</th>
                  <th className="text-right px-4 py-3 text-xs font-medium text-slate-500 uppercase tracking-wide">KM</th>
                  <th className="text-right px-4 py-3 text-xs font-medium text-slate-500 uppercase tracking-wide">Prix</th>
                  <th className="text-right px-4 py-3 text-xs font-medium text-slate-500 uppercase tracking-wide">Médiane</th>
                  <th className="text-right px-4 py-3 text-xs font-medium text-slate-500 uppercase tracking-wide">Écart</th>
                  <th className="px-4 py-3"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {listings.map((l, i) => (
                  <tr key={i} className="hover:bg-slate-50 transition-colors">
                    <td className="px-4 py-3 font-medium text-slate-900">
                      {l.year} {l.make} {l.model}
                    </td>
                    <td className="px-4 py-3 text-right text-slate-600">
                      {l.km ? formatKm(l.km) : '—'}
                    </td>
                    <td className="px-4 py-3 text-right font-semibold text-slate-900">
                      {formatPrice(l.price)}
                      {l.is_estimated && (
                        <span title="Prix estimé" className="ml-1 text-xs font-normal text-amber-500">~estimé</span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-right text-slate-500">
                      {l.market_median ? formatPrice(l.market_median) : '—'}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <DiffBadge diff={l.diff_pct ?? null} />
                    </td>
                    <td className="px-4 py-3">
                      {l.listing_url && (
                        <a href={l.listing_url} target="_blank" rel="noopener noreferrer"
                          className="text-xs text-indigo-600 hover:underline">↗</a>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  )
}
