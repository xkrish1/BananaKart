"use client"

import { useState, useEffect } from "react"
import KpiCard from "@/components/ui/KpiCard"
import ImpactCharts from "@/components/charts/ImpactCharts"
import KnotHub from "@/components/ui/KnotHub"
import { mockKPI, mockOrders } from "@/lib/mockData"

export default function DashboardPage() {
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setTimeout(() => setLoading(false), 300)
  }, [])

  if (loading) {
    return (
      <div className="px-4 py-6 max-w-4xl mx-auto">
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="card-glass h-32 animate-pulse" />
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="px-4 py-6 max-w-4xl mx-auto space-y-6">
      {/* KPI Overview */}
      <section>
        <h2 className="text-2xl font-bold mb-4">Analytics</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <KpiCard label="Total Orders" value={mockKPI.totalOrders.toString()} icon="📦" />
          <KpiCard label="Active Users" value={mockKPI.activeSustainability.toString()} icon="👥" />
          <KpiCard label="Carbon Saved" value={mockKPI.carbonReduction} icon="🌍" />
          <KpiCard label="Communities" value={mockKPI.communitySupported.toString()} icon="🤝" />
        </div>
      </section>

      {/* Impact Charts */}
      <section>
        <h3 className="text-lg font-semibold mb-4">Impact Over Time</h3>
        <ImpactCharts />
      </section>

      {/* Recent Orders */}
      <section>
        <h3 className="text-lg font-semibold mb-4">Recent Orders</h3>
        <div className="space-y-2">
          {mockOrders.map((order) => (
            <div key={order.id} className="card-glass p-3">
              <div className="flex justify-between items-center mb-2">
                <p className="font-semibold text-sm">{order.id}</p>
                <p
                  className={`text-xs font-bold px-2 py-1 rounded ${
                    order.status === "delivered"
                      ? "bg-secondary text-primary-foreground"
                      : "bg-primary text-primary-foreground"
                  }`}
                >
                  {order.status}
                </p>
              </div>
              <p className="text-xs text-muted-foreground mb-1">{order.date}</p>
              <p className="text-primary font-bold">${order.total}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Knot Hub */}
      <section>
        <h3 className="text-lg font-semibold mb-4">Smart Ordering</h3>
        <KnotHub />
      </section>
    </div>
  )
}
