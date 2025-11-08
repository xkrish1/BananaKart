"use client"

import { useEffect, useState } from "react"
import LocalCard from "@/components/ui/LocalCard"
import KpiCard from "@/components/ui/KpiCard"
import { mockKPI, mockCatalog } from "@/lib/mockData"

interface LocalStore {
  id: string
  name: string
  image: string
  distance: string
  rating: number
  tags: string[]
}

const mockLocalStores: LocalStore[] = [
  {
    id: "1",
    name: "Green Valley Farm",
    image: "/organic-farm-produce.png",
    distance: "2.3 km",
    rating: 4.8,
    tags: ["Organic", "Local", "Fresh"],
  },
  {
    id: "2",
    name: "Sunrise Market",
    image: "/farmer-market-vegetables.jpg",
    distance: "1.5 km",
    rating: 4.6,
    tags: ["Seasonal", "Certified", "Quality"],
  },
  {
    id: "3",
    name: "Urban Harvest Co",
    image: "/urban-garden-herbs.jpg",
    distance: "3.1 km",
    rating: 4.9,
    tags: ["Sustainable", "Fair Trade"],
  },
]

export default function HomePage() {
  const [stores, setStores] = useState<LocalStore[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setTimeout(() => {
      setStores(mockLocalStores)
      setLoading(false)
    }, 300)
  }, [])

  return (
    <div className="px-4 py-6 max-w-2xl mx-auto space-y-6">
      {/* Hero Banner */}
      <section className="rounded-lg overflow-hidden bg-primary text-primary-foreground p-6">
        <h2 className="text-3xl font-bold mb-2">Fresh From Local</h2>
        <p className="text-sm opacity-90">Support your community. Get farm-fresh produce delivered today.</p>
      </section>

      {/* KPI Cards */}
      <section>
        <h3 className="text-sm font-semibold text-muted-foreground mb-3">Your Impact</h3>
        <div className="grid grid-cols-2 gap-3">
          <KpiCard label="Orders" value={mockKPI.totalOrders.toString()} icon="📦" />
          <KpiCard label="Carbon Saved" value={mockKPI.carbonReduction} icon="🌱" />
          <KpiCard label="Communities" value={mockKPI.communitySupported.toString()} icon="👥" />
          <KpiCard label="Sustainability" value={mockKPI.activeSustainability.toString()} icon="♻️" />
        </div>
      </section>

      {/* Local Stores */}
      <section>
        <h3 className="text-lg font-semibold mb-4">Stores Near You</h3>
        {loading ? (
          <div className="grid grid-cols-1 gap-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="card-glass h-48 animate-pulse" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4">
            {stores.map((store) => (
              <LocalCard key={store.id} store={store} />
            ))}
          </div>
        )}
      </section>

      {/* Quick Reorder */}
      <section>
        <h3 className="text-lg font-semibold mb-4">Featured Products</h3>
        <div className="grid grid-cols-2 gap-3">
          {mockCatalog.products.slice(0, 4).map((product) => (
            <div key={product.id} className="card-glass p-3 hover:border-accent/30 transition">
              <div className="bg-muted h-24 rounded mb-2 overflow-hidden">
                <img
                  src={product.image || "/placeholder.svg"}
                  alt={product.name}
                  className="w-full h-full object-cover"
                />
              </div>
              <p className="font-medium text-sm">{product.name}</p>
              <p className="text-primary font-bold text-sm">${product.price}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}
