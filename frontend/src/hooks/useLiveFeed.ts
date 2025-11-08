"use client"

import { useState, useEffect } from "react"

export function useLiveFeed() {
  const [stats, setStats] = useState({ activeOrders: 12, itemsProcessed: 245, carbonReduced: 2.4 })

  useEffect(() => {
    // Simulate polling /api/livefeed
    const interval = setInterval(() => {
      setStats((prev) => ({
        activeOrders: prev.activeOrders + Math.floor(Math.random() * 3) - 1,
        itemsProcessed: prev.itemsProcessed + Math.floor(Math.random() * 5),
        carbonReduced: +(prev.carbonReduced + Math.random() * 0.1).toFixed(1),
      }))
    }, 3000)
    return () => clearInterval(interval)
  }, [])

  return { stats }
}
