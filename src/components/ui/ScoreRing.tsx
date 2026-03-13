'use client'

import { getScoreColor } from '@/lib/utils'

interface Props {
  score: number
  size?: number
}

export default function ScoreRing({ score, size = 64 }: Props) {
  const strokeWidth = Math.max(5, size * 0.09)
  const r = (size - strokeWidth) / 2
  const cx = size / 2
  const cy = size / 2
  const circumference = 2 * Math.PI * r
  const clamped = Math.min(100, Math.max(0, score))
  const offset = circumference * (1 - clamped / 100)
  const color = getScoreColor(score)

  return (
    <div style={{ position: 'relative', width: size, height: size, flexShrink: 0 }}>
      {/* SVG anneau rotaté -90° pour départ au sommet */}
      <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
        {/* Piste de fond */}
        <circle cx={cx} cy={cy} r={r} fill="none" stroke="#e2e8f0" strokeWidth={strokeWidth} />
        {/* Arc de progression */}
        <circle
          cx={cx} cy={cy} r={r}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeDasharray={`${circumference}`}
          strokeDashoffset={`${offset}`}
          strokeLinecap="round"
          style={{ transition: 'stroke-dashoffset 0.6s ease, stroke 0.3s ease' }}
        />
      </svg>
      {/* Score centré (div overlay pour éviter la rotation du texte) */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: size * 0.26,
          fontWeight: 700,
          color,
          fontVariantNumeric: 'tabular-nums',
          lineHeight: 1,
        }}
      >
        {Math.round(score)}
      </div>
    </div>
  )
}
