"use client"

import { useState } from "react"
import { mockCatalog } from "@/lib/mockData"

export function useCatalog() {
  const [products, setProducts] = useState(mockCatalog.products)
  const [loading, setLoading] = useState(false)

  const getProductsByCategory = (category: string) => {
    return products.filter((p) => p.category === category)
  }

  const searchProducts = (query: string) => {
    return products.filter((p) => p.name.toLowerCase().includes(query.toLowerCase()))
  }

  return {
    products,
    loading,
    getProductsByCategory,
    searchProducts,
  }
}
