"use client"

interface KpiCardProps {
  label: string
  value: string
  icon: string
}

export default function KpiCard({ label, value, icon }: KpiCardProps) {
  return (
    <div className="card-glass p-6 text-center group hover:bg-muted transition-colors">
      <div className="text-4xl mb-3 group-hover:scale-110 transition-transform duration-300">{icon}</div>
      <p className="text-muted-foreground text-sm mb-2 font-medium">{label}</p>
      <p className="text-2xl font-bold text-primary">{value}</p>
    </div>
  )
}
