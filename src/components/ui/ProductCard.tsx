"use client"

import { useBananakart } from "@/context/BananakartContext"
import { useState } from "react"

interface Product {
  id: string
  name: string
  price: number
  category: string
  image?: string
}

interface ProductCardProps {
  product: Product
  onSelect?: (product: Product) => void
}

export default function ProductCard({ product, onSelect }: ProductCardProps) {
  const { addToCart } = useBananakart()
  const [qty, setQty] = useState(1)

  const handleAddToCart = () => {
    addToCart({ id: product.id, name: product.name, price: product.price, quantity: qty })
  }

  return (
    <div className="card-glass overflow-hidden group">
      <div className="h-40 bg-muted overflow-hidden relative">
        <img
          src={product.image || "/placeholder.svg"}
          alt={product.name}
          className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
        />
        <div className="absolute inset-0 bg-black/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
      </div>
      <div className="p-4">
        <p className="text-xs text-muted-foreground mb-1 font-medium uppercase tracking-wider">{product.category}</p>
        <h4 className="font-semibold text-foreground mb-3 text-sm line-clamp-2">{product.name}</h4>
        <div className="flex justify-between items-center">
          <p className="text-lg font-bold text-primary">${product.price}</p>
          <button onClick={handleAddToCart} className="btn-secondary text-xs py-1.5 px-3">
            + Add
          </button>
        </div>
      </div>
    </div>
  )
}
