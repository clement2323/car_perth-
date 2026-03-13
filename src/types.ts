export interface Alert {
  type: 'bonus' | 'warning' | 'critical'
  message: string
  cost: number
  severity: 'bonus' | 'low' | 'medium' | 'high' | 'critical'
  km_threshold: number | null
}

export interface Listing {
  make: string
  model: string
  year: number
  km: number
  price: number
  seller_type: 'dealer' | 'private'
  dealer_name: string | null
  location: string | null
  listing_url: string | null
  date_scraped: string | null
  source: string | null
  badge: string | null
  transmission: string | null
  score: number
  score_category: string
  score_color: string
  prix_score: number
  km_score: number
  fiabilite_score: number
  annee_score: number
  alerts: Alert[]
  alerts_count: number
  alerts_detail: string | null
  median_price: number | null
}

export interface CapitalListing {
  make: string
  model: string
  year: number
  km: number
  price: number
  dealer_name: string | null
  listing_url: string | null
  market_median: number | null
  diff_pct: number | null
}

export interface ModelStat {
  make: string
  model: string
  count: number
  median_price: number
  min_price: number
  max_price: number
  median_km: number
  avg_score: number | null
  last_scraped: string | null
}

export interface DangerZone {
  km_threshold: number
  issue: string
  severity: string
  repair_cost_aud: number
}

export interface ReliabilityInfo {
  best_years: number[]
  avoid_years: number[]
  timing_type: 'chain' | 'belt'
  km_belt_change: number | null
  class_action: boolean
  class_action_url: string | null
  base_reliability_score: number
  avg_annual_service_cost_aud: number
  depreciation_5yr_pct: number
  danger_zones: DangerZone[]
  notes: string
}

export interface TcoResult {
  purchase_price: number
  total_service: number
  total_repairs: number
  resale_value: number
  net_total_cost: number
  annual_cost: number
}

export interface Filters {
  max_price: number
  max_km: number
  models: string[]
  seller_type: 'all' | 'dealer' | 'private'
}

export type TabId = 'deals' | 'market' | 'capital' | 'tco'
