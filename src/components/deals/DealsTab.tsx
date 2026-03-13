'use client'

import type { Filters } from '@/types'
import { useListings } from '@/hooks/useListings'
import ListingCard from './ListingCard'
import StatCard from '@/components/ui/StatCard'
import { formatPrice } from '@/lib/utils'

interface Props {
  filters: Filters
}

export default function DealsTab({ filters }: Props) {
  const { listings, loading, error } = useListings(filters)

  const avgScore = listings.length
    ? Math.round(listings.reduce((s, l) => s + l.score, 0) / listings.length)
    : 0
  const medianPrice = listings.length
    ? listings.map(l => l.price).sort((a, b) => a - b)[Math.floor(listings.length / 2)]
    : 0
  const excellent = listings.filter(l => l.score >= 75).length

  return (
    <div>
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-slate-900">Meilleures affaires</h2>
        <p className="text-sm text-slate-500 mt-1">
          Annonces scorées et classées par rapport qualité/prix
        </p>
      </div>

      {/* Stats */}
      {!loading && listings.length > 0 && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-6">
          <StatCard label="Annonces" value={listings.length} />
          <StatCard label="Score moyen" value={avgScore + '/100'} accent />
          <StatCard label="Prix médian" value={formatPrice(medianPrice)} />
          <StatCard label="Excellentes affaires" value={excellent} sub="score ≥ 75" />
        </div>
      )}

      {/* États */}
      {loading && (
        <div className="flex items-center justify-center h-48 text-slate-400">
          <svg className="animate-spin w-6 h-6 mr-2" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
          </svg>
          Chargement des annonces…
        </div>
      )}

      {error && (
        <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          Erreur : {error}
        </div>
      )}

      {!loading && !error && listings.length === 0 && (
        <div className="rounded-xl border border-slate-200 bg-white p-8 text-center text-slate-400">
          Aucune annonce ne correspond aux filtres sélectionnés.
        </div>
      )}

      {/* Liste des annonces */}
      {!loading && !error && (
        <div className="space-y-3">
          {listings.map((listing, i) => (
            <ListingCard key={`${listing.listing_url ?? i}-${i}`} listing={listing} />
          ))}
        </div>
      )}
    </div>
  )
}
