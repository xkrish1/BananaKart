"use client"

import { useEffect, useState } from "react"
import RouteClusterMap from "@/components/ui/RouteClusterMap"
import { mockRoutes } from "@/lib/mockData"

export default function MapPage() {
  const [clusters, setClusters] = useState(mockRoutes.clusters)
  const [selectedCluster, setSelectedCluster] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Simulate API call to /api/routes
    setTimeout(() => {
      setLoading(false)
    }, 500)
  }, [])

  return (
    <div className="h-screen w-full flex flex-col">
      {/* Map Area */}
      <div className="flex-1 relative bg-slate-900">
        {loading ? (
          <div className="w-full h-full flex items-center justify-center">
            <div className="text-center">
              <div className="text-3xl mb-2">🗺️</div>
              <p className="text-muted">Loading routes...</p>
            </div>
          </div>
        ) : (
          <RouteClusterMap clusters={clusters} selectedCluster={selectedCluster} onSelectCluster={setSelectedCluster} />
        )}
      </div>

      {/* Cluster Info Panel */}
      {selectedCluster && (
        <div className="border-t border-slate-700 bg-slate-900 p-4">
          <div className="max-w-2xl mx-auto">
            <h3 className="font-semibold mb-2">Delivery Cluster</h3>
            <p className="text-sm text-muted mb-3">
              {clusters.find((c) => c.id === selectedCluster)?.count} orders in this area
            </p>
            <button onClick={() => setSelectedCluster(null)} className="btn-secondary text-sm">
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
