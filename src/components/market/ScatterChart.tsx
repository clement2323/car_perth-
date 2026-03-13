'use client'

import {
  ScatterChart as ReScatter,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import type { Listing } from '@/types'
import { formatPrice, formatKm } from '@/lib/utils'

const MODEL_COLORS: Record<string, string> = {
  'Toyota Corolla': '#6366f1',
  'Mazda 3':        '#10b981',
  'Honda Civic':    '#f59e0b',
  'Hyundai i30':    '#ef4444',
  'Honda Jazz':     '#8b5cf6',
  'Suzuki Swift':   '#06b6d4',
}

interface Props {
  listings: Listing[]
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function CustomTooltip({ active, payload }: any) {
  if (!active || !payload?.length) return null
  const d = payload[0].payload as Listing
  return (
    <div className="bg-white border border-slate-200 rounded-lg p-3 shadow-lg text-xs">
      <p className="font-semibold text-slate-900 mb-1">{d.year} {d.make} {d.model}</p>
      <p className="text-slate-600">Prix : <span className="font-medium text-slate-900">{formatPrice(d.price)}</span></p>
      <p className="text-slate-600">KM : <span className="font-medium text-slate-900">{formatKm(d.km)}</span></p>
      <p className="text-slate-600">Score : <span className="font-medium text-slate-900">{d.score}/100</span></p>
      {d.dealer_name && <p className="text-slate-500 mt-1">{d.dealer_name}</p>}
    </div>
  )
}

export default function ScatterChart({ listings }: Props) {
  // Grouper par make+model
  const groups = listings.reduce<Record<string, Listing[]>>((acc, l) => {
    const key = `${l.make} ${l.model}`
    if (!acc[key]) acc[key] = []
    acc[key].push(l)
    return acc
  }, {})

  return (
    <ResponsiveContainer width="100%" height={380}>
      <ReScatter>
        <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
        <XAxis
          type="number"
          dataKey="km"
          name="Kilométrage"
          tickFormatter={v => `${(v / 1000).toFixed(0)}k`}
          label={{ value: 'Kilométrage', position: 'insideBottom', offset: -4, fontSize: 12, fill: '#94a3b8' }}
          tick={{ fontSize: 11, fill: '#94a3b8' }}
        />
        <YAxis
          type="number"
          dataKey="price"
          name="Prix"
          tickFormatter={v => `$${(v / 1000).toFixed(0)}k`}
          label={{ value: 'Prix (AUD)', angle: -90, position: 'insideLeft', offset: 10, fontSize: 12, fill: '#94a3b8' }}
          tick={{ fontSize: 11, fill: '#94a3b8' }}
        />
        <Tooltip content={<CustomTooltip />} />
        <Legend wrapperStyle={{ fontSize: 12, paddingTop: 16 }} />
        {Object.entries(groups).map(([key, data]) => (
          <Scatter
            key={key}
            name={key}
            data={data}
            fill={MODEL_COLORS[key] ?? '#94a3b8'}
            opacity={0.8}
          />
        ))}
      </ReScatter>
    </ResponsiveContainer>
  )
}
