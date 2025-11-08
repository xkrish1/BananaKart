"use client"

interface ImpactWidgetProps {
  carbonSaved: string
  itemsCount: number
}

export default function ImpactWidget({ carbonSaved, itemsCount }: ImpactWidgetProps) {
  return (
    <div className="card-glass p-4 bg-gradient-to-r from-green-900/50 to-emerald-900/50 border-green-700">
      <div className="flex items-center gap-3">
        <div className="text-3xl">🌱</div>
        <div className="flex-1">
          <p className="text-xs text-muted">Your Impact</p>
          <p className="font-bold text-green-400">{carbonSaved}kg CO2 saved</p>
          <p className="text-xs text-muted">{itemsCount} items from local producers</p>
        </div>
      </div>
    </div>
  )
}
