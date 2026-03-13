import Sidebar from './Sidebar'
import type { Filters, TabId } from '@/types'

interface Props {
  activeTab: TabId
  onTabChange: (tab: TabId) => void
  filters: Filters
  onFiltersChange: (f: Filters) => void
  children: React.ReactNode
}

export default function AppShell({ activeTab, onTabChange, filters, onFiltersChange, children }: Props) {
  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar
        activeTab={activeTab}
        onTabChange={onTabChange}
        filters={filters}
        onFiltersChange={onFiltersChange}
      />
      <main className="flex-1 overflow-y-auto bg-slate-50">
        <div className="max-w-7xl mx-auto px-6 py-6">
          {children}
        </div>
      </main>
    </div>
  )
}
