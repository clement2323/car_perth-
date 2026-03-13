'use client'

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ReferenceLine,
  ResponsiveContainer,
} from 'recharts'
import type { TcoResult } from '@/types'
import { formatPrice } from '@/lib/utils'

interface Props {
  tco: TcoResult
  years: number
}

export default function TcoBreakdown({ tco, years }: Props) {
  const data = [
    {
      name: 'Coûts totaux',
      'Achat':       tco.purchase_price,
      'Entretiens':  tco.total_service,
      'Réparations': tco.total_repairs,
    },
  ]

  return (
    <div className="space-y-4">
      {/* Résumé */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {[
          { label: 'Achat',         value: tco.purchase_price, color: 'text-indigo-600' },
          { label: `Entretiens (${years} ans)`, value: tco.total_service, color: 'text-amber-600' },
          { label: 'Réparations est.', value: tco.total_repairs, color: 'text-red-600' },
          { label: 'Valeur revente', value: -tco.resale_value, color: 'text-emerald-600' },
        ].map(item => (
          <div key={item.label} className="bg-white rounded-lg border border-slate-200 p-3">
            <p className="text-xs text-slate-500">{item.label}</p>
            <p className={`text-lg font-semibold ${item.color}`}>
              {item.value < 0 ? '-' : ''}{formatPrice(Math.abs(item.value))}
            </p>
          </div>
        ))}
      </div>

      {/* Coût net */}
      <div className="bg-slate-900 rounded-xl p-4 flex items-center justify-between">
        <div>
          <p className="text-slate-400 text-sm">Coût net total sur {years} an{years > 1 ? 's' : ''}</p>
          <p className="text-white text-2xl font-bold">{formatPrice(tco.net_total_cost)}</p>
        </div>
        <div className="text-right">
          <p className="text-slate-400 text-sm">Soit par an</p>
          <p className="text-indigo-400 text-xl font-bold">{formatPrice(tco.annual_cost)}</p>
        </div>
      </div>

      {/* Bar chart */}
      <div className="bg-white rounded-xl border border-slate-200 p-4">
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
            <XAxis dataKey="name" tick={false} />
            <YAxis tickFormatter={v => `$${(v / 1000).toFixed(0)}k`} tick={{ fontSize: 11, fill: '#94a3b8' }} />
            <Tooltip formatter={(v: number) => formatPrice(v)} />
            <Legend wrapperStyle={{ fontSize: 12 }} />
            <Bar dataKey="Achat"       stackId="a" fill="#6366f1" radius={[0,0,0,0]} />
            <Bar dataKey="Entretiens"  stackId="a" fill="#f59e0b" />
            <Bar dataKey="Réparations" stackId="a" fill="#ef4444" radius={[4,4,0,0]} />
            <ReferenceLine
              y={tco.resale_value}
              stroke="#10b981"
              strokeDasharray="4 4"
              label={{ value: 'Revente', position: 'right', fontSize: 11, fill: '#10b981' }}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
