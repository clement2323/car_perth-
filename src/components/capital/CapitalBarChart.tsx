'use client'

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  Cell,
  ResponsiveContainer,
} from 'recharts'
import type { CapitalListing } from '@/types'
import { formatPrice } from '@/lib/utils'

interface Props {
  listings: CapitalListing[]
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function CustomTooltip({ active, payload }: any) {
  if (!active || !payload?.length) return null
  const d = payload[0].payload as CapitalListing & { label: string }
  return (
    <div className="bg-white border border-slate-200 rounded-lg p-3 shadow-lg text-xs">
      <p className="font-semibold text-slate-900 mb-1">{d.label}</p>
      <p>Prix Capital : <span className="font-medium">{formatPrice(d.price)}</span></p>
      {d.market_median && (
        <p>Médiane marché : <span className="font-medium">{formatPrice(d.market_median)}</span></p>
      )}
      {d.diff_pct !== null && d.diff_pct !== undefined && (
        <p className={`font-semibold mt-1 ${d.diff_pct <= -10 ? 'text-emerald-600' : d.diff_pct >= 10 ? 'text-red-600' : 'text-amber-600'}`}>
          {d.diff_pct > 0 ? '+' : ''}{d.diff_pct.toFixed(1)}% vs marché
        </p>
      )}
    </div>
  )
}

function getBarColor(diff: number | null): string {
  if (diff === null) return '#94a3b8'
  if (diff <= -10) return '#10b981'
  if (diff >= 10)  return '#ef4444'
  return '#f59e0b'
}

export default function CapitalBarChart({ listings }: Props) {
  const data = listings
    .filter(l => l.diff_pct !== null)
    .slice(0, 20)
    .map(l => ({
      ...l,
      label: `${l.year} ${l.make} ${l.model}`,
    }))
    .sort((a, b) => (a.diff_pct ?? 0) - (b.diff_pct ?? 0))

  return (
    <ResponsiveContainer width="100%" height={Math.max(300, data.length * 32)}>
      <BarChart data={data} layout="vertical" margin={{ top: 0, right: 60, bottom: 0, left: 140 }}>
        <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#f1f5f9" />
        <XAxis
          type="number"
          tickFormatter={v => `${v > 0 ? '+' : ''}${v}%`}
          tick={{ fontSize: 11, fill: '#94a3b8' }}
        />
        <YAxis
          type="category"
          dataKey="label"
          tick={{ fontSize: 11, fill: '#64748b' }}
          width={136}
        />
        <Tooltip content={<CustomTooltip />} />
        <ReferenceLine x={0} stroke="#cbd5e1" strokeWidth={1.5} />
        <Bar dataKey="diff_pct" radius={[0, 4, 4, 0]}>
          {data.map((entry, index) => (
            <Cell key={index} fill={getBarColor(entry.diff_pct)} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
