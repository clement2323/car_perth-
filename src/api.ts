import type { Listing, CapitalListing, ModelStat, TcoResult, Filters } from './types'

async function get<T>(path: string): Promise<T> {
  const res = await fetch(path)
  if (!res.ok) throw new Error(`API ${path} → ${res.status}`)
  return res.json()
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) throw new Error(`API ${path} → ${res.status}`)
  return res.json()
}

export function buildListingsUrl(filters: Filters): string {
  const params = new URLSearchParams()
  if (filters.max_price < 15000) params.set('max_price', String(filters.max_price))
  if (filters.max_km < 200000) params.set('max_km', String(filters.max_km))
  if (filters.models.length > 0) params.set('models', filters.models.join(','))
  if (filters.seller_type !== 'all') params.set('seller_type', filters.seller_type)
  const qs = params.toString()
  return `/api/listings${qs ? `?${qs}` : ''}`
}

export const fetchListings = (filters: Filters) =>
  get<Listing[]>(buildListingsUrl(filters))

export const fetchCapital = () => get<CapitalListing[]>('/api/capital-motors')

export const fetchStats = () => get<ModelStat[]>('/api/stats')

export const fetchTco = (body: {
  make: string
  model: string
  year: number
  km: number
  price: number
  years: number
}) => post<TcoResult>('/api/tco', body)

export const triggerRefresh = () =>
  post<{ status: string; message: string }>('/api/refresh', {})
