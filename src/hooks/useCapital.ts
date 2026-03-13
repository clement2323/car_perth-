'use client'

import { useState, useEffect } from 'react'
import type { CapitalListing } from '@/types'
import { fetchCapital } from '@/api'

export function useCapital() {
  const [listings, setListings] = useState<CapitalListing[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchCapital()
      .then(data => { setListings(data); setError(null) })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  return { listings, loading, error }
}
