'use client'

import { useState } from 'react'
import type { Listing } from '@/types'
import ScoreRing from '@/components/ui/ScoreRing'
import { ScoreBadge } from '@/components/ui/Badge'
import AlertList from './AlertList'
import { formatPrice, formatKm, getScoreBorderColor } from '@/lib/utils'

interface Props {
  listing: Listing
}

export default function ListingCard({ listing }: Props) {
  const [expanded, setExpanded] = useState(false)
  const borderColor = getScoreBorderColor(listing.score)

  return (
    <div
      className="bg-white rounded-xl border border-slate-200 overflow-hidden transition-shadow hover:shadow-md"
      style={{ borderLeftWidth: 4, borderLeftColor: borderColor, borderLeftStyle: 'solid' }}
    >
      <div className="p-4">
        <div className="flex items-start gap-4">
          {/* Score ring */}
          <div className="flex flex-col items-center gap-1.5 shrink-0">
            <ScoreRing score={listing.score} size={64} />
            <ScoreBadge score={listing.score} label={listing.score_category} />
          </div>

          {/* Infos principales */}
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-slate-900 text-base leading-tight">
              {listing.year} {listing.make} {listing.model}
              {listing.badge ? <span className="text-slate-400 font-normal"> · {listing.badge}</span> : null}
            </h3>
            <div className="mt-1.5 flex flex-wrap gap-3 text-sm text-slate-600">
              <span className="font-semibold text-slate-900 text-base">
                {formatPrice(listing.price)}
                {listing.is_estimated && (
                  <span title="Prix estimé — données non scrapées en temps réel"
                    className="ml-1 text-xs font-normal text-amber-500 align-super">~estimé</span>
                )}
              </span>
              <span>{formatKm(listing.km)}</span>
              {listing.transmission && <span className="text-slate-400">{listing.transmission}</span>}
            </div>
            <div className="mt-1 flex flex-wrap gap-2 text-xs text-slate-500">
              {listing.dealer_name
                ? <span>🏪 {listing.dealer_name}</span>
                : <span>👤 Particulier</span>
              }
              {listing.location && <span>· {listing.location}</span>}
            </div>
            {/* Sous-scores */}
            <div className="mt-2 flex gap-3 text-xs">
              {[
                { label: 'Prix',      value: listing.prix_score },
                { label: 'KM',        value: listing.km_score },
                { label: 'Fiabilité', value: listing.fiabilite_score },
                { label: 'Année',     value: listing.annee_score },
              ].map(({ label, value }) => (
                <div key={label} className="text-center">
                  <p className="text-slate-400">{label}</p>
                  <p className="font-medium text-slate-700">{Math.round(value)}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Actions droite */}
          <div className="flex flex-col items-end gap-2 shrink-0">
            {listing.listing_url && (
              <a
                href={listing.listing_url}
                target="_blank"
                rel="noopener noreferrer"
                className="px-3 py-1.5 rounded-lg bg-indigo-600 text-white text-xs font-medium
                  hover:bg-indigo-700 transition-colors whitespace-nowrap"
              >
                Voir l&apos;annonce ↗
              </a>
            )}
            {listing.median_price && (
              <p className="text-xs text-slate-400">
                Médiane : {formatPrice(listing.median_price)}
              </p>
            )}
            {listing.alerts && listing.alerts.length > 0 && (
              <button
                onClick={() => setExpanded(v => !v)}
                className="text-xs text-slate-500 hover:text-slate-800 transition-colors flex items-center gap-1"
              >
                <span className={`text-amber-500 font-medium`}>{listing.alerts.length} alerte{listing.alerts.length > 1 ? 's' : ''}</span>
                <span>{expanded ? '▲' : '▼'}</span>
              </button>
            )}
          </div>
        </div>

        {/* Alertes (collapsible) */}
        {expanded && <AlertList alerts={listing.alerts} />}
      </div>
    </div>
  )
}
