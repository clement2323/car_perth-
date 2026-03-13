import type { Alert } from '@/types'
import { SeverityBadge } from '@/components/ui/Badge'
import { formatPrice } from '@/lib/utils'

interface Props {
  alerts: Alert[]
}

export default function AlertList({ alerts }: Props) {
  if (!alerts || alerts.length === 0) return null

  return (
    <div className="mt-3 pt-3 border-t border-slate-100 space-y-1.5">
      {alerts.map((alert, i) => (
        <div key={i} className="flex items-start gap-2">
          <SeverityBadge severity={alert.severity} className="shrink-0 mt-0.5">
            {alert.severity === 'bonus' ? 'Bonus' : alert.severity}
          </SeverityBadge>
          <div className="flex-1 min-w-0">
            <p className="text-xs text-slate-600 leading-snug">{alert.message}</p>
            {alert.cost > 0 && (
              <p className="text-xs text-slate-400 mt-0.5">
                Coût estimé : <span className="font-medium text-slate-600">{formatPrice(alert.cost)}</span>
              </p>
            )}
          </div>
        </div>
      ))}
    </div>
  )
}
