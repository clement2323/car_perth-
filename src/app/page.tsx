'use client'

import { useState } from 'react'
import AppShell from '@/components/layout/AppShell'
import DealsTab from '@/components/deals/DealsTab'
import MarketTab from '@/components/market/MarketTab'
import CapitalTab from '@/components/capital/CapitalTab'
import TcoTab from '@/components/tco/TcoTab'
import type { Filters, TabId } from '@/types'

const DEFAULT_FILTERS: Filters = {
  max_price: 15000,
  max_km: 200000,
  models: [],
  seller_type: 'all',
}

export default function Home() {
  const [activeTab, setActiveTab] = useState<TabId>('deals')
  const [filters, setFilters] = useState<Filters>(DEFAULT_FILTERS)

  return (
    <AppShell
      activeTab={activeTab}
      onTabChange={setActiveTab}
      filters={filters}
      onFiltersChange={setFilters}
    >
      {activeTab === 'deals'   && <DealsTab filters={filters} />}
      {activeTab === 'market'  && <MarketTab filters={filters} />}
      {activeTab === 'capital' && <CapitalTab />}
      {activeTab === 'tco'     && <TcoTab />}
    </AppShell>
  )
}
