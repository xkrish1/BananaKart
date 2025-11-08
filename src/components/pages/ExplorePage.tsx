"use client"

import { useState, useMemo } from "react"
import ProductCard from "@/components/ui/ProductCard"
import { useCatalog } from "@/hooks/useCatalog"

export default function ExplorePage() {
  const [search, setSearch] = useState("")
  const [selectedCategory, setSelectedCategory] = useState("all")
  const { products } = useCatalog()

  const categories = ["all", ...new Set(products.map((p) => p.category))]

  const filtered = useMemo(() => {
    return products.filter((p) => {
      const matchesSearch = p.name.toLowerCase().includes(search.toLowerCase())
      const matchesCategory = selectedCategory === "all" || p.category === selectedCategory
      return matchesSearch && matchesCategory
    })
  }, [search, selectedCategory, products])

  return (
    <div className="px-4 py-6 max-w-2xl mx-auto space-y-6">
      {/* Search Bar */}
      <div>
        <input
          type="text"
          placeholder="Search products..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full bg-card border border-border rounded-lg px-4 py-3 text-foreground placeholder-muted-foreground focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/30 transition"
        />
      </div>

      {/* Category Filters */}
      <div>
        <p className="text-sm text-muted-foreground mb-2">Categories</p>
        <div className="flex flex-wrap gap-2">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3 py-1.5 rounded-lg text-sm transition capitalize ${
                selectedCategory === cat
                  ? "bg-primary text-primary-foreground"
                  : "bg-muted text-foreground hover:bg-border border border-border"
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Products Grid */}
      <section>
        <p className="text-sm text-muted-foreground mb-4">{filtered.length} products found</p>
        {filtered.length > 0 ? (
          <div className="grid grid-cols-2 gap-3">
            {filtered.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        ) : (
          <div className="card-glass p-8 text-center">
            <p className="text-muted-foreground">No products found matching your search.</p>
          </div>
        )}
      </section>
    </div>
  )
}
