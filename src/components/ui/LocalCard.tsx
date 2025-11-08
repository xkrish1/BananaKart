"use client"

import Link from "next/link"
import { useState } from "react"

interface LocalCardProps {
  store: {
    id: string
    name: string
    image: string
    distance: string
    rating: number
    tags: string[]
  }
}

export default function LocalCard({ store }: LocalCardProps) {
  const [isLoading, setIsLoading] = useState(false)

  return (
    <Link href={`/explore?store=${store.id}`}>
      <div className="card-glass overflow-hidden group cursor-pointer">
        <div className="relative overflow-hidden h-48 bg-muted">
          <img
            src={store.image || "/placeholder.svg"}
            alt={store.name}
            className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
          />
          <div className="absolute inset-0 bg-black/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
          <div className="absolute top-3 right-3 bg-primary text-primary-foreground text-xs font-bold px-3 py-1.5 rounded-full shadow-sm group-hover:shadow-md transition-shadow">
            ⭐ {store.rating}
          </div>
        </div>
        <div className="p-5">
          <h4 className="font-bold text-foreground text-lg">{store.name}</h4>
          <p className="text-sm text-muted-foreground mb-4">{store.distance} away</p>
          <div className="flex flex-wrap gap-2">
            {store.tags.map((tag) => (
              <span
                key={tag}
                className="text-xs bg-muted text-foreground font-semibold px-3 py-1.5 rounded-full border border-border"
              >
                {tag}
              </span>
            ))}
          </div>
        </div>
      </div>
    </Link>
  )
}
