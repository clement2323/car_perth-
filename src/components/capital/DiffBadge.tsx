interface Props {
  diff: number | null
}

export default function DiffBadge({ diff }: Props) {
  if (diff === null || diff === undefined) {
    return <span className="text-xs text-slate-400">N/A</span>
  }

  const isGood = diff <= -10
  const isNeutral = diff > -10 && diff < 10
  const isBad = diff >= 10

  const cls = isGood
    ? 'bg-emerald-100 text-emerald-700'
    : isNeutral
    ? 'bg-amber-100 text-amber-700'
    : 'bg-red-100 text-red-700'

  const sign = diff > 0 ? '+' : ''

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold ${cls}`}>
      {sign}{diff.toFixed(1)}%
    </span>
  )
}
