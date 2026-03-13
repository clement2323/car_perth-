'use client'

import { useState, useEffect } from 'react'
import type { Listing, Filters } from '@/types'
import { fetchListings } from '@/api'
import { useDebounce } from './useDebounce'

export function useListings(filters: Filters) {
  const [listings, setListings] = useState<Listing[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Sérialiser les filtres pour la comparaison dans useEffect
  const debouncedFilters = useDebounce(filters, 400)
  const filtersKey = JSON.stringify(debouncedFilters)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    fetchListings(debouncedFilters)
      .then(data => { if (!cancelled) { setListings(data); setError(null) } })
      .catch(e => { if (!cancelled) setError(e.message) })
      .finally(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filtersKey])

  return { listings, loading, error }
}
