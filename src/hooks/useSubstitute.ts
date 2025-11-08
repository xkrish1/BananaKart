"use client"

import { useMemo } from "react"
import { mockCatalog } from "@/lib/mockData"

export function useSubstitute(productId: string) {
  const substitutes = useMemo(() => {
    const product = mockCatalog.products.find((p) => p.id === productId)
    if (!product) return []
    return mockCatalog.products.filter((p) => p.id !== productId && p.category === product.category)
  }, [productId])

  return { substitutes }
}
