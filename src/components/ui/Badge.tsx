import { cn, getScoreBadgeClass, getSeverityClass } from '@/lib/utils'

interface ScoreBadgeProps {
  score: number
  label: string
  className?: string
}

export function ScoreBadge({ score, label, className }: ScoreBadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border',
        getScoreBadgeClass(score),
        className,
      )}
    >
      {label}
    </span>
  )
}

interface SeverityBadgeProps {
  severity: string
  children: React.ReactNode
  className?: string
}

export function SeverityBadge({ severity, children, className }: SeverityBadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border',
        getSeverityClass(severity),
        className,
      )}
    >
      {children}
    </span>
  )
}
