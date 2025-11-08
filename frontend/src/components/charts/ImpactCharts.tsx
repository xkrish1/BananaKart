"use client"

const orderData = [
  { month: "Jan", orders: 45, carbon: 2.3 },
  { month: "Feb", orders: 52, carbon: 2.8 },
  { month: "Mar", orders: 68, carbon: 3.5 },
  { month: "Apr", orders: 79, carbon: 4.1 },
  { month: "May", orders: 95, carbon: 4.9 },
  { month: "Jun", orders: 112, carbon: 5.7 },
]

export default function ImpactCharts() {
  const maxOrders = Math.max(...orderData.map((d) => d.orders))
  const maxCarbon = Math.max(...orderData.map((d) => d.carbon))
  const chartHeight = 250
  const barWidth = 50

  return (
    <div className="space-y-6">
      {/* Orders Bar Chart */}
      <div className="card-glass p-4">
        <h4 className="text-sm font-semibold mb-4">Monthly Orders</h4>
        <svg width="100%" height={chartHeight} className="overflow-x-auto">
          {orderData.map((d, i) => {
            const barHeight = (d.orders / maxOrders) * (chartHeight - 40)
            const x = i * barWidth + 20
            const y = chartHeight - barHeight - 20
            return (
              <g key={`bar-${i}`}>
                <rect x={x} y={y} width={barWidth - 10} height={barHeight} fill="#2563eb" rx="4" />
                <text x={x + (barWidth - 10) / 2} y={chartHeight - 5} textAnchor="middle" fontSize="12" fill="#94a3b8">
                  {d.month}
                </text>
                <text x={x + (barWidth - 10) / 2} y={y - 5} textAnchor="middle" fontSize="11" fill="#10b981">
                  {d.orders}
                </text>
              </g>
            )
          })}
        </svg>
      </div>

      {/* Carbon Reduction Line Chart */}
      <div className="card-glass p-4">
        <h4 className="text-sm font-semibold mb-4">Carbon Reduction (T)</h4>
        <svg
          width="100%"
          height={chartHeight}
          className="overflow-x-auto"
          viewBox={`0 0 ${orderData.length * barWidth} ${chartHeight}`}
        >
          {/* Grid lines */}
          {[0, 1, 2, 3, 4, 5].map((i) => (
            <line
              key={`grid-${i}`}
              x1="0"
              y1={20 + i * ((chartHeight - 40) / 5)}
              x2={orderData.length * barWidth}
              y2={20 + i * ((chartHeight - 40) / 5)}
              stroke="#475569"
              strokeDasharray="4"
            />
          ))}

          <polyline
            points={orderData
              .map((d, i) => {
                const x = i * barWidth + barWidth / 2
                const y = chartHeight - 20 - (d.carbon / maxCarbon) * (chartHeight - 40)
                return `${x},${y}`
              })
              .join(" ")}
            fill="none"
            stroke="#10b981"
            strokeWidth="2"
          />

          {/* Dots */}
          {orderData.map((d, i) => {
            const x = i * barWidth + barWidth / 2
            const y = chartHeight - 20 - (d.carbon / maxCarbon) * (chartHeight - 40)
            return <circle key={`dot-${i}`} cx={x} cy={y} r="4" fill="#10b981" />
          })}

          {/* Labels */}
          {orderData.map((d, i) => (
            <g key={`label-${i}`}>
              <text
                x={i * barWidth + barWidth / 2}
                y={chartHeight - 5}
                textAnchor="middle"
                fontSize="12"
                fill="#94a3b8"
              >
                {d.month}
              </text>
              <text x={i * barWidth + barWidth / 2} y={20} textAnchor="middle" fontSize="11" fill="#10b981">
                {d.carbon.toFixed(1)}T
              </text>
            </g>
          ))}
        </svg>
      </div>
    </div>
  )
}
