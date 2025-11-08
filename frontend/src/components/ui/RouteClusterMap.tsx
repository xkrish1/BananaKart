"use client"

interface Cluster {
  id: string
  lat: number
  lng: number
  count: number
}

interface RouteClusterMapProps {
  clusters: Cluster[]
  selectedCluster?: string | null
  onSelectCluster?: (id: string) => void
}

export default function RouteClusterMap({ clusters, selectedCluster, onSelectCluster }: RouteClusterMapProps) {
  // Simplified SVG map visualization (Mapbox would be integrated here with proper API key)
  return (
    <div className="w-full h-full bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 relative overflow-hidden">
      {/* Map background */}
      <svg className="w-full h-full" viewBox="0 0 500 600">
        {/* Grid background */}
        <defs>
          <pattern id="grid" width="50" height="50" patternUnits="userSpaceOnUse">
            <path d="M 50 0 L 0 0 0 50" fill="none" stroke="#334155" strokeWidth="0.5" />
          </pattern>
        </defs>
        <rect width="500" height="600" fill="url(#grid)" />

        {/* Cluster markers */}
        {clusters.map((cluster) => {
          const x = (cluster.lng + 74.006) * 50
          const y = (cluster.lat - 40.7128) * 50 + 300
          const isSelected = selectedCluster === cluster.id

          return (
            <g key={cluster.id} onClick={() => onSelectCluster?.(cluster.id)} className="cursor-pointer">
              {/* Cluster circle background */}
              <circle
                cx={x}
                cy={y}
                r={isSelected ? 35 : 25}
                fill={isSelected ? "#2563eb" : "#06b6d4"}
                opacity={isSelected ? 0.9 : 0.7}
                className="transition-all"
              />
              {/* Cluster count */}
              <text
                x={x}
                y={y}
                textAnchor="middle"
                dy="0.3em"
                className="fill-white font-bold text-sm"
                pointerEvents="none"
              >
                {cluster.count}
              </text>
            </g>
          )
        })}
      </svg>

      {/* Info overlay */}
      <div className="absolute top-4 left-4 right-4 card-glass p-3">
        <p className="text-xs text-muted">Showing {clusters.length} delivery clusters</p>
      </div>
    </div>
  )
}
