"use client"

import { useMemo } from "react"
import { mockRoutes } from "@/lib/mockData"

export function useOptimize() {
  const clusters = useMemo(() => {
    return mockRoutes.clusters
  }, [])

  return { clusters }
}
