"use client"

interface ActionCardProps {
  title: string
  description: string
  action: string
  onAction: () => void
}

export default function ActionCard({ title, description, action, onAction }: ActionCardProps) {
  return (
    <div className="card-glass p-4">
      <h4 className="font-semibold text-sm mb-1">{title}</h4>
      <p className="text-xs text-muted mb-3">{description}</p>
      <button onClick={onAction} className="btn-primary text-xs py-1 px-3 w-full">
        {action}
      </button>
    </div>
  )
}
